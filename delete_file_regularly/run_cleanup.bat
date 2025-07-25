@echo off
chcp 65001 >nul
echo 檔案自動清理工具
echo ==================

echo.
echo 選擇執行模式：
echo 1. 互動式清理（推薦）
echo 2. 執行測試和示範
echo 3. 快速清理下載資料夾（保留30天）
echo 4. 快速清理暫存檔案（保留7天）
echo.

set /p choice="請輸入選項 (1-4): "

if "%choice%"=="1" (
    echo.
    echo 啟動互動式清理模式...
    python delete_file_regularly.py
    pause
) else if "%choice%"=="2" (
    echo.
    echo 啟動測試和示範...
    python test_cleanup.py
    pause
) else if "%choice%"=="3" (
    echo.
    echo 快速清理下載資料夾（保留30天）...
    python delete_file_regularly.py --path "%USERPROFILE%\Downloads" --days 30
    pause
) else if "%choice%"=="4" (
    echo.
    echo 快速清理暫存檔案（保留7天）...
    echo 注意：需要管理員權限
    python delete_file_regularly.py --path "C:\Windows\Temp" --days 7
    pause
) else (
    echo 無效選項
    pause
)
