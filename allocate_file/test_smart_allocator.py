#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檔案自動分類工具 - 測試程式
演示智能學習功能
"""

import tempfile
import os
from pathlib import Path
from allocate_file import FileAllocator


def create_test_files():
    """創建測試檔案來演示不同的檔名格式"""
    # 創建臨時資料夾
    test_dir = Path(tempfile.mkdtemp(prefix="file_allocator_test_"))
    
    # 不同格式的測試檔案
    test_files = [
        # 格式1: 合同_部門_日期
        "合同_財務部_2025Q3.pdf",
        "合同_人事部_2025Q4.docx",
        "合同_技術部_2025Q1.pdf",
        
        # 格式2: 報告_類型_部門_日期
        "報告_月報_財務部_202501.xlsx",
        "報告_週報_人事部_202502.docx",
        "報告_年報_技術部_2025.pdf",
        
        # 格式3: 發票_供應商_金額_日期
        "發票_ABC公司_50000_20250115.pdf",
        "發票_XYZ供應商_25000_20250120.pdf",
        
        # 格式4: 照片_事件_地點_日期
        "照片_會議_會議室A_20250125.jpg",
        "照片_聚餐_餐廳_20250130.png",
        
        # 格式5: 專案_名稱_階段_版本
        "專案_網站改版_設計_v1.docx",
        "專案_APP開發_測試_v2.pdf",
        
        # 新格式 - 程式會自動學習
        "客戶資料_VIP_台北_2025.xlsx",
        "會議記錄_董事會_季度_Q1.docx",
    ]
    
    # 創建測試檔案
    for filename in test_files:
        test_file = test_dir / filename
        test_file.write_text(f"測試內容：{filename}")
    
    return test_dir


def test_intelligent_learning():
    """測試智能學習功能"""
    print("檔案自動分類工具 - 智能學習測試")
    print("=" * 60)
    
    # 創建測試檔案
    test_dir = create_test_files()
    target_dir = test_dir / "OrganizedFiles"
    
    print(f"測試資料夾：{test_dir}")
    print(f"目標資料夾：{target_dir}")
    
    # 列出原始檔案
    print("\n原始檔案列表：")
    for file_path in sorted(test_dir.iterdir()):
        if file_path.is_file():
            print(f"  - {file_path.name}")
    
    # 創建檔案分配器
    allocator = FileAllocator(
        watch_folder=str(test_dir),
        target_folder=str(target_dir),
        separator="_"
    )
    
    print("\n" + "=" * 60)
    print("開始智能分析和分類...")
    print("=" * 60)
    
    # 掃描和整理檔案
    allocator.scan_and_organize()
    
    print("\n" + "=" * 60)
    print("學習結果")
    print("=" * 60)
    
    # 顯示學習到的模式
    allocator.show_learned_patterns()
    
    print("\n" + "=" * 60)
    print("分類結果")
    print("=" * 60)
    
    # 顯示分類後的資料夾結構
    def show_directory_tree(path, prefix=""):
        """遞歸顯示資料夾結構"""
        path = Path(path)
        if not path.exists():
            return
            
        items = sorted(path.iterdir())
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            print(f"{prefix}{current_prefix}{item.name}")
            
            if item.is_dir():
                extension_prefix = "    " if is_last else "│   "
                show_directory_tree(item, prefix + extension_prefix)
    
    if target_dir.exists():
        print(f"\n分類後的資料夾結構：")
        show_directory_tree(target_dir)
    
    return test_dir, allocator


def interactive_test():
    """互動式測試"""
    test_dir, allocator = test_intelligent_learning()
    
    print("\n" + "=" * 60)
    print("互動式測試")
    print("=" * 60)
    
    while True:
        print("\n測試選項：")
        print("1. 添加新的測試檔案")
        print("2. 查看學習到的模式")
        print("3. 手動添加模式")
        print("4. 測試檔名分析")
        print("5. 退出測試")
        
        choice = input("請選擇 (1-5): ").strip()
        
        if choice == "1":
            filename = input("請輸入新檔案名稱：").strip()
            if filename:
                test_file = test_dir / filename
                test_file.write_text(f"測試內容：{filename}")
                print(f"已創建檔案：{filename}")
                
                # 分析新檔案
                if allocator.move_file(test_file):
                    print("檔案移動成功！")
                else:
                    print("檔案移動失敗")
                    
        elif choice == "2":
            allocator.show_learned_patterns()
            
        elif choice == "3":
            allocator.add_pattern_manually()
            
        elif choice == "4":
            filename = input("請輸入要分析的檔名：").strip()
            if filename:
                pattern_info = allocator.analyze_filename_pattern(filename)
                print(f"\n分析結果：")
                print(f"  檔案：{filename}")
                print(f"  模式簽名：{pattern_info['pattern_signature']}")
                print(f"  建議結構：{' > '.join(pattern_info['suggested_structure'])}")
                
                folder_structure, is_known = allocator.get_folder_structure_for_file(filename)
                print(f"  資料夾結構：{' > '.join(folder_structure)}")
                print(f"  是否已知模式：{'是' if is_known else '否'}")
                
        elif choice == "5":
            break
        else:
            print("無效選項")
    
    print(f"\n測試完成！測試資料夾：{test_dir}")
    print("您可以手動檢查結果或刪除測試資料夾")


if __name__ == "__main__":
    try:
        interactive_test()
    except KeyboardInterrupt:
        print("\n測試中斷")
    except Exception as e:
        print(f"測試過程中發生錯誤：{e}")
        import traceback
        traceback.print_exc()
