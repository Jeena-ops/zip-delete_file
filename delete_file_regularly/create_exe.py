#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檔案清理工具 - EXE打包配置
使用 PyInstaller 將應用打包成獨立可執行檔案
"""

import os
import sys
from pathlib import Path

# 打包配置
BUILD_CONFIG = {
    "app_name": "檔案清理大師",
    "version": "3.1.0",
    "description": "智能檔案清理工具 - 支援壓縮歸檔、系統托盤、GUI界面",
    "author": "文件管理專家",
    "icon": "app_icon.ico"
}

def create_build_script():
    """創建PyInstaller打包腳本"""
    
    # 創建打包腳本
    build_script = f"""
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 主應用程序分析
a = Analysis(
    ['cleanup_tray.py'],  # 主程序（系統托盤版本）
    pathex=[],
    binaries=[],
    datas=[
        ('file_cleanup_gui.py', '.'),
        ('file_archive_manager.py', '.'),
        ('file_recovery.py', '.'),
        ('delete_file_regularly.py', '.'),
        ('requirements.txt', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'pystray',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'schedule',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'zipfile',
        'json',
        'logging',
        'pathlib',
        'datetime',
        'threading'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 收集所有文件
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 創建可執行檔案
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{BUILD_CONFIG["app_name"]}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不顯示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico'  # 應用程序圖標
)
"""
    
    with open("build_app.spec", "w", encoding="utf-8") as f:
        f.write(build_script)
    
    print("✅ PyInstaller 配置文件已創建: build_app.spec")

def create_icon():
    """創建應用程序圖標"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # 創建圖標
        size = 256
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # 繪製背景圓形
        margin = 20
        draw.ellipse([margin, margin, size-margin, size-margin], 
                    fill=(52, 152, 219, 255), outline=(41, 128, 185, 255), width=4)
        
        # 繪製清理圖標（垃圾桶）
        bin_left = size // 3
        bin_right = size * 2 // 3
        bin_top = size // 3
        bin_bottom = size * 2 // 3
        
        # 垃圾桶主體
        draw.rectangle([bin_left, bin_top + 10, bin_right, bin_bottom], 
                      fill=(255, 255, 255, 255), outline=(0, 0, 0, 0))
        
        # 垃圾桶蓋子
        draw.rectangle([bin_left - 5, bin_top, bin_right + 5, bin_top + 10], 
                      fill=(255, 255, 255, 255), outline=(0, 0, 0, 0))
        
        # 保存為ICO格式
        ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        icon_images = []
        for ico_size in ico_sizes:
            icon_img = image.resize(ico_size, Image.Resampling.LANCZOS)
            icon_images.append(icon_img)
        
        icon_images[0].save("app_icon.ico", format="ICO", sizes=ico_sizes)
        print("✅ 應用程序圖標已創建: app_icon.ico")
        
    except ImportError:
        print("⚠️  無法創建圖標，PIL未安裝")
    except Exception as e:
        print(f"⚠️  圖標創建失敗: {{e}}")

def create_build_batch():
    """創建一鍵打包批處理文件"""
    
    batch_content = f'''@echo off
chcp 65001 >nul
title {BUILD_CONFIG["app_name"]} - 一鍵打包

echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                      🚀 {BUILD_CONFIG["app_name"]} 打包工具                     ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo 版本: {BUILD_CONFIG["version"]}
echo 描述: {BUILD_CONFIG["description"]}
echo.

echo 📋 檢查環境...

REM 檢查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤：未找到 Python
    pause
    exit /b 1
)
echo ✅ Python 可用

REM 檢查PyInstaller
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo ⚠️  正在安裝 PyInstaller...
    pip install pyinstaller
)
echo ✅ PyInstaller 可用

echo.
echo 📦 開始打包...
echo.

REM 清理舊的構建文件
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"

REM 執行打包
pyinstaller build_app.spec

if errorlevel 1 (
    echo ❌ 打包失敗！
    pause
    exit /b 1
)

echo.
echo ✅ 打包完成！
echo.
echo 📂 可執行檔案位置: dist\\{BUILD_CONFIG["app_name"]}.exe
echo 💡 您可以將此exe檔案分享給任何人使用
echo.

REM 檢查文件是否存在
if exist "dist\\{BUILD_CONFIG["app_name"]}.exe" (
    echo 🎉 成功！檔案大小:
    dir "dist\\{BUILD_CONFIG["app_name"]}.exe" | find ".exe"
    echo.
    echo 是否要啟動應用程序測試？ (y/n)
    set /p test_choice=
    if /i "%test_choice%"=="y" (
        start "" "dist\\{BUILD_CONFIG["app_name"]}.exe"
    )
) else (
    echo ❌ 打包檔案未找到
)

pause
'''
    
    with open("build_exe.bat", "w", encoding="utf-8") as f:
        f.write(batch_content)
    
    print("✅ 一鍵打包腳本已創建: build_exe.bat")

def create_installer_script():
    """創建安裝程序配置"""
    
    nsis_content = f'''
; {BUILD_CONFIG["app_name"]} 安裝程序配置
; 使用 NSIS 創建專業安裝程序

!define APP_NAME "{BUILD_CONFIG["app_name"]}"
!define APP_VERSION "{BUILD_CONFIG["version"]}"
!define APP_PUBLISHER "{BUILD_CONFIG["author"]}"
!define APP_DESCRIPTION "{BUILD_CONFIG["description"]}"

; 安裝程序設置
Name "${{APP_NAME}}"
OutFile "{BUILD_CONFIG["app_name"]}_v{BUILD_CONFIG["version"]}_安裝程序.exe"
InstallDir "$PROGRAMFILES\\${{APP_NAME}}"
RequestExecutionLevel admin

; 安裝程序頁面
Page directory
Page instfiles
UninstPage uninstConfirm
UninstPage instfiles

; 安裝文件
Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    File "dist\\{BUILD_CONFIG["app_name"]}.exe"
    File "README.md"
    
    ; 創建開始菜單快捷方式
    CreateDirectory "$SMPROGRAMS\\${{APP_NAME}}"
    CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk" "$INSTDIR\\{BUILD_CONFIG["app_name"]}.exe"
    CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\解除安裝.lnk" "$INSTDIR\\uninstall.exe"
    
    ; 創建桌面快捷方式
    CreateShortCut "$DESKTOP\\${{APP_NAME}}.lnk" "$INSTDIR\\{BUILD_CONFIG["app_name"]}.exe"
    
    ; 創建解除安裝程序
    WriteUninstaller "$INSTDIR\\uninstall.exe"
    
    ; 註冊表項目
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayName" "${{APP_NAME}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "UninstallString" "$INSTDIR\\uninstall.exe"
SectionEnd

; 解除安裝
Section "Uninstall"
    Delete "$INSTDIR\\{BUILD_CONFIG["app_name"]}.exe"
    Delete "$INSTDIR\\README.md"
    Delete "$INSTDIR\\uninstall.exe"
    RMDir "$INSTDIR"
    
    Delete "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk"
    Delete "$SMPROGRAMS\\${{APP_NAME}}\\解除安裝.lnk"
    RMDir "$SMPROGRAMS\\${{APP_NAME}}"
    Delete "$DESKTOP\\${{APP_NAME}}.lnk"
    
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}"
SectionEnd
'''
    
    with open("installer.nsi", "w", encoding="utf-8") as f:
        f.write(nsis_content)
    
    print("✅ 安裝程序配置已創建: installer.nsi")

def main():
    """主函數"""
    print("🚀 EXE打包工具配置器")
    print("="*60)
    
    # 創建所有必要文件
    create_icon()
    create_build_script()
    create_build_batch()
    create_installer_script()
    
    print("\n" + "="*60)
    print("📋 EXE打包準備完成！")
    print("="*60)
    
    print(f"\n✅ 已創建文件:")
    print(f"  • build_app.spec     - PyInstaller配置")
    print(f"  • build_exe.bat      - 一鍵打包腳本")
    print(f"  • app_icon.ico       - 應用程序圖標")
    print(f"  • installer.nsi      - 安裝程序配置")
    
    print(f"\n🎯 使用方法:")
    print(f"  1. 雙擊 build_exe.bat 開始打包")
    print(f"  2. 打包完成後會生成 dist\\{BUILD_CONFIG['app_name']}.exe")
    print(f"  3. 將exe檔案分享給任何人都可以直接使用")
    
    print(f"\n💡 特色功能:")
    print(f"  • 無需安裝Python環境")
    print(f"  • 獨立可執行檔案")
    print(f"  • 包含所有依賴庫")
    print(f"  • 專業的圖標和界面")
    print(f"  • 支援系統托盤常駐")

if __name__ == "__main__":
    main()
