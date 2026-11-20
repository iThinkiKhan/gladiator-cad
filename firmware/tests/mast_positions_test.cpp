#include "../shared/MastPolicy.h"
#include <cassert>
#include <cstdio>
using namespace mast;
Calibration recorded(){Calibration c;c.pan={500,1500,2000,-100,100,true};c.tilt={1150,1450,1450,-100,0,false};
 c.panPin=10;c.tiltPin=13;c.frequencyHz=50;c.speedDeciDegPerSec=5;c.pulsePositions=true;return c;}
int main(){
 auto c=recorded();assert(c.valid());assert(!c.modelsVerified&&!c.clearanceVerified);
 assert(c.pan.pulse(-100)==2000&&c.pan.pulse(0)==1500&&c.pan.pulse(100)==500);
 assert(c.tilt.pulse(-100)==1150&&c.tilt.pulse(0)==1450);
 for(int p=-100;p<=100;++p){assert(c.pan.pulse(p)>=500&&c.pan.pulse(p)<=2000);}
 for(int t=-100;t<=0;++t){assert(c.tilt.pulse(t)>=1150&&c.tilt.pulse(t)<=1450);}
 auto bad=c;bad.tilt.maxDeciDeg=100;assert(!bad.valid());bad=c;bad.pan.neutralUs=499;assert(!bad.valid());
 bad=c;bad.panPin=13;assert(!bad.valid());bad=c;bad.pan.shaftMaxDeciDeg=900;assert(!bad.valid());
 Controller m;assert(m.configure(c)&&!m.enabled&&!m.referenced);assert(!m.reference(1,0,false));assert(m.reference(1,0,true));
 assert(m.pan==0&&m.tilt==0);uint32_t seq=0;
 auto send=[&](Operation op,int p,int t,uint32_t now){return m.command({m.session,++seq,op,int16_t(p),int16_t(t)},now,true);};
 assert(!send(Operation::MOVE,1,0,0));assert(!send(Operation::SCAN,0,0,0));assert(!send(Operation::RATE,31,0,0));
 assert(send(Operation::RATE,30,0,0));assert(!send(Operation::JOG,2,0,0));assert(send(Operation::JOG,1,-1,0));
 for(uint32_t now=20;now<=20000;now+=20){assert(send(Operation::KEEPALIVE,0,0,now));m.tick(now,true,true,false,false);
  assert(m.pan>=0&&m.pan<=100&&m.tilt>=-100&&m.tilt<=0);assert(c.pan.pulse(m.pan)>=500&&c.pan.pulse(m.pan)<=1500);
  assert(c.tilt.pulse(m.tilt)>=1150&&c.tilt.pulse(m.tilt)<=1450);}
 assert(m.pan==100&&m.tilt==-100);assert(send(Operation::JOG,-1,1,20000));
 for(uint32_t now=20020;now<=40000;now+=20){assert(send(Operation::KEEPALIVE,0,0,now));m.tick(now,true,true,true,false);}
 assert(m.pan==-100&&m.tilt==0);assert(send(Operation::HOLD,0,0,40000));
 assert(send(Operation::MOVE,0,0,40000));m.tick(40020,true,true,true,false);assert(m.pan> -100);
 m.tick(40800,true,true,true,false);assert(!m.enabled&&!m.referenced&&!m.session&&m.reason==Reason::LEASE);
 assert(!send(Operation::KEEPALIVE,0,0,40800));assert(m.reference(2,41000,true));assert(m.pan==0&&m.tilt==0);
 m.tick(41020,false,true,true,false);assert(!m.enabled&&m.reason==Reason::SAFETY);
 assert(m.reference(3,42000,true));m.tick(42020,true,false,true,false);assert(!m.enabled&&m.reason==Reason::LINK);
 assert(m.reference(4,43000,true));m.tick(43101,true,true,true,false);assert(!m.enabled&&m.reason==Reason::TIMING);
 puts("Saved positions passed: exact recorded anchors, asymmetric tilt, bounded direction/no wrap, no angle targets/scan, rate limits, no auto-enable, ownership/lease/safety/link/timing stops.");
}
