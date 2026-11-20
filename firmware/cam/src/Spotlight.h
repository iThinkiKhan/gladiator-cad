#pragma once
// Flash LED on GPIO4 as a spotlight that aims with the camera.
// Off at boot and during OTA. Each POST renews it; with no renewal for
// LIGHT_TIMEOUT_MS it turns itself off, so a closed phone cannot leave it on.
// Only the indicator task writes the LED; the HTTP handler sets the target.
std::atomic<int> lightLevel{0};
std::atomic<uint32_t> lightSetMs{0};
std::atomic<uint32_t> lightOutputDuty{0};
bool lightReady=false;
void setupLight(){
  lightReady=ledcSetup(config::LIGHT_CHANNEL,config::LIGHT_PWM_HZ,8)>0;
  if(lightReady){ledcAttachPin(config::LIGHT_PIN,config::LIGHT_CHANNEL);ledcWrite(config::LIGHT_CHANNEL,0);}
  else Serial.println("Spotlight PWM unavailable; flash LED stays off.");
}
uint32_t lightRemainingMs(){
  if(!lightLevel.load())return 0;
  uint32_t elapsed=millis()-lightSetMs.load();
  return elapsed>=config::LIGHT_TIMEOUT_MS?0:config::LIGHT_TIMEOUT_MS-elapsed;
}
void lightLoop(bool statusPulse){
  static int applied=-1;
  int want=lightLevel.load();
  // compare_exchange keeps a request that arrived during this check.
  if(want&&(otaUpdating||!lightRemainingMs())&&lightLevel.compare_exchange_strong(want,0))want=0;
  const int duty=indicator::flashDuty(statusPulse,otaUpdating.load(),streaming.load(),want,config::LIGHT_MAX_DUTY);
  if(lightReady&&duty!=applied){ledcWrite(config::LIGHT_CHANNEL,duty);lightOutputDuty=duty;applied=duty;}
}
// GET reads the level; POST {"level":0..100} sets and renews it. Works without the camera sensor.
esp_err_t lightHandler(httpd_req_t *req){
  if(otaUpdating)return cameraUnavailable(req,"Firmware update in progress");
  if(!lightReady)return cameraUnavailable(req,"Spotlight unavailable");
  if(req->method==HTTP_POST){
    if(!req->content_len||req->content_len>64)return httpd_resp_send_err(req,HTTPD_400_BAD_REQUEST,"Light body too large");
    char body[65]={};size_t got=0;while(got<req->content_len){int n=httpd_req_recv(req,body+got,req->content_len-got);if(n<=0)return ESP_FAIL;got+=n;}
    StaticJsonDocument<128> input;int level;
    if(deserializeJson(input,body)||!input.is<JsonObject>()||!cameraValue(input["level"],0,100,level))
      return httpd_resp_send_err(req,HTTPD_400_BAD_REQUEST,"Light level 0-100");
    lightSetMs=millis();lightLevel=level;
  }
  StaticJsonDocument<192> d;
  d["level"]=lightLevel.load();d["remainingMs"]=lightRemainingMs();d["timeoutMs"]=config::LIGHT_TIMEOUT_MS;
  d["maxDutyPercent"]=(config::LIGHT_MAX_DUTY*100+127)/255;
  String out;serializeJson(d,out);httpd_resp_set_type(req,"application/json");httpd_resp_set_hdr(req,"Cache-Control","no-store");
  return httpd_resp_send(req,out.c_str(),out.length());
}
