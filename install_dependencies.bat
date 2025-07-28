@echo off
chcp 65001 >nul
title 檔案清理大師 - 依賴安裝器

echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                      📦 檔案清理大師 依賴安裝器                            ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

echo 🔍 檢查 Python 環境...

python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤：未找到 Python
    echo.
    echo 請先安裝 Python:
    echo   1. 訪問 https://www.python.org/downloads/
    echo   2. 下載最新版本的 Python
    echo   3. 安裝時記得勾選 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set python_version=%%i
echo ✅ Python %python_version% 已安裝

echo.
echo 📦 安裝必要依賴...

echo.
echo 🔧 安裝系統托盤支援...
pip install pystray
if errorlevel 1 (
    echo ⚠️  pystray 安裝失敗，系統托盤功能可能不可用
) else (
    echo ✅ pystray 安裝成功
)

echo.
echo 🖼️  安裝圖像處理庫...
pip install pillow
if errorlevel 1 (
    echo ⚠️  pillow 安裝失敗，圖標功能可能不可用
) else (
    echo ✅ pillow 安裝成功
)

echo.
echo ⏰ 安裝任務調度庫...
pip install schedule
if errorlevel 1 (
    echo ⚠️  schedule 安裝失敗，自動清理功能可能不可用
) else (
    echo ✅ schedule 安裝成功
)

echo.
echo 🌐 安裝網頁框架（用於網頁版）...
pip install flask werkzeug
if errorlevel 1 (
    echo ⚠️  flask 安裝失敗，網頁版功能不可用
) else (
    echo ✅ flask 安裝成功
)

echo.
echo 🛠️  安裝打包工具（用於製作EXE）...
pip install pyinstaller
if errorlevel 1 (
    echo ⚠️  pyinstaller 安裝失敗，無法打包EXE
) else (
    echo ✅ pyinstaller 安裝成功
)

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                            🎉 安裝完成！                                    ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

echo 🧪 測試安裝結果...
python -c "import pystray, PIL, schedule; print('✅ 系統托盤功能可用')" 2>nul || echo "⚠️  系統托盤功能有問題"
python -c "import tkinter; print('✅ GUI界面可用')" 2>nul || echo "⚠️  GUI界面有問題"
python -c "import flask; print('✅ 網頁版功能可用')" 2>nul || echo "⚠️  網頁版功能有問題"

echo.
echo 🚀 現在可以使用的功能:
echo.
echo   📱 系統托盤版本:
echo      python cleanup_tray.py
echo.
echo   🖥️  GUI界面版本:
echo      python file_cleanup_gui.py
echo.
echo   🌐 網頁版本:
echo      python web_app.py
echo.
echo   📦 打包EXE版本:
echo      quick_build.bat
echo.
echo   🎛️  命令行版本:
echo      python delete_file_regularly.py
echo.

echo 💡 推薦使用流程:
echo   1. 新手: 雙擊 launcher.bat 選擇模式
echo   2. 日常: python cleanup_tray.py (系統托盤)
echo   3. 分享: quick_build.bat (製作EXE)
echo.

pause
