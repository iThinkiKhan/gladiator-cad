param(
  [string]$Gateway = '172.23.44.190',
  [string]$ExpectedVersion = 'gateway-2.4.2',
  [switch]$C6Only,
  [switch]$UsbPowered
)
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path
$runtimePythonPath = Join-Path $env:USERPROFILE '.platformio/penv/Scripts/python.exe'
$releasePath = Join-Path $projectRoot 'diagnostics/operator-20261023/release/candidate.json'
if (!(Test-Path -LiteralPath $runtimePythonPath)) { throw 'The local PlatformIO Python runtime is missing.' }
if (!(Test-Path -LiteralPath $releasePath)) { throw 'The reviewed operator release manifest is missing. Build and verify the release first.' }
$candidate = Get-Content -LiteralPath $releasePath -Raw | ConvertFrom-Json
Write-Host 'Install the saved-settings operator release after calibration is saved and servo tests are OFF.'
Write-Host 'This briefly restarts C6. The installer refuses an active mast/test or armed tracks.'
Write-Host 'Saved entries are read before the update and compared afterward. No calibration is applied and no motion is started.'
Push-Location -LiteralPath $projectRoot
try {
  $maintenanceArgs = @()
  if ($C6Only) { $maintenanceArgs += '--c6-only'; Write-Host 'C6-only: S3 must remain disconnected. Applying the profile and motion checks wait for robot power.' }
  if ($UsbPowered) { $maintenanceArgs += '--usb-powered'; Write-Host 'USB maintenance: fresh low-voltage electronics power, movement lockout and all outputs OFF are required.' }
  & $runtimePythonPath 'tools/booth/deploy_c6.py' @maintenanceArgs --host $Gateway --expect-version $ExpectedVersion --expect-sha256 $candidate.sha256
  if ($LASTEXITCODE -ne 0) { throw 'Installation or verification did not complete. Read the error; do not repeatedly upload after an accepted update.' }
  Write-Host "Verified. Open http://$Gateway/booth/ on this network."
} finally {
  Pop-Location
}
