@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0stop-native.ps1" %*
exit /b %errorlevel%
