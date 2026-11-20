#pragma once
// Masthead display artwork (320x170 landscape). Presentation only: every
// number, state and colour comes from the Scene, which main.cpp fills from the
// C6 /api/visual feed and the CAM's own Wi-Fi/camera state. Nothing here
// invents data or commands the robot.
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <Adafruit_GFX.h>
#include <Fonts/FreeSansBold9pt7b.h>
#include <Fonts/FreeSansBoldOblique9pt7b.h>
#include <Fonts/FreeSansBoldOblique18pt7b.h>
#include "FrameCanvas.h"
#include "VisualState.h"
#include "OperatorStatus.h"
#include "OperatorRender.h"  // opstatus::line

namespace face {
constexpr int W=320,H=170;
constexpr int HEADER_LINE=22,CONTENT_TOP=24,CONTENT_BOTTOM=139,FOOTER_LINE=141;
constexpr uint32_t SPLASH_MS=2700,WIPE_MS=340,GLITCH_MS=240;
// Battery bar spans S3 lockout (4 cells x 3.30 V, src/BoardConfig.h) to a full
// 4S pack. It is a voltage bar, not a state-of-charge estimate; it sags under
// motor load exactly as the S3's own reading does.
constexpr float GAUGE_EMPTY_V=13.2f,GAUGE_FULL_V=16.8f;

struct Rgb {float r,g,b;};
inline int clamp255(float v){return v<0?0:v>255?255:int(v);}
inline uint16_t pack(float r,float g,float b){
  const int R=clamp255(r),G=clamp255(g),B=clamp255(b);
  return uint16_t(((R&0xF8)<<8)|((G&0xFC)<<3)|(B>>3));
}
inline uint16_t shade(const Rgb &c,float k){return pack(c.r*k,c.g*k,c.b*k);}
// k = brightness, w = how far the colour is pushed toward white (0..1).
inline uint16_t hot(const Rgb &c,float k,float w){
  return pack((c.r+(255-c.r)*w)*k,(c.g+(255-c.g)*w)*k,(c.b+(255-c.b)*w)*k);
}
inline Rgb lerp(const Rgb &a,const Rgb &b,float t){return {a.r+(b.r-a.r)*t,a.g+(b.g-a.g)*t,a.b+(b.b-a.b)*t};}
inline float clamp01(float v){return v<0?0:v>1?1:v;}
inline uint32_t hash(uint32_t x){x^=x>>16;x*=0x7feb352dU;x^=x>>15;x*=0x846ca68bU;x^=x>>16;return x;}

constexpr Rgb CYAN{0,225,255},BLUE{40,150,255},ORANGE{255,118,0},RED{255,36,48},
  GREEN{40,255,130},GREY{120,132,145},AMBER{255,190,0},WHITE{255,255,255};
constexpr uint16_t BLACK=0x0000,TEXT_WHITE=0xFFFF;
inline uint16_t textGrey(){return pack(150,160,172);}
inline uint16_t textDim(){return pack(96,106,118);}

inline Rgb modeColor(visual::Mode m){
  switch(m){case visual::Mode::READY:return CYAN;case visual::Mode::SCANNING:return BLUE;
    case visual::Mode::ACTIVE:return ORANGE;case visual::Mode::ALERT:return RED;
    case visual::Mode::GREETING:return GREEN;default:return GREY;}
}
inline const char *modeLabel(visual::Mode m){
  switch(m){case visual::Mode::READY:return "READY";case visual::Mode::SCANNING:return "SCANNING";
    case visual::Mode::ACTIVE:return "ENGAGED";case visual::Mode::ALERT:return "ALERT";
    case visual::Mode::GREETING:return "HELLO";default:return "OFFLINE";}
}
inline Rgb levelColor(uint8_t level){return level==2?RED:level==1?AMBER:GREEN;}
inline Rgb healthRgb(opstatus::Health h){return h==opstatus::Health::OK?GREEN:h==opstatus::Health::UNKNOWN?GREY:AMBER;}
inline Rgb batteryColor(const char *b){
  if(!strcmp(b,"OK"))return GREEN;if(!strcmp(b,"WARN"))return AMBER;
  if(!strcmp(b,"LOCKOUT")||!strcmp(b,"CRITICAL"))return RED;return GREY;
}

struct Scene {
  uint32_t now=0;
  visual::Mode mode=visual::Mode::OFFLINE;
  bool statusView=false;
  opstatus::Message problem{0,"","",""};
  opstatus::Facts facts;
  opstatus::Local local;
  float volts=0;           // 0 = not reported
  const char *battery="UNKNOWN";
  int rangeMm=-1;          // -1 = no valid front range
  int rssi=0;
  const char *version="";
  char footer[64]={};
  bool operatorMessage=false;
};

// Up to two horizontal runs per row (two runs for the arched "happy" eyes).
struct Spans {
  int y0=0,y1=-1;int16_t l[H],r[H],l2[H],r2[H];
  void clear(int a,int b){y0=a<0?0:a;y1=b>=H?H-1:b;for(int y=y0;y<=y1;++y){l[y]=1;r[y]=0;l2[y]=1;r2[y]=0;}}
};
inline void convex(Spans &s,const float *xs,const float *ys,int n){
  float lo=ys[0],hi=ys[0];for(int i=1;i<n;++i){if(ys[i]<lo)lo=ys[i];if(ys[i]>hi)hi=ys[i];}
  s.clear(int(ceilf(lo-0.5f)),int(floorf(hi-0.5f)));
  for(int y=s.y0;y<=s.y1;++y){
    const float yc=y+0.5f;float a=1e9f,b=-1e9f;
    for(int i=0;i<n;++i){
      const int j=(i+1)%n;const float ya=ys[i],yb=ys[j];
      if((ya<=yc&&yb>yc)||(yb<=yc&&ya>yc)){const float x=xs[i]+(yc-ya)*(xs[j]-xs[i])/(yb-ya);if(x<a)a=x;if(x>b)b=x;}
    }
    if(a<=b){s.l[y]=int16_t(ceilf(a-0.5f));s.r[y]=int16_t(floorf(b-0.5f));}
  }
}
inline void fillSpans(FrameCanvas &c,const Spans &s,uint16_t color){
  for(int y=s.y0;y<=s.y1;++y){if(s.l[y]<=s.r[y])c.span(y,s.l[y],s.r[y],color);if(s.l2[y]<=s.r2[y])c.span(y,s.l2[y],s.r2[y],color);}
}
// Fill `shape` only where it overlaps `clip` (pupils stay inside the eye).
inline void fillClipped(FrameCanvas &c,const Spans &shape,const Spans &clip,uint16_t color,uint16_t scanColor){
  const int y0=shape.y0>clip.y0?shape.y0:clip.y0,y1=shape.y1<clip.y1?shape.y1:clip.y1;
  for(int y=y0;y<=y1;++y){
    const uint16_t col=(y%3==0)?scanColor:color;
    const int16_t sl[2]={shape.l[y],shape.l2[y]},sr[2]={shape.r[y],shape.r2[y]};
    const int16_t cl[2]={clip.l[y],clip.l2[y]},cr[2]={clip.r[y],clip.r2[y]};
    for(int i=0;i<2;++i)for(int j=0;j<2;++j){
      const int a=sl[i]>cl[j]?sl[i]:cl[j],b=sr[i]<cr[j]?sr[i]:cr[j];
      if(a<=b)c.span(y,a,b,col);
    }
  }
}

struct Pose {float w,h,slant,lift,pupilW,pupilH,gx,gy,dy,shake;};
inline Pose mix(const Pose &a,const Pose &b,float t){
  return {a.w+(b.w-a.w)*t,a.h+(b.h-a.h)*t,a.slant+(b.slant-a.slant)*t,a.lift+(b.lift-a.lift)*t,
    a.pupilW+(b.pupilW-a.pupilW)*t,a.pupilH+(b.pupilH-a.pupilH)*t,a.gx+(b.gx-a.gx)*t,
    a.gy+(b.gy-a.gy)*t,a.dy+(b.dy-a.dy)*t,b.shake};
}

// Angular visor eye. side=-1 is the left eye; its inner corner is toward the
// middle of the screen. slant>0 drops the inner top corner (an angry brow).
inline void visorSpans(Spans &s,float cx,float cy,const Pose &p,int side,float grow,float open){
  const float hw=p.w*0.5f+grow,h=p.h+2*grow;
  auto inner=[&](float u){return side<0?(u+hw)/(2*hw):(hw-u)/(2*hw);};
  auto top=[&](float u){return -h*0.5f+p.slant*inner(u);};
  auto bot=[&](float u){return h*0.5f-p.lift*(1-inner(u));};
  float ext=h-(p.slant>0?p.slant:0);if(h-p.lift<ext)ext=h-p.lift;
  float ch=p.h*0.28f;if(ch>12)ch=12;ch+=grow*0.4f;if(ch>ext*0.5f-0.5f)ch=ext*0.5f-0.5f;if(ch<0)ch=0;
  const float us[8]={-hw,-hw+ch,hw-ch,hw,hw,hw-ch,-hw+ch,-hw};
  float vs[8]={top(-hw)+ch,top(-hw+ch),top(hw-ch),top(hw)+ch,bot(hw)-ch,bot(hw-ch),bot(-hw+ch),bot(-hw)-ch};
  const float minOpen=3.0f/(h>3?h:3);if(open<minOpen)open=minOpen;
  float xs[8],ys[8];for(int i=0;i<8;++i){xs[i]=cx+us[i];ys[i]=cy+vs[i]*open;}
  convex(s,xs,ys,8);
}
inline void octagonSpans(Spans &s,float cx,float cy,float w,float h){
  const float hw=w*0.5f,hh=h*0.5f;float ch=(w<h?w:h)*0.3f;
  const float xs[8]={cx-hw,cx-hw+ch,cx+hw-ch,cx+hw,cx+hw,cx+hw-ch,cx-hw+ch,cx-hw};
  const float ys[8]={cy-hh+ch,cy-hh,cy-hh,cy-hh+ch,cy+hh-ch,cy+hh,cy+hh,cy+hh-ch};
  convex(s,xs,ys,8);
}
// Upside-down U: the "happy" eye. Legs end flat at cy.
inline void arcSpans(Spans &s,float cx,float cy,float ax,float ay,float thick,float grow){
  const float oax=ax+grow,oay=ay+grow,iax=ax-thick-grow,iay=ay-thick-grow;
  s.clear(int(ceilf(cy-oay-0.5f)),int(floorf(cy+grow-0.5f)));
  for(int y=s.y0;y<=s.y1;++y){
    float dy=y+0.5f-cy;if(dy>0)dy=0;
    const float q=1-(dy/oay)*(dy/oay);if(q<=0)continue;
    const float ow=oax*sqrtf(q);
    if(iay>0&&-dy<iay){
      const float iw=iax*sqrtf(1-(dy/iay)*(dy/iay));
      s.l[y]=int16_t(ceilf(cx-ow-0.5f));s.r[y]=int16_t(floorf(cx-iw-0.5f));
      s.l2[y]=int16_t(ceilf(cx+iw-0.5f));s.r2[y]=int16_t(floorf(cx+ow-0.5f));
    }else{s.l[y]=int16_t(ceilf(cx-ow-0.5f));s.r[y]=int16_t(floorf(cx+ow-0.5f));}
  }
}
// Lit eye surface: vertical gradient, fixed scanlines every third row (fixed
// to the screen, so they never crawl), and a diagonal glint that sweeps across.
inline void fillLit(FrameCanvas &c,const Spans &s,const Rgb &col,float bright,float glintX,float cy){
  const int height=s.y1-s.y0+1;if(height<=0)return;
  for(int y=s.y0;y<=s.y1;++y){
    float k=bright*(1.0f-0.30f*float(y-s.y0)/float(height));if(y%3==0)k*=0.52f;
    const uint16_t base=hot(col,k,0.10f);
    const float g0=glintX-(y-cy)*0.55f;
    const int16_t ls[2]={s.l[y],s.l2[y]},rs[2]={s.r[y],s.r2[y]};
    for(int i=0;i<2;++i){
      if(ls[i]>rs[i])continue;
      c.span(y,ls[i],rs[i],base);
      int a=int(g0-8),b=int(g0+8);if(a<ls[i])a=ls[i];if(b>rs[i])b=rs[i];
      for(int x=a;x<=b;++x){const float d=fabsf(x-g0)/8.0f;if(d<1)c.drawPixel(x,y,hot(col,k*(1+0.15f*(1-d)),0.10f+0.62f*(1-d)));}
    }
  }
}
template<class G>int textWidth(G &c,const char *text){int16_t x,y;uint16_t w,h;c.getTextBounds(text,0,0,&x,&y,&w,&h);return int(w)+x;}

class Renderer {
public:
  // `shown` is what the panel currently displays (for the wipe); may be null.
  void draw(FrameCanvas &c,const Scene &s,const uint16_t *shown){
    const uint32_t now=s.now;
    if(!started){started=true;firstMs=now;lastMs=now;}
    float dt=float(uint32_t(now-lastMs));if(dt>200)dt=200;lastMs=now;
    const View want=uint32_t(now-firstMs)<SPLASH_MS?View::SPLASH:s.statusView?View::STATUS:View::FACE;
    if(want!=view){wipeFull=view==View::SPLASH;view=want;wipeMs=now;wiping=shown!=nullptr;}
    const Rgb target=modeColor(s.mode);color=lerp(color,target,1-expf(-dt/140.0f));
    if(s.mode!=lastMode){if(view==View::FACE&&!wiping)glitchMs=now,glitching=true;lastMode=s.mode;}
    c.fillScreen(BLACK);
    if(view==View::SPLASH)splash(c,s,uint32_t(now-firstMs));
    else{
      const Rgb accent=s.problem.level?levelColor(s.problem.level):color;
      header(c,s,accent);footer(c,s,accent);
      if(view==View::FACE){faceView(c,s,dt);if(glitching)glitch(c,now);}
      else dashboard(c,s);
    }
    if(wiping)wipe(c,s,shown,now);
  }
private:
  enum class View:uint8_t {SPLASH,FACE,STATUS};
  bool started=false,wiping=false,wipeFull=false,glitching=false,poseReady=false;
  uint32_t firstMs=0,lastMs=0,wipeMs=0,glitchMs=0;
  View view=View::SPLASH;visual::Mode lastMode=visual::Mode::OFFLINE;
  Rgb color=GREY;Pose pose{};
  Spans eye,part;

  static void parallelogram(FrameCanvas &c,Spans &s,float x,float y,float w,float h,float lean,uint16_t col){
    const float xs[4]={x+lean,x+w+lean,x+w,x},ys[4]={y,y,y+h,y+h};convex(s,xs,ys,4);fillSpans(c,s,col);
  }
  void header(FrameCanvas &c,const Scene &s,const Rgb &accent){
    c.setFont(&FreeSansBoldOblique9pt7b);c.setTextColor(TEXT_WHITE);c.setCursor(8,16);c.print("GLADIATOR");
    int x=8+textWidth(c,"GLADIATOR")+8;
    for(int i=0;i<3;++i)parallelogram(c,part,float(x+i*9),4,6,13,5,shade(accent,1.0f-0.3f*i));
    const char *label=s.problem.level==2?"FAULT":s.problem.level==1?"CHECK":modeLabel(s.mode);
    const bool urgent=s.problem.level==2||s.mode==visual::Mode::ALERT;
    const bool dim=urgent&&(s.now/300)%2;
    c.setFont(&FreeSansBold9pt7b);const int tw=textWidth(c,label),pw=tw+22,px=W-8-pw;
    parallelogram(c,part,float(px),2,float(pw-6),17,6,dim?shade(accent,0.22f):hot(accent,1,0.05f));
    c.setTextColor(dim?hot(accent,1,0.2f):BLACK);c.setCursor(px+11,16);c.print(label);
    c.setFont(nullptr);
    c.drawFastHLine(0,HEADER_LINE,W,shade(accent,0.22f));
    const int sweep=int((s.now/7)%(W+160))-80;
    for(int i=-40;i<=40;++i){const float k=1-fabsf(float(i))/40.0f;c.drawPixel(sweep+i,HEADER_LINE,shade(accent,0.22f+0.78f*k*k));}
  }
  void footer(FrameCanvas &c,const Scene &s,const Rgb &accent){
    c.drawFastHLine(0,FOOTER_LINE,W,shade(accent,0.22f));
    // Battery: outline, nub, voltage bar coloured by the S3 battery state.
    const bool known=s.volts>0;const Rgb bc=batteryColor(s.battery);
    const bool low=!strcmp(s.battery,"LOCKOUT")||!strcmp(s.battery,"CRITICAL");
    const uint16_t outline=known?shade(bc,0.9f):textDim();
    c.drawRect(8,145,30,15,outline);c.drawRect(9,146,28,13,shade(bc,known?0.35f:0.2f));c.fillRect(38,149,3,7,outline);
    if(known&&!(low&&(s.now/400)%2)){
      const int fill=int(clamp01((s.volts-GAUGE_EMPTY_V)/(GAUGE_FULL_V-GAUGE_EMPTY_V))*24+0.5f);
      for(int x=0;x<fill;++x)c.drawFastVLine(11+x,148,9,(x%6==5)?shade(bc,0.45f):hot(bc,1,0.1f));
    }
    char text[24];
    c.setFont(&FreeSansBold9pt7b);
    if(known)snprintf(text,sizeof(text),"%.1fV",double(s.volts));else snprintf(text,sizeof(text),"--.-V");
    c.setTextColor(known?TEXT_WHITE:textDim());c.setCursor(47,158);c.print(text);
    const int bx=47+textWidth(c,text)+5;
    c.setFont(nullptr);c.setTextSize(1);c.setTextColor(shade(bc,known?1.0f:0.6f));c.setCursor(bx,150);
    c.print(known?s.battery:"NO DATA");
    // Front LiDAR nearest range: segments light up as something gets closer.
    const bool range=s.rangeMm>=0;
    const Rgb rc=!range?GREY:s.rangeMm<500?RED:s.rangeMm<1000?AMBER:accent;
    const int lit=range?int(clamp01((2000.0f-float(s.rangeMm))/1800.0f)*6+0.5f):0;
    c.setTextColor(textDim());c.setCursor(160,145);c.print("RANGE");
    for(int i=0;i<6;++i)c.fillRect(160+i*6,154,4,5,i<lit?hot(rc,1,0.1f):shade(range?rc:GREY,0.22f));
    c.setFont(&FreeSansBold9pt7b);
    if(range){if(s.rangeMm<1000)snprintf(text,sizeof(text),"%dmm",s.rangeMm);else snprintf(text,sizeof(text),"%.2fm",double(s.rangeMm)/1000.0);}
    else snprintf(text,sizeof(text),"--");
    c.setTextColor(range?TEXT_WHITE:textDim());c.setCursor(199,158);c.print(text);
    c.setFont(nullptr);
    // Wi-Fi bars from the CAM's own RSSI.
    const bool wifi=s.local.wifi;
    const int bars=!wifi?0:s.rssi>-55?4:s.rssi>-65?3:s.rssi>-75?2:s.rssi>-85?1:0;
    for(int i=0;i<4;++i){const int hgt=4+i*3;c.fillRect(W-27+i*5,159-hgt,3,hgt,i<bars?hot(accent,1,0.25f):shade(GREY,0.35f));}
    if(!wifi){c.drawLine(W-28,146,W-10,159,shade(RED,1));c.drawLine(W-28,159,W-10,146,shade(RED,1));}
    else{snprintf(text,sizeof(text),"%d",s.rssi);c.setTextColor(textGrey());c.setCursor(W-31-6*int(strlen(text)),150);c.print(text);}
    opstatus::line(c,8,162,1,s.footer,s.operatorMessage?hot(accent,1,0.35f):textDim(),W-16);
  }
  Pose targetPose(const Scene &s,uint32_t now)const{
    const float close=s.rangeMm>=0?clamp01((1500.0f-float(s.rangeMm))/1300.0f):0;
    Pose p{96,58,10,4,28,32,0,0,0,0};
    switch(s.mode){
      case visual::Mode::READY:{
        const uint32_t h=hash(now/2300);const float gx[7]={-22,-12,0,0,0,12,22},gy[4]={-5,0,0,4};
        p.gx=gx[h%7];p.gy=gy[(h>>8)%4];p.dy=sinf(now/900.0f)*1.5f;break;}
      case visual::Mode::SCANNING:p={100,46,14,4,24,28,sinf(now*6.2832f/2600.0f)*30,0,0,0};break;
      case visual::Mode::ACTIVE:p={108,42,24,2,26,26,float(int(hash(now/50)%3)-1),-3,0,0};break;
      case visual::Mode::ALERT:p={92,70,-3,0,15,17,0,0,0,float(int(hash(now/45)%5)-2)};break;
      case visual::Mode::GREETING:p={96,58,0,0,0,0,0,0,sinf(now/260.0f)*3,0};break;
      default:p={96,6,0,0,0,0,0,0,0,0};break;
    }
    if(s.mode==visual::Mode::READY||s.mode==visual::Mode::SCANNING||s.mode==visual::Mode::ACTIVE){
      p.h*=1-0.15f*close;p.pupilW*=1+0.4f*close;p.pupilH*=1+0.4f*close;
    }
    return p;
  }
  static float blink(visual::Mode m,uint32_t now){
    if(m==visual::Mode::ALERT||m==visual::Mode::GREETING||m==visual::Mode::OFFLINE)return 1;
    const uint32_t ph=now%4200;
    if(ph<150)return fabsf(float(ph)-75)/75.0f;
    if((now/4200)%3==1&&ph>=300&&ph<450)return fabsf(float(ph)-375)/75.0f;
    return 1;
  }
  void brackets(FrameCanvas &c,uint16_t col){
    const int x0=6,y0=27,x1=313,y1=136,L=14;
    for(int t=0;t<2;++t){
      c.drawFastHLine(x0,y0+t,L,col);c.drawFastVLine(x0+t,y0,L,col);
      c.drawFastHLine(x1-L+1,y0+t,L,col);c.drawFastVLine(x1-t,y0,L,col);
      c.drawFastHLine(x0,y1-t,L,col);c.drawFastVLine(x0+t,y1-L+1,L,col);
      c.drawFastHLine(x1-L+1,y1-t,L,col);c.drawFastVLine(x1-t,y1-L+1,L,col);
    }
  }
  void faceView(FrameCanvas &c,const Scene &s,float dt){
    const uint32_t now=s.now;const visual::Mode m=s.mode;
    const Pose want=targetPose(s,now);
    if(!poseReady){pose=want;poseReady=true;}else pose=mix(pose,want,1-expf(-dt/85.0f));
    const Rgb col=color;
    brackets(c,shade(col,0.5f));
    float bright=1,glowK=1;
    switch(m){
      case visual::Mode::READY:glowK=0.8f+0.2f*sinf(now/700.0f);break;
      case visual::Mode::ACTIVE:glowK=0.75f+0.5f*float(hash(now/60)%100)/100.0f;break;
      case visual::Mode::ALERT:{const float pulse=0.5f+0.5f*sinf(now*6.2832f/500.0f);glowK=0.5f+1.1f*pulse;bright=0.8f+0.2f*pulse;break;}
      case visual::Mode::OFFLINE:bright=0.45f+0.2f*sinf(now/1100.0f);glowK=bright;break;
      default:break;
    }
    if(m==visual::Mode::SCANNING){
      // Sweep beam, phase-locked to the pupils so the eyes follow it.
      const float ph=now*6.2832f/2600.0f;const int bx=int(160+150*sinf(ph));const int dir=cosf(ph)>0?-1:1;
      const float trail[5]={0.8f,0.4f,0.22f,0.12f,0.06f};
      for(int i=0;i<5;++i)c.drawFastVLine(bx+dir*i,30,104,shade(col,trail[i]));
      for(int x=20;x<=300;x+=10)c.drawFastVLine(x,x%50==10?129:131,x%50==10?5:3,shade(col,0.32f));
    }
    if(m==visual::Mode::ALERT&&(now/250)%2==0){
      for(int x:{24,296}){
        c.fillTriangle(x-12,95,x,72,x+12,95,shade(RED,1));c.fillRect(x-1,79,3,9,BLACK);c.fillRect(x-1,90,3,3,BLACK);
      }
    }
    const float open=blink(m,now);
    const float glint=float(int(now%3200))*0.22f-80;  // sweeps the face about every 3.2 s
    for(int side:{-1,1}){
      const float ecx=160+side*80+pose.gx*0.3f+pose.shake,ecy=82+pose.dy;
      if(m==visual::Mode::GREETING){
        const float acy=ecy+16;
        arcSpans(eye,ecx,acy,46,36,15,6);fillSpans(c,eye,shade(col,0.10f));
        arcSpans(eye,ecx,acy,46,36,15,3);fillSpans(c,eye,shade(col,0.24f));
        arcSpans(eye,ecx,acy,46,36,15,0);fillLit(c,eye,col,bright,glint,acy);
        continue;
      }
      visorSpans(eye,ecx,ecy,pose,side,6,open);fillSpans(c,eye,shade(col,0.10f*glowK));
      visorSpans(eye,ecx,ecy,pose,side,3,open);fillSpans(c,eye,shade(col,0.24f*glowK));
      visorSpans(eye,ecx,ecy,pose,side,0,open);fillLit(c,eye,col,bright,glint,ecy);
      if(pose.pupilW>2&&open>0.3f){
        const float px=ecx+pose.gx+(side<0?3:-3),py=ecy+pose.gy+pose.slant*0.15f;
        octagonSpans(part,px,py,pose.pupilW,pose.pupilH*open);fillClipped(c,part,eye,shade(col,0.30f),shade(col,0.18f));
        octagonSpans(part,px,py,pose.pupilW*0.58f,pose.pupilH*0.58f*open);fillClipped(c,part,eye,BLACK,BLACK);
        octagonSpans(part,px-pose.pupilW*0.12f,py-pose.pupilH*0.14f*open,5,5);fillClipped(c,part,eye,hot(col,1,0.85f),hot(col,1,0.85f));
      }
      if(m==visual::Mode::ACTIVE){
        // Brow blade parallel to the angled top edge.
        const float hw=pose.w*0.5f,topOuter=ecy-pose.h*0.5f*open,topInner=topOuter+pose.slant*open;
        const float ox=ecx-side*hw,ix=ecx+side*(hw-4);
        const float xs[4]={ox,ix,ix,ox},ys[4]={topOuter-12,topInner-12,topInner-8,topOuter-8};
        convex(part,xs,ys,4);fillSpans(c,part,hot(col,0.95f,0.15f));
      }
    }
    if(m==visual::Mode::GREETING){
      const int sx[3]={36,286,160},sy[3]={50,46,118};
      for(int i=0;i<3;++i){
        const int r=int(2+4*fabsf(sinf(now/320.0f+i*2.1f)));const uint16_t sc=hot(col,1,0.6f);
        c.drawFastHLine(sx[i]-r,sy[i],2*r+1,sc);c.drawFastVLine(sx[i],sy[i]-r,2*r+1,sc);c.fillRect(sx[i]-1,sy[i]-1,3,3,sc);
      }
    }
    if(m==visual::Mode::OFFLINE){c.setFont(nullptr);c.setTextSize(1);c.setTextColor(textDim());c.setCursor(160-21,108);c.print("STANDBY");}
  }
  void glitch(FrameCanvas &c,uint32_t now){
    const float t=float(uint32_t(now-glitchMs))/GLITCH_MS;
    if(t>=1){glitching=false;return;}
    const uint32_t seed=hash(now/40+0x9e37U);
    for(int y=CONTENT_TOP;y<=CONTENT_BOTTOM;++y){
      const uint32_t h=hash(seed^uint32_t(y/5)*2654435761U);
      if((h&3)!=0)continue;
      const int dx=int(float(int(h>>8)%29-14)*(1-t));if(!dx)continue;
      uint16_t *r=c.row(y);
      if(dx>0){memmove(r+dx,r,size_t(W-dx)*2);for(int x=0;x<dx;++x)r[x]=BLACK;}
      else{memmove(r,r-dx,size_t(W+dx)*2);for(int x=W+dx;x<W;++x)r[x]=BLACK;}
    }
  }
  void tile(FrameCanvas &c,int x,int y,const char *label,opstatus::Health h,uint32_t now){
    const int w=96,hgt=28;const Rgb hc=healthRgb(h);const bool ok=h==opstatus::Health::OK;
    c.fillRect(x,y,w,hgt,shade(hc,0.07f));c.drawRect(x,y,w,hgt,shade(hc,0.42f));
    const bool pulse=!ok&&h!=opstatus::Health::UNKNOWN&&(now/500)%2;
    c.fillRect(x,y,3,hgt,pulse?shade(hc,0.35f):hot(hc,1,0.1f));
    c.setTextSize(1);c.setTextColor(textGrey());c.setCursor(x+8,y+4);c.print(label);
    const char *state=opstatus::shortName(h);const bool big=int(strlen(state))*12<=w-12;
    c.setTextSize(big?2:1);c.setTextColor(hot(hc,1,0.15f));c.setCursor(x+8,big?y+13:y+16);c.print(state);c.setTextSize(1);
  }
  void dashboard(FrameCanvas &c,const Scene &s){
    const opstatus::Message &m=s.problem;const Rgb lc=levelColor(m.level);
    const opstatus::Local &l=s.local;const opstatus::Facts &f=s.facts;
    const bool live=l.wifi&&l.gateway&&l.controller;
    if(m.level){
      c.fillTriangle(10,47,21,28,32,47,hot(lc,1,0.05f));c.fillRect(20,34,3,7,BLACK);c.fillRect(20,43,3,2,BLACK);
    }else{
      c.fillCircle(21,38,10,hot(lc,1,0.05f));c.drawLine(16,38,20,42,BLACK);c.drawLine(16,39,20,43,BLACK);
      c.drawLine(20,42,27,34,BLACK);c.drawLine(20,43,27,35,BLACK);
    }
    c.setFont(&FreeSansBold9pt7b);c.setTextColor(hot(lc,1,0.2f));c.setCursor(40,42);
    char title[40];strncpy(title,m.title,sizeof(title)-1);title[sizeof(title)-1]=0;c.print(title);c.setFont(nullptr);
    opstatus::line(c,40,48,1,m.action,textGrey(),W-48);
    c.drawFastHLine(10,59,W-20,shade(lc,0.3f));
    const int xs[3]={10,112,214};
    tile(c,xs[0],64,"S3 BRAIN",live?opstatus::Health::OK:opstatus::Health::UNKNOWN,s.now);
    tile(c,xs[1],64,"POWER",live?f.power:opstatus::Health::UNKNOWN,s.now);
    tile(c,xs[2],64,"IMU",live?f.imu:opstatus::Health::UNKNOWN,s.now);
    tile(c,xs[0],96,"LIDAR",live?f.lidar:opstatus::Health::UNKNOWN,s.now);
    tile(c,xs[1],96,"CAMERA",l.camera?opstatus::Health::OK:opstatus::Health::OFFLINE,s.now);
    tile(c,xs[2],96,"RADAR",live?f.radar:opstatus::Health::UNKNOWN,s.now);
    char text[72];
    if(live&&strcmp(f.stop,"NONE"))snprintf(text,sizeof(text),"MAST %s | LAST STOP %s | LINK %s",f.mast,f.stop,f.link);
    else snprintf(text,sizeof(text),"MAST %s | LINK %s",live?f.mast:"UNKNOWN",l.gateway?f.link:"NONE");
    opstatus::line(c,10,129,1,text,textDim(),W-20);
  }
  void splash(FrameCanvas &c,const Scene &s,uint32_t t){
    const uint16_t grid=shade(CYAN,0.07f);
    for(int x=8;x<W;x+=16)c.drawFastVLine(x,0,H,grid);
    for(int y=5;y<H;y+=16)c.drawFastHLine(0,y,W,grid);
    c.setFont(&FreeSansBoldOblique18pt7b);
    const int tw=textWidth(c,"GLADIATOR"),tx=(W-tw)/2-4,base=72;
    c.setTextColor(shade(CYAN,0.35f));
    for(int d=-2;d<=2;d+=4){c.setCursor(tx+d,base);c.print("GLADIATOR");c.setCursor(tx,base+d);c.print("GLADIATOR");}
    c.setTextColor(TEXT_WHITE);c.setCursor(tx,base);c.print("GLADIATOR");c.setFont(nullptr);
    // Scan line reveals the wordmark top to bottom.
    const float rv=clamp01(float(t)/650.0f);const int reveal=40+int(rv*44);
    if(rv<1){for(int y=reveal;y<86;++y)c.drawFastHLine(0,y,W,(y-5)%16==0?grid:BLACK);
      for(int x=8;x<W;x+=16)c.drawFastVLine(x,reveal,86-reveal,grid);
      c.drawFastHLine(0,reveal,W,hot(CYAN,1,0.5f));c.drawFastHLine(0,reveal-1,W,shade(CYAN,0.5f));}
    const float bar=clamp01((float(t)-500)/400.0f);const int half=int(118*(1-(1-bar)*(1-bar)));
    if(half>0){c.fillRect(160-half,80,2*half,3,hot(CYAN,1,0.2f));c.fillRect(160-half,83,2*half,1,shade(CYAN,0.4f));}
    if(t>800){
      char ver[32];snprintf(ver,sizeof(ver),"%s",s.version);for(char *p=ver;*p;++p)if(*p>='a'&&*p<='z')*p-=32;
      c.setTextSize(1);c.setTextColor(textGrey());c.setCursor(160-3*int(strlen(ver)),90);c.print(ver);
    }
    struct Row {const char *name;bool good;const char *yes,*no;};
    const Row rows[3]={{"CAMERA",s.local.camera,"ONLINE","FAULT"},{"WI-FI",s.local.wifi,"LINKED","SEARCHING"},
      {"GATEWAY",s.local.gateway,"ONLINE","WAITING"}};
    for(int i=0;i<3;++i){
      if(t<1000+uint32_t(i)*280)break;
      const int y=110+i*13;c.setTextColor(textGrey());c.setCursor(92,y);c.print(rows[i].name);
      for(int x=92+6*int(strlen(rows[i].name))+4;x<200;x+=4)c.drawPixel(x,y+6,textDim());
      const char *st=rows[i].good?rows[i].yes:rows[i].no;
      c.setTextColor(rows[i].good?hot(GREEN,1,0.1f):hot(AMBER,1,0.1f));c.setCursor(228-6*int(strlen(st)),y);c.print(st);
    }
  }
  void wipe(FrameCanvas &c,const Scene &s,const uint16_t *shown,uint32_t now){
    const float t=float(uint32_t(now-wipeMs))/WIPE_MS;
    if(t>=1||!shown){wiping=false;return;}
    const float e=1-(1-t)*(1-t);const int wx=int(e*(W+8));
    const int y0=wipeFull?0:CONTENT_TOP,y1=wipeFull?H-1:CONTENT_BOTTOM;
    const Rgb accent=s.problem.level?levelColor(s.problem.level):color;
    for(int y=y0;y<=y1;++y){
      uint16_t *r=c.row(y);const uint16_t *o=shown+y*W;
      if(wx<W)memcpy(r+wx,o+wx,size_t(W-wx)*2);
      for(int i=0;i<8;++i){const int x=wx-1-i;if(x>=0&&x<W)r[x]=i<2?hot(accent,1,0.6f):shade(accent,0.7f*(1-i/8.0f));}
    }
  }
};
}
