// Host preview of the masthead display (cam/src/FaceRender.h).
// Runs the real renderer and the real changed-tile push against a fake panel,
// checks the panel always ends up identical to the frame, and estimates SPI
// time per frame at the CAM's 4 MHz draw clock.
// Output: <out>/<scenario>.rgb (raw RGB888 frames) and <out>/timing.json.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <vector>
#include <string>
#include "FaceRender.h"

using face::W;using face::H;
static const double SPI_HZ=4000000.0;
static const double RENDER_MS=12.0;  // assumed CPU time per frame on the ESP32 (not measured)

struct FakePanel {
  std::vector<uint16_t> glass=std::vector<uint16_t>(W*H,0);
  int wx=0,wy=0,ww=0,wh=0,cx=0,cy=0;uint64_t bytes=0,calls=0;
  void startWrite(){}
  void endWrite(){}
  void setAddrWindow(int x,int y,int w,int h){wx=x;wy=y;ww=w;wh=h;cx=cy=0;bytes+=11;++calls;}
  void writePixels(uint16_t *p,uint32_t n,bool,bool){
    for(uint32_t i=0;i<n;++i){glass[(wy+cy)*W+wx+cx]=p[i];if(++cx==ww){cx=0;++cy;}}
    bytes+=uint64_t(n)*2;++calls;
  }
};

struct World {
  visual::Mode mode=visual::Mode::READY;const char *state="SAFE",*battery="OK";
  float volts=15.84f;int range=1840;int rssi=-58;bool wifi=true,gateway=true,controller=true,camera=true;
  opstatus::Health power=opstatus::Health::OK,imu=opstatus::Health::OK,lidar=opstatus::Health::OK,radar=opstatus::Health::OFFLINE;
  int forceView=-1;  // -1 real 12 s rotation, 0 face, 1 status
  const char *message="";
};

static face::Scene scene(const World &w,uint32_t now){
  face::Scene s;s.now=now;
  s.local.wifi=w.wifi;s.local.gateway=w.wifi&&w.gateway;s.local.controller=s.local.gateway&&w.controller;
  s.local.camera=w.camera;s.local.starting=now<10000;s.local.battery=s.local.controller?w.battery:"UNKNOWN";
  s.facts.available=true;s.facts.power=w.power;s.facts.imu=w.imu;s.facts.lidar=w.lidar;s.facts.radar=w.radar;
  strcpy(s.facts.mast,"MANUAL");strcpy(s.facts.link,"UART");
  s.mode=s.local.controller?w.mode:visual::Mode::OFFLINE;
  s.problem=opstatus::select(s.facts,s.local,now);
  s.statusView=w.forceView<0?opstatus::dashboard(s.problem,now):w.forceView==1;
  if(s.problem.level)s.statusView=true;
  s.volts=s.local.controller?w.volts:0;s.battery=s.local.controller?w.battery:"UNKNOWN";
  s.rangeMm=s.local.controller?w.range:-1;s.rssi=w.wifi?w.rssi:0;s.version="masthead-1.4.0";
  if(w.message[0]&&s.local.controller){snprintf(s.footer,sizeof(s.footer),"%s",w.message);s.operatorMessage=true;}
  else snprintf(s.footer,sizeof(s.footer),"Gateway 192.168.8.1 | %s",w.wifi?"Wi-Fi OK":"Wi-Fi lost");
  return s;
}

typedef void (*Script)(World &,uint32_t t);
struct Scenario {const char *name;uint32_t ms;bool boot;Script script;};

static void bootScript(World &w,uint32_t t){w.wifi=t>1500;w.gateway=t>2300;w.forceView=0;}
static void readyScript(World &w,uint32_t){w.forceView=0;}
static void scanScript(World &w,uint32_t){w.mode=visual::Mode::SCANNING;w.state="ARMED";w.forceView=0;}
static void engagedScript(World &w,uint32_t t){
  w.forceView=0;w.mode=t<900?visual::Mode::READY:visual::Mode::ACTIVE;w.state=t<900?"SAFE":"DRIVE";
  w.range=int(1900-t*0.25);w.volts=15.6f-(t>900?0.9f:0);
}
static void alertScript(World &w,uint32_t t){w.forceView=0;w.mode=t<700?visual::Mode::ACTIVE:visual::Mode::ALERT;w.state="DRIVE";w.range=t<700?620:380;w.volts=14.9f;}
static void helloScript(World &w,uint32_t){w.forceView=0;w.mode=visual::Mode::GREETING;w.message="Welcome to the arena!";}
static void statusScript(World &w,uint32_t t){w.forceView=(t>1200&&t<5200)?1:0;}
static void checkScript(World &w,uint32_t){w.imu=opstatus::Health::NO_POSE;}
static void faultScript(World &w,uint32_t){w.gateway=false;}

int main(int argc,char **argv){
  const char *out=argc>1?argv[1]:".";
  const Scenario scenarios[]={
    {"boot",5200,true,bootScript},{"ready",6600,false,readyScript},{"scanning",5400,false,scanScript},
    {"engaged",5200,false,engagedScript},{"alert",3200,false,alertScript},{"hello",4200,false,helloScript},
    {"status",6400,false,statusScript},{"check",3000,false,checkScript},{"fault",3000,false,faultScript},
  };
  std::string json="{\"spiHz\":4000000,\"assumedRenderMs\":12,\"scenarios\":[";
  bool firstScenario=true;int failures=0;
  for(const auto &sc:scenarios){
    std::vector<uint16_t> a(W*H,0),shown(W*H,0);FrameCanvas canvas(W,H,a.data());
    FakePanel panel;face::Renderer renderer;World world;
    uint32_t now=sc.boot?500:20000;bool full=true;  // past the 10 s start-up grace, so faults show as faults
    if(!sc.boot){  // Skip the splash: run the renderer on the scenario's first state first.
      for(uint32_t t=0;t<face::SPLASH_MS+face::WIPE_MS+300;t+=67){World w;sc.script(w,0);renderer.draw(canvas,scene(w,now),shown.data());frame::pushChanged(panel,a.data(),shown.data(),W,H,full);full=false;now+=67;}
    }
    std::string path=std::string(out)+"/"+sc.name+".rgb";FILE *f=fopen(path.c_str(),"wb");if(!f){perror(path.c_str());return 1;}
    std::string times;double worst=0,total=0;int frames=0;uint64_t pushedPx=0;
    for(uint32_t t=0;t<sc.ms;){
      World w;sc.script(w,t);
      const uint64_t before=panel.bytes,callsBefore=panel.calls;
      renderer.draw(canvas,scene(w,now),shown.data());
      pushedPx+=frame::pushChanged(panel,a.data(),shown.data(),W,H,full);full=false;
      if(memcmp(panel.glass.data(),a.data(),size_t(W*H)*2)||memcmp(shown.data(),a.data(),size_t(W*H)*2)){++failures;fprintf(stderr,"%s t=%u: panel != frame\n",sc.name,t);}
      const double spiMs=double(panel.bytes-before)*8/SPI_HZ*1000+double(panel.calls-callsBefore)*0.02;
      double period=spiMs+RENDER_MS;if(period<67)period=67;
      if(spiMs>worst)worst=spiMs;total+=period;++frames;
      std::vector<uint8_t> rgb(W*H*3);
      for(int i=0;i<W*H;++i){const uint16_t p=panel.glass[i];rgb[i*3]=uint8_t(((p>>11)&31)*255/31);rgb[i*3+1]=uint8_t(((p>>5)&63)*255/63);rgb[i*3+2]=uint8_t((p&31)*255/31);}
      fwrite(rgb.data(),1,rgb.size(),f);
      char buf[24];snprintf(buf,sizeof(buf),"%s%.1f",times.empty()?"":",",period);times+=buf;
      t+=uint32_t(period);now+=uint32_t(period);
    }
    fclose(f);
    char head[256];snprintf(head,sizeof(head),"%s{\"name\":\"%s\",\"frames\":%d,\"fps\":%.1f,\"worstSpiMs\":%.1f,\"periodsMs\":[",firstScenario?"":",",sc.name,frames,frames*1000.0/total,worst);
    json+=head;json+=times;json+="]}";firstScenario=false;
    printf("%-9s frames=%3d  avg %.1f fps  worst push %.0f ms\n",sc.name,frames,frames*1000.0/total,worst);
  }
  json+="]}";FILE *j=fopen((std::string(out)+"/timing.json").c_str(),"w");fputs(json.c_str(),j);fclose(j);
  if(failures){printf("FAIL: %d frames where the panel did not match the frame\n",failures);return 2;}
  puts("Panel matched every frame (changed-tile push is lossless).");
  return 0;
}
