#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檔案自動分類整理工具 - 測試程式
創建測試檔案並驗證分類功能
"""

import os
import tempfile
import shutil
from pathlib import Path
from allocate_file import FileAllocator


def create_test_files(test_dir: Path):
    """創建測試檔案"""
    test_files = [
        # 正常分類檔案
        "合同_財務部_2025Q3.pdf",
        "報告_人事_月報_202501.docx", 
        "照片_旅遊_日本_2025.jpg",
        "發票_會計_電費_202501.pdf",
        "音樂_古典_貝多芬_交響曲.mp3",
        
        # 多層分類
        "工作_專案A_需求文件_20250125.docx",
        "學習_程式設計_Python_基礎教學.pdf",
        "個人_財務_銀行_對帳單_202501.pdf",
        
        # 特殊情況
        "無分隔符檔案.txt",  # 應該進入未分類
        "空檔案__test.docx",  # 空分類測試
        "特殊字符_<>:\"/\\|?*_測試.pdf",  # 特殊字符測試
        
        # 不支援的檔案類型
        "程式_工具_某個軟體.exe",
        "系統_配置_設定檔.ini",
    ]
    
    print(f"在 {test_dir} 中創建測試檔案：")
    for filename in test_files:
        file_path = test_dir / filename
        file_path.write_text(f"這是測試檔案：{filename}", encoding='utf-8')
        print(f"  ✓ {filename}")
    
    return test_files


def test_file_allocator():
    """測試檔案分配器"""
    print("檔案自動分類整理工具 - 測試")
    print("=" * 50)
    
    # 創建臨時測試目錄
    with tempfile.TemporaryDirectory(prefix="file_allocator_test_") as temp_dir:
        temp_path = Path(temp_dir)
        watch_dir = temp_path / "watch"
        target_dir = temp_path / "organized"
        
        watch_dir.mkdir()
        target_dir.mkdir()
        
        print(f"測試目錄：{temp_path}")
        print(f"監控目錄：{watch_dir}")
        print(f"目標目錄：{target_dir}")
        print()
        
        # 創建測試檔案
        test_files = create_test_files(watch_dir)
        print(f"\n總共創建了 {len(test_files)} 個測試檔案")
        
        # 初始化檔案分配器
        allocator = FileAllocator(
            watch_folder=str(watch_dir),
            target_folder=str(target_dir),
            separator="_"
        )
        
        print("\n開始測試檔案分類...")
        print("-" * 30)
        
        # 執行檔案整理
        allocator.scan_and_organize()
        
        print("\n測試結果分析：")
        print("-" * 30)
        
        # 分析結果
        analyze_results(target_dir)
        
        print(f"\n測試完成！您可以查看以下目錄結構：")
        print(f"目標目錄：{target_dir}")
        
        # 顯示目錄結構
        display_directory_tree(target_dir)
        
        input("\n按 Enter 鍵查看詳細結果，或 Ctrl+C 退出...")
        
        # 顯示詳細的檔案分佈
        show_detailed_results(target_dir)


def analyze_results(target_dir: Path):
    """分析整理結果"""
    if not target_dir.exists():
        print("❌ 目標目錄不存在")
        return
    
    total_files = 0
    folders_created = []
    
    for root, dirs, files in os.walk(target_dir):
        root_path = Path(root)
        if files:
            relative_path = root_path.relative_to(target_dir)
            folders_created.append(str(relative_path))
            total_files += len(files)
    
    print(f"✅ 總共處理檔案：{total_files} 個")
    print(f"✅ 創建資料夾：{len(folders_created)} 個")
    
    if folders_created:
        print("📁 創建的分類資料夾：")
        for folder in sorted(folders_created):
            print(f"   - {folder}")


def display_directory_tree(directory: Path, prefix: str = "", max_depth: int = 3, current_depth: int = 0):
    """顯示目錄樹結構"""
    if current_depth > max_depth:
        return
    
    if not directory.exists():
        return
    
    items = sorted(directory.iterdir(), key=lambda x: (x.is_file(), x.name))
    
    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        current_prefix = "└── " if is_last else "├── "
        
        print(f"{prefix}{current_prefix}{item.name}")
        
        if item.is_dir() and current_depth < max_depth:
            next_prefix = prefix + ("    " if is_last else "│   ")
            display_directory_tree(item, next_prefix, max_depth, current_depth + 1)


def show_detailed_results(target_dir: Path):
    """顯示詳細的整理結果"""
    print("\n詳細檔案分佈：")
    print("=" * 50)
    
    for root, dirs, files in os.walk(target_dir):
        root_path = Path(root)
        if files:
            relative_path = root_path.relative_to(target_dir)
            print(f"\n📁 {relative_path}/")
            for file in sorted(files):
                file_path = root_path / file
                size = file_path.stat().st_size
                print(f"   📄 {file} ({size} bytes)")


def test_filename_parsing():
    """測試檔名解析功能"""
    print("\n檔名解析測試：")
    print("=" * 30)
    
    allocator = FileAllocator(".", ".")
    
    test_cases = [
        "合同_財務部_2025Q3.pdf",
        "報告_人事_月報_202501.docx",
        "工作_專案A_需求文件_20250125.docx",
        "無分隔符檔案.txt",
        "空檔案__.txt",
        "特殊字符_<>:測試.pdf",
    ]
    
    for filename in test_cases:
        categories, new_name = allocator.parse_filename(filename)
        print(f"檔案：{filename}")
        print(f"  分類：{' > '.join(categories) if categories else '無'}")
        print(f"  新名：{new_name}")
        print()


if __name__ == "__main__":
    try:
        # 執行檔名解析測試
        test_filename_parsing()
        
        # 執行完整測試
        test_file_allocator()
        
    except KeyboardInterrupt:
        print("\n\n測試被用戶中斷")
    except Exception as e:
        print(f"\n❌ 測試過程中發生錯誤：{e}")
        import traceback
        traceback.print_exc()
