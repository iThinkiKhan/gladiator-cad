#pragma once
#include <Arduino.h>
#include <atomic>
#include "../sensors/SensorManager.h"
#include "../../shared/GladiatorLink.h"
#include "../../shared/WifiLink.h"
#include "../../shared/DetailCodec.h"
#include "../../shared/InterfaceVocabulary.h"

namespace gateway {
struct ControllerState {
  bool armed=false,watchdogStopped=false,sensorTaskStarted=false,deadman=false;
  bool batteryLockout=false,radiosShed=false,benchPower=false;
  int8_t leftPercent=0,rightPercent=0;uint8_t owner=0,power=25;
  uint32_t loopMaxUs=0,bootCount=0,epoch=0,client=0;
  interfacev1::State state=interfacev1::State::UNKNOWN;
  interfacev1::Battery battery=interfacev1::Battery::UNKNOWN;
};
struct PendingControl {robotlink::Control command;uint32_t receivedMs=0,generation=0;};
struct LinkStatus {
  bool started=false,uartAlive=false,uartStable=false,wifiAlive=false;
  robotlink::Transport active=robotlink::Transport::NONE;
  uint32_t rxFrames=0,txFrames=0,errors=0,rejected=0,peerBootId=0,switches=0,lastRxMs=0,drops=0;
};
class RobotLink {
public:
  bool begin(sensors::SensorManager &manager);
  void setController(const ControllerState &state);
  void setSystem(const String &json,const String &log);
  bool diagnosticsRequested()const{return wantsDetails_.load();}
  String statusJson();
  bool takeControl(PendingControl &c){return commands_&&xQueueReceive(commands_,&c,0)==pdTRUE;}
  void result(const robotlink::Control &c,robotlink::Result result,uint32_t epoch);
  uint32_t generation()const{return generation_.load();}
  bool needsWifi()const{return wantsWifi_.load();}
  bool online()const{return online_.load();}
  void requestWifi(uint32_t ms){wifiRequest_=ms?(ms>60000?60000:ms):UINT32_MAX;}
private:
  static void taskEntry(void *p);void run();
  bool send(robotlink::Type type,const void *payload,size_t length,robotlink::Transport transport);
  void send(robotlink::Type type,const robotlink::Writer &w,robotlink::Transport transport){send(type,w.data,w.size,transport);}
  void receive(const robotlink::Frame &frame,robotlink::Transport transport);
  void prepareDetail();
  sensors::SensorManager *manager_=nullptr;
  SemaphoreHandle_t mutex_=nullptr;QueueHandle_t commands_=nullptr,results_=nullptr;
  HardwareSerial serial_{1};ControllerState controller_;
  LinkStatus status_,published_,visible_;String system_,log_;
  // Large transport buffers live in S3 PSRAM, preserving internal RAM for BLE,
  // Wi-Fi, interrupt handlers and the motor/sensor tasks during recovery.
  struct Buffers {
    robotlink::Decoder decoder,wifiDecoder;robotlink::WifiChannel wifi;
    robotlink::DetailWriter detail;
    uint8_t raw[robotlink::MAX_RAW],tx[robotlink::MAX_FRAME];
  };
  Buffers *buffers_=nullptr;
  robotlink::Health uartHealth_,wifiHealth_;robotlink::Selector selector_;
  size_t detailOffset_=0;uint32_t detailId_=0;
  uint32_t sequence_[3]={},bootId_=0,wifiLeaseStart_=0,wifiLeaseMs_=0,lastConnect_=0;
  uint32_t detailStart_=0,detailLease_=0,detailInterval_=1000,lastDetail_=0;
  std::atomic<uint32_t> generation_{0},wifiRequest_{0};
  std::atomic<bool> wantsWifi_{true},online_{false},wantsDetails_{false};bool detailRequested_=false;
};
}
