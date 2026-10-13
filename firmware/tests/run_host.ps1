$ErrorActionPreference = 'Stop'
Push-Location (Join-Path $PSScriptRoot '..')
try {
  $compilerDir = Join-Path $env:USERPROFILE '.platformio\packages\toolchain-gccmingw32\bin'
  $env:PATH = "$compilerDir;$env:PATH"
  New-Item -ItemType Directory -Force 'build-output\host' | Out-Null
  & "$compilerDir\g++.exe" -std=c++17 -Wall -Wextra -Werror tests/visual_state_test.cpp -o build-output/host/visual_state_test.exe
  if ($LASTEXITCODE) { throw 'Visual policy compilation failed' }
  & .\build-output\host\visual_state_test.exe
  if ($LASTEXITCODE) { throw 'Visual policy tests failed' }
  $cjsonDir = 'gateway/managed_components/espressif__cjson/cJSON'
  & "$compilerDir\gcc.exe" -std=c99 "-I$cjsonDir" -c "$cjsonDir/cJSON.c" -o build-output/host/cJSON.o
  if ($LASTEXITCODE) { throw 'cJSON compilation failed' }
  & "$compilerDir\g++.exe" -std=c++17 -Wall -Wextra -Werror "-I$cjsonDir" tests/gateway_visual_test.cpp build-output/host/cJSON.o -lws2_32 -o build-output/host/gateway_visual_test.exe
  if ($LASTEXITCODE) { throw 'Gateway handler compilation failed' }
  & .\build-output\host\gateway_visual_test.exe
  if ($LASTEXITCODE) { throw 'Gateway handler tests failed' }
  node tests/field_page_test.js
  if ($LASTEXITCODE) { throw 'Browser tests failed' }
} finally { Pop-Location }
