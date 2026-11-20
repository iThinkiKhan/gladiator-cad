#pragma once
// C6 relays operator intent; calibration, PWM and safety remain on the S3.
esp_err_t mastHandler(httpd_req_t *req){
  lock();auto robot=copyRobot();auto s=state;unlock();
  auto m=cJSON_DetachItemFromObjectCaseSensitive(robot,"mast");cJSON_Delete(robot);
  if(!m)m=cJSON_CreateObject();
  bool fresh=s.receivedUs&&esp_timer_get_time()-s.receivedUs<250000;
  auto age=cJSON_GetObjectItemCaseSensitive(m,"transportAgeMs");
  auto sourceAge=cJSON_GetObjectItemCaseSensitive(m,"sourceAgeMs");
  fresh=fresh&&cJSON_IsNumber(age)&&age->valuedouble>=0&&age->valuedouble<250&&
    cJSON_IsNumber(sourceAge)&&sourceAge->valuedouble>=0&&sourceAge->valuedouble<250;
  cJSON_AddBoolToObject(m,"fresh",fresh);return replyJson(req,serialize(m));
}
esp_err_t mastCommandHandler(httpd_req_t *req){
  // Key-free operator requests are validated and executed exclusively by S3.
  std::string body;if(!readBody(req,body,256))return httpd_resp_send_err(req,HTTPD_400_BAD_REQUEST,"Invalid mast command");
  auto doc=cJSON_ParseWithLength(body.data(),body.size());double token=0,seq=0,op=0,pan=0,tilt=0;
  bool valid=cJSON_IsObject(doc)&&integerValue(doc,"session",1,4294967295.0,token)&&
    integerValue(doc,"sequence",1,4294967295.0,seq)&&integerValue(doc,"operation",0,8,op)&&
    integerValue(doc,"pan",-450,450,pan)&&integerValue(doc,"tilt",-200,200,tilt);
  cJSON_Delete(doc);
  if(!valid)return httpd_resp_send_err(req,HTTPD_400_BAD_REQUEST,"Expected session, sequence, operation 0-8 and valid pan/tilt parameters");
  mast::Command c;c.session=uint32_t(token);c.sequence=uint32_t(seq);c.operation=mast::Operation(uint8_t(op));c.pan=int16_t(pan);c.tilt=int16_t(tilt);
  return queueRequest(req,Type::MAST_CONTROL,c.encode());
}
esp_err_t mastConfigHandler(httpd_req_t *req){
  std::string body;if(!readBody(req,body,768))return httpd_resp_send_err(req,HTTPD_400_BAD_REQUEST,"Invalid mast commissioning body");
  auto doc=cJSON_ParseWithLength(body.data(),body.size());const char *a=textValue(doc,"action");
  if(!strcmp(a,"positions")){
    double revision=0;cJSON *saved=nullptr;
    if(!integerValue(doc,"revision",1,2147483647,revision)||mastSetupRead(&saved)!=ESP_OK){cJSON_Delete(doc);cJSON_Delete(saved);return httpd_resp_send_err(req,HTTPD_400_BAD_REQUEST,"Read the saved robot positions first");}
    auto fields=cJSON_GetObjectItemCaseSensitive(saved,"fields");
    bool valid=revision==cJSON_GetObjectItemCaseSensitive(saved,"revision")->valuedouble;
    auto profile=cJSON_CreateObject();cJSON_AddStringToObject(profile,"action","positions");cJSON_AddNumberToObject(profile,"setupRevision",revision);
    cJSON_AddNumberToObject(profile,"frequencyHz",50);
    for(const char *axis:{"pan","tilt"}){auto obj=cJSON_AddObjectToObject(profile,axis);
      for(auto key:{std::pair<const char *,const char *>{"Pin","pin"},{"Low","lowUs"},{"Neutral","neutralUs"},{"High","highUs"}}){
        char name[32];snprintf(name,sizeof(name),"%s%s",axis,key.first);auto v=cJSON_GetObjectItemCaseSensitive(fields,name);char *end=nullptr;
        long n=cJSON_IsString(v)&&v->valuestring[0]?strtol(v->valuestring,&end,10):-1;
        if(!end||*end||n<0||n>2575)valid=false;
        cJSON_AddNumberToObject(obj,key.second,n);
      }
      char reverse[32];snprintf(reverse,sizeof(reverse),"%sReverse",axis);cJSON_AddBoolToObject(obj,"reversed",cJSON_IsTrue(cJSON_GetObjectItemCaseSensitive(fields,reverse)));
    }
    // serialize consumes the cJSON tree.
    body=serialize(profile);cJSON_Delete(saved);cJSON_Delete(doc);
    if(!valid){httpd_resp_set_status(req,"409 Conflict");return replyJson(req,"{\"error\":\"Saved positions changed or are incomplete; reload them\"}");}
    robotlink::Writer w;for(char c:body)w.u8(uint8_t(c));return queueRequest(req,Type::MAST_CONFIG,w);
  }
  bool valid=cJSON_IsObject(doc)&&(!strcmp(a,"calibrate")||!strcmp(a,"test")||!strcmp(a,"jog-test")||!strcmp(a,"stop"));
  bool pinRequired=!strcmp(a,"jog-test");auto pin=cJSON_GetObjectItemCaseSensitive(doc,"pin");
  bool pinValid=cJSON_IsNumber(pin)&&(pin->valuedouble==10||pin->valuedouble==13);
  cJSON_Delete(doc);if(!valid)return httpd_resp_send_err(req,HTTPD_400_BAD_REQUEST,"Expected calibrate/test/jog-test/stop action");
  if(pinRequired&&!pinValid)return httpd_resp_send_err(req,HTTPD_400_BAD_REQUEST,"Jog requires selected GPIO10 or GPIO13; reload the control page");
  robotlink::Writer w;for(char c:body)w.u8(uint8_t(c));return queueRequest(req,Type::MAST_CONFIG,w);
}
