@echo off
setlocal
title Gladiator Opal LAN health check
echo Read-only check: no movement or calibration changes.
echo Keep this PC connected to SOIT-Field-5G or SOIT-Field.
echo This check takes about one minute.
"C:\Users\jimsc\.platformio\penv\Scripts\python.exe" "C:\PlatformIO\Gladiator\tools\booth\check_gateway_readonly.py" --host 172.23.44.190 --seconds 60 --out "C:\PlatformIO\Gladiator\diagnostics\field-lan-latest.json"
if errorlevel 1 (
 echo CHECK FAILED. Review the output and diagnostics\field-lan-latest.json.
) else (
 echo CHECK PASSED. This does not replace a battery or movement rehearsal.
)
pause
