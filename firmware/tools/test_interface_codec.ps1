$ErrorActionPreference = 'Stop'
Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    $taskSource = [IO.File]::ReadAllText((Join-Path (Get-Location) 'gateway/src/LinkApplication.h'))
    $taskStart = $taskSource.IndexOf('void number(')
    $taskEnd = $taskSource.IndexOf('void receiveTyped(', $taskStart)
    [IO.File]::WriteAllText((Join-Path (Get-Location) 'diagnostics/interface-decoder.inc'), $taskSource.Substring($taskStart, $taskEnd - $taskStart))
    & diagnostics/test-tools/ziglang/zig.exe cc -c gateway/managed_components/espressif__cjson/cJSON/cJSON.c -o diagnostics/interface-cjson.o
    if ($LASTEXITCODE -ne 0) { throw 'cJSON compilation failed' }
    & diagnostics/test-tools/ziglang/zig.exe c++ -std=c++17 test/host/test_interface.cpp diagnostics/interface-cjson.o -o diagnostics/interface-codec-tests.exe
    if ($LASTEXITCODE -ne 0) { throw 'Interface codec compilation failed' }
    & diagnostics/interface-codec-tests.exe
    if ($LASTEXITCODE -ne 0) { throw 'Interface codec tests failed' }
} finally { Pop-Location }
