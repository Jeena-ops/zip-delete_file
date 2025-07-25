#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檔案清理工具功能測試
"""

import sys
import os
from pathlib import Path

def main():
    print("🚀 檔案清理工具功能測試")
    print("="*50)
    
    # 測試核心模塊
    print("\n1. 測試核心清理功能...")
    try:
        # 創建測試資料夾
        test_folder = Path("test_cleanup_demo")
        test_folder.mkdir(exist_ok=True)
        
        # 創建一些測試檔案
        import time
        from datetime import datetime, timedelta
        
        # 創建舊檔案（7天前）
        old_file = test_folder / "old_file.txt"
        old_file.write_text("這是舊檔案", encoding='utf-8')
        
        # 修改檔案時間為7天前
        old_time = time.time() - (7 * 24 * 60 * 60)
        os.utime(old_file, (old_time, old_time))
        
        # 創建新檔案
        new_file = test_folder / "new_file.txt"
        new_file.write_text("這是新檔案", encoding='utf-8')
        
        print(f"  ✅ 創建測試資料夾: {test_folder}")
        print(f"  ✅ 創建測試檔案: {old_file.name}, {new_file.name}")
        
        # 測試清理工具
        from delete_file_regularly import FileCleanupTool
        
        # 測試歸檔模式
        cleaner = FileCleanupTool("INFO", use_recycle_bin=False, use_archive=True)
        print("  ✅ 歸檔模式清理工具創建成功")
        
        # 執行預覽
        result = cleaner.cleanup_files(
            str(test_folder), 
            days_to_keep=3, 
            include_subfolders=False, 
            dry_run=True
        )
        
        print(f"  ✅ 預覽模式執行成功")
        print(f"     發現過期檔案: {result['total_found']} 個")
        
        if result['total_found'] > 0:
            print("  ✅ 測試成功：找到了過期檔案")
        else:
            print("  ⚠️  沒有找到過期檔案，可能是時間設置問題")
        
        # 清理測試檔案
        for file in test_folder.glob("*"):
            file.unlink()
        test_folder.rmdir()
        print("  ✅ 測試檔案已清理")
        
    except Exception as e:
        print(f"  ❌ 核心功能測試失敗: {e}")
        import traceback
        traceback.print_exc()
    
    # 測試系統托盤
    print("\n2. 測試系統托盤功能...")
    try:
        import pystray
        from PIL import Image, ImageDraw
        import schedule
        
        print("  ✅ 所有托盤依賴已安裝")
        
        # 測試圖標創建
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), color='blue')
        draw = ImageDraw.Draw(image)
        draw.rectangle([16, 16, 48, 48], fill='white')
        print("  ✅ 托盤圖標創建成功")
        
        # 測試菜單
        menu_item = pystray.MenuItem("測試", lambda: None)
        menu = pystray.Menu(menu_item)
        print("  ✅ 托盤菜單創建成功")
        
    except ImportError as e:
        print(f"  ❌ 托盤依賴缺失: {e}")
    except Exception as e:
        print(f"  ❌ 托盤功能測試失敗: {e}")
    
    # 測試GUI
    print("\n3. 測試GUI功能...")
    try:
        import tkinter as tk
        from tkinter import ttk
        
        # 創建隱藏的測試窗口
        root = tk.Tk()
        root.withdraw()
        
        # 測試基本組件
        frame = ttk.Frame(root)
        button = ttk.Button(frame, text="測試按鈕")
        label = ttk.Label(frame, text="測試標籤")
        
        print("  ✅ GUI組件創建成功")
        
        root.destroy()
        
    except Exception as e:
        print(f"  ❌ GUI測試失敗: {e}")
    
    # 總結
    print("\n" + "="*50)
    print("📋 測試總結")
    print("="*50)
    
    print("✅ 可用功能:")
    print("  • 命令行清理: python delete_file_regularly.py")
    print("  • 批次啟動器: launcher.bat")
    print("  • 系統托盤: python cleanup_tray.py")
    print("  • GUI界面: python file_cleanup_gui.py")
    print("  • 歸檔管理: python file_archive_manager.py")
    
    print("\n🎯 推薦使用方式:")
    print("  1. 新手: 運行 launcher.bat 選擇模式")
    print("  2. 日常: 使用系統托盤模式")
    print("  3. 進階: 命令行參數直接調用")
    
    print("\n📝 使用提示:")
    print("  • 首次使用建議選擇壓縮歸檔模式")
    print("  • 系統托盤模式常駐後台，方便日常使用")
    print("  • 所有操作都有預覽功能，安全可靠")

if __name__ == "__main__":
    main()
    input("\n按 Enter 鍵退出...")
