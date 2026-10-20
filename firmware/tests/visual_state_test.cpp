#include "../shared/VisualState.h"
#include <cassert>
#include <cstdio>
#include <initializer_list>
int main() {
  using namespace visual;Input s;assert(automatic(s)==Mode::OFFLINE);
  s.controllerFresh=true;assert(automatic(s)==Mode::OFFLINE);
  strcpy(s.battery,"CRITICAL");assert(automatic(s)==Mode::OFFLINE);strcpy(s.battery,"UNKNOWN");
  s.controllerFresh=true;strcpy(s.state,"SAFE");assert(automatic(s)==Mode::READY);
  strcpy(s.state,"ARMED");assert(automatic(s)==Mode::SCANNING);
  strcpy(s.state,"DRIVE");assert(automatic(s)==Mode::ACTIVE);
  s.present=true;assert(automatic(s)==Mode::ACTIVE);
  strcpy(s.state,"SAFE");assert(automatic(s)==Mode::READY);
  s.presenceValid=true;assert(automatic(s)==Mode::GREETING);
  s.rangeValid=true;s.nearestMm=499;assert(automatic(s)==Mode::ALERT);
  s.nearestMm=500;assert(automatic(s)==Mode::GREETING);
  s.rangeValid=false;s.nearestMm=1;assert(automatic(s)==Mode::GREETING);
  s.presenceValid=false;s.mastScanning=true;assert(automatic(s)==Mode::SCANNING);
  s.rangeValid=true;s.nearestMm=100;assert(automatic(s)==Mode::ALERT);
  s.rangeValid=false;s.mastScanning=false;
  for(const char *b:{"LOCKOUT","CRITICAL"}){strcpy(s.battery,b);assert(automatic(s)==Mode::ALERT);}
  s.controllerFresh=false;assert(automatic(s)==Mode::OFFLINE);
  assert(fresh(20,0xfffffff0u,37));assert(!fresh(20,0xfffffff0u,36));
  assert(effective(Mode::READY,Mode::GREETING,500,0,1000)==Mode::GREETING);
  assert(effective(Mode::READY,Mode::GREETING,1000,0,1000)==Mode::READY);
  assert(effective(Mode::OFFLINE,Mode::GREETING,500,0,1000)==Mode::OFFLINE);
  assert(effective(Mode::ALERT,Mode::GREETING,500,0,1000)==Mode::ALERT);
  assert(effective(Mode::READY,Mode::GREETING,500,0,0)==Mode::READY);
  Mode m;assert(!parseMode("invalid",m));
  for(unsigned i=0;i<6;++i){assert(parseMode(name(Mode(i)),m));assert(m==Mode(i));}
  puts("Visual policy checks passed (freshness, priority, override expiry, wraparound).");
}
