@echo off
chcp 65001 >nul
title 🌐 NGROK TUNNEL - ANDROID ACCESS
color 0B

echo ==========================================
echo    NGROK TUNNEL FOR ANDROID APP
echo ==========================================
echo Creates public URL to your laptop
echo Android connects to ngrok URL
echo ==========================================
echo.

cd /d C:\ngrok

REM 🔑 GET YOUR FREE NGROK TOKEN:
REM 1. Go to: https://dashboard.ngrok.com/signup
REM 2. Sign up (free)
REM 3. Go to: https://dashboard.ngrok.com/get-started/your-authtoken
REM 4. Copy token and replace below:

set NGROK_TOKEN=YOUR_NGROK_TOKEN_HERE

echo Setting up ngrok...
ngrok config add-authtoken %NGROK_TOKEN%

echo.
echo 🌐 Starting tunnel to localhost:5000...
echo 📱 Android will use the URL shown below
echo 💡 URL changes each time ngrok restarts
echo.

:tunnel
ngrok http 5000 --region=ap

echo.
echo Tunnel stopped. Restarting in 5 seconds...
timeout /t 5 /nobreak >nul
goto tunnel
