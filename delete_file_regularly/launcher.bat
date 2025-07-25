@echo off
chcp 65001 >nul
title 檔案清理工具選單

:main
cls
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                           📁 檔案清理工具選單 v3.1                          ║
echo ╠══════════════════════════════════════════════════════════════════════════════╣
echo ║                                                                              ║
echo ║  1. 📦 壓縮歸檔模式    - 壓縮存檔，節省空間且可恢復（推薦）                 ║
echo ║  2. ✅ 安全清理模式    - 移動到回收站，可恢復但仍占用空間                   ║
echo ║  3. ⚠️  釋放空間模式   - 永久刪除，立即釋放空間，無法恢復                   ║
echo ║  4. 🧠 智能清理模式    - 先移到回收站，稍後可選擇永久刪除                   ║
echo ║                                                                              ║
echo ║  5. 🔄 檔案恢復工具    - 管理回收站中的檔案                                 ║
echo ║  6. 📤 歸檔管理工具    - 管理壓縮歸檔的檔案                                 ║
echo ║  7. 🖥️  GUI 介面       - 啟動圖形介面版本                                   ║
echo ║  8. 🚀 系統托盤模式    - 常駐托盤，想開就開想關就關（推薦）                 ║
echo ║                                                                              ║
echo ║  0. 🚪 退出程式                                                              ║
echo ║                                                                              ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
set /p choice="請選擇操作 (0-8) [預設: 8]: "

if "%choice%"=="" set choice=8

if "%choice%"=="1" goto archive_mode
if "%choice%"=="2" goto safe_mode
if "%choice%"=="3" goto permanent_mode
if "%choice%"=="4" goto smart_mode
if "%choice%"=="5" goto recovery_tool
if "%choice%"=="6" goto archive_manager
if "%choice%"=="7" goto gui_mode
if "%choice%"=="8" goto tray_mode
if "%choice%"=="0" goto exit

echo 無效選項，請重新選擇
pause
goto main

:tray_mode
cls
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                             🚀 系統托盤模式                                 ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo 🚀 系統托盤模式特點：
echo   • 常駐系統托盤，不佔用桌面空間
echo   • 想開就開，想關就關
echo   • 支援自動定時清理
echo   • 右鍵托盤圖示快速操作
echo   • 一鍵清理、設定、統計
echo   • 完整的圖形化介面
echo.
echo 💡 首次使用提示：
echo   • 程式啟動後會出現在系統托盤
echo   • 雙擊托盤圖示開啟控制面板
echo   • 右鍵托盤圖示查看快速選單
echo   • 請先在設定中添加清理路徑
echo.
echo 正在啟動系統托盤模式...
echo.
python cleanup_tray.py
pause
goto main

:archive_mode
cls
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                              📦 壓縮歸檔模式                                 ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo 📦 壓縮歸檔模式特點：
echo   • 檔案被壓縮存檔，大幅節省磁碟空間
echo   • 可以隨時提取恢復檔案
echo   • 保持原始目錄結構
echo   • 按日期自動分組歸檔
echo   • 提供完整的歸檔管理功能
echo.
echo 正在啟動壓縮歸檔模式...
echo.
python delete_file_regularly.py --archive
pause
goto main

:safe_mode
cls
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                              ✅ 安全清理模式                                 ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo ✅ 安全清理模式特點：
echo   • 檔案移動到回收站，可以恢復
echo   • 仍然占用磁碟空間
echo   • 最安全的清理方式
echo   • 可使用恢復工具管理
echo.
echo 正在啟動安全清理模式...
echo.
python delete_file_regularly.py
pause
goto main

:permanent_mode
cls
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                             ⚠️  釋放空間模式                                 ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo ⚠️  釋放空間模式特點：
echo   • 檔案被永久刪除，無法恢復
echo   • 立即釋放磁碟空間
echo   • 適合確定不需要的檔案
echo   • 操作無法復原
echo.
echo 正在啟動釋放空間模式...
echo.
python delete_file_regularly.py --no-recycle-bin
pause
goto main

:smart_mode
cls
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                              🧠 智能清理模式                                 ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo 🧠 智能清理模式特點：
echo   • 先移動到回收站保證安全
echo   • 清理完成後可選擇永久刪除釋放空間
echo   • 兼顧安全性和空間管理
echo   • 提供多種後續選項
echo.
echo 正在啟動智能清理模式...
echo.
python delete_file_regularly.py
pause
goto main

:recovery_tool
cls
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                              🔄 檔案恢復工具                                 ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo 🔄 檔案恢復工具功能：
echo   • 查看回收站中的檔案
echo   • 恢復指定檔案到原位置
echo   • 批量恢復檔案
echo   • 永久刪除回收站檔案
echo   • 管理回收站空間
echo.
echo 正在啟動檔案恢復工具...
echo.
python file_recovery.py
pause
goto main

:archive_manager
cls
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                              📤 歸檔管理工具                                 ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo 📤 歸檔管理工具功能：
echo   • 瀏覽所有壓縮歸檔
echo   • 查看歸檔內容和統計
echo   • 提取單個檔案或整個歸檔
echo   • 刪除不需要的歸檔
echo   • 清理損壞的歸檔檔案
echo.
echo 正在啟動歸檔管理工具...
echo.
python file_archive_manager.py
pause
goto main

:gui_mode
cls
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                              🖥️  圖形介面模式                                ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo 🖥️  圖形介面模式特點：
echo   • 友善的圖形使用者介面
echo   • 支援系統列常駐
echo   • 排程自動清理
echo   • 視覺化操作
echo.
echo 正在啟動圖形介面...
echo.
python file_cleanup_gui.py
pause
goto main

:exit
echo.
echo 感謝使用檔案清理工具！
echo.
exit /b 0
