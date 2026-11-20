// Exercise the actual C6 HTTP handler with its consuming serialize contract.
#include <cassert>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <unordered_set>
#include "cJSON.h"
#include "../shared/MastPolicy.h"
using Type=robotlink::Type;
using esp_err_t=int;
constexpr int ESP_OK=0,ESP_FAIL=-1,HTTPD_400_BAD_REQUEST=400;
struct httpd_req_t{std::string body,response,status;};
std::unordered_set<void*> allocations;
void *trackedMalloc(size_t n){auto p=std::malloc(n);if(p)assert(allocations.insert(p).second);return p;}
void trackedFree(void *p){if(p){assert(allocations.erase(p)==1);std::free(p);}}
struct {long long receivedUs=0;} state;
void lock(){}void unlock(){}long long esp_timer_get_time(){return 0;}
cJSON *copyRobot(){return cJSON_CreateObject();}
std::string serialize(cJSON *doc){auto s=cJSON_PrintUnformatted(doc);std::string result=s?s:"{}";cJSON_free(s);cJSON_Delete(doc);return result;}
esp_err_t replyJson(httpd_req_t *r,const std::string &s){r->response=s;return ESP_OK;}
esp_err_t httpd_resp_send_err(httpd_req_t *r,int code,const char *s){r->status=std::to_string(code);r->response=s;return code;}
void httpd_resp_set_status(httpd_req_t*r,const char*s){r->status=s;}
bool readBody(httpd_req_t*r,std::string &body,size_t limit){body=r->body;return body.size()<=limit;}
const char *textValue(cJSON*d,const char*k){auto v=cJSON_GetObjectItemCaseSensitive(d,k);return cJSON_IsString(v)?v->valuestring:"";}
bool integerValue(cJSON*d,const char*k,double lo,double hi,double &n){auto v=cJSON_GetObjectItemCaseSensitive(d,k);if(!cJSON_IsNumber(v)||!std::isfinite(v->valuedouble)||std::floor(v->valuedouble)!=v->valuedouble||v->valuedouble<lo||v->valuedouble>hi)return false;n=v->valuedouble;return true;}
bool incomplete=false;
esp_err_t mastSetupRead(cJSON **d){
 *d=cJSON_Parse(R"({"schema":1,"revision":12,"fields":{"panPin":"10","tiltPin":"13","panLow":"500","panNeutral":"1500","panHigh":"2000","panReverse":true,"tiltLow":"1150","tiltNeutral":"1450","tiltHigh":"1450"}})");
 if(incomplete)cJSON_DeleteItemFromObjectCaseSensitive(cJSON_GetObjectItemCaseSensitive(*d,"fields"),"panHigh");return ESP_OK;
}
std::string queued;
esp_err_t queueRequest(httpd_req_t*r,Type,const robotlink::Writer&w){queued.assign(reinterpret_cast<const char*>(w.data),w.size);r->status="202 Accepted";return ESP_OK;}
#include "../gateway/src/MastApplication.h"
int main(){
 cJSON_Hooks hooks={trackedMalloc,trackedFree};cJSON_InitHooks(&hooks);
 for(int i=0;i<1000;++i){httpd_req_t r;r.body=R"({"action":"positions","revision":12,"pan":{"lowUs":1}})";
  assert(mastConfigHandler(&r)==ESP_OK&&r.status=="202 Accepted");
  auto p=cJSON_Parse(queued.c_str());assert(p);
  assert(cJSON_GetObjectItemCaseSensitive(p,"setupRevision")->valueint==12);
  auto pan=cJSON_GetObjectItemCaseSensitive(p,"pan"),tilt=cJSON_GetObjectItemCaseSensitive(p,"tilt");
  assert(cJSON_GetObjectItemCaseSensitive(pan,"lowUs")->valueint==500);
  assert(cJSON_GetObjectItemCaseSensitive(pan,"neutralUs")->valueint==1500);
  assert(cJSON_GetObjectItemCaseSensitive(pan,"highUs")->valueint==2000);
  assert(cJSON_IsTrue(cJSON_GetObjectItemCaseSensitive(pan,"reversed")));
  assert(cJSON_GetObjectItemCaseSensitive(tilt,"lowUs")->valueint==1150);
  assert(cJSON_GetObjectItemCaseSensitive(tilt,"neutralUs")->valueint==1450&&cJSON_GetObjectItemCaseSensitive(tilt,"highUs")->valueint==1450);
  cJSON_Delete(p);assert(allocations.empty());
 }
 for(const char *body:{R"({"action":"positions","revision":13})",R"({"action":"positions","revision":0})",R"({"action":"positions","revision":"12"})","invalid"}){
  queued="";httpd_req_t r;r.body=body;mastConfigHandler(&r);assert(queued.empty()&&r.status!="202 Accepted");assert(allocations.empty());
 }
 incomplete=true;queued="";httpd_req_t r;r.body=R"({"action":"positions","revision":12})";mastConfigHandler(&r);assert(queued.empty()&&r.status=="409 Conflict");assert(allocations.empty());
 puts("C6 position handoff passed: 1000 actual handler calls, exact flash positions, caller pulses ignored, revision/missing-field checks, balanced cJSON ownership.");
}
