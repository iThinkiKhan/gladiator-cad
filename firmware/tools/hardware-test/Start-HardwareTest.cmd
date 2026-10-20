@echo off
setlocal
cd /d "%~dp0"
set "GLADIATOR_PYTHON=%USERPROFILE%\.platformio\penv\Scripts\python.exe"
if exist "%GLADIATOR_PYTHON%" (
  "%GLADIATOR_PYTHON%" serve.py --open
) else (
  py -3 serve.py --open
)
if errorlevel 1 pause
