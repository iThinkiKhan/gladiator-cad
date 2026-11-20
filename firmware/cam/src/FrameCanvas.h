#pragma once
// Full-screen RGB565 frame for the masthead display, plus a changed-tile push.
// The panel runs at 4 MHz SPI (about 220 ms for a full 320x170 frame), so only
// the 32x10 tiles that differ from what is already on the glass are sent.
#include <Adafruit_GFX.h>
#include <stdint.h>
#include <string.h>

class FrameCanvas : public Adafruit_GFX {
public:
  uint16_t *pixels=nullptr;
  FrameCanvas(int16_t w,int16_t h,uint16_t *buffer=nullptr):Adafruit_GFX(w,h),pixels(buffer){}
  void drawPixel(int16_t x,int16_t y,uint16_t c) override {
    if(pixels&&x>=0&&y>=0&&x<_width&&y<_height)pixels[y*_width+x]=c;
  }
  void fillScreen(uint16_t c) override {fillRect(0,0,_width,_height,c);}
  void drawFastHLine(int16_t x,int16_t y,int16_t w,uint16_t c) override {span(y,x,x+w-1,c);}
  void drawFastVLine(int16_t x,int16_t y,int16_t h,uint16_t c) override {fillRect(x,y,1,h,c);}
  void fillRect(int16_t x,int16_t y,int16_t w,int16_t h,uint16_t c) override {
    if(!pixels)return;
    int x0=x<0?0:x,x1=x+w>_width?_width:x+w,y0=y<0?0:y,y1=y+h>_height?_height:y+h;
    for(int yy=y0;yy<y1;++yy){uint16_t *p=pixels+yy*_width;for(int xx=x0;xx<x1;++xx)p[xx]=c;}
  }
  // Inclusive horizontal run, clipped.
  void span(int y,int x0,int x1,uint16_t c){
    if(!pixels||y<0||y>=_height)return;
    if(x0<0)x0=0;if(x1>=_width)x1=_width-1;
    uint16_t *p=pixels+y*_width;for(int x=x0;x<=x1;++x)p[x]=c;
  }
  uint16_t *row(int y){return pixels+y*_width;}
};

namespace frame {
constexpr int TILE_W=32,TILE_H=10,MAX_TILES=16;
// Sends every changed tile run of `next` and copies it into `shown`, which
// must always hold exactly what the panel displays. Returns pixels sent.
template<class Display>uint32_t pushChanged(Display &tft,const uint16_t *next,uint16_t *shown,int w,int h,bool full){
  uint32_t sent=0;const int tiles=(w+TILE_W-1)/TILE_W;
  bool started=false;
  for(int by=0;by<h;by+=TILE_H){
    const int bh=by+TILE_H>h?h-by:TILE_H;
    bool dirty[MAX_TILES];
    for(int t=0;t<tiles&&t<MAX_TILES;++t){
      dirty[t]=full;if(full)continue;
      const int x0=t*TILE_W,tw=x0+TILE_W>w?w-x0:TILE_W;
      for(int y=by;y<by+bh&&!dirty[t];++y)dirty[t]=memcmp(next+y*w+x0,shown+y*w+x0,size_t(tw)*2)!=0;
    }
    for(int t=0;t<tiles&&t<MAX_TILES;){
      if(!dirty[t]){++t;continue;}
      int t1=t;while(t1<tiles&&t1<MAX_TILES&&dirty[t1])++t1;
      const int x0=t*TILE_W,x1=t1*TILE_W>w?w:t1*TILE_W,rw=x1-x0;
      if(!started){tft.startWrite();started=true;}
      tft.setAddrWindow(x0,by,rw,bh);
      for(int y=by;y<by+bh;++y){
        tft.writePixels(const_cast<uint16_t *>(next+y*w+x0),uint32_t(rw),true,false);
        memcpy(shown+y*w+x0,next+y*w+x0,size_t(rw)*2);
      }
      sent+=uint32_t(rw)*bh;t=t1;
    }
  }
  if(started)tft.endWrite();
  return sent;
}
}
