#pragma once
#include <Arduino.h>
#include <driver/ledc.h>
#include "../BoardConfig.h"
#include "../../shared/MastPolicy.h"
namespace mast {
// GPIO6 is a heartbeat to an EXTERNAL normally-off watchdog power/signal gate.
// A fixed high level must NOT enable it. See FINAL_INTEGRATION.md.
class Hardware {
public:
  void begin(){digitalWrite(board::MAST_GATE_HEARTBEAT,LOW);pinMode(board::MAST_GATE_HEARTBEAT,OUTPUT);
    pinMode(board::MAST_PAN,INPUT_PULLDOWN);pinMode(board::MAST_TILT,INPUT_PULLDOWN);}
  bool start(const Calibration &c){
    ledc_timer_config_t timer={};timer.speed_mode=LEDC_LOW_SPEED_MODE;timer.timer_num=LEDC_TIMER_2;
    timer.duty_resolution=LEDC_TIMER_14_BIT;timer.freq_hz=c.frequencyHz;timer.clk_cfg=LEDC_USE_APB_CLK;
    hz_=c.frequencyHz;
    if(ledc_timer_config(&timer)!=ESP_OK)return false;
    for(unsigned i=0;i<2;++i){ledc_channel_config_t ch={};ch.gpio_num=i?board::MAST_TILT:board::MAST_PAN;
      ch.speed_mode=LEDC_LOW_SPEED_MODE;ch.channel=i?LEDC_CHANNEL_5:LEDC_CHANNEL_4;
      ch.timer_sel=LEDC_TIMER_2;ch.duty=duty(i?c.tilt.neutralUs:c.pan.neutralUs);
      if(ledc_channel_config(&ch)!=ESP_OK){stop();return false;}}
    attached_=true;heartbeatMs_=millis();return true;
  }
  void stop(){digitalWrite(board::MAST_GATE_HEARTBEAT,LOW);heartbeat_=false;
    ledc_stop(LEDC_LOW_SPEED_MODE,LEDC_CHANNEL_4,0);ledc_stop(LEDC_LOW_SPEED_MODE,LEDC_CHANNEL_5,0);
    pinMode(board::MAST_PAN,INPUT_PULLDOWN);pinMode(board::MAST_TILT,INPUT_PULLDOWN);attached_=false;}
  bool write(const Controller &c,uint32_t now){
    if(!c.enabled){if(attached_)stop();return true;}
    if(!attached_)return false;
    if(ledc_set_duty(LEDC_LOW_SPEED_MODE,LEDC_CHANNEL_4,duty(c.calibration.pan.pulse(c.pan)))!=ESP_OK||
       ledc_update_duty(LEDC_LOW_SPEED_MODE,LEDC_CHANNEL_4)!=ESP_OK||
       ledc_set_duty(LEDC_LOW_SPEED_MODE,LEDC_CHANNEL_5,duty(c.calibration.tilt.pulse(c.tilt)))!=ESP_OK||
       ledc_update_duty(LEDC_LOW_SPEED_MODE,LEDC_CHANNEL_5)!=ESP_OK)return false;
    if(uint32_t(now-heartbeatMs_)>=25){heartbeatMs_=now;heartbeat_=!heartbeat_;digitalWrite(board::MAST_GATE_HEARTBEAT,heartbeat_?HIGH:LOW);}return true;
  }
private:
  bool attached_=false,heartbeat_=false;uint16_t hz_=0;uint32_t heartbeatMs_=0;
  uint32_t duty(uint16_t us)const{return uint32_t(uint64_t(us)*hz_*16384/1000000);}
};
}
