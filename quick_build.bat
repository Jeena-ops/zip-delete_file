@echo off
chcp 65001 >nul
title 檔案清理大師 - 快速打包工具

echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                      🚀 檔案清理大師 快速打包                              ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

echo 📋 檢查環境...

REM 檢查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤：未找到 Python
    echo 請先安裝 Python: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python 可用

REM 檢查PyInstaller
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo ⚠️  正在安裝 PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo ❌ PyInstaller 安裝失敗
        pause
        exit /b 1
    )
)
echo ✅ PyInstaller 可用

echo.
echo 📦 開始打包...
echo.

REM 清理舊的構建文件
if exist "build" rmdir /s /q "build" 2>nul
if exist "dist" rmdir /s /q "dist" 2>nul

REM 基本打包命令
echo 正在打包系統托盤版本...
pyinstaller --onefile --windowed --name "檔案清理大師" ^
    --add-data "file_cleanup_gui.py;." ^
    --add-data "file_archive_manager.py;." ^
    --add-data "file_recovery.py;." ^
    --hidden-import "pystray" ^
    --hidden-import "PIL.Image" ^
    --hidden-import "PIL.ImageDraw" ^
    --hidden-import "schedule" ^
    --hidden-import "tkinter" ^
    --hidden-import "tkinter.ttk" ^
    cleanup_tray.py

if errorlevel 1 (
    echo ❌ 打包失敗！
    echo.
    echo 嘗試簡化版本打包...
    echo.
    
    REM 簡化版本（如果完整版失敗）
    pyinstaller --onefile --name "檔案清理工具_簡化版" delete_file_regularly.py
    
    if errorlevel 1 (
        echo ❌ 簡化版本也失敗！
        pause
        exit /b 1
    ) else (
        echo ✅ 簡化版本打包成功！
        set "exe_name=檔案清理工具_簡化版.exe"
    )
) else (
    echo ✅ 完整版本打包成功！
    set "exe_name=檔案清理大師.exe"
)

echo.
echo 🎉 打包完成！
echo.

REM 檢查文件
if exist "dist\%exe_name%" (
    echo 📂 輸出檔案: dist\%exe_name%
    echo 📊 檔案大小:
    dir "dist\%exe_name%" | find ".exe"
    echo.
    
    echo 🧪 測試選項:
    echo   1. 測試運行程序
    echo   2. 開啟輸出資料夾
    echo   3. 退出
    echo.
    set /p choice=請選擇 (1-3): 
    
    if "%choice%"=="1" (
        echo 正在啟動程序測試...
        start "" "dist\%exe_name%"
    )
    if "%choice%"=="2" (
        start "" "dist"
    )
    
    echo.
    echo 💡 使用說明:
    echo   • 將 dist\%exe_name% 複製給任何人都可以使用
    echo   • 無需安裝 Python 或其他依賴
    echo   • 支援 Windows 7/8/10/11
    echo   • 程序啟動後會出現在系統托盤
    
) else (
    echo ❌ 找不到輸出檔案
)

echo.
pause
