#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檔案清理工具完整測試腳本
測試所有功能模塊和依賴
"""

import os
import sys
import traceback
from pathlib import Path

def test_imports():
    """測試所有必要的模塊導入"""
    print("🧪 測試模塊導入...")
    
    tests = [
        ("標準庫", ["os", "sys", "json", "zipfile", "datetime", "pathlib"]),
        ("GUI相關", ["tkinter", "tkinter.ttk", "tkinter.messagebox"]),
        ("系統托盤", ["pystray", "PIL.Image", "PIL.ImageDraw"]),
        ("排程", ["schedule"]),
        ("主要模塊", ["delete_file_regularly"])
    ]
    
    results = {}
    
    for category, modules in tests:
        print(f"\n📦 測試 {category}:")
        results[category] = []
        
        for module in modules:
            try:
                if "." in module:
                    # 處理子模塊
                    parts = module.split(".")
                    imported = __import__(parts[0])
                    for part in parts[1:]:
                        imported = getattr(imported, part)
                else:
                    __import__(module)
                print(f"  ✅ {module}")
                results[category].append((module, True, ""))
            except ImportError as e:
                print(f"  ❌ {module}: {e}")
                results[category].append((module, False, str(e)))
            except Exception as e:
                print(f"  ⚠️  {module}: {e}")
                results[category].append((module, False, str(e)))
    
    return results

def test_core_functionality():
    """測試核心清理功能"""
    print("\n🔧 測試核心功能...")
    
    try:
        from delete_file_regularly import FileCleanupTool
        
        # 測試基本初始化
        print("  ✅ FileCleanupTool 類可以導入")
        
        # 測試不同模式的初始化
        modes = [
            ("回收站模式", True, False),
            ("歸檔模式", False, True),
            ("直接刪除模式", False, False)
        ]
        
        for mode_name, use_recycle, use_archive in modes:
            try:
                cleaner = FileCleanupTool("INFO", use_recycle, use_archive)
                print(f"  ✅ {mode_name} 初始化成功")
            except Exception as e:
                print(f"  ❌ {mode_name} 初始化失敗: {e}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 核心功能測試失敗: {e}")
        return False

def test_gui_availability():
    """測試GUI相關功能"""
    print("\n🖥️  測試GUI功能...")
    
    try:
        import tkinter as tk
        from tkinter import ttk
        
        # 創建測試窗口
        root = tk.Tk()
        root.withdraw()  # 隱藏窗口
        
        # 測試基本widget
        frame = ttk.Frame(root)
        button = ttk.Button(frame, text="Test")
        label = ttk.Label(frame, text="Test")
        
        print("  ✅ tkinter GUI 可用")
        root.destroy()
        return True
        
    except Exception as e:
        print(f"  ❌ GUI 測試失敗: {e}")
        return False

def test_tray_functionality():
    """測試系統托盤功能"""
    print("\n🔔 測試系統托盤功能...")
    
    try:
        import pystray
        from PIL import Image, ImageDraw
        
        # 創建測試圖標
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), color='blue')
        draw = ImageDraw.Draw(image)
        draw.rectangle([16, 16, 48, 48], fill='white')
        
        print("  ✅ 可以創建托盤圖標")
        
        # 測試菜單項創建
        menu_item = pystray.MenuItem("Test", lambda: None)
        menu = pystray.Menu(menu_item)
        
        print("  ✅ 可以創建托盤菜單")
        return True
        
    except Exception as e:
        print(f"  ❌ 系統托盤測試失敗: {e}")
        return False

def test_file_operations():
    """測試檔案操作功能"""
    print("\n📁 測試檔案操作...")
    
    try:
        # 創建測試目錄
        test_dir = Path("test_cleanup_temp")
        test_dir.mkdir(exist_ok=True)
        
        # 創建測試檔案
        test_file = test_dir / "test_file.txt"
        test_file.write_text("這是測試檔案", encoding='utf-8')
        
        print("  ✅ 可以創建測試檔案")
        
        # 測試檔案資訊獲取
        stat_info = test_file.stat()
        print(f"  ✅ 可以獲取檔案資訊: {stat_info.st_size} bytes")
        
        # 清理測試檔案
        test_file.unlink()
        test_dir.rmdir()
        
        print("  ✅ 檔案操作測試完成")
        return True
        
    except Exception as e:
        print(f"  ❌ 檔案操作測試失敗: {e}")
        return False

def test_archive_functionality():
    """測試壓縮歸檔功能"""
    print("\n📦 測試壓縮歸檔功能...")
    
    try:
        import zipfile
        
        # 創建測試目錄和檔案
        test_dir = Path("test_archive_temp")
        test_dir.mkdir(exist_ok=True)
        
        test_file = test_dir / "test_archive.txt"
        test_file.write_text("測試壓縮內容", encoding='utf-8')
        
        # 創建壓縮檔
        zip_path = test_dir / "test.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(test_file, test_file.name)
        
        print("  ✅ 可以創建壓縮檔")
        
        # 測試讀取壓縮檔
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            file_list = zipf.namelist()
            print(f"  ✅ 可以讀取壓縮檔內容: {file_list}")
        
        # 清理測試檔案
        test_file.unlink()
        zip_path.unlink()
        test_dir.rmdir()
        
        return True
        
    except Exception as e:
        print(f"  ❌ 壓縮歸檔測試失敗: {e}")
        return False

def generate_test_report(import_results, core_ok, gui_ok, tray_ok, file_ok, archive_ok):
    """生成測試報告"""
    print("\n" + "="*80)
    print("📋 測試報告總結")
    print("="*80)
    
    # 統計導入結果
    total_modules = 0
    failed_modules = 0
    
    for category, results in import_results.items():
        category_failed = sum(1 for _, success, _ in results if not success)
        total_modules += len(results)
        failed_modules += category_failed
        
        if category_failed == 0:
            print(f"✅ {category}: 全部通過 ({len(results)} 個模塊)")
        else:
            print(f"⚠️  {category}: {len(results)-category_failed}/{len(results)} 通過")
    
    print(f"\n📊 模塊導入統計: {total_modules-failed_modules}/{total_modules} 通過")
    
    # 功能測試結果
    print(f"\n🔧 功能測試結果:")
    tests = [
        ("核心清理功能", core_ok),
        ("GUI界面", gui_ok),
        ("系統托盤", tray_ok),
        ("檔案操作", file_ok),
        ("壓縮歸檔", archive_ok)
    ]
    
    passed_tests = sum(1 for _, result in tests if result)
    
    for test_name, result in tests:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"  {test_name}: {status}")
    
    print(f"\n📊 功能測試統計: {passed_tests}/{len(tests)} 通過")
    
    # 總體評估
    overall_score = (total_modules - failed_modules + passed_tests) / (total_modules + len(tests)) * 100
    
    print(f"\n🎯 總體評估: {overall_score:.1f}%")
    
    if overall_score >= 90:
        print("🎉 優秀！系統完全可用")
        return "excellent"
    elif overall_score >= 75:
        print("👍 良好！大部分功能可用")
        return "good"
    elif overall_score >= 50:
        print("⚠️  一般！部分功能需要修復")
        return "fair"
    else:
        print("❌ 需要修復！多個關鍵功能不可用")
        return "poor"

def main():
    """主測試函數"""
    print("🚀 檔案清理工具 - 完整功能測試")
    print("="*80)
    
    try:
        # 執行所有測試
        import_results = test_imports()
        core_ok = test_core_functionality()
        gui_ok = test_gui_availability()
        tray_ok = test_tray_functionality()
        file_ok = test_file_operations()
        archive_ok = test_archive_functionality()
        
        # 生成測試報告
        result = generate_test_report(
            import_results, core_ok, gui_ok, tray_ok, file_ok, archive_ok
        )
        
        # 提供使用建議
        print(f"\n💡 使用建議:")
        if result in ["excellent", "good"]:
            print("  • 可以正常使用所有功能")
            print("  • 推薦使用系統托盤模式: python cleanup_tray.py")
            print("  • 或使用啟動器: launcher.bat 選擇選項 8")
        elif result == "fair":
            print("  • 基本功能可用，建議先使用命令行模式")
            print("  • 檢查缺失的依賴並安裝")
        else:
            print("  • 需要先解決依賴問題")
            print("  • 執行: pip install pystray pillow schedule")
        
    except Exception as e:
        print(f"\n❌ 測試過程中發生錯誤: {e}")
        print(f"錯誤詳情:\n{traceback.format_exc()}")

if __name__ == "__main__":
    main()
