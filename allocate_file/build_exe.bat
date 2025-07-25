@echo off
chcp 65001
echo 智能檔案自動分類工具 - 打包成 EXE
echo ==========================================

echo.
echo 正在檢查 Python 環境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 錯誤：未找到 Python
    echo 請確保已安裝 Python 並添加到 PATH
    pause
    exit /b 1
)

echo Python 環境檢查通過 ✓

echo.
echo 正在檢查依賴套件...
python -c "import watchdog, schedule, PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安裝缺少的套件...
    pip install watchdog schedule pyinstaller
)

echo.
echo 開始打包程式...
python build_smart_exe.py

echo.
echo 打包完成！
pause
