// Exercise the production SH2 command processor with missing and timely replies.
#include "../build-output/host/sh2.c"
#include <assert.h>
#include <stdio.h>
static uint32_t clock_us;static unsigned services,complete_after,opens,closes;
static uint32_t clockNow(sh2_Hal_t*h){(void)h;clock_us+=1000;return clock_us;}
void *shtp_open(sh2_Hal_t*h){++opens;return h;}
void shtp_close(void*p){(void)p;++closes;}
void shtp_setEventCallback(void*p,shtp_EventCallback_t*c,void*k){(void)p;(void)c;(void)k;}
int shtp_listenChan(void*p,uint16_t g,const char*n,shtp_Callback_t*c,void*k){(void)p;(void)g;(void)n;(void)c;(void)k;return 0;}
int shtp_listenAdvert(void*p,uint16_t g,shtp_AdvertCallback_t*c,void*k){(void)p;(void)g;(void)c;(void)k;return 0;}
uint8_t shtp_chanNo(void*p,const char*a,const char*c){(void)p;(void)a;(void)c;return 2;}
int shtp_send(void*p,uint8_t c,const uint8_t*b,uint16_t n){(void)p;(void)c;(void)b;(void)n;return SH2_OK;}
void shtp_service(void*p){(void)p;if(complete_after&&++services==complete_after)opCompleted(&_sh2,SH2_OK);}
static int start(sh2_t*s){(void)s;return SH2_OK;}
int main(void){
 sh2_Hal_t hal={0};hal.getTimeUs=clockNow;_sh2.pHal=&hal;_sh2.controlChan=2;
 sh2_ProductIds_t ids={0};uint8_t cal=0;uint32_t before=clock_us;
 assert(sh2_getProdIds(&ids)==SH2_ERR_TIMEOUT);assert(clock_us-before>=500000&&clock_us-before<503000);assert(_sh2.pOp==0);
 assert(sh2_getCalConfig(&cal)==SH2_ERR_TIMEOUT);assert(sh2_saveDcdNow()==SH2_ERR_TIMEOUT);
 sh2_Op_t explicitDeadline={5000,start,0};before=clock_us;assert(opProcess(&_sh2,&explicitDeadline)==SH2_ERR_TIMEOUT);assert(clock_us-before<8000);
 sh2_Op_t reply={0,start,0};complete_after=5;services=0;assert(opProcess(&_sh2,&reply)==SH2_OK);complete_after=0;
 clock_us=0xfffffff0;before=clock_us;assert(sh2_getProdIds(&ids)==SH2_ERR_TIMEOUT);assert((uint32_t)(clock_us-before)<503000);
 sh2_SensorConfig_t config={0};assert(sh2_setSensorConfig(SH2_ACCELEROMETER,&config)==SH2_OK);
 for(unsigned i=0;i<5;++i)assert(sh2_open(&hal,0,0)==SH2_OK);assert(opens==5&&closes==4);sh2_close();assert(closes==5);
 puts("SH2 passed: missing replies time out, timed replies succeed, explicit deadlines and clock wrap preserved, later commands recover.");return 0;
}
