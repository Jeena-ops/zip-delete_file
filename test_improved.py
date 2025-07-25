#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試改進後的檔案重新命名工具
驗證對已轉換檔案和不同日期格式的處理
"""

import tempfile
from pathlib import Path
from rename_files import FileRenamer


def test_improved_renamer():
    """測試改進後的重新命名功能"""
    print("測試改進後的檔案重新命名工具")
    print("=" * 60)
    
    # 創建臨時測試資料夾
    test_dir = Path(tempfile.mkdtemp(prefix="improved_rename_test_"))
    
    # 創建各種格式的測試檔案
    test_files = [
        # 已經是標準格式的檔案（不應該被修改）
        "123456789_USD_202504_TRF001.pdf",
        "987654321_EUR_202505_TRF002.xlsx", 
        
        # 需要轉換的 MMYYYY 格式
        "555666777_JPY_042025_TRF003.txt",
        "TRF004_111222333_GBP_052025.doc",
        
        # 混合格式（一些已轉換，一些未轉換）
        "444555666_TWD_202506_TRF005.csv",  # 已轉換
        "777888999_062025_CAD_TRF006.docx", # 未轉換
        
        # 錯誤的日期格式（應該被跳過）
        "999000111_USD_132025_TRF007.txt",  # 13月，無效
        "222333444_EUR_202513_TRF008.pdf",  # 13月，無效
        
        # 無法解析的檔案
        "invalid_file.txt",
    ]
    
    print(f"測試資料夾: {test_dir}")
    print("\n創建測試檔案:")
    for filename in test_files:
        test_file = test_dir / filename
        test_file.write_text(f"測試內容：{filename}")
        print(f"  - {filename}")
    
    # 初始化重新命名工具
    renamer = FileRenamer()
    
    print("\n" + "=" * 60)
    print("執行重新命名預覽")
    print("=" * 60)
    
    # 執行預覽
    results = renamer.rename_files_in_directory(str(test_dir), dry_run=True)
    
    # 列印摘要
    renamer.print_summary(results)
    
    # 分析結果
    print("\n" + "=" * 60)
    print("結果分析")
    print("=" * 60)
    
    already_standard = 0
    successfully_parsed = 0
    failed_to_parse = 0
    
    for original, new, success in results:
        if success and original == new:
            already_standard += 1
        elif success and original != new:
            successfully_parsed += 1
        else:
            failed_to_parse += 1
    
    print(f"已經是標準格式: {already_standard} 個檔案")
    print(f"成功解析並轉換: {successfully_parsed} 個檔案") 
    print(f"無法解析: {failed_to_parse} 個檔案")
    
    return test_dir


def test_date_format_detection():
    """測試日期格式檢測功能"""
    print("\n" + "=" * 60)
    print("測試日期格式檢測")
    print("=" * 60)
    
    renamer = FileRenamer()
    
    test_cases = [
        ("123456789_USD_042025_TRF001", "MMYYYY 格式，應該轉換"),
        ("123456789_USD_202504_TRF001", "YYYYMM 格式，不應轉換"),
        ("123456789_USD_132025_TRF001", "無效月份，應該跳過"),
        ("123456789_USD_202513_TRF001", "無效月份，應該跳過"),
        ("123456789_USD_202504_TRF001", "標準格式，應該直接跳過"),
    ]
    
    for filename_without_ext, description in test_cases:
        print(f"\n測試檔案: {filename_without_ext}")
        print(f"描述: {description}")
        
        # 檢查是否已經是標準格式
        is_standard = renamer.is_already_standard_format(filename_without_ext)
        print(f"是否標準格式: {is_standard}")
        
        if not is_standard:
            # 解析檔名組件
            components = renamer.parse_filename(filename_without_ext)
            print(f"解析結果: {components}")


if __name__ == "__main__":
    # 執行主要測試
    test_dir = test_improved_renamer()
    
    # 執行日期格式檢測測試
    test_date_format_detection()
    
    print(f"\n測試完成！測試檔案位於: {test_dir}")
    print("您可以檢查結果或刪除測試資料夾")
