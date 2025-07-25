@echo off
chcp 65001 >nul
title 檔案清理工具測試

echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                            🧪 功能測試報告                                  ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

echo 🔍 檢查檔案是否存在...
if exist "delete_file_regularly.py" (
    echo   ✅ 主程式: delete_file_regularly.py
) else (
    echo   ❌ 主程式檔案缺失
)

if exist "cleanup_tray.py" (
    echo   ✅ 托盤程式: cleanup_tray.py
) else (
    echo   ❌ 托盤程式檔案缺失
)

if exist "file_cleanup_gui.py" (
    echo   ✅ GUI程式: file_cleanup_gui.py
) else (
    echo   ❌ GUI程式檔案缺失
)

if exist "launcher.bat" (
    echo   ✅ 啟動器: launcher.bat
) else (
    echo   ❌ 啟動器檔案缺失
)

echo.
echo 🧪 測試Python依賴...
python -c "import sys; print('  ✅ Python 版本:', sys.version.split()[0])"

echo   測試標準庫...
python -c "import os, sys, json, zipfile; print('  ✅ 標準庫可用')"

echo   測試GUI庫...
python -c "import tkinter; print('  ✅ tkinter 可用')" 2>nul || echo   ❌ tkinter 不可用

echo   測試托盤依賴...
python -c "import pystray, PIL, schedule; print('  ✅ 托盤依賴可用')" 2>nul || echo   ❌ 托盤依賴不完整

echo.
echo 🚀 測試核心功能...
python -c "from delete_file_regularly import FileCleanupTool; c=FileCleanupTool('INFO'); print('  ✅ 核心模塊正常')" 2>nul || echo   ❌ 核心模塊錯誤

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                            📋 使用指南                                      ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo 🎯 推薦使用方式:
echo   1. 新手入門: 雙擊 launcher.bat
echo   2. 系統托盤: python cleanup_tray.py
echo   3. GUI界面:  python file_cleanup_gui.py
echo   4. 命令行:   python delete_file_regularly.py
echo.
echo 💡 功能特色:
echo   • 壓縮歸檔模式 - 節省空間且可恢復
echo   • 系統托盤常駐 - 想開就開想關就關
echo   • 完整預覽功能 - 安全可靠不誤刪
echo   • 多種清理模式 - 適合不同需求
echo.

pause
