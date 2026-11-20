#pragma once
#include <stdint.h>

namespace fieldnet {
constexpr char SSID[] = "Gladiator-Gateway";
constexpr char GATEWAY_URL[] = "http://192.168.8.1";
constexpr uint8_t PREFIX_A = 192, PREFIX_B = 168, PREFIX_C = 8;
constexpr uint8_t GATEWAY = 1, CAMERA = 2;
constexpr uint8_t DHCP_FIRST = 10, DHCP_LAST = 109;
static_assert(GATEWAY < DHCP_FIRST && CAMERA < DHCP_FIRST,
              "Fixed field addresses must stay outside the DHCP pool");
}
