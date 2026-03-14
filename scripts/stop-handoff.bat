@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0stop-handoff.ps1" %*
exit /b %errorlevel%
