#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檔案批次重新命名工具
功能：將資料夾內的檔案重新命名為統一格式
格式：帳戶_幣別_日期_轉帳號碼.ext
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class FileRenamer:
    """檔案重新命名類別"""
    
    def __init__(self):
        # 定義可能的幣別代碼（可根據需要擴充）
        self.currencies = {
            'USD', 'EUR', 'JPY', 'GBP', 'AUD', 'CAD', 'CHF', 'CNY', 'HKD', 'SGD',
            'TWD', 'KRW', 'THB', 'MYR', 'PHP', 'IDR', 'VND', 'INR', 'BRL', 'MXN'
        }
        
        # 定義日期格式的正則表達式
        # MMYYYY 格式（需要轉換）
        self.date_pattern_mmyyyy = re.compile(r'\b(\d{2})(\d{4})\b')
        # YYYYMM 格式（已經是標準格式）
        self.date_pattern_yyyymm = re.compile(r'\b(\d{4})(\d{2})\b')
        
        # 定義帳戶號碼模式（通常為數字，長度較長）
        self.account_pattern = re.compile(r'\b\d{8,}\b')
        
        # 定義轉帳編號模式（通常包含字母和數字的組合）
        self.transfer_pattern = re.compile(r'\b[A-Z0-9]{6,}\b')

    def parse_filename(self, filename: str) -> Dict[str, Optional[str]]:
        """
        解析檔名中的各個組件
        
        Args:
            filename: 檔案名稱（不含副檔名）
            
        Returns:
            包含帳戶、幣別、日期、轉帳編號的字典
        """
        result = {
            'account': None,
            'currency': None,
            'date': None,
            'transfer_id': None
        }
        
        # 將檔名分割成各個部分
        parts = filename.split('_')
        
        for part in parts:
            part = part.strip().upper()
            
            # 檢查是否為幣別
            if part in self.currencies:
                result['currency'] = part
                continue
            
            # 檢查是否為日期格式
            # 首先檢查是否已經是 YYYYMM 格式
            yyyymm_match = self.date_pattern_yyyymm.match(part)
            if yyyymm_match:
                year, month = yyyymm_match.groups()
                # 驗證月份是否有效（01-12）
                if 1 <= int(month) <= 12:
                    result['date'] = part  # 已經是正確格式，直接使用
                    continue
            
            # 檢查是否為 MMYYYY 格式（需要轉換）
            mmyyyy_match = self.date_pattern_mmyyyy.match(part)
            if mmyyyy_match:
                month, year = mmyyyy_match.groups()
                # 驗證月份是否有效（01-12）
                if 1 <= int(month) <= 12:
                    # 轉換為 YYYYMM 格式
                    result['date'] = f"{year}{month}"
                    continue
            
            # 檢查是否為帳戶號碼（長數字）
            if self.account_pattern.match(part) and not result['account']:
                result['account'] = part
                continue
            
            # 檢查是否為轉帳編號
            if self.transfer_pattern.match(part) and not result['transfer_id']:
                result['transfer_id'] = part
                continue
        
        return result

    def is_already_standard_format(self, filename: str) -> bool:
        """
        檢查檔名是否已經是標準格式（帳戶_幣別_YYYYMM_轉帳號碼）
        
        Args:
            filename: 檔案名稱（不含副檔名）
            
        Returns:
            True 如果已經是標準格式，False 否則
        """
        parts = filename.split('_')
        if len(parts) != 4:
            return False
        
        account, currency, date, transfer_id = parts
        
        # 檢查各部分是否符合標準格式
        # 帳戶：8位以上數字
        if not re.match(r'^\d{8,}$', account):
            return False
        
        # 幣別：3位字母且在支援列表中
        if currency.upper() not in self.currencies:
            return False
        
        # 日期：YYYYMM 格式
        if not re.match(r'^\d{4}(0[1-9]|1[0-2])$', date):
            return False
        
        # 轉帳編號：6位以上字母數字組合
        if not re.match(r'^[A-Z0-9]{6,}$', transfer_id.upper()):
            return False
        
        return True

    def generate_new_filename(self, components: Dict[str, Optional[str]], extension: str) -> Optional[str]:
        """
        根據解析的組件生成新的檔案名稱
        
        Args:
            components: 檔案名稱組件字典
            extension: 檔案副檔名
            
        Returns:
            新的檔案名稱，如果組件不完整則返回 None
        """
        # 檢查必要的組件是否存在
        required_fields = ['account', 'currency', 'date', 'transfer_id']
        missing_fields = [field for field in required_fields if not components[field]]
        
        if missing_fields:
            print(f"警告：缺少必要欄位 {missing_fields}")
            return None
        
        # 生成新檔名：帳戶_幣別_日期_轉帳號碼.ext
        new_filename = f"{components['account']}_{components['currency']}_{components['date']}_{components['transfer_id']}{extension}"
        return new_filename

    def rename_files_in_directory(self, directory_path: str, dry_run: bool = True) -> List[Tuple[str, str, bool]]:
        """
        批次重新命名指定資料夾中的檔案
        
        Args:
            directory_path: 目標資料夾路徑
            dry_run: 是否為預覽模式（不實際執行重新命名）
            
        Returns:
            重新命名結果列表：(原檔名, 新檔名, 是否成功)
        """
        results = []
        
        try:
            directory = Path(directory_path)
            if not directory.exists():
                print(f"錯誤：資料夾 '{directory_path}' 不存在")
                return results
            
            if not directory.is_dir():
                print(f"錯誤：'{directory_path}' 不是一個資料夾")
                return results
            
            # 獲取所有檔案
            files = [f for f in directory.iterdir() if f.is_file()]
            
            if not files:
                print("資料夾中沒有找到任何檔案")
                return results
            
            print(f"找到 {len(files)} 個檔案")
            print("-" * 60)
            
            for file_path in files:
                try:
                    original_name = file_path.name
                    filename_without_ext = file_path.stem
                    extension = file_path.suffix
                    
                    print(f"處理檔案: {original_name}")
                    
                    # 首先檢查是否已經是標準格式
                    if self.is_already_standard_format(filename_without_ext):
                        print(f"  ✓ 檔案已經是標準格式，跳過")
                        results.append((original_name, original_name, True))
                        print()
                        continue
                    
                    # 解析檔名組件
                    components = self.parse_filename(filename_without_ext)
                    print(f"  解析結果: {components}")
                    
                    # 生成新檔名
                    new_filename = self.generate_new_filename(components, extension)
                    
                    if new_filename:
                        new_file_path = directory / new_filename
                        
                        # 檢查新檔名是否已存在
                        if new_file_path.exists() and new_file_path != file_path:
                            print(f"  警告: 新檔名 '{new_filename}' 已存在，跳過此檔案")
                            results.append((original_name, new_filename, False))
                            continue
                        
                        if not dry_run:
                            # 實際執行重新命名
                            file_path.rename(new_file_path)
                            print(f"  ✓ 重新命名為: {new_filename}")
                            results.append((original_name, new_filename, True))
                        else:
                            print(f"  預覽: 將重新命名為 {new_filename}")
                            results.append((original_name, new_filename, True))
                    else:
                        print(f"  ✗ 無法解析檔名，跳過此檔案")
                        results.append((original_name, "", False))
                    
                    print()
                    
                except Exception as e:
                    print(f"  錯誤: 處理檔案 '{file_path.name}' 時發生錯誤: {e}")
                    results.append((file_path.name, "", False))
                    continue
            
        except Exception as e:
            print(f"錯誤: 處理資料夾時發生錯誤: {e}")
        
        return results

    def print_summary(self, results: List[Tuple[str, str, bool]]):
        """列印重新命名摘要"""
        total_files = len(results)
        successful_renames = sum(1 for _, _, success in results if success)
        failed_renames = total_files - successful_renames
        
        print("=" * 60)
        print("重新命名摘要")
        print("=" * 60)
        print(f"總檔案數: {total_files}")
        print(f"成功重新命名: {successful_renames}")
        print(f"失敗或跳過: {failed_renames}")
        
        if failed_renames > 0:
            print("\n失敗的檔案:")
            for original, new, success in results:
                if not success:
                    print(f"  - {original}")


def main():
    """主程式"""
    renamer = FileRenamer()
    
    print("檔案批次重新命名工具")
    print("=" * 60)
    
    # 獲取使用者輸入的資料夾路徑
    while True:
        directory_path = input("請輸入資料夾路徑: ").strip()
        if directory_path:
            break
        print("請輸入有效的資料夾路徑")
    
    # 移除引號（如果有的話）
    directory_path = directory_path.strip('\'"')
    
    print(f"\n目標資料夾: {directory_path}")
    
    # 首先執行預覽模式
    print("\n=== 預覽模式 ===")
    results = renamer.rename_files_in_directory(directory_path, dry_run=True)
    
    if not results:
        print("沒有找到可處理的檔案")
        return
    
    renamer.print_summary(results)
    
    # 詢問是否要實際執行重新命名
    while True:
        confirm = input("\n是否要執行實際的重新命名操作？(y/n): ").strip().lower()
        if confirm in ['y', 'yes', '是']:
            print("\n=== 執行重新命名 ===")
            final_results = renamer.rename_files_in_directory(directory_path, dry_run=False)
            renamer.print_summary(final_results)
            break
        elif confirm in ['n', 'no', '否']:
            print("操作已取消")
            break
        else:
            print("請輸入 y 或 n")


if __name__ == "__main__":
    main()
