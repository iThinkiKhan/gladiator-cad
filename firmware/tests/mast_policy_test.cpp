#include "../shared/MastPolicy.h"
#include <cassert>
#include <cstdio>
#include <initializer_list>
using namespace mast;
Calibration fixture(){Calibration c;c.pan={1200,1500,1800,-100,120,false};
  c.tilt={1300,1500,1700,-50,50,true};c.frequencyHz=50;c.speedDeciDegPerSec=50;
  c.modelsVerified=c.gateVerified=c.clearanceVerified=true;return c;}
Command request(uint32_t session,uint32_t seq,Operation op,int16_t p=0,int16_t t=0){return {session,seq,op,p,t};}
int main(){
  Controller m;assert(!m.enabled&&!m.referenced&&!m.calibrated&&m.session==0);
  assert(!m.reference(7,0,true));assert(!m.configure(Calibration{}));
  auto c=fixture();assert(c.valid());assert(m.configure(c));assert(!m.enabled);
  auto bad=c;bad.pan.maxDeciDeg=451;assert(!bad.valid());bad=c;bad.gateVerified=false;assert(!bad.valid());
  bad=c;bad.pan.neutralUs=bad.pan.lowUs;assert(!bad.valid());bad=c;bad.frequencyHz=0;assert(!bad.valid());
  assert(!m.reference(7,0,false));assert(!m.reference(0,0,true));assert(m.reference(7,0,true));
  assert(m.awaitingOperator&&m.targetPan==0&&m.targetTilt==0);
  assert(!m.configure(c));assert(!m.reference(8,0,true));
  auto move=request(7,1,Operation::MOVE,120,50);assert(m.command(move,0,true));
  assert(!m.command(move,0,true));assert(!m.command(request(8,2,Operation::MOVE),0,true));
  assert(!m.command(request(7,2,Operation::MOVE,121),0,true));
  assert(!m.command(request(7,2,Operation::MOVE,0,51),0,true));
  assert(!m.command(request(7,2,Operation(255)),0,true));
  m.tick(20,true,true,true,false);assert(m.pan==1&&m.tilt==1);
  unsigned checked=0;
  for(int p=-451;p<=451;++p)for(int t=-201;t<=201;++t){
    Controller x;assert(x.configure(c));assert(x.reference(7,0,true));
    bool expected=c.pan.contains(p)&&c.tilt.contains(t);
    assert(x.command(request(7,1,Operation::MOVE,p,t),0,true)==expected);++checked;
  }
  assert(m.command(request(7,2,Operation::SCAN),20,true));
  for(uint32_t now=40,seq=3;now<=20000;now+=20,++seq){
    assert(m.command(request(7,seq,Operation::KEEPALIVE),now,true));
    float previous=m.pan;m.tick(now,true,true,true,false);
    assert(m.pan>=c.pan.minDeciDeg&&m.pan<=c.pan.maxDeciDeg&&fabsf(m.pan-previous)<=1.001F);
    auto pulse=c.pan.pulse(m.pan);assert(pulse>=c.pan.lowUs&&pulse<=c.pan.highUs);
  }
  assert(m.scanning);m.tick(20020,true,true,false,false);assert(!m.scanning&&m.enabled);
  assert(m.command(request(7,2000,Operation::SCAN),20020,true));
  m.tick(20040,true,true,true,true);assert(!m.scanning);
  m.tick(20800,true,true,true,false);assert(!m.enabled&&!m.referenced&&!m.session);
  assert(!m.command(request(7,2001,Operation::KEEPALIVE),20800,true));
  for(auto fault:{Reason::SAFETY,Reason::LINK,Reason::TIMING}){
    Controller x;assert(x.configure(c));assert(x.reference(9,100,true));
    x.tick(fault==Reason::TIMING?201:120,fault!=Reason::SAFETY,fault!=Reason::LINK,true,false);
    assert(!x.enabled&&!x.referenced&&x.reason==fault);
    assert(!x.command(request(9,1,Operation::MOVE),220,true));
  }
  Controller wrap;assert(wrap.configure(c));assert(wrap.reference(9,0xfffffff0,true));
  wrap.tick(4,true,true,true,false);assert(wrap.enabled);
  assert(wrap.command(request(9,1,Operation::KEEPALIVE),4,true));
  wrap.tick(24,true,true,true,false);assert(wrap.enabled);
  assert(wrap.command(request(9,2,Operation::STOP),24,true));assert(!wrap.referenced);
  Controller waiting;assert(waiting.configure(c));assert(waiting.reference(10,0,true));
  for(uint32_t n=20;n<=10000;n+=20)waiting.tick(n,true,true,true,false);
  assert(!waiting.enabled&&waiting.reason==Reason::LEASE);
  assert(c.tilt.pulse(-50)==1700&&c.tilt.pulse(0)==1500&&c.tilt.pulse(50)==1300);
  Axis endpoint{1200,1500,1500,-100,0,false};assert(endpoint.valid(450));
  assert(endpoint.pulse(-100)==1200&&endpoint.pulse(0)==1500&&!endpoint.contains(1));
  auto w=move.encode();robotlink::Frame frame{robotlink::Type::MAST_CONTROL,0,0,reinterpret_cast<const char *>(w.data),w.size};
  Command decoded;assert(decoded.decode(frame));assert(decoded.pan==120&&decoded.tilt==50&&decoded.session==7);
  frame.length--;assert(!decoded.decode(frame));
  puts("Mast policy passed: boot lock, measured bounds, ramp, scan, invalid sensors, stop, replay, faults, expiry and clock wrap.");
  printf("Checked %u angle pairs.\n",checked);
}
