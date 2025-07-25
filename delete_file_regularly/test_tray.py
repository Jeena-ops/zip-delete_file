#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單測試系統托盤功能
"""

import sys
import time

print("🧪 測試系統托盤依賴...")

try:
    import pystray
    print("✅ pystray 已安裝")
except ImportError as e:
    print(f"❌ pystray 未安裝: {e}")
    sys.exit(1)

try:
    from PIL import Image, ImageDraw
    print("✅ PIL (Pillow) 已安裝")
except ImportError as e:
    print(f"❌ PIL 未安裝: {e}")
    sys.exit(1)

try:
    import schedule
    print("✅ schedule 已安裝")
except ImportError as e:
    print(f"❌ schedule 未安裝: {e}")
    sys.exit(1)

print("\n🎉 所有依賴都已正確安裝！")
print("\n現在可以運行系統托盤應用：")
print("方法1: python cleanup_tray.py")
print("方法2: 運行 launcher.bat 然後選擇選項 8")
print("方法3: 運行 start_tray.bat")

print("\n系統托盤應用功能：")
print("📌 常駐系統托盤，右鍵點擊托盤圖標可以：")
print("   • 快速清理檔案")
print("   • 打開控制面板")
print("   • 查看統計資訊") 
print("   • 管理自動清理設定")
print("   • 退出應用")

input("\n按 Enter 鍵繼續...")
