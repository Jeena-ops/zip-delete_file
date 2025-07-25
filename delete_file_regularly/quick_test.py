#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單測試腳本
"""

print("🧪 開始測試...")

# 測試基本導入
try:
    print("1. 測試基本模塊...")
    import os, sys, json
    print("  ✅ 標準庫 OK")
    
    from pathlib import Path
    from datetime import datetime
    print("  ✅ Path 和 datetime OK")
    
    import zipfile
    print("  ✅ zipfile OK")
    
except Exception as e:
    print(f"  ❌ 基本模塊錯誤: {e}")

# 測試GUI
try:
    print("2. 測試GUI...")
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    root.destroy()
    print("  ✅ tkinter OK")
except Exception as e:
    print(f"  ❌ GUI錯誤: {e}")

# 測試托盤依賴
try:
    print("3. 測試托盤依賴...")
    import pystray
    print("  ✅ pystray OK")
    
    from PIL import Image, ImageDraw
    print("  ✅ PIL OK")
    
    import schedule
    print("  ✅ schedule OK")
    
except Exception as e:
    print(f"  ❌ 托盤依賴錯誤: {e}")

# 測試主模塊
try:
    print("4. 測試主模塊...")
    from delete_file_regularly import FileCleanupTool
    
    # 創建實例
    cleaner = FileCleanupTool("INFO", use_recycle_bin=True, use_archive=False)
    print("  ✅ FileCleanupTool 創建成功")
    
    # 測試歸檔模式
    archive_cleaner = FileCleanupTool("INFO", use_recycle_bin=False, use_archive=True)
    print("  ✅ 歸檔模式創建成功")
    
except Exception as e:
    print(f"  ❌ 主模塊錯誤: {e}")

# 測試托盤應用
try:
    print("5. 測試托盤應用...")
    
    # 檢查文件是否存在
    if Path("cleanup_tray.py").exists():
        print("  ✅ cleanup_tray.py 存在")
        
        # 嘗試導入
        import cleanup_tray
        print("  ✅ cleanup_tray 模塊可導入")
        
    else:
        print("  ❌ cleanup_tray.py 不存在")
        
except Exception as e:
    print(f"  ❌ 托盤應用錯誤: {e}")

print("\n🎉 測試完成！")
print("\n可用的啟動方式:")
print("1. 命令行模式: python delete_file_regularly.py")
print("2. 啟動器: launcher.bat")
print("3. 系統托盤: python cleanup_tray.py") 
print("4. GUI模式: python file_cleanup_gui.py")

input("\n按 Enter 鍵退出...")
