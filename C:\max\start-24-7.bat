@echo off
chcp 65001 >nul
title 🤖 AI TEACHER 24/7 - LAPTOP SERVER
color 0A

echo ==========================================
echo    AI TEACHER 24/7 - LOCAL SERVER
echo    Running on YOUR Laptop (RTX 3050)
echo ==========================================
echo Model: llama3.2:3b (already installed)
echo GPU: RTX 3050 4GB
echo Local: http://localhost:5000
echo Android: Use ngrok tunnel
echo ==========================================
echo.

cd /d C:\max

:check_ollama
echo 1. Checking Ollama service...
tasklist | findstr "ollama.exe" >nul
if errorlevel 1 (
    echo   Starting Ollama server...
    start "Ollama Server" /B ollama serve
    timeout /t 15 /nobreak >nul
) else (
    echo   Ollama already running
)

:start_flask
echo 2. Starting Flask backend (port 5000)...
echo   Server will auto-restart if crashes
echo   Press Ctrl+C to stop
echo.

python app.py

echo.
echo 3. Backend stopped. Restarting in 10 seconds...
timeout /t 10 /nobreak >nul
goto start_flask
