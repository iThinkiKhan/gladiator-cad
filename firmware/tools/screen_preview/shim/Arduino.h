#pragma once
// Host-only stand-in so Adafruit GFX and the CAM renderer compile on the PC.
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdio.h>
#include "pgmspace.h"
typedef bool boolean;
typedef uint8_t byte;
class __FlashStringHelper;
class String { public: const char *c_str() const { return ""; } unsigned length() const { return 0; } };
#define radians(d) ((d) * 0.017453292519943295)
#define degrees(r) ((r) * 57.29577951308232)
