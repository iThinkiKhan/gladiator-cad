#pragma once
#include <driver/rtc_io.h>
#include <soc/gpio_struct.h>
#include <soc/rtc_io_reg.h>
#include <esp32-hal-matrix.h>
// Only the render/setup task writes SPI. HTTP queues bounded display-only work.
std::atomic<uint32_t> displayDrawHz{config::DISPLAY_DRAW_HZ},displaySpiMode{0},displayInitializations{0},displayWrites{0},displayAppliedSequence{0};
std::atomic<uint32_t> displayWidth{0},displayHeight{0};
std::atomic<bool> displayPatternActive{false},displaySoftwareSpi{false};
std::atomic<bool> displayDcProbeActive{false};
std::atomic<uint32_t> displayDcProbeLevel{1};
// Separate driver objects avoid changing Adafruit's hardware/software union.
Adafruit_ST7789 softwareDisplay(config::CS,config::DC,config::MOSI,config::SCLK,config::RESET);
Adafruit_ST7789 &diagnosticDisplay(){return displaySoftwareSpi.load()?softwareDisplay:tft;}
struct DisplayRequest {uint32_t sequence=0,hz=config::DISPLAY_DRAW_HZ,mode=0,duration=0;bool reinit=false,software=false,probe=false;uint32_t level=1;};
DisplayRequest displayRequest;
void initializeDisplay(bool clear=true){
  auto &screen=diagnosticDisplay();
  // RESET is tied high on the mounted panel. This is an SPI software reset,
  // not a hardware reset or a power cycle. Allow power/oscillator settling
  // before reapplying the display state, including after a warm CAM reboot.
  pinMode(config::CS,OUTPUT);digitalWrite(config::CS,HIGH);delay(200);
  screen.init(VISUAL_TFT_WIDTH,VISUAL_TFT_HEIGHT,displaySpiMode.load()==3?SPI_MODE3:SPI_MODE0);
  screen.sendCommand(ST77XX_SWRESET);delay(150);
  screen.sendCommand(ST77XX_SLPOUT);delay(150);
  const uint8_t colorMode=0x55;
  screen.sendCommand(ST77XX_COLMOD,&colorMode,1);delay(10);
  constexpr uint8_t idleModeOff=0x38; // ST7789 IDMOFF; no Adafruit ST77XX constant.
  screen.sendCommand(idleModeOff);screen.sendCommand(ST77XX_NORON);
  screen.invertDisplay(true);screen.sendCommand(ST77XX_DISPON);delay(150);
  screen.setRotation(config::DISPLAY_ROTATION);
  // setSPISpeed writes the hardware union even for a software-SPI object.
  if(!displaySoftwareSpi)screen.setSPISpeed(displayDrawHz.load());
  if(clear)screen.fillScreen(ST77XX_BLACK);
  displayWidth=screen.width();displayHeight=screen.height();
  ++displayInitializations;
  Serial.printf("Display init: %ux%u rotation=%u transport=%s\n",screen.width(),screen.height(),config::DISPLAY_ROTATION,displaySoftwareSpi?"software":"hardware");
}
void drawDisplayPattern(){
  auto &screen=diagnosticDisplay();const int w=screen.width(),h=screen.height();
  screen.fillRect(0,0,w/2,h/2,ST77XX_RED);lastLoopMs=millis();
  screen.fillRect(w/2,0,w-w/2,h/2,ST77XX_GREEN);lastLoopMs=millis();
  screen.fillRect(0,h/2,w/2,h-h/2,ST77XX_BLUE);lastLoopMs=millis();
  screen.fillRect(w/2,h/2,w-w/2,h-h/2,ST77XX_WHITE);lastLoopMs=millis();
  screen.drawRect(0,0,w,h,ST77XX_WHITE);screen.drawFastHLine(0,h/2,w,ST77XX_BLACK);screen.drawFastVLine(w/2,0,h,ST77XX_BLACK);
  screen.fillRect(8,8,w-16,42,ST77XX_BLACK);screen.setTextColor(ST77XX_WHITE);screen.setTextSize(2);screen.setCursor(14,12);screen.print("DISPLAY CHECK");
  screen.setTextSize(1);screen.setCursor(14,35);
  if(displaySoftwareSpi)screen.print("Software SPI | clock not measured");else screen.printf("%u Hz | SPI mode %u",displayDrawHz.load(),displaySpiMode.load());++displayWrites;
}
void restoreHardwareDisplay(){
  displaySoftwareSpi=false;displaySpiMode=0;
  displaySpi.begin(config::SCLK,-1,config::MOSI,config::CS);initializeDisplay();
}
bool serviceDisplayCommand(uint32_t now){
  static uint32_t started=0,duration=0,lastBlink=0;static bool blink=false;
  DisplayRequest request;xSemaphoreTake(stateMutex,portMAX_DELAY);request=displayRequest;xSemaphoreGive(stateMutex);
  if(request.sequence!=displayAppliedSequence.load()){
    if(request.probe){
      if(displaySoftwareSpi){displaySoftwareSpi=false;displaySpi.begin(config::SCLK,-1,config::MOSI,config::CS);}
      pinMode(config::CS,OUTPUT);digitalWrite(config::CS,HIGH);
      // This probe is restricted to the existing CAM display DC pin.
      // Detach RTC ownership and explicitly configure a push-pull GPIO output.
      if(rtc_gpio_is_valid_gpio(static_cast<gpio_num_t>(config::DC)))rtc_gpio_deinit(static_cast<gpio_num_t>(config::DC));
      pinMatrixOutDetach(config::DC,false,false);
      pinMode(config::DC,OUTPUT);digitalWrite(config::DC,request.level?HIGH:LOW);
      displayDcProbeLevel=request.level;displayDcProbeActive=true;displayPatternActive=false;
      started=millis();duration=request.duration;
    }else{
    const bool wasProbe=displayDcProbeActive.exchange(false);
    const bool changed=displaySoftwareSpi.load()!=request.software;
    if(changed){if(request.software)displaySpi.end();else displaySpi.begin(config::SCLK,-1,config::MOSI,config::CS);}
    displaySoftwareSpi=request.software;displayDrawHz=request.hz;displaySpiMode=request.mode;
    if(request.reinit||changed||wasProbe)initializeDisplay(request.duration==0);else if(!request.software)tft.setSPISpeed(request.hz);
    lastLoopMs=millis();
    started=millis();duration=request.duration;displayPatternActive=duration>0;
    if(duration)drawDisplayPattern();
    }
    displayAppliedSequence=request.sequence;lastBlink=millis();
  }
  now=millis(); // Reinitialization/pattern writes may take time; do not use a pre-write timestamp.
  if(displayDcProbeActive&&uint32_t(now-started)>=duration){displayDcProbeActive=false;initializeDisplay();}
  if(displayPatternActive&&uint32_t(now-started)>=duration){displayPatternActive=false;if(displaySoftwareSpi)restoreHardwareDisplay();}
  if(displayPatternActive&&uint32_t(now-lastBlink)>=500){lastBlink=now;blink=!blink;auto &screen=diagnosticDisplay();screen.fillRect(screen.width()-20,screen.height()-20,12,12,blink?ST77XX_BLACK:ST77XX_YELLOW);++displayWrites;}
  return displayPatternActive.load()||displayDcProbeActive.load();
}
esp_err_t displayHandler(httpd_req_t *req){
  if(req->method==HTTP_POST){
    if(!camAuthorize(req))return ESP_OK;
    if(otaUpdating)return cameraUnavailable(req,"Firmware update in progress");
    if(!req->content_len||req->content_len>192)return httpd_resp_send_err(req,HTTPD_400_BAD_REQUEST,"Display body too large");
    char body[193]={};size_t got=0;while(got<req->content_len){int n=httpd_req_recv(req,body+got,req->content_len-got);if(n<=0)return ESP_FAIL;got+=n;}
    StaticJsonDocument<384> doc;bool valid=!deserializeJson(doc,body)&&doc.is<JsonObject>();const char *action=doc["action"]|"";
    const bool pattern=!strcmp(action,"pattern"),normal=!strcmp(action,"normal"),reinit=!strcmp(action,"reinit"),probe=!strcmp(action,"dc-probe");valid=valid&&(pattern||normal||reinit||probe);
    int hz=displayDrawHz.load(),mode=displaySpiMode.load(),duration=60000,level=1;
    if(doc.containsKey("dcLevel"))valid=valid&&cameraValue(doc["dcLevel"],0,1,level);
    const char *transport=doc["transport"]|"hardware";const bool software=!strcmp(transport,"software");
    valid=valid&&(software||!strcmp(transport,"hardware"));
    if(doc.containsKey("spiHz"))valid=valid&&cameraValue(doc["spiHz"],1000000,20000000,hz);
    if(doc.containsKey("spiMode"))valid=valid&&cameraValue(doc["spiMode"],0,3,mode)&&(mode==0||mode==3);
    if(doc.containsKey("durationMs"))valid=valid&&cameraValue(doc["durationMs"],1000,120000,duration);
    valid=valid&&(!software||(pattern&&mode==0));
    if(!valid)return httpd_resp_send_err(req,HTTPD_400_BAD_REQUEST,"Display action pattern/normal/reinit/dc-probe; dcLevel0/1; 1-20MHz; mode0/3; 1-120s; software only for mode0 pattern");
    xSemaphoreTake(stateMutex,portMAX_DELAY);displayRequest.hz=hz;displayRequest.mode=mode;displayRequest.duration=(pattern||probe)?duration:0;
    displayRequest.probe=probe;displayRequest.level=level;
    displayRequest.software=software;displayRequest.reinit=reinit||doc.containsKey("spiHz")||doc.containsKey("spiMode");++displayRequest.sequence;xSemaphoreGive(stateMutex);
  }
  StaticJsonDocument<1024> status;status["initHz"]=displaySoftwareSpi?0:config::DISPLAY_INIT_HZ;status["drawHz"]=displaySoftwareSpi?0:displayDrawHz.load();status["spiMode"]=displaySpiMode.load();status["rotation"]=config::DISPLAY_ROTATION;
  status["transport"]=displaySoftwareSpi?"software":"hardware";status["clockMeasured"]=false;
  status["resetMethod"]="spi-software";status["wakeDelayMs"]=150;
  status["width"]=displayWidth.load();status["height"]=displayHeight.load();status["pattern"]=displayPatternActive.load();status["initializations"]=displayInitializations.load();status["writes"]=displayWrites.load();status["appliedSequence"]=displayAppliedSequence.load();status["hardwareReadbackAvailable"]=false;
  auto dc=status.createNestedObject("dc");dc["pin"]=config::DC;dc["probeActive"]=displayDcProbeActive.load();dc["requestedLevel"]=displayDcProbeLevel.load();
  dc["outputEnabled"]=bool(GPIO.enable&(1UL<<config::DC));dc["latch"]=bool(GPIO.out&(1UL<<config::DC));dc["input"]=bool(GPIO.in&(1UL<<config::DC));
  dc["outputSignal"]=uint32_t(GPIO.func_out_sel_cfg[config::DC].func_sel);
  dc["rtcMux"]=config::DC==2?bool(REG_READ(RTC_IO_TOUCH_PAD2_REG)&RTC_IO_TOUCH_PAD2_MUX_SEL):false;
  char body[1024];size_t n=serializeJson(status,body,sizeof(body));httpd_resp_set_type(req,"application/json");return httpd_resp_send(req,body,n);
}
