#include "../shared/CamOtaPolicy.h"
#include <cassert>
#include <cstdio>
int main(){
  using namespace camota;
  assert(matchesKey("0123456789abcdef0123456789abcdef","0123456789abcdef0123456789abcdef"));
  assert(!matchesKey("0123456789abcdef0123456789abcdee","0123456789abcdef0123456789abcdef"));
  assert(!matchesKey("wrong","0123456789abcdef0123456789abcdef"));
  assert(!validHex("gggggggggggggggggggggggggggggggg",32));
  uint8_t image[512]={};image[0]=0xe9;image[1]=5;image[23]=1;
  const uint32_t magic=0xabcd5432;memcpy(image+32,&magic,4);memcpy(image+IDENTITY_OFFSET,&IDENTITY,sizeof(IDENTITY));
  assert(validPrefix(image,sizeof(image)));assert(!validPrefix(image,128));
  image[12]=13;assert(!validPrefix(image,sizeof(image)));image[12]=0;
  image[23]=0;assert(!validPrefix(image,sizeof(image)));image[23]=1;
  image[IDENTITY_OFFSET]='X';assert(!validPrefix(image,sizeof(image)));memcpy(image+IDENTITY_OFFSET,&IDENTITY,sizeof(IDENTITY));
  image[IDENTITY_OFFSET+24]='X';assert(!validPrefix(image,sizeof(image)));
  puts("CAM OTA policy checks passed (auth, image identity, chip, layout, digest requirement).");
}
