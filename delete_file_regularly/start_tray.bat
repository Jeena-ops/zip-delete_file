@echo off
chcp 65001 >nul
title 檔案清理工具 - 系統托盤啟動器

echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                          🚀 檔案清理工具啟動器                              ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo 正在檢查依賴套件...

REM 檢查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤：未找到 Python，請先安裝 Python
    pause
    exit /b 1
)

echo ✅ Python 已安裝

REM 檢查必要套件
echo 正在檢查必要套件...
python -c "import pystray, PIL" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  缺少必要套件，正在安裝...
    echo.
    echo 安裝 pystray (系統托盤支援)...
    pip install pystray
    echo.
    echo 安裝 Pillow (圖像處理支援)...
    pip install Pillow
    echo.
    echo 安裝 schedule (定時任務支援)...
    pip install schedule
    echo.
    
    REM 再次檢查
    python -c "import pystray, PIL, schedule" >nul 2>&1
    if errorlevel 1 (
        echo ❌ 套件安裝失敗，請手動執行：
        echo    pip install pystray Pillow schedule
        pause
        exit /b 1
    )
)

echo ✅ 所有依賴套件已就緒
echo.
echo 🚀 正在啟動檔案清理工具...
echo.
echo 💡 提示：
echo    • 程式將在系統托盤中運行
echo    • 右鍵點擊托盤圖示可以開啟選單
echo    • 雙擊托盤圖示可以開啟控制面板
echo    • 首次使用請先設定清理路徑
echo.

REM 啟動托盤程序
python cleanup_tray.py

echo.
echo 程式已結束
pause
