#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檔案清理工具測試腳本
用於創建測試檔案和驗證清理功能
"""

import os
import time
from pathlib import Path
from datetime import datetime, timedelta
from delete_file_regularly import FileCleanupTool


def create_test_files():
    """創建測試檔案和資料夾結構"""
    test_folder = Path("test_cleanup")
    test_folder.mkdir(exist_ok=True)
    
    # 創建子資料夾
    (test_folder / "subfolder1").mkdir(exist_ok=True)
    (test_folder / "subfolder2").mkdir(exist_ok=True)
    
    # 創建不同時間的測試檔案
    test_files = [
        # 舊檔案（超過30天）
        ("old_file_1.txt", 35),
        ("old_file_2.pdf", 45),
        ("subfolder1/old_sub_file.log", 40),
        
        # 中等檔案（10-20天）
        ("medium_file_1.doc", 15),
        ("medium_file_2.xlsx", 18),
        ("subfolder2/medium_sub_file.txt", 12),
        
        # 新檔案（5天內）
        ("new_file_1.txt", 2),
        ("new_file_2.jpg", 1),
        ("subfolder1/new_sub_file.py", 3),
    ]
    
    print("創建測試檔案...")
    for filename, days_old in test_files:
        file_path = test_folder / filename
        
        # 創建檔案
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"這是測試檔案: {filename}\n")
            f.write(f"創建時間: {datetime.now()}\n")
            f.write(f"模擬天數: {days_old} 天前\n")
            f.write("內容" * 100)  # 增加一些內容
        
        # 修改檔案時間
        old_time = datetime.now() - timedelta(days=days_old)
        timestamp = old_time.timestamp()
        os.utime(file_path, (timestamp, timestamp))
        
        print(f"  ✓ {filename} (模擬 {days_old} 天前)")
    
    print(f"\n測試環境創建完成！")
    print(f"測試資料夾：{test_folder.absolute()}")
    print(f"總共創建：{len(test_files)} 個檔案")
    return test_folder


def run_cleanup_test():
    """執行清理測試"""
    print("\n" + "="*60)
    print("檔案清理工具測試")
    print("="*60)
    
    # 創建測試檔案
    test_folder = create_test_files()
    
    # 創建清理工具
    cleaner = FileCleanupTool("INFO")
    
    print(f"\n測試 1: 預覽模式 - 刪除30天前的檔案")
    print("-" * 40)
    
    try:
        # 執行預覽
        result = cleaner.cleanup_files(
            str(test_folder), 
            days_to_keep=30, 
            include_subfolders=True, 
            dry_run=True
        )
        
        cleaner.print_summary(result)
        
        # 詢問是否執行實際清理
        if result['total_found'] > 0:
            confirm = input(f"\n是否執行實際清理測試？ (y/n): ").strip().lower()
            if confirm in ['y', 'yes']:
                print(f"\n測試 2: 實際清理模式")
                print("-" * 40)
                
                actual_result = cleaner.cleanup_files(
                    str(test_folder), 
                    days_to_keep=30, 
                    include_subfolders=True, 
                    dry_run=False
                )
                
                cleaner.print_summary(actual_result)
                
                # 驗證結果
                remaining_files = list(test_folder.rglob("*"))
                remaining_files = [f for f in remaining_files if f.is_file()]
                print(f"\n剩餘檔案數量：{len(remaining_files)}")
                
                if remaining_files:
                    print("剩餘檔案：")
                    for f in remaining_files:
                        rel_path = f.relative_to(test_folder)
                        print(f"  - {rel_path}")
        
        # 詢問是否清理測試資料夾
        cleanup_test = input(f"\n是否刪除測試資料夾？ (y/n): ").strip().lower()
        if cleanup_test in ['y', 'yes']:
            import shutil
            shutil.rmtree(test_folder)
            print(f"測試資料夾已刪除：{test_folder}")
        else:
            print(f"測試資料夾保留：{test_folder}")
            
    except Exception as e:
        print(f"測試過程中發生錯誤：{e}")
        return False
    
    return True


def demo_different_scenarios():
    """示範不同使用情境"""
    print("\n" + "="*60)
    print("使用情境示範")
    print("="*60)
    
    scenarios = [
        {
            'name': '清理下載資料夾（保留30天）',
            'path': r'C:\Users\%USERNAME%\Downloads',
            'days': 30,
            'description': '適合清理下載檔案，保留最近一個月的檔案'
        },
        {
            'name': '清理暫存檔案（保留7天）',
            'path': r'C:\Windows\Temp',
            'days': 7,
            'description': '清理系統暫存檔案，保留最近一週的檔案'
        },
        {
            'name': '清理日誌檔案（保留90天）',
            'path': r'C:\logs',
            'days': 90,
            'description': '清理應用程式日誌，保留最近三個月的記錄'
        },
        {
            'name': '清理桌面檔案（保留60天）',
            'path': r'C:\Users\%USERNAME%\Desktop',
            'days': 60,
            'description': '整理桌面檔案，保留最近兩個月的檔案'
        }
    ]
    
    print("常見使用情境：\n")
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario['name']}")
        print(f"   路徑: {scenario['path']}")
        print(f"   保留: {scenario['days']} 天")
        print(f"   說明: {scenario['description']}")
        print(f"   命令: python delete_file_regularly.py --path \"{scenario['path']}\" --days {scenario['days']}")
        print()
    
    print("注意事項：")
    print("- 請根據實際需求調整路徑和保留天數")
    print("- 建議先使用預覽模式確認要刪除的檔案")
    print("- 重要檔案請先備份")


if __name__ == "__main__":
    print("檔案清理工具測試與示範")
    print("="*60)
    
    while True:
        print("\n請選擇要執行的操作：")
        print("1. 執行功能測試（創建測試檔案並測試清理）")
        print("2. 查看使用情境示範")
        print("3. 退出")
        
        choice = input("\n請輸入選項 (1-3): ").strip()
        
        if choice == '1':
            run_cleanup_test()
        elif choice == '2':
            demo_different_scenarios()
        elif choice == '3':
            print("再見！")
            break
        else:
            print("無效選項，請重新選擇")
