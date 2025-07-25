@echo off
chcp 65001 >nul
title 檔案清理大師 - 網頁版啟動器

echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                          🌐 檔案清理大師 網頁版                            ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

echo 🔍 檢查環境...

REM 檢查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤：未找到 Python
    echo 請先安裝 Python: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python 可用

REM 檢查Flask
pip show flask >nul 2>&1
if errorlevel 1 (
    echo ⚠️  正在安裝 Flask...
    pip install flask
)
echo ✅ Flask 可用

echo.
echo 🚀 啟動網頁伺服器...
echo.
echo 📱 使用方法:
echo   • 伺服器啟動後會自動開啟瀏覽器
echo   • 如果沒有自動開啟，請手動訪問: http://localhost:5000
echo   • 按 Ctrl+C 可停止伺服器
echo.

REM 啟動Flask應用
start "" http://localhost:5000
python web_app.py

pause
