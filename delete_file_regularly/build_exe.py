#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檔案清理工具 - PyInstaller 打包腳本
將工具打包成獨立的 exe 可執行檔
"""

import os
import sys
import subprocess
from pathlib import Path

def install_pyinstaller():
    """安裝 PyInstaller"""
    print("📦 安裝 PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller 安裝成功")
        return True
    except Exception as e:
        print(f"❌ PyInstaller 安裝失敗: {e}")
        return False

def create_spec_file():
    """創建 .spec 檔案"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

# 獲取專案路徑
project_path = Path.cwd()

a = Analysis(
    ['delete_file_regularly.py'],
    pathex=[str(project_path)],
    binaries=[],
    datas=[
        ('file_cleanup_gui.py', '.'),
        ('cleanup_tray.py', '.'),
        ('file_archive_manager.py', '.'),
        ('file_recovery.py', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'pystray',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'schedule',
        'zipfile',
        'json',
        'pathlib',
        'datetime',
        'logging',
        'argparse',
        'shutil',
        'stat',
        'threading',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# 添加托盤圖標
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FileCleanupTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    version='version_info.txt'
)

# 創建GUI版本（無控制台）
exe_gui = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FileCleanupTool_GUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 無控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    with open('FileCleanupTool.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ .spec 檔案創建成功")

def create_version_info():
    """創建版本資訊檔案"""
    version_content = '''# UTF-8
#
# 檔案清理工具版本資訊
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(3,1,0,0),
    prodvers=(3,1,0,0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'File Cleanup Tool'),
        StringStruct(u'FileDescription', u'檔案自動清理工具'),
        StringStruct(u'FileVersion', u'3.1.0.0'),
        StringStruct(u'InternalName', u'FileCleanupTool'),
        StringStruct(u'LegalCopyright', u'Copyright 2025'),
        StringStruct(u'OriginalFilename', u'FileCleanupTool.exe'),
        StringStruct(u'ProductName', u'檔案清理工具'),
        StringStruct(u'ProductVersion', u'3.1.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
    
    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_content)
    
    print("✅ 版本資訊檔案創建成功")

def build_exe():
    """編譯 EXE"""
    print("🔨 開始編譯 EXE...")
    try:
        # 清理舊的構建
        if Path('build').exists():
            import shutil
            shutil.rmtree('build')
        if Path('dist').exists():
            import shutil
            shutil.rmtree('dist')
        
        # 使用 spec 檔案編譯
        subprocess.check_call(['pyinstaller', '--clean', 'FileCleanupTool.spec'])
        
        print("✅ EXE 編譯成功！")
        print(f"📁 檔案位置: {Path('dist').absolute()}")
        
        # 列出生成的檔案
        dist_path = Path('dist')
        if dist_path.exists():
            exe_files = list(dist_path.glob('*.exe'))
            for exe_file in exe_files:
                size_mb = exe_file.stat().st_size / (1024 * 1024)
                print(f"   📄 {exe_file.name} ({size_mb:.1f} MB)")
        
        return True
        
    except Exception as e:
        print(f"❌ EXE 編譯失敗: {e}")
        return False

def create_launcher_script():
    """創建啟動器腳本"""
    launcher_content = '''@echo off
chcp 65001 >nul
title 檔案清理工具 - 可執行版本

echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                        🚀 檔案清理工具 v3.1                                 ║
echo ║                           可執行版本啟動器                                  ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

echo 請選擇啟動方式：
echo.
echo 1. 命令行版本（推薦新手）
echo 2. GUI圖形界面版本
echo 3. 系統托盤版本（常駐後台）
echo 4. 檔案歸檔管理器
echo 5. 檔案恢復工具
echo 0. 退出
echo.

set /p choice="請輸入選項 (0-5): "

if "%choice%"=="1" (
    echo 啟動命令行版本...
    FileCleanupTool.exe
) else if "%choice%"=="2" (
    echo 啟動GUI版本...
    FileCleanupTool_GUI.exe
) else if "%choice%"=="3" (
    echo 啟動系統托盤版本...
    FileCleanupTool_GUI.exe --tray
) else if "%choice%"=="4" (
    echo 啟動歸檔管理器...
    FileCleanupTool_GUI.exe --archive-manager
) else if "%choice%"=="5" (
    echo 啟動恢復工具...
    FileCleanupTool_GUI.exe --recovery
) else if "%choice%"=="0" (
    exit
) else (
    echo 無效選項，請重新選擇
    pause
    goto :eof
)

pause
'''
    
    with open('dist/啟動器.bat', 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    print("✅ 啟動器腳本創建成功")

def main():
    """主函數"""
    print("🚀 檔案清理工具 - EXE 打包工具")
    print("="*60)
    
    # 檢查並安裝 PyInstaller
    try:
        import PyInstaller
        print("✅ PyInstaller 已安裝")
    except ImportError:
        if not install_pyinstaller():
            return
    
    # 創建必要檔案
    create_version_info()
    create_spec_file()
    
    # 編譯 EXE
    if build_exe():
        create_launcher_script()
        
        print("\n🎉 EXE 打包完成！")
        print("="*60)
        print("📁 生成的檔案:")
        print("   • FileCleanupTool.exe - 命令行版本")
        print("   • FileCleanupTool_GUI.exe - GUI版本")
        print("   • 啟動器.bat - 統一啟動器")
        print()
        print("💡 使用說明:")
        print("   1. 將 dist 資料夾複製到任何電腦")
        print("   2. 雙擊 啟動器.bat 選擇版本")
        print("   3. 或直接執行對應的 .exe 檔案")
        print()
        print("🎯 特色:")
        print("   • 無需安裝 Python")
        print("   • 無需額外依賴")
        print("   • 一鍵執行，即開即用")
        print("   • 支援所有原有功能")
    else:
        print("\n❌ EXE 打包失敗，請檢查錯誤訊息")

if __name__ == "__main__":
    main()
