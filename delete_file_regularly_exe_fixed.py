#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檔案自動清理工具 - EXE 優化版本
功能：根據設定的保留天數自動清理過期檔案
支援：Windows 平台，完整的日誌記錄和錯誤處理
EXE 修正：修正路徑問題、文件對話框問題
"""

import os
import sys
import time
import shutil
import logging
import argparse
import json
import zipfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import stat


def get_script_directory():
    """獲取腳本所在目錄，支援 EXE 和 Python 腳本"""
    if getattr(sys, 'frozen', False):
        # 如果是被打包的可執行檔案
        return Path(sys.executable).parent
    else:
        # 如果是 Python 腳本
        return Path(__file__).parent


def get_user_documents_folder():
    """獲取用戶文檔資料夾作為預設存檔位置"""
    try:
        documents = Path.home() / "Documents"
        if documents.exists():
            return documents
        return Path.home()
    except:
        return Path.cwd()


class FileCleanupTool:
    """檔案自動清理工具類別"""
    
    def __init__(self, log_level: str = "INFO", use_recycle_bin: bool = True, use_archive: bool = False):
        """
        初始化清理工具
        
        Args:
            log_level: 日誌級別 (DEBUG, INFO, WARNING, ERROR)
            use_recycle_bin: 是否使用回收站（True=移到回收站，False=直接刪除）
            use_archive: 是否使用壓縮歸檔（True=壓縮歸檔，False=使用回收站或直接刪除）
        """
        self.script_dir = get_script_directory()
        self.setup_logging(log_level)
        self.deleted_files = []
        self.failed_deletions = []
        self.total_size_freed = 0
        self.use_recycle_bin = use_recycle_bin
        self.use_archive = use_archive
        
        # 設定歸檔或回收站
        if self.use_archive:
            self.setup_archive()
        elif self.use_recycle_bin:
            self.setup_recycle_bin()
        
    def setup_logging(self, log_level: str):
        """設定日誌系統"""
        # 創建日誌資料夾（使用絕對路徑）
        log_folder = self.script_dir / "logs"
        log_folder.mkdir(exist_ok=True)
        
        # 設定日誌檔案（按日期分類）
        today = datetime.now().strftime('%Y%m%d')
        log_file = log_folder / f"file_cleanup_{today}.log"
        
        # 設定日誌格式
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 設定檔案處理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        
        # 設定控制台處理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # 設定 logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info(f"檔案清理工具啟動 - 日誌級別：{log_level}")
        self.logger.info(f"工作目錄：{self.script_dir}")
        self.logger.info(f"日誌檔案：{log_file}")
    
    def setup_recycle_bin(self):
        """設定回收站"""
        # 使用絕對路徑
        self.recycle_bin = self.script_dir / "recycle_bin"
        self.recycle_bin.mkdir(exist_ok=True)
        self.recovery_log = self.recycle_bin / "recovery_log.json"
        self.logger.info(f"回收站位置：{self.recycle_bin.absolute()}")
    
    def setup_archive(self):
        """設定歸檔資料夾"""
        # 使用絕對路徑
        self.archive_folder = self.script_dir / "archived_files"
        self.archive_folder.mkdir(exist_ok=True)
        self.archive_log = self.archive_folder / "archive_log.json"
        self.logger.info(f"歸檔資料夾位置：{self.archive_folder.absolute()}")
    
    def load_archive_log(self) -> List[Dict]:
        """載入歸檔日誌"""
        try:
            if hasattr(self, 'archive_log') and self.archive_log.exists():
                with open(self.archive_log, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            self.logger.warning(f"載入歸檔日誌失敗：{e}")
            return []
    
    def save_archive_log(self, log_data: List[Dict]):
        """儲存歸檔日誌"""
        try:
            if hasattr(self, 'archive_log'):
                with open(self.archive_log, 'w', encoding='utf-8') as f:
                    json.dump(log_data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            self.logger.warning(f"儲存歸檔日誌失敗：{e}")
    
    def load_recovery_log(self) -> List[Dict]:
        """載入恢復日誌"""
        try:
            if hasattr(self, 'recovery_log') and self.recovery_log.exists():
                with open(self.recovery_log, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            self.logger.warning(f"載入恢復日誌失敗：{e}")
            return []
    
    def save_recovery_log(self, log_data: List[Dict]):
        """儲存恢復日誌"""
        try:
            if hasattr(self, 'recovery_log'):
                with open(self.recovery_log, 'w', encoding='utf-8') as f:
                    json.dump(log_data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            self.logger.warning(f"儲存恢復日誌失敗：{e}")
    
    def validate_path(self, path: str) -> Path:
        """
        驗證資料夾路徑
        
        Args:
            path: 資料夾路徑字串
            
        Returns:
            Path: 驗證後的 Path 物件
            
        Raises:
            ValueError: 路徑無效時拋出異常
        """
        try:
            folder_path = Path(path).resolve()
            
            if not folder_path.exists():
                raise ValueError(f"資料夾不存在：{folder_path}")
            
            if not folder_path.is_dir():
                raise ValueError(f"指定的路徑不是資料夾：{folder_path}")
            
            # 檢查讀取權限
            test_file = folder_path / ".test_access"
            try:
                with open(test_file, 'w') as f:
                    f.write("test")
                test_file.unlink()
            except PermissionError:
                raise ValueError(f"對資料夾沒有寫入權限：{folder_path}")
            except Exception:
                pass  # 忽略其他錯誤，可能資料夾是只讀的
            
            return folder_path
            
        except Exception as e:
            raise ValueError(f"路徑驗證失敗：{e}")
    
    def format_size(self, size_bytes: int) -> str:
        """格式化檔案大小"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.2f} {size_names[i]}"
    
    def is_file_expired(self, file_path: Path, days_to_keep: int) -> bool:
        """
        檢查檔案是否過期
        
        Args:
            file_path: 檔案路徑
            days_to_keep: 保留天數
            
        Returns:
            bool: 是否過期
        """
        try:
            file_stat = file_path.stat()
            modified_time = datetime.fromtimestamp(file_stat.st_mtime)
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            return modified_time < cutoff_date
        except Exception as e:
            self.logger.warning(f"檢查檔案日期失敗 {file_path}：{e}")
            return False
    
    def can_delete_file(self, file_path: Path) -> bool:
        """
        檢查檔案是否可以被刪除
        
        Args:
            file_path: 檔案路徑
            
        Returns:
            bool: 是否可以刪除
        """
        try:
            # 檢查檔案是否被鎖定
            if os.name == 'nt':  # Windows
                # 嘗試重新命名來檢查檔案是否被使用
                temp_name = file_path.with_suffix(file_path.suffix + '.tmp')
                try:
                    file_path.rename(temp_name)
                    temp_name.rename(file_path)
                    return True
                except (PermissionError, OSError):
                    return False
            else:
                # Unix-like 系統
                return os.access(file_path, os.W_OK)
        except Exception:
            return False
    
    def find_expired_files(self, folder_path: Path, days_to_keep: int, include_subfolders: bool = True) -> List[Dict]:
        """
        找出過期檔案
        
        Args:
            folder_path: 資料夾路徑
            days_to_keep: 保留天數
            include_subfolders: 是否包含子資料夾
            
        Returns:
            List[Dict]: 過期檔案資訊列表
        """
        expired_files = []
        
        try:
            if include_subfolders:
                # 遞歸搜尋所有檔案
                pattern = "**/*"
            else:
                # 只搜尋當前資料夾的檔案
                pattern = "*"
            
            for file_path in folder_path.glob(pattern):
                if file_path.is_file():
                    try:
                        if self.is_file_expired(file_path, days_to_keep):
                            file_stat = file_path.stat()
                            file_info = {
                                'path': file_path,
                                'size': file_stat.st_size,
                                'modified_time': datetime.fromtimestamp(file_stat.st_mtime),
                                'can_delete': self.can_delete_file(file_path)
                            }
                            expired_files.append(file_info)
                    except Exception as e:
                        self.logger.warning(f"處理檔案時發生錯誤 {file_path}：{e}")
                        continue
                        
        except Exception as e:
            self.logger.error(f"掃描資料夾時發生錯誤：{e}")
        
        return expired_files
    
    def archive_file(self, file_info: Dict) -> bool:
        """
        將檔案壓縮歸檔
        
        Args:
            file_info: 檔案資訊字典
            
        Returns:
            bool: 是否成功歸檔
        """
        try:
            original_path = file_info['path']
            archived_time = datetime.now()
            
            # 生成歸檔檔案名稱（按日期分組）
            date_folder = archived_time.strftime('%Y%m%d')
            archive_name = f"archived_files_{date_folder}.zip"
            archive_path = self.archive_folder / archive_name
            
            # 在壓縮檔內的路徑（保持原始目錄結構，修正相對路徑問題）
            try:
                # 嘗試計算相對路徑
                relative_path = str(original_path.relative_to(original_path.anchor))
            except ValueError:
                # 如果無法計算相對路徑，使用檔案名
                relative_path = f"{archived_time.strftime('%Y%m%d_%H%M%S')}_{original_path.name}"
            
            # 添加到壓縮檔
            with zipfile.ZipFile(archive_path, 'a', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
                zipf.write(original_path, relative_path)
            
            # 檢查壓縮後大小
            compressed_size = archive_path.stat().st_size
            
            # 刪除原始檔案
            original_path.unlink()
            
            # 記錄到歸檔日誌
            log_data = self.load_archive_log()
            log_entry = {
                "original_path": str(original_path),
                "archive_path": str(archive_path),
                "archive_internal_path": relative_path,
                "original_size": file_info['size'],
                "modified_time": file_info['modified_time'].isoformat(),
                "archived_time": archived_time.isoformat(),
                "extracted": False
            }
            log_data.append(log_entry)
            self.save_archive_log(log_data)
            
            return True
            
        except Exception as e:
            self.logger.error(f"壓縮歸檔檔案失敗：{e}")
            return False
    
    def move_to_recycle_bin(self, file_info: Dict) -> bool:
        """
        將檔案移動到回收站
        
        Args:
            file_info: 檔案資訊字典
            
        Returns:
            bool: 是否成功移動
        """
        try:
            original_path = file_info['path']
            deleted_time = datetime.now()
            
            # 生成回收站中的檔案名稱（加上時間戳避免重複）
            timestamp = deleted_time.strftime('%Y%m%d_%H%M%S_%f')
            new_filename = f"{timestamp}_{original_path.name}"
            recycle_path = self.recycle_bin / new_filename
            
            # 移動檔案到回收站
            shutil.move(str(original_path), str(recycle_path))
            
            # 記錄到恢復日誌
            log_data = self.load_recovery_log()
            log_entry = {
                "original_path": str(original_path),
                "recycle_path": str(recycle_path),
                "original_size": file_info['size'],
                "modified_time": file_info['modified_time'].isoformat(),
                "deleted_time": deleted_time.isoformat(),
                "recovered": False
            }
            log_data.append(log_entry)
            self.save_recovery_log(log_data)
            
            return True
            
        except Exception as e:
            self.logger.error(f"移動檔案到回收站失敗：{e}")
            return False
    
    def delete_file_permanently(self, file_info: Dict) -> bool:
        """
        永久刪除檔案
        
        Args:
            file_info: 檔案資訊字典
            
        Returns:
            bool: 是否成功刪除
        """
        try:
            file_path = file_info['path']
            
            # 如果檔案是只讀的，先更改權限
            if os.name == 'nt':  # Windows
                try:
                    os.chmod(file_path, stat.S_IWRITE)
                except:
                    pass
            
            # 刪除檔案
            file_path.unlink()
            return True
            
        except Exception as e:
            self.logger.error(f"永久刪除檔案失敗：{e}")
            return False
    
    def process_file(self, file_info: Dict) -> bool:
        """
        根據設定處理檔案（歸檔、回收站或永久刪除）
        
        Args:
            file_info: 檔案資訊字典
            
        Returns:
            bool: 是否成功處理
        """
        if self.use_archive:
            return self.archive_file(file_info)
        elif self.use_recycle_bin:
            return self.move_to_recycle_bin(file_info)
        else:
            return self.delete_file_permanently(file_info)
    
    def cleanup_files(self, folder_path: str, days_to_keep: int, include_subfolders: bool = True, dry_run: bool = False) -> Dict:
        """
        清理過期檔案
        
        Args:
            folder_path: 資料夾路徑
            days_to_keep: 保留天數
            include_subfolders: 是否包含子資料夾
            dry_run: 是否為預覽模式（不實際刪除）
            
        Returns:
            Dict: 清理結果統計
        """
        start_time = datetime.now()
        
        try:
            # 驗證路徑
            validated_path = self.validate_path(folder_path)
            
            # 清空統計變數
            self.deleted_files = []
            self.failed_deletions = []
            self.total_size_freed = 0
            
            # 找出過期檔案
            expired_files = self.find_expired_files(validated_path, days_to_keep, include_subfolders)
            
            if not expired_files:
                self.logger.info("沒有找到需要清理的檔案")
                return {
                    'total_found': 0,
                    'successfully_deleted': 0,
                    'failed_deletions': 0,
                    'total_size_freed': 0,
                    'execution_time': (datetime.now() - start_time).total_seconds()
                }
            
            self.logger.info(f"找到 {len(expired_files)} 個過期檔案")
            
            # 處理檔案
            successfully_processed = 0
            failed_count = 0
            
            for file_info in expired_files:
                file_path = file_info['path']
                file_size = file_info['size']
                
                if dry_run:
                    # 預覽模式，只記錄不實際處理
                    self.deleted_files.append(str(file_path))
                    self.total_size_freed += file_size
                    successfully_processed += 1
                    self.logger.debug(f"預覽：{file_path} ({self.format_size(file_size)})")
                else:
                    # 實際處理檔案
                    if not file_info['can_delete']:
                        self.logger.warning(f"檔案被鎖定，跳過：{file_path}")
                        self.failed_deletions.append(str(file_path))
                        failed_count += 1
                        continue
                    
                    if self.process_file(file_info):
                        self.deleted_files.append(str(file_path))
                        self.total_size_freed += file_size
                        successfully_processed += 1
                        self.logger.info(f"已處理：{file_path} ({self.format_size(file_size)})")
                    else:
                        self.failed_deletions.append(str(file_path))
                        failed_count += 1
                        self.logger.error(f"處理失敗：{file_path}")
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # 記錄統計結果
            mode_text = "壓縮歸檔" if self.use_archive else ("回收站" if self.use_recycle_bin else "永久刪除")
            if not dry_run:
                self.logger.info(f"清理完成！{mode_text} {successfully_processed} 個檔案，"
                               f"失敗 {failed_count} 個，"
                               f"釋放空間 {self.format_size(self.total_size_freed)}，"
                               f"耗時 {execution_time:.2f} 秒")
            
            return {
                'total_found': len(expired_files),
                'successfully_deleted': successfully_processed,
                'failed_deletions': failed_count,
                'total_size_freed': self.total_size_freed,
                'execution_time': execution_time
            }
            
        except Exception as e:
            self.logger.error(f"清理過程中發生錯誤：{e}")
            return {
                'total_found': 0,
                'successfully_deleted': 0,
                'failed_deletions': 0,
                'total_size_freed': 0,
                'execution_time': (datetime.now() - start_time).total_seconds(),
                'error': str(e)
            }
    
    def print_summary(self, result: Dict, use_recycle_bin: bool, use_archive: bool, mode: str = "safe"):
        """列印清理結果摘要"""
        print("\n" + "="*60)
        print("📋 清理結果摘要")
        print("="*60)
        
        if 'error' in result:
            print(f"❌ 清理過程中發生錯誤：{result['error']}")
            return
        
        print(f"📁 找到檔案：{result['total_found']} 個")
        
        if use_archive:
            print(f"📦 成功歸檔：{result['successfully_deleted']} 個")
            print(f"📂 歸檔位置：{self.archive_folder.absolute()}")
        elif use_recycle_bin:
            if mode == "smart":
                print(f"🧠 智能處理：{result['successfully_deleted']} 個")
            else:
                print(f"♻️  移至回收站：{result['successfully_deleted']} 個")
            print(f"📂 回收站位置：{self.recycle_bin.absolute()}")
        else:
            print(f"🗑️  永久刪除：{result['successfully_deleted']} 個")
        
        if result['failed_deletions'] > 0:
            print(f"❌ 處理失敗：{result['failed_deletions']} 個")
        
        print(f"💾 釋放空間：{self.format_size(result['total_size_freed'])}")
        print(f"⏱️  執行時間：{result['execution_time']:.2f} 秒")
        print("="*60)


def select_folder_simple():
    """簡單的資料夾選擇，適用於 EXE"""
    print("\n請選擇要清理的資料夾：")
    print("1. 手動輸入路徑")
    print("2. 選擇常用位置")
    
    while True:
        choice = input("請選擇 (1-2): ").strip()
        if choice == "1":
            path = input("請輸入資料夾路徑: ").strip().strip('"')
            if path:
                return path
        elif choice == "2":
            print("\n常用位置：")
            home = Path.home()
            common_folders = [
                str(home / "Downloads"),
                str(home / "Documents"),
                str(home / "Desktop"),
                str(home / "Pictures"),
                "C:\\Windows\\Temp",
                "C:\\Temp"
            ]
            
            for i, folder in enumerate(common_folders, 1):
                exists = "✓" if Path(folder).exists() else "✗"
                print(f"{i}. {folder} {exists}")
            
            try:
                folder_choice = int(input("請選擇資料夾 (1-6): ").strip())
                if 1 <= folder_choice <= len(common_folders):
                    return common_folders[folder_choice - 1]
            except ValueError:
                pass
        
        print("請輸入有效選項")


def get_user_input(use_recycle_bin: bool = True) -> Tuple[str, int, bool, str, bool, bool]:
    """
    獲取使用者輸入（EXE 優化版本）
    
    Returns:
        Tuple: (資料夾路徑, 保留天數, 包含子資料夾, 模式, 使用回收站, 使用歸檔)
    """
    print("🗂️  檔案清理工具 - 設定精靈")
    print("="*50)
    
    # 選擇資料夾
    folder_path = select_folder_simple()
    
    # 驗證路徑
    while True:
        try:
            test_path = Path(folder_path)
            if not test_path.exists():
                print(f"❌ 資料夾不存在：{folder_path}")
                folder_path = select_folder_simple()
                continue
            if not test_path.is_dir():
                print(f"❌ 指定的路徑不是資料夾：{folder_path}")
                folder_path = select_folder_simple()
                continue
            break
        except Exception as e:
            print(f"❌ 路徑無效：{e}")
            folder_path = select_folder_simple()
    
    # 保留天數
    while True:
        try:
            days_input = input("\n請輸入要保留的天數 (例如：30): ").strip()
            days = int(days_input)
            if days < 0:
                print("❌ 天數不能為負數")
                continue
            break
        except ValueError:
            print("❌ 請輸入有效的數字")
    
    # 是否包含子資料夾
    while True:
        subfolder_choice = input("\n是否包含子資料夾？(y/n，預設 y): ").strip().lower()
        if subfolder_choice in ['y', 'yes', '是', '']:
            include_subfolders = True
            break
        elif subfolder_choice in ['n', 'no', '否']:
            include_subfolders = False
            break
        else:
            print("請輸入 y 或 n")
    
    # 選擇清理模式
    print("\n請選擇清理模式：")
    print("1. 🗜️  壓縮歸檔 (節省空間，可恢復) 【推薦】")
    print("2. ♻️  回收站 (安全，可恢復)")
    print("3. 🗑️  永久刪除 (立即釋放空間)")
    
    while True:
        mode_choice = input("請選擇模式 (1-3，預設 1): ").strip()
        if mode_choice in ['1', '']:
            mode = "archive"
            use_recycle_bin = False
            use_archive = True
            break
        elif mode_choice == '2':
            mode = "safe"
            use_recycle_bin = True
            use_archive = False
            break
        elif mode_choice == '3':
            mode = "permanent"
            use_recycle_bin = False
            use_archive = False
            # 二次確認
            while True:
                confirm = input("⚠️  永久刪除無法恢復，確定要使用此模式嗎？(y/n): ").strip().lower()
                if confirm in ['y', 'yes', '是']:
                    break
                elif confirm in ['n', 'no', '否']:
                    print("已取消，請重新選擇模式")
                    mode_choice = None
                    break
                else:
                    print("請輸入 y 或 n")
            if mode_choice is None:
                continue
            break
        else:
            print("請輸入 1、2 或 3")
    
    return folder_path, days, include_subfolders, mode, use_recycle_bin, use_archive


def main():
    """主程式"""
    try:
        # 解析命令列參數
        parser = argparse.ArgumentParser(description='檔案自動清理工具 - EXE 優化版本')
        parser.add_argument('--path', '-p', help='資料夾路徑')
        parser.add_argument('--days', '-d', type=int, help='保留天數')
        parser.add_argument('--no-subfolders', action='store_true', help='不包含子資料夾')
        parser.add_argument('--no-preview', action='store_true', help='跳過預覽，直接執行')
        parser.add_argument('--no-recycle-bin', action='store_true', help='直接刪除，不使用回收站')
        parser.add_argument('--archive', action='store_true', help='使用壓縮歸檔模式')
        parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                           default='INFO', help='日誌級別')
        
        args = parser.parse_args()
        
        # 獲取參數
        if args.path and args.days is not None:
            folder_path = args.path
            days = args.days
            include_subfolders = not args.no_subfolders
            use_recycle_bin = not args.no_recycle_bin and not args.archive
            use_archive = args.archive
            if args.archive:
                mode = "archive"
            elif args.no_recycle_bin:
                mode = "permanent"
            else:
                mode = "safe"
        else:
            # 先創建臨時清理工具來顯示初始信息
            temp_use_recycle_bin = not args.no_recycle_bin and not args.archive
            temp_use_archive = args.archive
            if temp_use_archive:
                print("📦 使用壓縮歸檔模式 - 檔案將被壓縮存檔，節省空間且可恢復")
            elif temp_use_recycle_bin:
                print("📦 使用回收站模式 - 檔案將被移動到回收站，可以恢復")
            else:
                print("⚠️  直接刪除模式 - 檔案將被永久刪除，無法恢復")
            
            folder_path, days, include_subfolders, mode, use_recycle_bin, use_archive = get_user_input(temp_use_recycle_bin)
        
        # 根據最終參數創建清理工具
        cleaner = FileCleanupTool(args.log_level, use_recycle_bin, use_archive)
        
        # 顯示選擇的模式
        if use_archive:
            print("📦 壓縮歸檔模式 - 檔案將被壓縮存檔，節省空間且可恢復")
            print(f"   歸檔位置：{cleaner.archive_folder.absolute()}")
        elif use_recycle_bin:
            if mode == "smart":
                print("🧠 智能模式 - 先移到回收站，稍後可選擇永久刪除")
            else:
                print("📦 安全模式 - 檔案將被移動到回收站，可以恢復")
            print(f"   回收站位置：{cleaner.recycle_bin.absolute()}")
        else:
            print("⚠️  釋放空間模式 - 檔案將被永久刪除，立即釋放空間")
        
        # 執行預覽
        print("\n正在掃描檔案...")
        preview_result = cleaner.cleanup_files(
            folder_path, days, include_subfolders, dry_run=True
        )
        
        cleaner.print_summary(preview_result, use_recycle_bin, use_archive, mode)
        
        # 如果有檔案要刪除且不是 no-preview 模式
        if preview_result['total_found'] > 0 and not args.no_preview:
            if use_archive:
                action_text = "壓縮歸檔"
                space_info = "（壓縮存檔，節省空間）"
            elif use_recycle_bin:
                action_text = "移動到回收站"
                space_info = "（仍占用空間，但可恢復）"
            else:
                action_text = "永久刪除"
                space_info = "（立即釋放空間，無法恢復）"
            
            # 計算總大小
            total_size = 0
            expired_files = cleaner.find_expired_files(
                cleaner.validate_path(folder_path), days, include_subfolders
            )
            for file_info in expired_files:
                total_size += file_info['size']
            
            while True:
                confirm = input(f"\n確定要{action_text}這 {preview_result['total_found']} 個檔案嗎？{space_info} (y/n): ").strip().lower()
                if confirm in ['y', 'yes', '是']:
                    break
                elif confirm in ['n', 'no', '否']:
                    print("操作已取消")
                    return
                else:
                    print("請輸入 y 或 n")
        
        # 執行實際清理
        if preview_result['total_found'] > 0:
            print("\n開始實際清理...")
            actual_result = cleaner.cleanup_files(
                folder_path, days, include_subfolders, dry_run=False
            )
            cleaner.print_summary(actual_result, use_recycle_bin, use_archive, mode)
            
            # 提示管理工具
            if use_archive and actual_result['successfully_deleted'] > 0:
                print(f"\n💡 提示：如需提取歸檔檔案，請執行：python file_archive_manager.py")
                print(f"📂 歸檔位置：{cleaner.archive_folder.absolute()}")
            elif use_recycle_bin and actual_result['successfully_deleted'] > 0 and mode != "smart":
                print(f"\n💡 提示：如需管理回收站檔案，請執行：python file_recovery.py")
                print(f"📂 回收站位置：{cleaner.recycle_bin.absolute()}")
        
        # 暫停讓用戶看到結果（EXE 模式下很重要）
        if getattr(sys, 'frozen', False):
            input("\n按 Enter 鍵退出...")
        
    except KeyboardInterrupt:
        print("\n\n操作已被使用者中斷")
    except Exception as e:
        print(f"\n程式執行時發生錯誤：{e}")
        if getattr(sys, 'frozen', False):
            input("\n按 Enter 鍵退出...")
        sys.exit(1)


if __name__ == "__main__":
    main()
