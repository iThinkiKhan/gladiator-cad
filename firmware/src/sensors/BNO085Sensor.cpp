#include "BNO085Sensor.h"
#include <esp_timer.h>
#include <math.h>

namespace sensors {
namespace {
// Euler angles from a normalized *copy*; the native quaternion is never touched.
// Returns false for a quaternion that is not plausibly unit length.
bool eulerFrom(float real, float i, float j, float k,
               float &rollDeg, float &pitchDeg, float &yawDeg) {
  const float norm = real*real + i*i + j*j + k*k;
  if (!isfinite(norm) || norm <= 0.5F || norm >= 1.5F) return false;
  const float scale = 1.0F / sqrtf(norm);
  const float w=real*scale, x=i*scale, y=j*scale, z=k*scale;
  constexpr float deg = 57.295779513F;
  rollDeg = atan2f(2*(w*x+y*z),1-2*(x*x+y*y))*deg;
  pitchDeg = asinf(fmaxf(-1, fminf(1,2*(w*y-z*x))))*deg;
  yawDeg = atan2f(2*(w*z+x*y),1-2*(y*y+z*z))*deg;
  return true;
}
// Same, with the fixed sensor-to-chassis mount tilt removed:
//   q_chassis = q_sensor (x) conj(q_mount)
// The tilt is fixed in the body frame, so it composes on the right. Checked
// against a live quaternion: this leaves yaw unchanged to 0.004 deg, while
// left-multiplying rotates heading by ~0.45 deg, and either wrong order
// doubles the tilt instead of cancelling it. The native quaternion is not
// modified; a consumer wanting raw sensor-frame angles can recompute from it.
bool eulerFromMounted(float real, float i, float j, float k,
                      float &rollDeg, float &pitchDeg, float &yawDeg) {
  constexpr float halfRad = 0.0087266462F; // degrees -> radians, halved
  const float r = board::IMU_MOUNT_ROLL_DEG * halfRad;
  const float p = board::IMU_MOUNT_PITCH_DEG * halfRad;
  const float cr = cosf(r), sr = sinf(r), cp = cosf(p), sp = sinf(p);
  // conj of the mount quaternion built from (roll, pitch, yaw = 0)
  const float mw = cr*cp, mx = -sr*cp, my = -cr*sp, mz = sr*sp;
  const float w = real*mw - i*mx - j*my - k*mz;
  const float x = real*mx + i*mw + j*mz - k*my;
  const float y = real*my - i*mz + j*mw + k*mx;
  const float z = real*mz + i*my - j*mx + k*mw;
  return eulerFrom(w, x, y, z, rollDeg, pitchDeg, yawDeg);
}
} // namespace
const char *reportName(sh2_SensorId_t id) {
  switch (id) {
    case SH2_ROTATION_VECTOR: return "rotationVector";
    case SH2_GAME_ROTATION_VECTOR: return "gameRotationVector";
    case SH2_ACCELEROMETER: return "accelerometer";
    case SH2_GYROSCOPE_CALIBRATED: return "gyroscope";
    case SH2_MAGNETIC_FIELD_CALIBRATED: return "magnetometer";
    case SH2_LINEAR_ACCELERATION: return "linearAcceleration";
    case SH2_GRAVITY: return "gravity";
    case SH2_RAW_ACCELEROMETER: return "rawAccelerometer";
    case SH2_RAW_GYROSCOPE: return "rawGyroscope";
    case SH2_RAW_MAGNETOMETER: return "rawMagnetometer";
    default: return "unknown";
  }
}
BNO085Sensor::BNO085Sensor(I2CBus &bus, ImuData &data) : bus_(bus), data_(data), device_(-1) {
  const sh2_SensorId_t ids[] = {SH2_ROTATION_VECTOR, SH2_ACCELEROMETER, SH2_GYROSCOPE_CALIBRATED,
    SH2_MAGNETIC_FIELD_CALIBRATED, SH2_LINEAR_ACCELERATION, SH2_GRAVITY,
    SH2_RAW_ACCELEROMETER, SH2_RAW_GYROSCOPE, SH2_RAW_MAGNETOMETER,
    SH2_GAME_ROTATION_VECTOR};
  const uint32_t intervals[] = {10000,10000,10000,40000,20000,20000,10000,10000,40000,10000};
  for (size_t i = 0; i < IMU_REPORT_COUNT; ++i) {
    data_.reports[i].id = ids[i]; data_.reports[i].intervalUs = intervals[i];
  }
}
bool BNO085Sensor::begin() {
  auto &m = data_.meta;
  m.lastAttemptMs = millis(); m.health = SensorHealth::INITIALIZING;
  for (uint8_t address : {uint8_t(0x4A), uint8_t(0x4B)}) {
    if (!bus_.present(address)) continue;
    m.address = address;
    if (!device_.begin_I2C(address, &bus_.wire())) continue;
    data_.product = device_.prodIds;
    // SH2 can deliver MULTIPLE reports in a single packet. A last-event getter
    // loses the preceding reports; capture each callback instead.
    sh2_setSensorCallback(onReport, this);
    device_.wasReset();
    m.initialized = m.online = true;
    m.hasSample = false;
    configureReports();
    m.lastAttemptMs = millis();
    return true;
  }
  m.error(millis()); m.health = SensorHealth::OFFLINE; m.online = false;
  return false;
}
void BNO085Sensor::configureReports() {
  data_.derived.valid = false;
  for (auto &report : data_.reports) {
    report.sequenceKnown = false;
    report.hasSample = false;
    report.enabled = device_.enableReport(report.id, report.intervalUs);
    if (!report.enabled) { ++data_.configurationErrors; ++data_.meta.errorCount; }
  }
  configureCalibration();
}
void BNO085Sensor::configureCalibration() {
  // Neither the Adafruit wrapper nor the SH2 default turns on dynamic gyro and
  // magnetometer calibration, which is why those accuracy bytes never leave 0
  // however much the chassis moves. Read the config back rather than assuming
  // the write took: the answer is the only evidence that it is really running.
  constexpr uint8_t WANTED = SH2_CAL_ACCEL | SH2_CAL_GYRO | SH2_CAL_MAG;
  data_.calibration.requested = WANTED;
  if (sh2_setCalConfig(WANTED) != SH2_OK) ++data_.calibration.configErrors;
  uint8_t active = 0;
  data_.calibration.known = sh2_getCalConfig(&active) == SH2_OK;
  data_.calibration.active = data_.calibration.known ? active : 0;
  savedAccuracy_ = 0;
  data_.calibration.savedAccuracy = 0;
}
void BNO085Sensor::maybeSaveCalibration(uint32_t now) {
  // Converged calibration lives in RAM until it is written to the chip, so a
  // power cycle otherwise discards it. Save only while reports are actually
  // arriving: sh2_saveDcdNow busy-waits with no timeout, so it must not be
  // issued to a device that has already stopped answering.
  // Gate on whichever calibration has actually converged. Waiting on the
  // magnetometer-backed rotation vector alone would never save on a chassis
  // where the magnetometer cannot calibrate, discarding good gyro data.
  uint8_t accuracy = 0;
  bool fresh = false;
  for (size_t index : {IMU_GYRO_INDEX, IMU_ROTATION_INDEX, IMU_GAME_INDEX}) {
    const auto &report = data_.reports[index];
    if (!report.hasSample || now - report.lastUpdateMs > 100) continue;
    fresh = true;
    const uint8_t reported = report.native.status & 3;
    if (reported > accuracy) accuracy = reported;
  }
  if (!fresh || accuracy < 2 || accuracy <= savedAccuracy_) return;
  if (sh2_saveDcdNow() == SH2_OK) {
    savedAccuracy_ = accuracy;
    data_.calibration.savedAccuracy = accuracy;
    ++data_.calibration.saves;
  } else {
    ++data_.calibration.saveErrors;
  }
}
void BNO085Sensor::onReport(void *cookie, sh2_SensorEvent_t *event) {
  static_cast<BNO085Sensor *>(cookie)->receive(event);
}
void BNO085Sensor::receive(sh2_SensorEvent_t *event) {
  sh2_SensorValue_t value = {};
  if (sh2_decodeSensorEvent(&value, event) != SH2_OK) {
    ++data_.decodeErrors; data_.meta.error(millis()); return;
  }
  for (auto &report : data_.reports) {
    if (report.id != value.sensorId) continue;
    if (report.sequenceKnown) report.missedReports += uint8_t(value.sequence - report.native.sequence - 1);
    report.native = value;
    report.hasSample = report.sequenceKnown = true;
    report.receivedUs = esp_timer_get_time();
    report.lastUpdateMs = millis(); ++report.count;
    data_.meta.good(report.lastUpdateMs);
    if (value.sensorId == SH2_ROTATION_VECTOR) {
      const auto &q = value.un.rotationVector;
      auto &d = data_.derived;
      d.valid = eulerFromMounted(q.real, q.i, q.j, q.k, d.rollDeg, d.pitchDeg, d.yawDeg);
    } else if (value.sensorId == SH2_GAME_ROTATION_VECTOR) {
      const auto &q = value.un.gameRotationVector;
      auto &d = data_.gameDerived;
      d.valid = eulerFromMounted(q.real, q.i, q.j, q.k, d.rollDeg, d.pitchDeg, d.yawDeg);
    }
    return;
  }
}
void BNO085Sensor::update() {
  uint32_t now = millis();
  auto &m = data_.meta;
  m.age(now, 300, 2000);
  if (!m.online) {
    if (!tried_ || now-lastDiscoveryMs_ >= board::SENSOR_RETRY_MS) {
      tried_=true; lastDiscoveryMs_=now; begin();
    }
    return;
  }
  if (device_.wasReset()) {
    ++data_.resetCount; m.health = SensorHealth::INITIALIZING;
    configureReports(); m.lastAttemptMs = millis();
  }
  const uint64_t start = esp_timer_get_time();
  for (int i=0; i<4 && esp_timer_get_time()-start < 2500; ++i) sh2_service();
  now = millis();
  m.age(now, 300, 2000);
  if (m.health == SensorHealth::OK || m.health == SensorHealth::DEGRADED) {
    bool degraded = false;
    for (const auto &report : data_.reports) {
      if (!report.enabled || !report.hasSample || now-report.lastUpdateMs > 300) degraded = true;
    }
    // Orientation quality is judged on the game rotation vector: it is the
    // stream this chassis can actually calibrate, since the magnetometer sits
    // beside the drive motors. Judging it on the magnetometer-backed rotation
    // vector would pin health at DEGRADED forever and hide real faults.
    const auto &game = data_.reports[IMU_GAME_INDEX];
    if (!game.hasSample || (game.native.status & 3) < 2) degraded = true;
    m.health = degraded ? SensorHealth::DEGRADED : SensorHealth::OK;
  }
  const auto &rotation = data_.reports[IMU_ROTATION_INDEX];
  const auto &game = data_.reports[IMU_GAME_INDEX];
  if (!rotation.hasSample || now-rotation.lastUpdateMs > 300) data_.derived.valid=false;
  if (!game.hasSample || now-game.lastUpdateMs > 300) data_.gameDerived.valid=false;
  maybeSaveCalibration(now);
}
}
