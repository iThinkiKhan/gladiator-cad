#pragma once
#include <stdint.h>
namespace indicator {
enum class Code : uint8_t { Starting=0, Ready=1, BootHealthy=2, Camera=3, Wifi=4, Gateway=5, Service=6, Updating=7 };
constexpr uint32_t BOOT_CONFIRM_MS=480,NETWORK_GRACE_MS=30000,STARTUP_LIMIT_MS=10000;
constexpr Code select(bool starting,bool updating,bool service,bool camera,bool wifi,bool gateway) {
  return updating?Code::Updating:starting?Code::Starting:!service?Code::Service:
    !camera?Code::Camera:!wifi?Code::Wifi:!gateway?Code::Gateway:Code::Ready;
}
constexpr bool pulse(Code code,uint32_t elapsed) {
  return code==Code::BootHealthy?(elapsed<BOOT_CONFIRM_MS && elapsed%240<60):
    (code>=Code::Camera && code<=Code::Service && elapsed%5000<uint32_t(code)*240 && (elapsed%5000)%240<60);
}
constexpr Code outputCode(Code current,bool bootSequence,uint32_t bootAge) {
  return current==Code::Updating?current:
    bootSequence && current!=Code::Camera && current!=Code::Service?Code::BootHealthy:
    ((current==Code::Wifi||current==Code::Gateway)&&bootAge<NETWORK_GRACE_MS)?Code::Starting:current;
}
constexpr uint32_t flashDuty(bool pulseOn,bool updating,bool streaming,int spotlight,uint32_t maxDuty) {
  return updating?0:spotlight>0?(uint32_t(spotlight)*maxDuty+50)/100:
    streaming?0:pulseOn?6:0; // Status pulses are only 6/255, for 60 ms.
}
inline const char *name(Code c) {
  switch(c){case Code::Starting:return "starting-or-waiting";case Code::Ready:return "ready";case Code::BootHealthy:return "boot-healthy";
    case Code::Wifi:return "wifi-disconnected";case Code::Camera:return "camera-fault";
    case Code::Gateway:return "gateway-data-unavailable";case Code::Service:return "service-or-loop-fault";
    case Code::Updating:return "updating";}
  return "unknown";
}
}
