#pragma once
#include <stdint.h>
#include <math.h>
#include "GladiatorLink.h"

// Head-relative degrees, never servo-shaft degrees. No saved position, auto
// attach, raw-pulse remote API, modulo angle, or unbounded rotation.
namespace mast {
constexpr uint32_t LEASE_MS=750,MAX_TICK_MS=100;
constexpr uint32_t REFERENCE_WAIT_MS=10000;
enum class Operation:uint8_t { STOP, HOLD, MOVE, SCAN, KEEPALIVE };
enum class Reason:uint8_t { BOOT, READY, STOPPED, LEASE, SAFETY, LINK, TIMING, HARDWARE };
inline const char *name(Reason r){
  switch(r){case Reason::READY:return "ready";case Reason::STOPPED:return "stopped";
    case Reason::LEASE:return "operator lease expired";case Reason::SAFETY:return "S3 safety inhibit";
    case Reason::LINK:return "link changed or lost";case Reason::TIMING:return "loop timing fault";
    case Reason::HARDWARE:return "PWM failure";default:return "boot: position unknown";}
}
struct Axis {
  uint16_t lowUs=0,neutralUs=0,highUs=0;
  int16_t minDeciDeg=0,maxDeciDeg=0;
  bool reversed=false;
  bool valid(int16_t ceiling)const{
    // These are validation bounds, NOT a claim about any SG90's usable range.
    const uint16_t neg=reversed?highUs:lowUs,pos=reversed?lowUs:highUs;
    return lowUs>=500&&highUs<=2500&&lowUs<highUs&&lowUs<=neutralUs&&neutralUs<=highUs&&
      minDeciDeg<=0&&maxDeciDeg>=0&&minDeciDeg<maxDeciDeg&&minDeciDeg>=-ceiling&&maxDeciDeg<=ceiling&&
      (minDeciDeg==0?neg==neutralUs:neg!=neutralUs)&&(maxDeciDeg==0?pos==neutralUs:pos!=neutralUs);
  }
  bool contains(int16_t p)const{return p>=minDeciDeg&&p<=maxDeciDeg;}
  uint16_t pulse(float p)const{
    if(p==0)return neutralUs;
    const float negative=reversed?highUs:lowUs,positive=reversed?lowUs:highUs;
    const float v=p<0?neutralUs+(negative-neutralUs)*p/minDeciDeg:
                         neutralUs+(positive-neutralUs)*p/maxDeciDeg;
    return uint16_t(lroundf(v));
  }
};
struct Calibration {
  Axis pan,tilt;uint16_t frequencyHz=0;uint8_t speedDeciDegPerSec=0;
  bool modelsVerified=false,gateVerified=false,clearanceVerified=false;
  bool valid()const{return modelsVerified&&gateVerified&&clearanceVerified&&
    pan.valid(450)&&tilt.valid(200)&&frequencyHz>=50&&frequencyHz<=100&&
    speedDeciDegPerSec>=1&&speedDeciDegPerSec<=100;}
};
struct Command {
  uint32_t session=0,sequence=0;Operation operation=Operation::STOP;
  int16_t pan=0,tilt=0;
  robotlink::Writer encode()const{robotlink::Writer w;w.u32(session);w.u32(sequence);
    w.u8(uint8_t(operation));w.u8(uint8_t(pan));w.u8(uint16_t(pan)>>8);
    w.u8(uint8_t(tilt));w.u8(uint16_t(tilt)>>8);return w;}
  bool decode(const robotlink::Frame &f){robotlink::Reader r(f);session=r.u32();sequence=r.u32();
    operation=Operation(r.u8());uint16_t p=r.u8();p|=uint16_t(r.u8())<<8;
    uint16_t t=r.u8();t|=uint16_t(r.u8())<<8;pan=int16_t(p);tilt=int16_t(t);return r.done();}
};
class Controller {
public:
  Calibration calibration;
  bool calibrated=false,enabled=false,referenced=false,scanning=false,awaitingOperator=false;
  float pan=0,tilt=0;int16_t targetPan=0,targetTilt=0;
  uint32_t session=0,sequence=0;Reason reason=Reason::BOOT;
  bool configure(const Calibration &c){if(enabled||!c.valid())return false;
    calibration=c;calibrated=true;referenced=false;session=0;return true;}
  bool reference(uint32_t token,uint32_t now,bool safe){
    if(enabled||!calibrated||!safe||!token)return false;
    pan=tilt=0;targetPan=targetTilt=0;session=token;sequence=0;
    enabled=referenced=awaitingOperator=true;scanning=false;lastTick_=lastCommand_=now;reason=Reason::READY;return true;
  }
  void stop(Reason why){enabled=referenced=scanning=awaitingOperator=false;session=0;reason=why;}
  bool command(const Command &c,uint32_t now,bool safe){
    if(!enabled||!referenced||!safe||!c.session||c.session!=session||c.sequence<=sequence||
       uint32_t(now-lastCommand_)>=(awaitingOperator?REFERENCE_WAIT_MS:LEASE_MS)||uint32_t(now-lastTick_)>MAX_TICK_MS)return false;
    if(uint8_t(c.operation)>uint8_t(Operation::KEEPALIVE))return false;
    if(c.operation==Operation::MOVE&&(!calibration.pan.contains(c.pan)||!calibration.tilt.contains(c.tilt)))return false;
    sequence=c.sequence;lastCommand_=now;awaitingOperator=false;
    switch(c.operation){
      case Operation::STOP:stop(Reason::STOPPED);break;
      case Operation::HOLD:scanning=false;targetPan=int16_t(lroundf(pan));targetTilt=int16_t(lroundf(tilt));break;
      case Operation::MOVE:scanning=false;targetPan=c.pan;targetTilt=c.tilt;break;
      case Operation::SCAN:scanning=true;targetPan=calibration.pan.minDeciDeg;targetTilt=0;break;
      case Operation::KEEPALIVE:break;
    }return true;
  }
  void tick(uint32_t now,bool safe,bool linkSame,bool rangeGood,bool nearby){
    if(!enabled)return;
    if(!safe){stop(Reason::SAFETY);return;}if(!linkSame){stop(Reason::LINK);return;}
    if(uint32_t(now-lastCommand_)>=(awaitingOperator?REFERENCE_WAIT_MS:LEASE_MS)){stop(Reason::LEASE);return;}
    const uint32_t dt=now-lastTick_;lastTick_=now;
    if(dt>MAX_TICK_MS){stop(Reason::TIMING);return;}
    if(scanning&&(!rangeGood||nearby)){scanning=false;targetPan=int16_t(lroundf(pan));targetTilt=int16_t(lroundf(tilt));}
    const float step=calibration.speedDeciDegPerSec*(dt>20?20:dt)/1000.0F;
    pan=approach(pan,targetPan,step);tilt=approach(tilt,targetTilt,step);
    if(scanning&&pan==targetPan)targetPan=targetPan==calibration.pan.minDeciDeg?calibration.pan.maxDeciDeg:calibration.pan.minDeciDeg;
  }
private:
  uint32_t lastTick_=0,lastCommand_=0;
  static float approach(float p,float t,float step){return p<t?fminf(p+step,t):fmaxf(p-step,t);}
};
}
