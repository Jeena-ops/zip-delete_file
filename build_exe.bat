@echo off
echo 檔案批次重新命名工具 - 打包成 EXE
echo ==========================================

echo.
echo 正在檢查 PyInstaller...
python -c "import PyInstaller" 2>nul
if %errorlevel% neq 0 (
    echo 錯誤：PyInstaller 未安裝
    echo 請執行：pip install pyinstaller
    pause
    exit /b 1
)

echo PyInstaller 已安裝 ✓

echo.
echo 正在清理之前的建置檔案...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "__pycache__" rmdir /s /q "__pycache__"

echo.
echo 正在打包程式...
pyinstaller --clean FileRenamer.spec

if %errorlevel% equ 0 (
    echo.
    echo ==========================================
    echo 打包完成！
    echo ==========================================
    echo 可執行檔位置：dist\FileRenamer.exe
    echo.
    echo 檔案大小：
    for %%A in ("dist\FileRenamer.exe") do echo   %%~zA bytes
    echo.
    echo 您可以將 dist\FileRenamer.exe 複製到任何地方使用
    echo.
) else (
    echo.
    echo 打包失敗！請檢查錯誤訊息
)

pause
