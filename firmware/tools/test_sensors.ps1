param([string]$Compiler = '')
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
Push-Location $taskRoot
try {
    if (-not $Compiler) {
        $localCompiler = Join-Path $taskRoot 'diagnostics/test-tools/ziglang/zig.exe'
        if (Test-Path -LiteralPath $localCompiler) { $Compiler = $localCompiler }
        else { $Compiler = 'g++' }
    }
    $compilerArgs = @()
    if ([IO.Path]::GetFileNameWithoutExtension($Compiler) -eq 'zig') { $compilerArgs += 'c++' }
    $compilerArgs += @('-std=c++17', '-DGLADIATOR_HOST_TEST=1', '-I', 'test/host', '-I', 'src', '-I',
        '.pio/libdeps/gladiator_s3/Adafruit BNO08x/src', 'test/host/test_sensors.cpp',
        'src/sensors/INA226Sensor.cpp', 'src/sensors/MatrixLidarSensor.cpp',
        'src/sensors/PresenceSensor.cpp', '-o', 'diagnostics/sensor-tests.exe')
    & $Compiler @compilerArgs
    if ($LASTEXITCODE -ne 0) { throw 'Sensor test compilation failed' }
    & (Join-Path $taskRoot 'diagnostics/sensor-tests.exe')
    if ($LASTEXITCODE -ne 0) { throw 'Sensor tests failed' }
} finally { Pop-Location }
