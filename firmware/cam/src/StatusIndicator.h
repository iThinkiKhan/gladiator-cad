#pragma once
// A separate task keeps reporting startup progress even if setup/display stalls.
// It owns both LED outputs; HTTP only sets the spotlight target.
std::atomic<bool> startupComplete{false};
std::atomic<const char *> startupStage{"entry"};
std::atomic<indicator::Code> indicatorCode{indicator::Code::Starting};
std::atomic<bool> bootConfirmed{false},indicatorPulseOn{false};
void bootStage(const char *stage){startupStage=stage;Serial.printf("CAM boot: %s\n",stage);}
void indicatorTask(void *) {
  indicator::Code previous=indicator::Code::Starting;const uint32_t born=millis();uint32_t since=born,bootAt=0;
  bool sentBoot=false,wasOn=false;uint8_t bootPulses=0;
  for(;;){
    const uint32_t now=millis();bool gateway=false;
    if(xSemaphoreTake(stateMutex,0)==pdTRUE){gateway=state.received&&state.fresh&&visual::fresh(now,state.received,config::STALE_MS);xSemaphoreGive(stateMutex);}
    const bool service=httpReady&&uint32_t(now-lastLoopMs.load())<3000&&uint32_t(now-lastNetworkMs.load())<3000;
    auto current=indicator::select(!startupComplete.load(),otaUpdating.load(),service,cameraReady.load(),WiFi.status()==WL_CONNECTED,gateway);
    if(current==indicator::Code::Starting && uint32_t(now-born)>=indicator::STARTUP_LIMIT_MS)current=indicator::Code::Service;
    if(!sentBoot&&startupComplete.load()&&service&&cameraReady.load()&&!otaUpdating.load()){
      sentBoot=true;bootAt=now;bootConfirmed=true;Serial.println("CAM boot healthy: two flashes once; no healthy heartbeat.");
    }
    const auto code=indicator::outputCode(current,sentBoot&&uint32_t(now-bootAt)<indicator::BOOT_CONFIRM_MS,uint32_t(now-born));
    if(code!=previous){previous=code;since=now;Serial.printf("CAM status %u: %s\n",unsigned(code),indicator::name(code));}
    indicatorCode=code;
    const bool on=indicator::pulse(code,uint32_t(now-since));
    indicatorPulseOn=on;
    digitalWrite(config::STATUS_LED_PIN,on?LOW:HIGH); // AI-Thinker GPIO33 is active-low.
    lightLoop(on); // White pulses suppressed during streaming, OTA, or a requested spotlight.
    if(code==indicator::Code::BootHealthy&&on&&!wasOn)Serial.printf("CAM boot flash %u at %ums; whiteDuty=%u\n",++bootPulses,now,lightOutputDuty.load());
    wasOn=on;
    vTaskDelay(pdMS_TO_TICKS(20));
  }
}
