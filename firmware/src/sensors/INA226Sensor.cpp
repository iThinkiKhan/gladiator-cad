#include "INA226Sensor.h"
#include <esp_timer.h>
#include <math.h>

namespace sensors {
bool INA226Sensor::begin() {
  auto &m = data_.meta;
  m.lastAttemptMs = millis();
  m.health = SensorHealth::INITIALIZING;
  for (uint8_t a = 0x40; a <= 0x4F; ++a) {
    // 0x4A/B are reserved for BNO08x: register-style probes could consume SHTP data.
    if (a == 0x4A || a == 0x4B || !bus_.present(a)) continue;
    uint16_t manufacturer = 0, device = 0;
    if (!bus_.read16(a, 0xFE, manufacturer) || manufacturer != 0x5449 ||
        !bus_.read16(a, 0xFF, device) || (device & 0xFFF0) != 0x2260) continue;
    m.address = a;
    if (!bus_.write16(a, 0, board::INA226_CONFIG)) break;
    m.initialized = m.online = true;
    m.hasSample = false;
    m.consecutiveErrors = 0;
    lastPollMs_ = millis();
    return true;
  }
  m.error(millis()); m.online = false; m.health = SensorHealth::OFFLINE;
  return false;
}
void INA226Sensor::update() {
  const uint32_t now = millis();
  auto &m = data_.meta;
  m.age(now, 250, 1500);
  if (!m.online) {
    if (!tried_ || now - lastDiscoveryMs_ >= board::SENSOR_RETRY_MS) {
      tried_ = true; lastDiscoveryMs_ = now; begin();
    }
    return;
  }
  if (now - lastPollMs_ < board::POWER_INTERVAL_MS) return;
  lastPollMs_ = m.lastAttemptMs = now;
  uint16_t bus = 0, shunt = 0;
  if (!bus_.read16(m.address, 2, bus) || !bus_.read16(m.address, 1, shunt)) { m.error(now); return; }
  data_.raw.busCounts = bus;
  data_.raw.shuntCounts = static_cast<int16_t>(shunt);
  data_.raw.receivedUs = esp_timer_get_time();
  auto &d = data_.derived;
  d.busVolts = bus * 0.00125F;
  d.shuntVolts = data_.raw.shuntCounts * 0.0000025F;
  d.currentAmps = d.shuntVolts / board::SHUNT_OHMS;
  d.watts = d.busVolts * d.currentAmps;
  if (d.busVolts > 0 && (!d.hasMinimum || d.busVolts < d.minimumVolts)) {
    d.minimumVolts = d.busVolts; d.hasMinimum = true;
  }
  d.peakAbsAmps = fmaxf(d.peakAbsAmps, fabsf(d.currentAmps));
  m.good(now);
}
}
