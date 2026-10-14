#include <atomic>
#include <string>
#include <cstring>
#include <cstdio>
#include <algorithm>
#include <cmath>
#include <unistd.h>
#include <fcntl.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "driver/gpio.h"
#include "driver/uart.h"
#include "driver/usb_serial_jtag.h"
#include "driver/usb_serial_jtag_vfs.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_netif.h"
#include "esp_http_server.h"
#include "esp_ota_ops.h"
#include "esp_app_desc.h"
#include "esp_app_format.h"
#include "esp_random.h"
#include "esp_system.h"
#include "esp_timer.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "nvs.h"
#include "cJSON.h"
#include "RobotProtocol.h"
#include "GladiatorLink.h"
#include "WifiLink.h"
#include "DetailCodec.h"
#include "FieldPage.h"
#include "InterfaceVocabulary.h"
#include "GatewayConfig.h"
#include "GatewayPage.h"
#include "VisualState.h"
#include "MastPolicy.h"

namespace {
constexpr char TAG[]="gateway";
SemaphoreHandle_t stateMutex;
httpd_handle_t server=nullptr;
esp_netif_t *station=nullptr;
uint32_t bootId=0;
char adminKey[33]={},wifiSsid[33]={},wifiPassword[65]={};
struct State {
  robotlink::Transport active=robotlink::Transport::NONE;
  bool uartAlive=false,uartStable=false,wifiLinkAlive=false;
  uint32_t drops=0,detailErrors=0,wifiLeaseMs=0,resultClient=0,resultSequence=0,resultEpoch=0;
  uint8_t resultCode=0;
  bool wifiConnect…28412 tokens truncated…head; turns carry their own differential and Overdrive is untrimmed
// by design.
void applyStraightTrim(int8_t &left, int8_t &right) {
  orientation::straightTrim(left, right, commandOverdrive);
}

void updateMotorOutputs() {
  ControlGuard guard;
  if(batteryInhibitsMotion()){coastAll();return;}
  const bool controlSourceOnline =
      activeControlSource == ControlSource::WEB ||
      (activeControlSource == ControlSource::FIELD && remoteSession.armed) ||
      (activeControlSource == ControlSource::LINK && gatewayLink.online() && remoteSession.armed) ||
      (activeControlSource == ControlSource::BLE && bleConnected);
  if (!controlSourceOnline || !commandArmed || !commandDeadman) {
    if (leftMotor.currentPercent != 0 || rightMotor.currentPercent != 0) {
      coastAll();
    }
    return;
  }

  int8_t outputLeft = targetLeftPercent;
  int8_t outputRight = targetRightPercent;
  applyStraightTrim(outputLeft, outputRight);

  // Overdrive intentionally bypasses soft start and commands full-duty values
  // immediately. Direction and magnitude still come from the signed frame.
  if (commandOverdrive && overdrivePending) {
    overdrivePending = false;
    applyMotor(leftMotor, outputLeft);
    applyMotor(rightMotor, outputRight);
    return;
  }

  const uint32_t now = millis();
  if (now - lastRampMs < RAMP_INTERVAL_MS) {
    return;
  }
  lastRampMs = now;

  const int8_t nextLeft = rampToward(leftMotor.currentPercent, outputLeft);
  const int8_t nextRight = rampToward(rightMotor.currentPercent, outputRight);
  applyMotor(leftMotor, nextLeft);
  applyMotor(rightMotor, nextRight);
}

void publishStatus(bool force = false) {
  if (!bleConnected || statusCharacteristic == nullptr) {
    return;
  }

  const uint32_t now = millis();
  if (!force && now - lastStatusMs < STATUS_INTERVAL_MS) {
    return;
  }
  lastStatusMs = now;

  uint8_t frame[FRAME_SIZE] = {};
  frame[0] = FRAME_MAGIC_STATUS;
  frame[1] = PROTOCOL_VERSION;
  frame[2] = (bleConnected ? 0x01 : 0x00) |
             (commandArmed ? 0x02 : 0x00) |
             ((leftMotor.currentPercent != 0 || rightMotor.currentPercent != 0) ? 0x04 : 0x00) |
             (watchdogStopped ? 0x08 : 0x00) |
             (commandOverdrive ? 0x10 : 0x00);
  frame[3] = static_cast<uint8_t>(leftMotor.currentPercent);
  frame[4] = static_cast<uint8_t>(rightMotor.currentPercent);
  frame[5] = selectedPowerMode;
  frame[6] = lastSequence;
  frame[7] = checksum(frame, FRAME_SIZE - 1);

  statusCharacteristic->setValue(frame, sizeof(frame));
  statusCharacteristic->notify();
}

void publishPowerTelemetry(bool force = false) {
  if (!bleConnected || powerCharacteristic == nullptr) {
    return;
  }

  const uint32_t now = millis();
  if (!force && now - lastStatusMs < STATUS_INTERVAL_MS) {
    return;
  }

  uint8_t frame[POWER_FRAME_SIZE] = {};
  frame[0] = POWER_FRAME_MAGIC;
  frame[1] = PROTOCOL_VERSION;
  frame[2] = (ina226Present ? 0x01 : 0x00) |
             (ina226SampleValid ? 0x02 : 0x00) |
             (currentMilliamps < 0 ? 0x04 : 0x00) |
             ((leftMotor.currentPercent != 0 || rightMotor.currentPercent != 0)
                  ? 0x08
                  : 0x00);
  frame[3] = ina226Address;
  writeLe16(frame, 4, busMillivolts);
  writeLe32(frame, 6, currentMilliamps);
  writeLe32(frame, 10, powerMilliwatts);
  writeLe16(frame, 14,
            minimumBusMillivolts == UINT16_MAX ? 0 : minimumBusMillivolts);
  writeLe16(frame, 16, peakCurrentMilliamps);
  frame[18] = ina226SampleSequence;
  frame[19] = checksum(frame, POWER_FRAME_SIZE - 1);

  powerCharacteristic->setValue(frame, sizeof(frame));
  powerCharacteristic->notify();
}

class CommandCallbacks final : public BLECharacteristicCallbacks {
  void rejectInput(){
    bleMustRelease=true;
    if(activeControlSource==ControlSource::BLE){
      commandArmed=commandDeadman=commandOverdrive=false;activeControlSource=ControlSource::NONE;
      targetLeftPercent=targetRightPercent=0;watchdogStopped=true;coastAll();
    }
  }
  void onWrite(BLECharacteristic *characteristic) override {
    ControlGuard guard;
    const std::string value = characteristic->getValue();
    if (value.size() != FRAME_SIZE) {
      rejectInput();
      return;
    }

    const auto *frame = reinterpret_cast<const uint8_t *>(value.data());
    if (frame[0] != FRAME_MAGIC_COMMAND ||
        frame[1] != PROTOCOL_VERSION ||
        frame[7] != checksum(frame, FRAME_SIZE - 1)) {
      rejectInput();
      return;
    }

    const int8_t left = static_cast<int8_t>(frame[4]);
    const int8_t right = static_cast<int8_t>(frame[5]);
    if (left < -100 || left > 100 || right < -100 || right > 100) {
      rejectInput();
      return;
    }

    if (activeControlSource != ControlSource::BLE && activeControlSource != ControlSource::NONE && commandArmed &&
        commandDeadman &&
        (targetLeftPercent != 0 || targetRightPercent != 0)) {
      appendLog("BLE command rejected while web controller is actively driving");
      return;
    }
    if (batteryInhibitsMotion()) {
      coastAll();
      return; // guard already logged; do not spam per frame
    }
    if(!(frame[3]&FLAG_ARMED))bleMustRelease=false;
    if(bleMustRelease&&(frame[3]&FLAG_ARMED))return;
    revokeRemote=true;
    activeControlSource = ControlSource::BLE;

    lastSequence = frame[2];
    commandArmed = (frame[3] & FLAG_ARMED) != 0;
    commandDeadman = (frame[3] & FLAG_DEADMAN) != 0;
    commandOverdrive = (frame[3] & FLAG_OVERDRIVE) != 0;
    targetLeftPercent = left;
    targetRightPercent = right;
    selectedPowerMode = frame[6];
    lastCommandMs = millis();
    watchdogStopped = false;
    overdrivePending = commandOverdrive && commandDeadman;

    if (!commandArmed || !commandDeadman || (left == 0 && right == 0)) {
      coastAll();
    }
    publishStatus(true);
    publishPowerTelemetry(true);
  }
};

class ServerCallbacks final : public BLEServerCallbacks {
  void onConnect(BLEServer *) override {
    ControlGuard guard;
    bleConnected = true;
    if ((activeControlSource != ControlSource::WEB && activeControlSource != ControlSource::LINK && activeControlSource != ControlSource::FIELD) || !commandArmed) {
      commandArmed = false;
      commandDeadman = false;
      commandOverdrive = false;
      watchdogStopped = false;
      lastCommandMs = millis();
      coastAll();
    }
    appendLog("Phone connected; motors remain disarmed unless web control is active.");
  }

  void onDisconnect(BLEServer *server) override {
    ControlGuard guard;
    bleConnected = false;
    if (activeControlSource == ControlSource::BLE) {
      bleMustRelease=true;
      activeControlSource = ControlSource::NONE;
      commandArmed = false;
      commandDeadman = false;
      commandOverdrive = false;
      watchdogStopped = true;
      coastAll();
      appendLog("Phone disconnected; motors coasted and disarmed.");
    } else {
      appendLog("Phone disconnected; web controller ownership unchanged.");
    }
    delay(40);
    server->getAdvertising()->start();
  }
};

CommandCallbacks commandCallbacks;
ServerCallbacks serverCallbacks;

void setupPwmPin(uint8_t pin, uint8_t channel) {
  ledcSetup(channel, PWM_FREQUENCY_HZ, PWM_RESOLUTION_BITS);
  ledcAttachPin(pin, channel);
  ledcWrite(channel, 0);
}

void setupMotors() {
  pinMode(LEFT_R_EN_PIN, OUTPUT);
  pinMode(LEFT_L_EN_PIN, OUTPUT);
  pinMode(RIGHT_R_EN_PIN, OUTPUT);
  pinMode(RIGHT_L_EN_PIN, OUTPUT);

  digitalWrite(LEFT_R_EN_PIN, LOW);
  digitalWrite(LEFT_L_EN_PIN, LOW);
  digitalWrite(RIGHT_R_EN_PIN, LOW);
  digitalWrite(RIGHT_L_EN_PIN, LOW);

  setupPwmPin(LEFT_RPWM_PIN, LEFT_RPWM_CHANNEL);
  setupPwmPin(LEFT_LPWM_PIN, LEFT_LPWM_CHANNEL);
  setupPwmPin(RIGHT_RPWM_PIN, RIGHT_RPWM_CHANNEL);
  setupPwmPin(RIGHT_LPWM_PIN, RIGHT_LPWM_CHANNEL);
  coastAll();
}

void setupBle() {
  BLEDevice::init(DEVICE_NAME);
  BLEDevice::setMTU(64);

  bleServer = BLEDevice::createServer();
  bleServer->setCallbacks(&serverCallbacks);

  BLEService *service = bleServer->createService(SERVICE_UUID);
  BLECharacteristic *commandCharacteristic = service->createCharacteristic(
      COMMAND_UUID,
      BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_WRITE_NR);
  commandCharacteristic->setCallbacks(&commandCallbacks);

  statusCharacteristic = service->createCharacteristic(
      STATUS_UUID,
      BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY);
  statusCharacteristic->addDescriptor(new BLE2902());

  powerCharacteristic = service->createCharacteristic(
      POWER_UUID,
      BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY);
  powerCharacteristic->addDescriptor(new BLE2902());

  uint8_t initialStatus[FRAME_SIZE] = {
      FRAME_MAGIC_STATUS, PROTOCOL_VERSION, 0, 0, 0, 25, 0, 0};
  initialStatus[7] = checksum(initialStatus, FRAME_SIZE - 1);
  statusCharacteristic->setValue(initialStatus, sizeof(initialStatus));

  uint8_t initialPower[POWER_FRAME_SIZE] = {};
  initialPower[0] = POWER_FRAME_MAGIC;
  initialPower[1] = PROTOCOL_VERSION;
  initialPower[2] = ina226Present ? 0x01 : 0;
  initialPower[3] = ina226Address;
  initialPower[19] = checksum(initialPower, POWER_FRAME_SIZE - 1);
  powerCharacteristic->setValue(initialPower, sizeof(initialPower));

  service->start();

  BLEAdvertising *advertising = BLEDevice::getAdvertising();
  advertising->addServiceUUID(SERVICE_UUID);
  advertising->setScanResponse(true);
  advertising->setMinPreferred(0x06);
  advertising->setMaxPreferred(0x12);
  advertising->start();
}

} // namespace

void setup() {
  // Nothing in this project subscribed to the platform task watchdog before
  // this line, despite the SDK shipping one (5 s, panic-reboot) by default:
  // a hang anywhere in loop() - motors, Wi-Fi, BLE, the web server - froze
  // the board forever with no automatic recovery. Enable it first so it also
  // covers a hang during the rest of setup() itself.
  enableLoopWDT();
  commandMutex=xSemaphoreCreateRecursiveMutex();configASSERT(commandMutex);
  pinMode(board::BENCH_POWER_DETECT_PIN, INPUT_PULLUP);
  benchPowerViaPin = digitalRead(board::BENCH_POWER_DETECT_PIN) ==
                     (board::BENCH_POWER_DETECT_ACTIVE_LOW ? LOW : HIGH);
  benchPowerCandidate = benchPowerActive = benchPowerViaPin;
  benchPowerCandidateSinceMs = millis();
  setupMotors();
  mastHardware.begin(); // No PWM attachment or power-gate heartbeat at boot.

  // Read why the controller restarted before anything else can overwrite it.
  bootReason = esp_reset_reason();
  bootRawReason = static_cast<uint32_t>(rtc_get_reset_reason(0));
  if (rtcBootMagic != BOOT_MAGIC) {
    rtcBootMagic = BOOT_MAGIC;
    rtcBootCount = 0;
  }
  bootCount = ++rtcBootCount;
  statusLed.begin(bootReason, bootRawReason, bootCount);

  // Confirm this image unconditionally. Leaving it PENDING_VERIFY blocks every
  // later OTA at activation, which is indistinguishable from a bad image.
  const esp_partition_t *running = esp_ota_get_running_partition();
  if (running) {
    strlcpy(otaPartition, running->label, sizeof(otaPartition));
    esp_ota_img_states_t state = ESP_OTA_IMG_UNDEFINED;
    if (esp_ota_get_state_partition(running, &state) == ESP_OK) {
      switch (state) {
        case ESP_OTA_IMG_NEW: otaStateName = "NEW"; break;
        case ESP_OTA_IMG_PENDING_VERIFY: otaStateName = "PENDING_VERIFY"; break;
        case ESP_OTA_IMG_VALID: otaStateName = "VALID"; break;
        case ESP_OTA_IMG_INVALID: otaStateName = "INVALID"; break;
        case ESP_OTA_IMG_ABORTED: otaStateName = "ABORTED"; break;
        default: otaStateName = "UNDEFINED"; break;
      }
    }
    otaMarkedValid = esp_ota_mark_app_valid_cancel_rollback() == ESP_OK;
  }

  Serial.begin(115200);
  delay(500);
  Serial.println();
  appendLog("Gladiator tracked robot controller starting");
  appendLogf("Boot #%u since power-on | reset=%s (esp %d, raw 0x%02X) | blink code %u",
             bootCount, status::resetReasonName(bootReason), int(bootReason),
             bootRawReason, statusLed.code());
  appendLogf("OTA slot %s was %s at boot; mark-valid %s", otaPartition, otaStateName,
             otaMarkedValid ? "OK" : "FAILED");
  appendLog("Safety state: outputs disabled, waiting for BLE + ARM + held direction");
  appendLog(benchPowerActive
                ? "Bench power detected at boot on GPIO7; LiPo voltage protection bypassed"
                : "LiPo power policy active; ground GPIO7 only with the bench-power harness");

  sensorTaskStarted = sensorManager.begin();
  remoteSession.epoch=esp_random()|1;
  appendLog(gatewayLink.begin(sensorManager) ? "C6 UART link started on TX4/RX5 at 460800 baud" : "C6 UART task failed to start");
  appendLog(sensorTaskStarted ? "Sensor Core v1: I2C GPIO8/9 worker started" : "Sensor task failed to start");
  setupMaintenanceWifi();
  setupBle();

  appendLog("BLE advertising as Gladiator");
}

void loop() {
  const uint32_t loopStartedUs = micros();
  const uint32_t now = millis();
  if (commandArmed && now - lastCommandMs > COMMAND_TIMEOUT_MS) {
    ControlGuard guard;
    webMustRelease=true;bleMustRelease=true;remoteSession.invalidate();
    activeControlSource = ControlSource::NONE;
    commandArmed = false;
    commandDeadman = false;
    commandOverdrive = false;
    watchdogStopped = true;
    coastAll();
    appendLog("Command watchdog expired; motors coasted and disarmed.");
    publishStatus(true);
  }

  updateSensors();
  updateBenchPower(now);
  updateBatteryGuard(now);
  serviceFieldControl(now);
  updateMotorOutputs();
  serviceMast();
  updateSerialConsole();
  logIna226();
  publishPowerTelemetry();
  publishStatus();
  maintenanceServer.handleClient();
  ArduinoOTA.handle();
  updateLinkRadios(now);
  updateStatusLed(now);
  gateway::ControllerState linkController;
  linkController.armed=commandArmed;
  linkController.state=currentInterfaceState();linkController.battery=batteryState;
  linkController.deadman=commandDeadman;linkController.owner=uint8_t(activeControlSource);linkController.power=selectedPowerMode;
  linkController.batteryLockout=batteryLockout;linkController.radiosShed=batteryRadiosShed;linkController.benchPower=benchPowerActive;
  linkController.epoch=remoteSession.epoch;linkController.client=remoteSession.client;
  linkController.leftPercent=leftMotor.currentPercent;
  linkController.rightPercent=rightMotor.currentPercent;
  linkController.watchdogStopped=watchdogStopped;
  linkController.sensorTaskStarted=sensorTaskStarted;
  linkController.loopMaxUs=loopMaxUs;
  linkController.bootCount=bootCount;
  gatewayLink.setController(linkController);
  static uint32_t lastSystem=0;
  if(now-lastSystem>=1000){ControlGuard guard;lastSystem=now;JsonDocument system;
    system["firmware"]="Gladiator S3 Interface v1 / Link v2 / Mast v1";system["build"]=__DATE__ " " __TIME__;system["freeHeap"]=ESP.getFreeHeap();
    system["orientation"]=orientation::NAME;
    system["resetReason"]=status::resetReasonName(bootReason);system["bootCount"]=bootCount;system["otaSlot"]=otaPartition;
    system["batteryState"]=batteryStateName(batteryState);system["powerSource"]=benchPowerActive?"BENCH":"LIPO";
    system["benchPower"]=benchPowerActive;system["benchPowerSource"]=benchPowerSourceName();
    system["benchDetectPin"]=board::BENCH_POWER_DETECT_PIN;
    system["radioShed"]=batteryRadiosShed;system["apUp"]=maintenanceApActive;
    system["logTail"]=webLog.substring(webLog.length()>450?webLog.length()-450:0);
    String s;serializeJson(system,s);gatewayLink.setSystem(s,webLog);
  }
  loopMaxUs = max(loopMaxUs, uint32_t(micros()-loopStartedUs));
  delay(2);
}
