#pragma once
#include <Arduino.h>
#include <Wire.h>
#include "../BoardConfig.h"

namespace sensors {
// Only the sensor worker owns Wire. UI/control code uses copied snapshots.
class I2CBus {
public:
  bool begin() {
    const bool ok = Wire.begin(board::I2C_SDA, board::I2C_SCL, board::I2C_HZ);
    Wire.setTimeOut(board::I2C_TIMEOUT_MS);
    return ok;
  }
  bool present(uint8_t address) {
    Wire.beginTransmission(address);
    return Wire.endTransmission() == 0;
  }
  bool read(uint8_t address, uint8_t *data, uint8_t size) {
    if (Wire.requestFrom(address, size) != size) return false;
    for (uint8_t i=0; i<size; ++i) data[i]=Wire.read();
    return true;
  }
  bool readRegisters(uint8_t address, uint8_t reg, uint8_t *data, uint8_t size) {
    Wire.beginTransmission(address); Wire.write(reg);
    return Wire.endTransmission(false)==0 && read(address,data,size);
  }
  bool write(uint8_t address, const uint8_t *data, uint8_t size) {
    Wire.beginTransmission(address); Wire.write(data,size);
    return Wire.endTransmission()==0;
  }
  bool read16(uint8_t address, uint8_t reg, uint16_t &value) {
    Wire.beginTransmission(address); Wire.write(reg);
    if (Wire.endTransmission(false) != 0 || Wire.requestFrom(address, uint8_t(2)) != 2) return false;
    value = uint16_t(Wire.read()) << 8;
    value |= uint16_t(Wire.read());
    return true;
  }
  bool write16(uint8_t address, uint8_t reg, uint16_t value) {
    Wire.beginTransmission(address); Wire.write(reg);
    Wire.write(uint8_t(value >> 8)); Wire.write(uint8_t(value));
    return Wire.endTransmission() == 0;
  }
  TwoWire &wire() { return Wire; }
};
}
