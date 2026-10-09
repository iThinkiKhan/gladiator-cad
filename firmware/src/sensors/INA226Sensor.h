#pragma once
#include "I2CBus.h"
#include "SensorData.h"

namespace sensors {
class INA226Sensor {
public:
  INA226Sensor(I2CBus &bus, PowerData &data) : bus_(bus), data_(data) {}
  void update();
private:
  bool begin();
  I2CBus &bus_;
  PowerData &data_;
  uint32_t lastPollMs_ = 0, lastDiscoveryMs_ = 0;
  bool tried_ = false;
};
}
