$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
Push-Location $taskRoot
try {
    & diagnostics/test-tools/ziglang/zig.exe c++ -std=c++17 -DGLADIATOR_PROTOCOL_TEST=1 test/host/test_protocol.cpp -o diagnostics/protocol-tests.exe
    if ($LASTEXITCODE -ne 0) { throw 'Protocol test compilation failed' }
    & diagnostics/protocol-tests.exe
    if ($LASTEXITCODE -ne 0) { throw 'Protocol tests failed' }
    & diagnostics/test-tools/ziglang/zig.exe c++ -std=c++17 test/host/test_link.cpp -o diagnostics/link-tests.exe
    if ($LASTEXITCODE -ne 0) { throw 'Gladiator Link test compilation failed' }
    & diagnostics/link-tests.exe
    if ($LASTEXITCODE -ne 0) { throw 'Gladiator Link tests failed' }
    & diagnostics/test-tools/ziglang/zig.exe c++ -std=c++17 -I test/host test/host/test_wifi.cpp -lbcrypt -o diagnostics/wifi-link-tests.exe
    if ($LASTEXITCODE -ne 0) { throw 'Wi-Fi adapter test compilation failed' }
    & diagnostics/wifi-link-tests.exe
    if ($LASTEXITCODE -ne 0) { throw 'Wi-Fi adapter tests failed' }
} finally { Pop-Location }
