#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
創建桌面快捷方式
"""

import os
import sys
from pathlib import Path

def create_desktop_shortcut():
    """創建桌面快捷方式"""
    try:
        # 獲取桌面路徑
        desktop = Path.home() / "Desktop"
        if not desktop.exists():
            desktop = Path.home() / "桌面"  # 中文系統
        
        if not desktop.exists():
            print("❌ 無法找到桌面資料夾")
            return False
        
        # 快捷方式內容
        current_dir = Path.cwd()
        batch_file = current_dir / "start_tray.bat"
        
        if not batch_file.exists():
            print("❌ 找不到啟動腳本 start_tray.bat")
            return False
        
        # Windows 快捷方式創建
        if sys.platform.startswith('win'):
            import winshell
            from win32com.client import Dispatch
            
            shell = Dispatch('WScript.Shell')
            shortcut_path = desktop / "檔案清理工具.lnk"
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = str(batch_file)
            shortcut.WorkingDirectory = str(current_dir)
            shortcut.IconLocation = str(batch_file)
            shortcut.Description = "檔案清理工具 - 系統托盤版本"
            shortcut.save()
            
            print(f"✅ 桌面快捷方式已創建：{shortcut_path}")
            return True
        else:
            print("❌ 目前只支援 Windows 系統")
            return False
            
    except ImportError:
        print("❌ 缺少必要套件，請執行：pip install pywin32 winshell")
        return False
    except Exception as e:
        print(f"❌ 創建快捷方式失敗：{e}")
        return False

def main():
    """主程式"""
    print("🖥️ 檔案清理工具 - 桌面快捷方式創建器")
    print("=" * 50)
    
    if create_desktop_shortcut():
        print("\n🎉 快捷方式創建成功！")
        print("💡 您現在可以：")
        print("   • 雙擊桌面上的「檔案清理工具」圖示啟動程式")
        print("   • 程式會在系統托盤中常駐運行")
        print("   • 右鍵托盤圖示可以快速清理檔案")
    else:
        print("\n❌ 快捷方式創建失敗")
        print("💡 您可以手動創建快捷方式：")
        print("   • 右鍵桌面 → 新增 → 捷徑")
        print(f"   • 位置：{Path.cwd() / 'start_tray.bat'}")
    
    input("\n按任意鍵退出...")

if __name__ == "__main__":
    main()
