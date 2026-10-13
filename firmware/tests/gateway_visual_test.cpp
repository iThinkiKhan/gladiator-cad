// Exercise the production endpoint handlers against deterministic HTTP/NVS/time doubles.
#if defined(_WIN32) && !defined(_WIN32_WINNT)
#define _WIN32_WINNT 0x0600
#endif
#include <string>
#include <cstring>
#include <cstdio>
#include <cmath>
#include <cassert>
#ifdef _WIN32
#ifndef _WIN32_WINNT
#define _WIN32_WINNT 0x0600
#endif
#include <winsock2.h>
#include <ws2tcpip.h>
#else
#include <arpa/inet.h>
#endif
#include "cJSON.h"
#include "../shared/VisualState.h"
using esp_err_t=int;using nvs_handle_t=int;
constexpr int ESP_OK=0,NVS_READONLY=0,NVS_READWRITE=1,HTTPD_400_BAD_REQUEST=400,HTTPD_500_INTERNAL_SERVER_ERROR=500;
struct httpd_req_t {std::string body,response;bool authorized=true;int status=200;};
struct State {uint64_t receivedUs=0;} state;
uint32_t clockMs=1000;
cJSON *cache=nullptr;
uint32_t nowMs(){return clockMs;}
uint64_t esp_timer_get_time(){return uint64_t(clockMs)*1000;}
void lock(){}void unlock(){}
size_t strlcpy(char *dst,const char *src,size_t n){size_t size=strlen(src);if(n){size_t copy=size<n?size:n-1;memcpy(dst,src,copy);dst[copy]=0;}return size;}
const char *textValue(const cJSON *o,const char *key){auto p=cJSON_GetObjectItemCaseSensitive(o,key);return cJSON_IsString(p)?p->valuestring:"";}
void number(cJSON *o,const char *k,double v){cJSON_AddNumberToObject(o,k,v);}
cJSON *copyRobot(){return cJSON_Duplicate(cache,true);}
std::string serialize(cJSON *d){char *p=cJSON_PrintUnformatted(d);std::string s=p;cJSON_free(p);cJSON_Delete(d);return s;}
esp_err_t replyJson(httpd_req_t *r,const std::string &s){r->response=s;return 0;}
esp_err_t httpd_resp_send_err(httpd_req_t *r,int status,const char *s){r->status=status;r->response=s;return 0;}
bool authorize(httpd_req_t *r){if(!r->authorized)r->status=401;return r->authorized;}
bool readBody(httpd_req_t *r,std::string &s,size_t maximum){s=r->body;return !s.empty()&&s.size()<=maximum;}
bool integerValue(cJSON *d,const char *key,double low,double high,double &out){auto v=cJSON_GetObjectItemCaseSensitive(d,key);if(!cJSON_IsNumber(v)||!std::isfinite(v->valuedouble)||std::floor(v->valuedouble)!=v->valuedouble||v->valuedouble<low||v->valuedouble>high)return false;out=v->valuedouble;return true;}
int nvs_open(const char *,int,nvs_handle_t *n){*n=1;return 0;}
int nvs_get_str(nvs_handle_t,const char *,char *,size_t *){return -1;}
int nvs_set_str(nvs_handle_t,const char *,const char *){return 0;}
int nvs_commit(nvs_handle_t){return 0;}void nvs_close(nvs_handle_t){}
#include "../gateway/src/VisualApplication.h"
void fixture(const char *battery="OK",int age=0,int range=900){
  cJSON_Delete(cache);char json[1024];snprintf(json,sizeof(json),R"({"controller":{"state":"SAFE","battery":"%s"},"tofFront":{"meta":{"health":"OK","ageMs":%d},"derived":{"valid":true,"nearestMm":%d}},"presence":{"meta":{"health":"OK","ageMs":0},"derived":{"presenceValid":true,"present":false}},"power":{"meta":{"health":"OK","ageMs":0},"derived":{"busVolts":7.8}}})",battery,age,range);
  cache=cJSON_Parse(json);state.receivedUs=esp_timer_get_time();
}
cJSON *get(){httpd_req_t r;visualHandler(&r);auto d=cJSON_Parse(r.response.c_str());assert(d);return d;}
void expectMode(const char *mode){auto d=get();assert(!strcmp(textValue(d,"mode"),mode));cJSON_Delete(d);}
int post(const char *json,bool authorized=true){httpd_req_t r;r.body=json;r.authorized=authorized;visualCommandHandler(&r);return r.status;}
int configPost(const char *json){httpd_req_t r;r.body=json;visualConfigHandler(&r);return r.status;}
int main(){
  fixture();expectMode("ready");auto d=get();assert(cJSON_IsTrue(cJSON_GetObjectItemCaseSensitive(d,"fresh")));assert(cJSON_IsNumber(cJSON_GetObjectItemCaseSensitive(d,"volts")));cJSON_Delete(d);
  assert(post(R"({"mode":"greeting","leaseMs":1000,"message":"Hello"})")==200);expectMode("greeting");
  clockMs=1500;fixture();expectMode("greeting");clockMs=2000;fixture();expectMode("ready");
  assert(post(R"({"mode":"scanning","leaseMs":60000})")==200);expectMode("scanning");
  fixture("CRITICAL");expectMode("alert");fixture("OK",0,499);expectMode("alert");
  fixture("OK",1000,499);expectMode("scanning"); // Expired range cannot raise an alert.
  state.receivedUs=esp_timer_get_time()-500000;expectMode("offline");
  d=get();assert(cJSON_IsNull(cJSON_GetObjectItemCaseSensitive(d,"nearestMm")));assert(cJSON_IsNull(cJSON_GetObjectItemCaseSensitive(d,"volts")));cJSON_Delete(d);
  fixture();assert(post(R"({"mode":"auto"})")==200);expectMode("ready");
  assert(post(R"({"mode":"alert","leaseMs":1000})",false)==401);expectMode("ready");
  for(const char *json:{R"({"mode":"wrong","leaseMs":1000})",R"({"mode":"alert","leaseMs":999})",R"({"mode":"alert","leaseMs":60001})",R"({"mode":"alert","leaseMs":1000.5})",R"({"mode":"alert","leaseMs":"1000"})",R"({"mode":"alert","leaseMs":1000,"message":"bad\ntext"})","[]","null","{"})assert(post(json)==400);
  assert(configPost(R"({"cameraIp":"192.168.8.2"})")==200);d=get();assert(!strcmp(textValue(d,"streamUrl"),"http://192.168.8.2:81/stream"));cJSON_Delete(d);
  assert(configPost(R"({"cameraIp":"10.0.0.5"})")==200);assert(configPost(R"({"cameraIp":"172.16.0.2"})")==200);
  assert(configPost(R"({"cameraIp":"172.32.0.2"})")==400);assert(configPost(R"({"cameraIp":"8.8.8.8"})")==400);
  assert(configPost(R"({"cameraIp":"<script>"})")==400);assert(configPost("{}")==400);assert(configPost(R"({"cameraIp":null})")==400);
  assert(configPost(R"({"cameraIp":""})")==200);d=get();assert(!textValue(d,"streamUrl")[0]);cJSON_Delete(d);cJSON_Delete(cache);
  puts("Gateway production handler checks passed (auth, validation, stale sensors, override expiry, camera config).");
}
