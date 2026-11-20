#pragma once
#if __has_include("LocalConfig.h")
#include "LocalConfig.h"
#endif
#ifndef VISUAL_WIFI_SSID
#define VISUAL_WIFI_SSID ""
#define VISUAL_WIFI_PASSWORD ""
#endif
#ifndef VISUAL_GATEWAY_URL
#define VISUAL_GATEWAY_URL "http://192.168.8.1"
#endif
#ifndef VISUAL_TFT_WIDTH
#define VISUAL_TFT_WIDTH 170
#endif
#ifndef VISUAL_TFT_HEIGHT
#define VISUAL_TFT_HEIGHT 320
#endif
#ifndef VISUAL_TFT_ROTATION
#define VISUAL_TFT_ROTATION 1
#endif
#ifndef VISUAL_OTA_KEY
#define VISUAL_OTA_KEY ""
#endif
#ifndef VISUAL_FIRMWARE_VERSION
#define VISUAL_FIRMWARE_VERSION "masthead-1.4.2"
#endif
namespace config {
constexpr int SCLK=14,MOSI=13,DC=2,CS=15,RESET=-1;
constexpr int LIGHT_PIN=4,LIGHT_CHANNEL=2; // Camera XCLK owns LEDC channel 0 / timer 0.
constexpr int STATUS_LED_PIN=33;
constexpr uint32_t DISPLAY_INIT_HZ=1000000,DISPLAY_DRAW_HZ=4000000;
// Physical panel is upside down. Apply offset even to existing LocalConfig.
constexpr uint8_t DISPLAY_ROTATION=(VISUAL_TFT_ROTATION+2)%4;
constexpr uint32_t STALE_MS=1500,FRAME_MS=67,POLL_MS=200;
constexpr char VERSION[]=VISUAL_FIRMWARE_VERSION;
constexpr uint32_t OTA_CONFIRM_MS=120000,RECOVERY_MS=30000;
// Flash LED spotlight on GPIO4. 100% on the operator slider = LIGHT_MAX_DUTY of 255
// (about half power): the bare LED runs hot, and it sits under a PLA light tube.
constexpr uint32_t LIGHT_MAX_DUTY=128,LIGHT_PWM_HZ=20000,LIGHT_TIMEOUT_MS=120000;
}
