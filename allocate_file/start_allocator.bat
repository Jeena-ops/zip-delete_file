@echo off
title 檔案自動分類整理工具
echo 正在啟動檔案自動分類整理工具...

REM 切換到腳本所在目錄
cd /d "%~dp0"

REM 檢查 Python 是否可用
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 錯誤：找不到 Python，請確認 Python 已正確安裝
    pause
    exit /b 1
)

REM 檢查是否安裝了必要的套件
echo 檢查必要套件...
python -c "import schedule, watchdog" >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安裝必要套件...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo 套件安裝失敗，請手動執行：pip install -r requirements.txt
        pause
        exit /b 1
    )
)

echo 套件檢查完成 ✓

REM 啟動主程式
echo.
echo 啟動檔案自動分類整理工具...
echo 注意：關閉此視窗將停止檔案監控功能
echo.

python allocate_file.py

REM 如果程式異常退出，顯示錯誤訊息
if %errorlevel% neq 0 (
    echo.
    echo 程式異常退出，錯誤代碼：%errorlevel%
    echo 請檢查日誌檔案或聯繫技術支援
    pause
)
