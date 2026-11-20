// Exercise the production SHTP transmitter against a failed I2C HAL.
#include "../build-output/host/shtp.c"
#include <assert.h>
#include <stdio.h>
static uint32_t clock_us;
static unsigned writes, fail_count;
static int write_error;
static uint32_t clockNow(sh2_Hal_t *h){(void)h;clock_us+=1000;return clock_us;}
static int readNone(sh2_Hal_t *h,uint8_t *b,unsigned n,uint32_t *t){(void)h;(void)b;(void)n;(void)t;return 0;}
static int writeFake(sh2_Hal_t *h,uint8_t *b,unsigned n){(void)h;(void)b;++writes;if(write_error)return write_error;return writes<=fail_count?0:(int)n;}
int main(void){
 sh2_Hal_t hal={0};hal.getTimeUs=clockNow;hal.read=readNone;hal.write=writeFake;
 shtp_t transport={0};transport.pHal=&hal;transport.outMaxTransfer=64;transport.advertPhase=ADVERT_IDLE;
 const uint8_t data[3]={1,2,3};uint32_t start=clock_us;
 fail_count=1000000;
 assert(txProcess(&transport,2,data,sizeof(data))==SH2_ERR_TIMEOUT);
 assert((uint32_t)(clock_us-start)>=500000 && (uint32_t)(clock_us-start)<503000);
 assert(transport.txDiscards==1);
 // A failed transfer does not poison a later successful command.
 fail_count=3;writes=0;assert(txProcess(&transport,2,data,sizeof(data))==SH2_OK);assert(writes==4);
 clock_us=0xfffffff0;start=clock_us;fail_count=1000000;writes=0;
 assert(txProcess(&transport,2,data,sizeof(data))==SH2_ERR_TIMEOUT);
 assert((uint32_t)(clock_us-start)<503000);
 write_error=-7;assert(txProcess(&transport,2,data,sizeof(data))==-7);
 write_error=0;fail_count=0;writes=0;assert(txProcess(&transport,2,data,sizeof(data))==SH2_OK);
 puts("SHTP passed: failed writes time out; transient failures, clock wrap, explicit errors and later recovery work.");return 0;
}
