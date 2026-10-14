#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
mkdir -p build-output/host
g++ -std=c++17 -Wall -Wextra -Werror tests/mast_policy_test.cpp -o build-output/host/mast_policy_test
build-output/host/mast_policy_test
g++ -std=c++17 -Wall -Wextra -Werror tests/visual_state_test.cpp -o build-output/host/visual_state_test
build-output/host/visual_state_test
g++ -std=c++17 -Wall -Wextra -Werror tests/cam_ota_test.cpp -o build-output/host/cam_ota_test
build-output/host/cam_ota_test
CJSON_DIR=gateway/managed_components/espressif__cjson/cJSON
gcc -std=c99 -I"$CJSON_DIR" -c "$CJSON_DIR/cJSON.c" -o build-output/host/cJSON.o
g++ -std=c++17 -Wall -Wextra -Werror -I"$CJSON_DIR" tests/gateway_visual_test.cpp build-output/host/cJSON.o -o build-output/host/gateway_visual_test
build-output/host/gateway_visual_test
node tests/field_page_test.js
node tests/cam_maintenance_test.js
