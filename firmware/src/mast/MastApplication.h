#pragma once
// Included in the S3 namespace, after control/power/sensor state declarations.
mast::Controller mastController;
mast::Hardware mastHardware;
uint32_t mastGeneration=0,mastRejected=0;
bool mastSafe(){
  const auto &p=sensorData.power.meta;
  return !commandArmed&&!commandDeadman&&!leftMotor.currentPercent&&!rightMotor.currentPercent&&
    !targetLeftPercent&&!targetRightPercent&&!batteryInhibitsMotion()&&
    p.hasSample&&p.health==sensors::SensorHealth::OK&&uint32_t(millis()-p.lastUpdateMs)<250&&
    gatewayLink.online();
}
String mastJson(){
  JsonDocument d;d["schema"]=1;d["s3Ms"]=millis();d["enabled"]=mastController.enabled;
  d["calibrated"]=mastController.calibrated;d["referenced"]=mastController.referenced;
  d["scanning"]=mastController.scanning;d["session"]=mastController.session;
  d["awaitingOperator"]=mastController.awaitingOperator;
  d["sequence"]=mastController.sequence;d["reason"]=mast::name(mastController.reason);
  d["rejected"]=mastRejected;d["safe"]=mastSafe();
  // Positions are commanded estimates; SG90 has no position feedback.
  d["commandedPanDeg"]=mastController.pan/10;d["commandedTiltDeg"]=mastController.tilt/10;
  const auto &c=mastController.calibration;
  d["panMinDeg"]=c.pan.minDeciDeg/10.0F;d["panMaxDeg"]=c.pan.maxDeciDeg/10.0F;
  d["tiltMinDeg"]=c.tilt.minDeciDeg/10.0F;d["tiltMaxDeg"]=c.tilt.maxDeciDeg/10.0F;
  String out;serializeJson(d,out);return out;
}
bool mastInteger(JsonVariantConst v,int low,int high,int &out){
  if(!v.is<int>())return false;out=v.as<int>();return out>=low&&out<=high;
}
bool mastAxis(JsonVariantConst obj,mast::Axis &a,int ceiling){
  int lo,neutral,hi,mn,mx;
  if(!mastInteger(obj["lowUs"],500,2500,lo)||!mastInteger(obj["neutralUs"],500,2500,neutral)||
     !mastInteger(obj["highUs"],500,2500,hi)||!mastInteger(obj["minDeciDeg"],-ceiling,0,mn)||
     !mastInteger(obj["maxDeciDeg"],0,ceiling,mx)||!obj["reversed"].is<bool>())return false;
  a.lowUs=lo;a.neutralUs=neutral;a.highUs=hi;a.minDeciDeg=mn;a.maxDeciDeg=mx;
  a.reversed=obj["reversed"].as<bool>();return a.valid(ceiling);
}
bool mastSerial(const String &line){
  if(!line.startsWith("mast"))return false;
  ControlGuard guard;
  if(line=="mast-status"){Serial.println(mastJson());return true;}
  if(line=="mast-stop"){mastController.stop(mast::Reason::STOPPED);mastHardware.stop();Serial.println(mastJson());return true;}
  if(line.startsWith("mast-config ")){
    if(mastController.enabled||!mastSafe()){Serial.println("Mast config rejected: disarm, restore power monitor and C6 link.");return true;}
    // A rejected replacement must not leave an older pulse map reusable.
    mastController.calibrated=false;mastController.calibration=mast::Calibration{};
    JsonDocument d;mast::Calibration c;int hz,speed;
    bool ok=!deserializeJson(d,line.substring(12))&&
      d["panModel"].is<const char *>()&&strlen(d["panModel"].as<const char *>())>0&&
      d["tiltModel"].is<const char *>()&&strlen(d["tiltModel"].as<const char *>())>0&&
      d["positionalVerified"].is<bool>()&&d["positionalVerified"].as<bool>()&&
      d["gateVerified"].is<bool>()&&d["gateVerified"].as<bool>()&&
      d["clearanceVerified"].is<bool>()&&d["clearanceVerified"].as<bool>()&&
      mastAxis(d["pan"],c.pan,450)&&mastAxis(d["tilt"],c.tilt,200)&&
      mastInteger(d["frequencyHz"],50,100,hz)&&mastInteger(d["speedDeciDegPerSec"],1,100,speed);
    if(ok){c.frequencyHz=hz;c.speedDeciDegPerSec=speed;c.modelsVerified=c.gateVerified=c.clearanceVerified=true;ok=mastController.configure(c);}
    Serial.println(ok?"Mast calibration accepted for this boot only; outputs remain off.":"Mast calibration rejected; no outputs enabled.");return true;
  }
  if(line=="mast-reference CONFIRM_NEUTRAL_AND_GATE"){
    mastGeneration=gatewayLink.generation();
    if(!mastController.reference(esp_random()|1,millis(),mastSafe())){Serial.println("Mast reference rejected: verify calibration, S3 SAFE, power and link.");return true;}
    if(!mastHardware.start(mastController.calibration)){mastController.stop(mast::Reason::HARDWARE);mastHardware.stop();}
    Serial.println(mastJson());return true;
  }
  Serial.println("Mast USB: mast-status | mast-config {measured calibration} | mast-reference CONFIRM_NEUTRAL_AND_GATE | mast-stop");return true;
}
void serviceMast(){
  ControlGuard guard;
  const uint32_t now=millis();const bool safe=mastSafe();
  const auto &r=sensorData.tofFront;const auto &p=sensorData.presence;
  bool rangeGood=r.meta.hasSample&&r.meta.health==sensors::SensorHealth::OK&&
    uint32_t(now-r.meta.lastUpdateMs)<500&&r.derived.valid;
  bool nearby=(rangeGood&&r.derived.nearestMm<500)||
    (p.meta.hasSample&&p.meta.health==sensors::SensorHealth::OK&&uint32_t(now-p.meta.lastUpdateMs)<800&&p.derived.presenceValid&&p.derived.present);
  // Evaluate expiry/generation BEFORE queued commands can renew a dead session.
  mastController.tick(now,safe,mastGeneration==gatewayLink.generation(),rangeGood,nearby);
  gateway::PendingMast request;
  for(unsigned budget=0;budget<4&&gatewayLink.takeMast(request);++budget){
    const uint32_t commandNow=millis(); // RX task may timestamp after tick's sample.
    if(request.generation!=mastGeneration||uint32_t(commandNow-request.receivedMs)>150||
       (request.command.operation==mast::Operation::SCAN&&(!rangeGood||nearby))||
       !mastController.command(request.command,commandNow,safe))++mastRejected;
  }
  if(!mastHardware.write(mastController,now)){mastController.stop(mast::Reason::HARDWARE);mastHardware.stop();}
  static uint32_t last=0;if(uint32_t(now-last)>=50){last=now;gatewayLink.setMast(mastJson());}
}
