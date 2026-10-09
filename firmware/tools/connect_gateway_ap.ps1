$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
$taskProfile = Join-Path $taskRoot 'diagnostics/gateway-private/ap-profile.xml'
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $taskProfile) | Out-Null
$secrets = Join-Path $taskRoot 'shared/secrets.h'
if (-not (Test-Path $secrets)) { $secrets = Join-Path $taskRoot 'shared/secrets.example.h' }
$fieldPassword = [regex]::Match((Get-Content -Raw $secrets), 'GLADIATOR_FIELD_PASSWORD\s+"([^"]+)"').Groups[1].Value
@"
<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
  <name>Gladiator-Gateway</name>
  <SSIDConfig><SSID><name>Gladiator-Gateway</name></SSID></SSIDConfig>
  <connectionType>ESS</connectionType><connectionMode>manual</connectionMode>
  <MSM><security><authEncryption><authentication>WPA2PSK</authentication><encryption>AES</encryption><useOneX>false</useOneX></authEncryption>
  <sharedKey><keyType>passPhrase</keyType><protected>false</protected><keyMaterial>$fieldPassword</keyMaterial></sharedKey></security></MSM>
</WLANProfile>
"@ | Set-Content -LiteralPath $taskProfile -Encoding utf8
netsh wlan add profile filename="$taskProfile" user=current
netsh wlan connect name=Gladiator-Gateway
