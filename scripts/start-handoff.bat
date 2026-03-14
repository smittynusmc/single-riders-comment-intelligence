@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-handoff.ps1" %*
exit /b %errorlevel%
