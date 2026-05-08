@echo off
chcp 65001 >nul
echo 正在启动单词学习服务器...
echo.

:: 用 PowerShell 获取局域网 IP
for /f "usebackq delims=" %%i in (`powershell -Command "Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254.*'} | Select-Object -First 1 -ExpandProperty IPAddress"`) do (
    set "ip=%%i"
)

if "%ip%"=="" (
    echo 未能自动获取 IP 地址，请手动查看网络设置
    set "ip=UNKNOWN"
)

cd /d "%~dp0"

echo ========================================
echo   服务器已启动！
echo ========================================
echo.
echo 请用手机浏览器访问：
echo   http://%ip%:8080/
echo.
echo 电脑也可以访问：
echo   http://localhost:8080/
echo.
echo 按 Ctrl+C 停止服务器
echo.
echo ========================================

python -m http.server 8080
