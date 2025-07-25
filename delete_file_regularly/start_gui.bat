@echo off
chcp 65001 >nul
title 檔案自動清理工具 - 圖形化版本

echo 檔案自動清理工具 v2.0 - GUI 版本
echo =====================================
echo.

REM 檢查 Python 是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo 錯誤：找不到 Python！
    echo 請確認已安裝 Python 3.7 或更高版本
    echo.
    pause
    exit /b 1
)

echo 正在檢查依賴套件...

REM 檢查是否已安裝依賴套件
python -c "import pystray, PIL, schedule" >nul 2>&1
if errorlevel 1 (
    echo 偵測到缺少依賴套件，正在安裝...
    echo.
    
    REM 安裝依賴套件
    echo 安裝 pystray（系統托盤功能）...
    pip install pystray
    
    echo 安裝 Pillow（圖像處理）...
    pip install Pillow
    
    echo 安裝 schedule（任務排程）...
    pip install schedule
    
    echo.
    echo 依賴套件安裝完成！
    echo.
)

echo 啟動檔案清理工具...
echo.

REM 啟動 GUI 程式
python file_cleanup_gui.py

if errorlevel 1 (
    echo.
    echo 程式執行時發生錯誤！
    echo 請檢查錯誤訊息並確認所有依賴套件已正確安裝。
    echo.
    pause
)
