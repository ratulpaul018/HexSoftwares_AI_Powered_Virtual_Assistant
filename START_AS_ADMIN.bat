@echo off
REM This batch file runs the AI Assistant Flask app as Administrator
REM Right-click this file and select "Run as Administrator"

cd /d "%~dp0"

echo.
echo ========================================
echo AI Virtual Assistant - Admin Launch
echo ========================================
echo.
echo This will start Flask with ADMIN privileges
echo All Wi-Fi, Bluetooth, and system controls will work.
echo.

python app.py

pause
