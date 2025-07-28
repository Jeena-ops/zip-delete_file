@echo off
chcp 65001 >nul
echo 🌐 檔案清理大師 - 網絡版啟動器
echo ================================================
echo.

echo 📡 獲取網絡信息...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    set "ip=%%a"
    goto :found
)
:found
set ip=%ip: =%

echo 本機IP地址: %ip%
echo.

echo 📦 檢查Python和依賴...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤: 未找到Python
    echo 請先安裝Python 3.7或更新版本
    pause
    exit /b 1
)

python -c "import flask, werkzeug" >nul 2>&1
if errorlevel 1 (
    echo 🔧 正在安裝必要的依賴包...
    pip install flask werkzeug pillow schedule
)

echo ✅ 準備就緒

echo.
echo 🚀 啟動網頁伺服器...
echo ================================================
echo.
echo 📌 訪問地址:
echo    本機訪問: http://localhost:5000
echo    網絡訪問: http://%ip%:5000
echo.
echo 💡 讓其他人訪問的方法:
echo    1. 同一WiFi的設備直接訪問: http://%ip%:5000
echo    2. 如果無法訪問，可能需要關閉防火牆或添加例外
echo    3. 手機、平板、其他電腦都可以使用
echo.
echo 🛑 按 Ctrl+C 停止伺服器
echo ================================================
echo.

rem 等待3秒後自動打開瀏覽器
timeout /t 3 /nobreak >nul
start http://localhost:5000

rem 啟動Flask應用（允許外部訪問）
python web_app.py

pause
