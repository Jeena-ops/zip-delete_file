#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檔案自動清理工具
功能：根據設定的保留天數自動清理過期檔案
支援：Windows 平台，完整的日誌記錄和錯誤處理
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
        # 創建日誌資料夾
        log_folder = Path("logs")
        log_folder.mkdir(exist_ok=True)
        
        # 日誌檔案名稱包含日期
        log_file = log_folder / f"file_cleanup_{datetime.now().strftime('%Y%m%d')}.log"
        
        # 設定日誌格式
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        
        # 設定日誌處理器
        handlers = [
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
        
        # 配置日誌
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format=log_format,
            handlers=handlers,
            force=True
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("檔案清理工具初始化完成")
    
    def setup_recycle_bin(self):
        """設定回收站"""
        self.recycle_bin = Path("recycle_bin")
        self.recycle_bin.mkdir(exist_ok=True)
        self.recovery_log = self.recycle_bin / "recovery_log.json"
        self.logger.info(f"回收站位置：{self.recycle_bin.absolute()}")
    
    def setup_archive(self):
        """設定壓縮歸檔"""
        self.archive_folder = Path("archived_files")
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
                raise ValueError(f"路徑不是資料夾：{folder_path}")
            
            # 檢查讀取權限
            if not os.access(folder_path, os.R_OK):
                raise ValueError(f"無法讀取資料夾：{folder_path}")
            
            # 檢查寫入權限（刪除檔案需要）
            if not os.access(folder_path, os.W_OK):
                raise ValueError(f"無法寫入資料夾：{folder_path}")
            
            return folder_path
            
        except Exception as e:
            self.logger.error(f"路徑驗證失敗：{e}")
            raise
    
    def validate_days(self, days: str) -> int:
        """
        驗證保留天數
        
        Args:
            days: 天數字串
            
        Returns:
            int: 驗證後的天數
            
        Raises:
            ValueError: 天數無效時拋出異常
        """
        try:
            days_int = int(days)
            
            if days_int < 0:
                raise ValueError("保留天數不能為負數")
            
            if days_int > 3650:  # 約10年
                raise ValueError("保留天數不能超過3650天")
            
            return days_int
            
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError("請輸入有效的數字")
            raise
    
    def get_file_info(self, file_path: Path) -> Dict:
        """
        獲取檔案詳細資訊
        
        Args:
            file_path: 檔案路徑
            
        Returns:
            Dict: 檔案資訊字典
        """
        try:
            stat_info = file_path.stat()
            
            return {
                'path': file_path,
                'size': stat_info.st_size,
                'modified_time': datetime.fromtimestamp(stat_info.st_mtime),
                'access_time': datetime.fromtimestamp(stat_info.st_atime),
                'created_time': datetime.fromtimestamp(stat_info.st_ctime),
                'is_readonly': bool(stat_info.st_mode & stat.S_IREAD and not stat_info.st_mode & stat.S_IWRITE)
            }
        except Exception as e:
            self.logger.warning(f"無法獲取檔案資訊：{file_path} - {e}")
            return None
    
    def format_file_size(self, size_bytes: int) -> str:
        """
        格式化檔案大小
        
        Args:
            size_bytes: 檔案大小（位元組）
            
        Returns:
            str: 格式化後的大小字串
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def find_expired_files(self, folder_path: Path, days_to_keep: int, 
                          include_subfolders: bool = True) -> List[Dict]:
        """
        查找過期檔案
        
        Args:
            folder_path: 要掃描的資料夾
            days_to_keep: 保留天數
            include_subfolders: 是否包含子資料夾
            
        Returns:
            List[Dict]: 過期檔案列表
        """
        expired_files = []
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        self.logger.info(f"開始掃描資料夾：{folder_path}")
        self.logger.info(f"刪除標準：{cutoff_date.strftime('%Y-%m-%d %H:%M:%S')} 之前的檔案")
        
        try:
            # 選擇掃描模式
            if include_subfolders:
                file_pattern = "**/*"
                scan_mode = "遞歸掃描"
            else:
                file_pattern = "*"
                scan_mode = "單層掃描"
            
            self.logger.info(f"掃描模式：{scan_mode}")
            
            # 掃描檔案
            for item in folder_path.glob(file_pattern):
                if item.is_file():
                    file_info = self.get_file_info(item)
                    
                    if file_info and file_info['modified_time'] < cutoff_date:
                        expired_files.append(file_info)
                        self.logger.debug(f"發現過期檔案：{item} (修改時間：{file_info['modified_time']})")
            
            self.logger.info(f"掃描完成，發現 {len(expired_files)} 個過期檔案")
            return expired_files
            
        except Exception as e:
            self.logger.error(f"掃描資料夾時發生錯誤：{e}")
            raise
    
    def remove_readonly_attribute(self, file_path: Path) -> bool:
        """
        移除檔案的唯讀屬性（Windows 專用）
        
        Args:
            file_path: 檔案路徑
            
        Returns:
            bool: 是否成功移除唯讀屬性
        """
        try:
            if sys.platform.startswith('win'):
                # Windows 系統移除唯讀屬性
                current_attrs = file_path.stat().st_mode
                file_path.chmod(current_attrs | stat.S_IWRITE)
                return True
            return True
        except Exception as e:
            self.logger.warning(f"無法移除唯讀屬性：{file_path} - {e}")
            return False
    
    def delete_file_safely(self, file_info: Dict) -> bool:
        """
        安全地刪除檔案
        
        Args:
            file_info: 檔案資訊字典
            
        Returns:
            bool: 是否成功刪除
        """
        file_path = file_info['path']
        
        try:
            # 如果是唯讀檔案，先移除唯讀屬性
            if file_info.get('is_readonly', False):
                if not self.remove_readonly_attribute(file_path):
                    raise PermissionError("無法移除唯讀屬性")
            
            if self.use_archive:
                # 壓縮歸檔檔案
                success = self.archive_file(file_info)
                if not success:
                    raise Exception("壓縮歸檔失敗")
                action_text = "已壓縮歸檔"
            elif self.use_recycle_bin:
                # 移動到回收站
                success = self.move_to_recycle_bin(file_info)
                if not success:
                    raise Exception("移動到回收站失敗")
                action_text = "已移至回收站"
            else:
                # 直接刪除檔案
                file_path.unlink()
                action_text = "已刪除"
            
            # 記錄成功刪除
            self.deleted_files.append(file_info)
            self.total_size_freed += file_info['size']
            
            self.logger.info(f"{action_text}：{file_path} ({self.format_file_size(file_info['size'])})")
            return True
            
        except PermissionError as e:
            self.logger.error(f"權限不足，無法刪除：{file_path} - {e}")
            self.failed_deletions.append({'file': file_info, 'error': str(e)})
            return False
        except FileNotFoundError:
            self.logger.warning(f"檔案已不存在：{file_path}")
            return False
        except Exception as e:
            self.logger.error(f"刪除檔案時發生錯誤：{file_path} - {e}")
            self.failed_deletions.append({'file': file_info, 'error': str(e)})
            return False
    
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
            
            # 在壓縮檔內的路徑（保持原始目錄結構）
            relative_path = str(original_path.relative_to(original_path.anchor))
            
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
            
            # 生成唯一檔案ID
            file_id = f"{deleted_time.strftime('%Y%m%d_%H%M%S_%f')}_{original_path.name}"
            recycle_path = self.recycle_bin / file_id
            
            # 移動檔案
            shutil.move(str(original_path), str(recycle_path))
            
            # 記錄到恢復日誌
            log_data = self.load_recovery_log()
            log_entry = {
                "file_id": file_id,
                "original_path": str(original_path),
                "recycle_path": str(recycle_path),
                "file_size": file_info['size'],
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
    
    def cleanup_files(self, folder_path: str, days_to_keep: int, 
                     include_subfolders: bool = True, 
                     dry_run: bool = True) -> Dict:
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
        try:
            # 重置統計
            self.deleted_files = []
            self.failed_deletions = []
            self.total_size_freed = 0
            
            # 驗證輸入
            validated_path = self.validate_path(folder_path)
            validated_days = self.validate_days(str(days_to_keep))
            
            mode = "預覽模式" if dry_run else "實際清理"
            self.logger.info(f"開始檔案清理 - {mode}")
            self.logger.info(f"目標資料夾：{validated_path}")
            self.logger.info(f"保留天數：{validated_days} 天")
            
            # 查找過期檔案
            expired_files = self.find_expired_files(
                validated_path, 
                validated_days, 
                include_subfolders
            )
            
            if not expired_files:
                self.logger.info("沒有發現需要清理的檔案")
                return self._generate_result_summary(expired_files, dry_run)
            
            # 顯示將要刪除的檔案
            self._display_files_to_delete(expired_files, dry_run)
            
            # 執行刪除（如果不是預覽模式）
            if not dry_run:
                self._execute_deletion(expired_files)
            
            # 生成結果報告
            return self._generate_result_summary(expired_files, dry_run)
            
        except Exception as e:
            self.logger.error(f"清理過程中發生錯誤：{e}")
            raise
    
    def _display_files_to_delete(self, expired_files: List[Dict], dry_run: bool):
        """顯示將要刪除的檔案列表"""
        action = "將要刪除" if not dry_run else "預覽刪除"
        
        print(f"\n{action}的檔案列表：")
        print("=" * 80)
        print(f"{'檔案路徑':<50} {'大小':<10} {'修改時間':<20}")
        print("-" * 80)
        
        total_size = 0
        for file_info in expired_files:
            file_path = file_info['path']
            file_size = self.format_file_size(file_info['size'])
            modified_time = file_info['modified_time'].strftime('%Y-%m-%d %H:%M:%S')
            
            # 截斷過長的路徑
            display_path = str(file_path)
            if len(display_path) > 47:
                display_path = "..." + display_path[-44:]
            
            print(f"{display_path:<50} {file_size:<10} {modified_time:<20}")
            total_size += file_info['size']
        
        print("-" * 80)
        print(f"總計：{len(expired_files)} 個檔案，{self.format_file_size(total_size)}")
        print("=" * 80)
    
    def _execute_deletion(self, expired_files: List[Dict]):
        """執行檔案刪除"""
        self.logger.info(f"開始刪除 {len(expired_files)} 個檔案...")
        
        success_count = 0
        for i, file_info in enumerate(expired_files, 1):
            print(f"正在刪除 ({i}/{len(expired_files)}): {file_info['path'].name}")
            
            if self.delete_file_safely(file_info):
                success_count += 1
        
        self.logger.info(f"刪除完成：成功 {success_count} 個，失敗 {len(self.failed_deletions)} 個")
    
    def _generate_result_summary(self, expired_files: List[Dict], dry_run: bool) -> Dict:
        """生成結果摘要"""
        return {
            'mode': '預覽模式' if dry_run else '實際清理',
            'total_found': len(expired_files),
            'successfully_deleted': len(self.deleted_files),
            'failed_deletions': len(self.failed_deletions),
            'total_size_freed': self.total_size_freed,
            'deleted_files': self.deleted_files,
            'failed_files': self.failed_deletions
        }
    
    def print_summary(self, result: Dict, use_recycle_bin: bool = True, use_archive: bool = False, mode: str = "safe"):
        """列印清理結果摘要"""
        if use_archive:
            action_text = "壓縮歸檔"
        elif use_recycle_bin:
            action_text = "移至回收站"
        else:
            action_text = "永久刪除"
        
        print(f"\n清理結果摘要 ({result['mode']})：")
        print("=" * 50)
        print(f"發現過期檔案：{result['total_found']} 個")
        
        if result['mode'] == '實際清理':
            print(f"成功{action_text}：{result['successfully_deleted']} 個")
            print(f"{action_text}失敗：{result['failed_deletions']} 個")
            
            if use_archive:
                # 計算壓縮比例
                if result['total_size_freed'] > 0:
                    # 獲取今日歸檔檔案大小
                    today = datetime.now().strftime('%Y%m%d')
                    archive_name = f"archived_files_{today}.zip"
                    archive_path = self.archive_folder / archive_name
                    if archive_path.exists():
                        compressed_size = archive_path.stat().st_size
                        compression_ratio = (1 - compressed_size / result['total_size_freed']) * 100
                        print(f"原始大小：{self.format_file_size(result['total_size_freed'])}")
                        print(f"壓縮後大小：{self.format_file_size(compressed_size)}")
                        print(f"節省空間：{compression_ratio:.1f}%")
                        print(f"📦 歸檔位置：{archive_path}")
                print("💡 提示：檔案已壓縮歸檔，既節省空間又可以恢復")
            elif use_recycle_bin:
                print(f"暫時占用空間：{self.format_file_size(result['total_size_freed'])}")
                print("💡 提示：這些檔案仍在回收站中，稍後可以永久刪除以釋放空間")
            else:
                print(f"已釋放空間：{self.format_file_size(result['total_size_freed'])}")
            
            if result['failed_files']:
                print(f"\n{action_text}失敗的檔案：")
                for failed in result['failed_files']:
                    print(f"  - {failed['file']['path']}: {failed['error']}")
        
        print("=" * 50)
        
        # 智能模式的額外提示
        if mode == "smart" and use_recycle_bin and result['mode'] == '實際清理' and result['successfully_deleted'] > 0:
            self.show_smart_mode_options(result)
    
    def show_smart_mode_options(self, result: Dict):
        """顯示智能模式的後續選項"""
        print(f"\n🧠 智能模式後續選項：")
        print(f"檔案已移動到回收站，當前占用空間：{self.format_file_size(result['total_size_freed'])}")
        print()
        print("您現在可以選擇：")
        print("1. 保留在回收站（可隨時恢復）")
        print("2. 立即永久刪除（釋放磁碟空間）")
        print("3. 稍後決定（使用恢復工具管理）")
        
        while True:
            choice = input("\n請選擇 (1-3) [預設: 3]: ").strip()
            if choice in ['', '3']:
                print("✅ 檔案保留在回收站，您可以稍後使用恢復工具管理")
                print(f"💡 執行 'python file_recovery.py' 來管理回收站檔案")
                break
            elif choice == '1':
                print("✅ 檔案將保留在回收站，可隨時恢復")
                break
            elif choice == '2':
                self.confirm_permanent_deletion(result)
                break
            else:
                print("無效選項，請輸入 1、2 或 3")
    
    def confirm_permanent_deletion(self, result: Dict):
        """確認永久刪除"""
        print(f"\n⚠️  永久刪除確認")
        print(f"這將永久刪除 {result['successfully_deleted']} 個檔案")
        print(f"釋放磁碟空間：{self.format_file_size(result['total_size_freed'])}")
        print("此操作無法復原！")
        
        confirm = input("\n確定要永久刪除這些檔案嗎？ (yes/no): ").strip().lower()
        if confirm in ['yes', 'y', '確定']:
            success_count = self.permanently_delete_recent_files()
            print(f"✅ 已永久刪除 {success_count} 個檔案")
            print(f"💾 成功釋放磁碟空間：{self.format_file_size(result['total_size_freed'])}")
        else:
            print("❌ 已取消永久刪除，檔案保留在回收站")
    
    def permanently_delete_recent_files(self) -> int:
        """永久刪除最近移動到回收站的檔案"""
        log_data = self.load_recovery_log()
        success_count = 0
        current_time = datetime.now()
        
        # 找出最近5分鐘內移動到回收站的檔案
        recent_files = []
        for entry in log_data:
            if not entry.get("recovered", False) and not entry.get("permanently_deleted", False):
                deleted_time = datetime.fromisoformat(entry["deleted_time"])
                time_diff = current_time - deleted_time
                if time_diff.total_seconds() <= 300:  # 5分鐘內
                    recent_files.append(entry)
        
        # 永久刪除這些檔案
        for entry in recent_files:
            try:
                recycle_path = Path(entry["recycle_path"])
                if recycle_path.exists():
                    recycle_path.unlink()
                    success_count += 1
                
                # 標記為永久刪除
                entry["permanently_deleted"] = True
                entry["permanent_delete_time"] = current_time.isoformat()
                
            except Exception as e:
                self.logger.error(f"永久刪除失敗：{entry['recycle_path']} - {e}")
        
        # 更新日誌
        self.save_recovery_log(log_data)
        return success_count


def get_user_input(use_recycle_bin: bool = True):
    """獲取使用者輸入"""
    print("檔案自動清理工具 v3.1")
    print("=" * 50)
    
    # 讓用戶選擇清理模式
    print("請選擇清理模式：")
    print("1. 安全模式 - 移動到回收站（可恢復，但仍占用空間）")
    print("2. 釋放空間模式 - 永久刪除（立即釋放空間，無法恢復）")
    print("3. 智能模式 - 先移到回收站，稍後可選擇永久刪除")
    print("4. 壓縮歸檔模式 - 壓縮存檔（節省空間且可恢復）")
    
    while True:
        choice = input("\n請選擇模式 (1-4) [預設: 4]: ").strip()
        if choice in ['', '4']:
            mode = "archive"
            use_recycle_bin = False
            use_archive = True
            print("📦 已選擇壓縮歸檔模式 - 檔案將被壓縮存檔，節省空間且可恢復")
            break
        elif choice == '1':
            mode = "safe"
            use_recycle_bin = True
            use_archive = False
            print("✅ 已選擇安全模式 - 檔案將移動到回收站")
            break
        elif choice == '2':
            mode = "permanent"
            use_recycle_bin = False
            use_archive = False
            print("⚠️  已選擇釋放空間模式 - 檔案將被永久刪除")
            print("   注意：這將立即釋放磁碟空間，但檔案無法恢復！")
            break
        elif choice == '3':
            mode = "smart"
            use_recycle_bin = True
            use_archive = False
            print("🧠 已選擇智能模式 - 先移到回收站，稍後可清理回收站")
            break
        else:
            print("無效選項，請輸入 1、2、3 或 4")
    
    print()
    
    while True:
        folder_path = input("請輸入要清理的資料夾路徑: ").strip().strip('"')
        if folder_path:
            break
        print("資料夾路徑不能為空，請重新輸入")
    
    while True:
        try:
            days_input = input("請輸入保留天數 (超過此天數的檔案將被清理): ").strip()
            days = int(days_input)
            if days < 0:
                print("保留天數不能為負數，請重新輸入")
                continue
            break
        except ValueError:
            print("請輸入有效的數字")
    
    while True:
        include_sub = input("是否包含子資料夾? (y/n) [預設: y]: ").strip().lower()
        if include_sub in ['', 'y', 'yes', '是']:
            include_subfolders = True
            break
        elif include_sub in ['n', 'no', '否']:
            include_subfolders = False
            break
        else:
            print("請輸入 y 或 n")
    
    return folder_path, days, include_subfolders, mode, use_recycle_bin, use_archive


def main():
    """主程式"""
    try:
        # 解析命令列參數
        parser = argparse.ArgumentParser(description='檔案自動清理工具')
        parser.add_argument('--path', '-p', help='資料夾路徑')
        parser.add_argument('--days', '-d', type=int, help='保留天數')
        parser.add_argument('--no-subfolders', action='store_true', help='不包含子資料夾')
        parser.add_argument('--no-preview', action='store_true', help='跳過預覽，直接執行')
        parser.add_argument('--no-recycle-bin', action='store_true', help='直接刪除，不使用回收站')
        parser.add_argument('--archive', action='store_true', help='使用壓縮歸檔模式')
        parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                           default='INFO', help='日誌級別')
        
        args = parser.parse_args()
        
        # 創建清理工具
        use_recycle_bin = not args.no_recycle_bin and not args.archive
        use_archive = args.archive
        cleaner = FileCleanupTool(args.log_level, use_recycle_bin, use_archive)
        
        if use_archive:
            print("📦 使用壓縮歸檔模式 - 檔案將被壓縮存檔，節省空間且可恢復")
            print(f"   歸檔位置：{cleaner.archive_folder.absolute()}")
        elif use_recycle_bin:
            print("📦 使用回收站模式 - 檔案將被移動到回收站，可以恢復")
            print(f"   回收站位置：{cleaner.recycle_bin.absolute()}")
        else:
            print("⚠️  直接刪除模式 - 檔案將被永久刪除，無法恢復")
        
        # 獲取參數
        if args.path and args.days is not None:
            folder_path = args.path
            days = args.days
            include_subfolders = not args.no_subfolders
            if args.archive:
                mode = "archive"
            elif args.no_recycle_bin:
                mode = "permanent"
            else:
                mode = "safe"
        else:
            folder_path, days, include_subfolders, mode, use_recycle_bin, use_archive = get_user_input(use_recycle_bin)
        
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
            elif use_recycle_bin and actual_result['successfully_deleted'] > 0 and mode != "smart":
                print(f"\n💡 提示：如需管理回收站檔案，請執行：python file_recovery.py")
        
    except KeyboardInterrupt:
        print("\n\n操作已被使用者中斷")
    except Exception as e:
        print(f"\n程式執行時發生錯誤：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
