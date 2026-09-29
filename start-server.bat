@echo off
echo Starting vocab server...
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python first.
    echo Download: https://www.python.org/downloads/
    echo.
    pause
    exit /b
)

:: Get LAN IP
for /f "delims=" %%i in ('powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0get-ip.ps1"') do set "ip=%%i"
if "%ip%"=="" set "ip=127.0.0.1"

cd /d "%~dp0"

echo ========================================
echo   Server is running!
echo ========================================
echo.
echo On this computer (opens automatically):
echo   http://localhost:8080/
echo.
echo Open on your phone (same WiFi):
echo   http://%ip%:8080/
echo.
echo Press Ctrl+C to stop.
echo ========================================
echo.

:: Open the browser automatically after 2 seconds (give the server time to start)
start "" /min cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:8080/"

python -m http.server 8080
if errorlevel 1 (
    echo.
    echo [ERROR] Server failed to start.
    pause
)
