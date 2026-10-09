#include <cassert>
#include <cstring>
#include <cstdio>
#include <initializer_list>
#include "../../shared/GladiatorLink.h"
#include "../../shared/InterfaceVocabulary.h"
#include "../../gateway/managed_components/espressif__cjson/cJSON/cJSON.h"
using namespace robotlink;
// Generated from the production C6 decoder by test_interface_codec.ps1.
#include "../../diagnostics/interface-decoder.inc"
Frame frame(Type type,const Writer &w){Frame f;f.type=type;f.length=w.size;f.payload=reinterpret_cast<const char *>(w.data);return f;}
int main(){
  using interfacev1::State;
  assert(interfacev1::controllerState(false,10,10)==State::SAFE);
  assert(interfacev1::controllerState(true,0,0)==State::ARMED);
  assert(interfacev1::controllerState(true,-1,0)==State::DRIVE);
  Writer w;w.u32(100);w.u32(1);w.u32(2);w.u8(1);w.u8(1);w.u8(0);w.u8(3);
  w.u8(90);w.u8(90);w.u8(25);w.u8(1);w.u8(0);w.u8(0);w.u8(0);w.u32(5);w.u32(6);
  int topic=-1;const char *key=nullptr;
  auto legacy=decodeTelemetry(frame(Type::CONTROLLER,w),topic,key);
  assert(legacy&&topic==0&&!strcmp(key,"controller"));
  assert(!strcmp(cJSON_GetObjectItem(legacy,"state")->valuestring,"UNKNOWN"));cJSON_Delete(legacy);
  // S3 says SAFE while motor/armed fields disagree: the decoder must not infer DRIVE.
  w.u8(uint8_t(State::SAFE));auto partial=decodeTelemetry(frame(Type::CONTROLLER,w),topic,key);assert(!partial);
  w.u8(uint8_t(interfacev1::Battery::WARN));auto current=decodeTelemetry(frame(Type::CONTROLLER,w),topic,key);
  assert(current&&!strcmp(cJSON_GetObjectItem(current,"state")->valuestring,"SAFE"));
  assert(!strcmp(cJSON_GetObjectItem(current,"battery")->valuestring,"WARN"));cJSON_Delete(current);
  Writer imu;imu.u32(100);imu.u8(2);imu.u8(3);imu.u32(90);imu.u32(10);imu.u32(0);imu.f32(20);imu.u8(1);imu.u8(1);
  for(int i=0;i<6;++i)imu.f32(float(i));
  auto oldImu=decodeTelemetry(frame(Type::ORIENTATION,imu),topic,key);
  assert(oldImu&&!cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(oldImu,"derived"),"headingValid")));cJSON_Delete(oldImu);
  imu.u8(1);auto newImu=decodeTelemetry(frame(Type::ORIENTATION,imu),topic,key);
  assert(newImu&&cJSON_IsTrue(cJSON_GetObjectItem(cJSON_GetObjectItem(newImu,"derived"),"headingValid")));cJSON_Delete(newImu);
  imu.u8(1);assert(!decodeTelemetry(frame(Type::ORIENTATION,imu),topic,key));
  assert(!strcmp(interfacev1::healthName(7),"DISABLED"));assert(!strcmp(interfacev1::healthName(255),"UNKNOWN"));
  puts("Interface codec passed: S3 state authority, battery vocabulary, legacy UNKNOWN, truncated/extra bytes, heading validity.");
}
