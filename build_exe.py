#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包腳本：將 rename_files.py 打包成可執行檔
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def check_pyinstaller():
    """檢查 PyInstaller 是否已安裝"""
    try:
        import PyInstaller
        print("✓ PyInstaller 已安裝")
        return True
    except ImportError:
        print("✗ PyInstaller 未安裝")
        print("請執行：pip install pyinstaller")
        return False


def clean_build_files():
    """清理之前的建置檔案"""
    print("\n正在清理之前的建置檔案...")
    
    dirs_to_clean = ['dist', 'build', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  - 已刪除 {dir_name}/")


def build_exe():
    """使用 PyInstaller 建置可執行檔"""
    print("\n正在打包程式...")
    
    # 使用 spec 檔案進行打包
    cmd = ['pyinstaller', '--clean', 'FileRenamer.spec']
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"打包失敗：{e}")
        print(f"錯誤輸出：{e.stderr}")
        return False


def get_file_size(file_path):
    """獲取檔案大小（格式化）"""
    size_bytes = os.path.getsize(file_path)
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def main():
    """主函數"""
    print("檔案批次重新命名工具 - 打包成 EXE")
    print("=" * 50)
    
    # 檢查 PyInstaller
    if not check_pyinstaller():
        return False
    
    # 檢查必要檔案
    required_files = ['rename_files.py', 'FileRenamer.spec', 'version_info.txt']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"\n錯誤：缺少必要檔案：{missing_files}")
        return False
    
    # 清理建置檔案
    clean_build_files()
    
    # 建置可執行檔
    if build_exe():
        exe_path = Path('dist/FileRenamer.exe')
        
        if exe_path.exists():
            print("\n" + "=" * 50)
            print("打包完成！")
            print("=" * 50)
            print(f"可執行檔位置：{exe_path}")
            print(f"檔案大小：{get_file_size(exe_path)}")
            print("\n您可以將 FileRenamer.exe 複製到任何地方使用")
            print("程式不需要安裝 Python 環境即可運行")
            return True
        else:
            print("\n錯誤：找不到建置的可執行檔")
            return False
    else:
        print("\n打包失敗！")
        return False


if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n按 Enter 鍵退出...")
        input()
        sys.exit(1)
    
    print("\n按 Enter 鍵退出...")
    input()
