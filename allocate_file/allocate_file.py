#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檔案自動分類整理工具
功能：監控指定資料夾，根據檔名自動分類並移動檔案到對應子資料夾
"""

import os
import re
import json
import time
import shutil
import logging
import schedule
import threading
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class FileAllocator:
    """檔案自動分配器 - 智能學習版本"""
    
    def __init__(self, 
                 watch_folder: str = "Downloads",
                 target_folder: str = "OrganizedFiles",
                 separator: str = "_",
                 supported_extensions: List[str] = None):
        """
        初始化檔案分配器
        
        Args:
            watch_folder: 監控的資料夾路徑
            target_folder: 整理後的目標資料夾
            separator: 檔名中的分隔符
            supported_extensions: 支援的檔案副檔名
        """
        self.watch_folder = Path(watch_folder).resolve()
        self.target_folder = Path(target_folder).resolve()
        self.separator = separator
        
        # 預設支援的檔案類型
        if supported_extensions is None:
            self.supported_extensions = {
                '.pdf', '.docx', '.xlsx', '.pptx', '.txt', '.doc', '.xls', '.ppt',
                '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',
                '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv',
                '.mp3', '.wav', '.flac', '.aac', '.ogg',
                '.zip', '.rar', '.7z', '.tar', '.gz'
            }
        else:
            self.supported_extensions = {ext.lower() for ext in supported_extensions}
        
        # 格式學習系統
        self.patterns_file = Path("learned_patterns.json")
        self.learned_patterns = self.load_learned_patterns()
        self.unknown_patterns = {}  # 記錄未知格式
        
        # 設定日誌
        self.setup_logging()
        
        # 確保目標資料夾存在
        self.target_folder.mkdir(parents=True, exist_ok=True)
        
        # 檔案監控器
        self.observer = None
        self.is_running = False
        
    def setup_logging(self):
        """設定日誌系統"""
        log_folder = Path("logs")
        log_folder.mkdir(exist_ok=True)
        
        log_file = log_folder / f"file_allocator_{datetime.now().strftime('%Y%m')}.log"
        
        # 設定日誌格式
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("檔案分配器初始化完成")
        
    def load_learned_patterns(self) -> Dict[str, Dict]:
        """載入已學習的檔案格式模式"""
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"載入格式模式失敗：{e}")
                return {}
        return {}
    
    def save_learned_patterns(self):
        """保存已學習的格式模式"""
        try:
            with open(self.patterns_file, 'w', encoding='utf-8') as f:
                json.dump(self.learned_patterns, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存格式模式失敗：{e}")
    
    def analyze_filename_pattern(self, filename: str) -> Dict[str, any]:
        """
        分析檔名模式
        
        Args:
            filename: 檔案名稱
            
        Returns:
            分析結果字典
        """
        name_without_ext = Path(filename).stem
        parts = name_without_ext.split(self.separator)
        
        pattern_info = {
            'original_filename': filename,
            'parts_count': len(parts),
            'parts': parts,
            'pattern_signature': self.get_pattern_signature(parts),
            'suggested_structure': self.suggest_folder_structure(parts)
        }
        
        return pattern_info
    
    def get_pattern_signature(self, parts: List[str]) -> str:
        """
        獲取檔名模式簽名（用於識別相似格式）
        
        Args:
            parts: 檔名分割部分
            
        Returns:
            模式簽名
        """
        signature_parts = []
        
        for part in parts:
            if re.match(r'^\d{4}$', part):  # 四位數字（年份）
                signature_parts.append('YYYY')
            elif re.match(r'^\d{6}$', part):  # 六位數字（日期）
                signature_parts.append('YYYYMM')
            elif re.match(r'^\d{8}$', part):  # 八位數字（完整日期）
                signature_parts.append('YYYYMMDD')
            elif re.match(r'^\d+$', part):  # 純數字
                signature_parts.append('NUMBER')
            elif re.match(r'^[A-Za-z]+$', part):  # 純字母
                signature_parts.append('TEXT')
            elif re.match(r'^[A-Za-z0-9]+$', part):  # 字母數字混合
                signature_parts.append('ALPHANUMERIC')
            else:  # 其他混合格式
                signature_parts.append('MIXED')
        
        return self.separator.join(signature_parts)
    
    def suggest_folder_structure(self, parts: List[str]) -> List[str]:
        """
        建議資料夾結構
        
        Args:
            parts: 檔名分割部分
            
        Returns:
            建議的資料夾層級
        """
        if len(parts) < 2:
            return ["未分類"]
        
        # 基本策略：前面的部分作為分類，最後的部分作為檔名
        if len(parts) == 2:
            return [parts[0]]  # 只有一層分類
        elif len(parts) == 3:
            return parts[:2]   # 兩層分類
        else:
            # 超過3個部分，前面都作為分類
            return parts[:-1]
    
    def learn_new_pattern(self, filename: str, user_confirmed_structure: List[str] = None):
        """
        學習新的檔名模式
        
        Args:
            filename: 檔案名稱
            user_confirmed_structure: 使用者確認的資料夾結構
        """
        pattern_info = self.analyze_filename_pattern(filename)
        signature = pattern_info['pattern_signature']
        
        if user_confirmed_structure:
            # 使用者手動指定結構
            structure = user_confirmed_structure
        else:
            # 自動建議結構
            structure = pattern_info['suggested_structure']
        
        # 保存到學習模式
        if signature not in self.learned_patterns:
            self.learned_patterns[signature] = {
                'folder_structure': structure,
                'examples': [filename],
                'count': 1,
                'last_seen': datetime.now().isoformat()
            }
        else:
            # 更新現有模式
            self.learned_patterns[signature]['count'] += 1
            self.learned_patterns[signature]['last_seen'] = datetime.now().isoformat()
            if filename not in self.learned_patterns[signature]['examples']:
                self.learned_patterns[signature]['examples'].append(filename)
                # 保留最多10個範例
                if len(self.learned_patterns[signature]['examples']) > 10:
                    self.learned_patterns[signature]['examples'].pop(0)
        
        self.save_learned_patterns()
        self.logger.info(f"學習新模式：{signature} → {'/'.join(structure)}")
    
    def get_folder_structure_for_file(self, filename: str) -> Tuple[List[str], bool]:
        """
        根據已學習的模式獲取資料夾結構
        
        Args:
            filename: 檔案名稱
            
        Returns:
            (資料夾結構, 是否為已知模式)
        """
        pattern_info = self.analyze_filename_pattern(filename)
        signature = pattern_info['pattern_signature']
        
        if signature in self.learned_patterns:
            # 已知模式
            structure = self.learned_patterns[signature]['folder_structure']
            
            # 將模式中的部分替換為實際檔名中的部分
            parts = pattern_info['parts']
            actual_structure = []
            
            for i, folder_name in enumerate(structure):
                if i < len(parts):
                    actual_structure.append(self.clean_folder_name(parts[i]))
                else:
                    actual_structure.append(folder_name)
            
            return actual_structure, True
        else:
            # 未知模式，記錄並使用建議結構
            self.unknown_patterns[filename] = pattern_info
            suggested = pattern_info['suggested_structure']
            
            # 清理並返回建議結構
            actual_structure = []
            parts = pattern_info['parts']
            
            for i, folder_name in enumerate(suggested):
                if i < len(parts):
                    actual_structure.append(self.clean_folder_name(parts[i]))
                else:
                    actual_structure.append(folder_name)
            
            return actual_structure, False
        
    def parse_filename(self, filename: str) -> Tuple[List[str], str]:
        """
        解析檔名，提取分類資訊（使用智能學習）
        
        Args:
            filename: 檔案名稱（含副檔名）
            
        Returns:
            (分類路徑列表, 檔案名稱)
        """
        # 使用智能分析獲取資料夾結構
        folder_structure, is_known_pattern = self.get_folder_structure_for_file(filename)
        
        if not is_known_pattern:
            # 新模式，自動學習
            self.learn_new_pattern(filename)
            self.logger.info(f"發現新檔名模式：{filename}")
        
        # 移除副檔名重新構建檔名
        name_without_ext = Path(filename).stem
        extension = Path(filename).suffix
        parts = name_without_ext.split(self.separator)
        
        # 根據資料夾結構決定新檔名
        if len(parts) > len(folder_structure):
            # 剩餘部分作為檔名
            remaining_parts = parts[len(folder_structure):]
            new_filename = self.separator.join(remaining_parts) + extension
        else:
            # 使用原檔名
            new_filename = filename
            
        return folder_structure, new_filename
    
    def clean_folder_name(self, name: str) -> str:
        """
        清理資料夾名稱，移除非法字符
        
        Args:
            name: 原始名稱
            
        Returns:
            清理後的名稱
        """
        # Windows 非法字符
        illegal_chars = '<>:"/\\|?*'
        
        cleaned = name.strip()
        for char in illegal_chars:
            cleaned = cleaned.replace(char, '-')
        
        # 移除多餘空格和點
        cleaned = ' '.join(cleaned.split())
        cleaned = cleaned.strip('.')
        
        return cleaned if cleaned else "未知"
    
    def create_folder_structure(self, categories: List[str]) -> Path:
        """
        創建資料夾結構
        
        Args:
            categories: 分類列表
            
        Returns:
            目標資料夾路徑
        """
        target_path = self.target_folder
        
        for category in categories:
            target_path = target_path / category
            target_path.mkdir(parents=True, exist_ok=True)
        
        return target_path
    
    def move_file(self, source_path: Path) -> bool:
        """
        移動檔案到對應分類資料夾
        
        Args:
            source_path: 源檔案路徑
            
        Returns:
            是否成功移動
        """
        try:
            # 檢查檔案類型
            if source_path.suffix.lower() not in self.supported_extensions:
                self.logger.debug(f"不支援的檔案類型：{source_path.name}")
                return False
            
            # 解析檔名
            categories, new_filename = self.parse_filename(source_path.name)
            
            # 創建目標資料夾
            target_folder = self.create_folder_structure(categories)
            target_path = target_folder / new_filename
            
            # 處理檔名衝突
            if target_path.exists():
                base_name = target_path.stem
                extension = target_path.suffix
                counter = 1
                
                while target_path.exists():
                    new_name = f"{base_name}_{counter}{extension}"
                    target_path = target_folder / new_name
                    counter += 1
            
            # 移動檔案
            shutil.move(str(source_path), str(target_path))
            
            # 記錄日誌
            category_path = " > ".join(categories)
            pattern_info = self.analyze_filename_pattern(source_path.name)
            signature = pattern_info['pattern_signature']
            
            if signature in self.learned_patterns:
                self.logger.info(f"檔案移動成功（已知模式 {signature}）：{source_path.name} → {category_path}/{target_path.name}")
            else:
                self.logger.info(f"檔案移動成功（新模式 {signature}）：{source_path.name} → {category_path}/{target_path.name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"移動檔案失敗：{source_path.name} - {str(e)}")
            return False
    
    def scan_and_organize(self):
        """掃描監控資料夾並整理現有檔案"""
        if not self.watch_folder.exists():
            self.logger.error(f"監控資料夾不存在：{self.watch_folder}")
            return
        
        self.logger.info(f"開始掃描資料夾：{self.watch_folder}")
        
        # 獲取所有檔案
        files = [f for f in self.watch_folder.iterdir() if f.is_file()]
        
        if not files:
            self.logger.info("沒有找到需要整理的檔案")
            return
        
        success_count = 0
        total_count = len(files)
        
        for file_path in files:
            if self.move_file(file_path):
                success_count += 1
        
        self.logger.info(f"掃描完成：總計 {total_count} 個檔案，成功整理 {success_count} 個")
    
    def start_monitoring(self):
        """開始監控檔案系統"""
        if self.is_running:
            self.logger.warning("監控已在運行中")
            return
        
        if not self.watch_folder.exists():
            self.logger.error(f"監控資料夾不存在：{self.watch_folder}")
            return
        
        # 設定檔案系統事件處理器
        event_handler = FileEventHandler(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.watch_folder), recursive=False)
        
        # 啟動監控
        self.observer.start()
        self.is_running = True
        
        self.logger.info(f"開始監控資料夾：{self.watch_folder}")
        
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """停止監控"""
        if self.observer and self.is_running:
            self.observer.stop()
            self.observer.join()
            self.is_running = False
            self.logger.info("停止檔案監控")
    
    def schedule_daily_scan(self, hour: int = 2, minute: int = 0):
        """
        設定每日定時掃描
        
        Args:
            hour: 執行小時（24小時制）
            minute: 執行分鐘
        """
        schedule.clear()
        schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(self.scan_and_organize)
        
        self.logger.info(f"設定每日 {hour:02d}:{minute:02d} 自動掃描")
        
        # 在背景執行排程
        def run_schedule():
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # 每分鐘檢查一次
        
        schedule_thread = threading.Thread(target=run_schedule, daemon=True)
        schedule_thread.start()
    
    def show_learned_patterns(self):
        """顯示已學習的檔名模式"""
        if not self.learned_patterns:
            print("尚未學習任何檔名模式")
            return
        
        print("\n已學習的檔名模式：")
        print("=" * 60)
        
        for signature, info in self.learned_patterns.items():
            structure_path = " > ".join(info['folder_structure'])
            print(f"模式：{signature}")
            print(f"  資料夾結構：{structure_path}")
            print(f"  使用次數：{info['count']}")
            print(f"  最後使用：{info['last_seen'][:19]}")
            print(f"  範例檔案：{', '.join(info['examples'][:3])}...")
            print()
    
    def show_unknown_patterns(self):
        """顯示未知的檔名模式"""
        if not self.unknown_patterns:
            print("沒有發現未知模式")
            return
        
        print("\n發現的新檔名模式：")
        print("=" * 60)
        
        for filename, pattern_info in self.unknown_patterns.items():
            signature = pattern_info['pattern_signature']
            suggested = " > ".join(pattern_info['suggested_structure'])
            print(f"檔案：{filename}")
            print(f"  模式：{signature}")
            print(f"  建議結構：{suggested}")
            print()
    
    def manage_patterns_interactive(self):
        """互動式模式管理"""
        while True:
            print("\n檔名模式管理：")
            print("1. 查看已學習的模式")
            print("2. 查看新發現的模式")
            print("3. 手動添加模式")
            print("4. 刪除模式")
            print("5. 清空未知模式記錄")
            print("6. 返回主選單")
            
            choice = input("請選擇操作 (1-6): ").strip()
            
            if choice == "1":
                self.show_learned_patterns()
            elif choice == "2":
                self.show_unknown_patterns()
            elif choice == "3":
                self.add_pattern_manually()
            elif choice == "4":
                self.delete_pattern()
            elif choice == "5":
                self.unknown_patterns.clear()
                print("已清空未知模式記錄")
            elif choice == "6":
                break
            else:
                print("無效選項")
    
    def add_pattern_manually(self):
        """手動添加檔名模式"""
        print("\n手動添加檔名模式：")
        filename = input("請輸入範例檔名：").strip()
        
        if not filename:
            print("檔名不能為空")
            return
        
        pattern_info = self.analyze_filename_pattern(filename)
        print(f"檢測到的模式：{pattern_info['pattern_signature']}")
        print(f"建議的資料夾結構：{' > '.join(pattern_info['suggested_structure'])}")
        
        print("\n請輸入自定義資料夾結構（用逗號分隔各層級）：")
        custom_structure = input("例如：合同,財務部 或按 Enter 使用建議結構：").strip()
        
        if custom_structure:
            structure = [s.strip() for s in custom_structure.split(",")]
        else:
            structure = pattern_info['suggested_structure']
        
        self.learn_new_pattern(filename, structure)
        print(f"已添加模式：{pattern_info['pattern_signature']} → {' > '.join(structure)}")
    
    def delete_pattern(self):
        """刪除已學習的模式"""
        if not self.learned_patterns:
            print("沒有可刪除的模式")
            return
        
        print("\n已學習的模式：")
        signatures = list(self.learned_patterns.keys())
        
        for i, signature in enumerate(signatures, 1):
            info = self.learned_patterns[signature]
            structure = " > ".join(info['folder_structure'])
            print(f"{i}. {signature} → {structure}")
        
        try:
            choice = int(input(f"請選擇要刪除的模式 (1-{len(signatures)}): ")) - 1
            if 0 <= choice < len(signatures):
                deleted_signature = signatures[choice]
                del self.learned_patterns[deleted_signature]
                self.save_learned_patterns()
                print(f"已刪除模式：{deleted_signature}")
            else:
                print("無效選項")
        except ValueError:
            print("請輸入有效數字")


class FileEventHandler(FileSystemEventHandler):
    """檔案系統事件處理器"""
    
    def __init__(self, allocator: FileAllocator):
        self.allocator = allocator
        self.processed_files = set()  # 避免重複處理
        
    def on_created(self, event):
        """檔案創建事件"""
        if not event.is_directory:
            file_path = Path(event.src_path)
            
            # 避免重複處理
            if str(file_path) in self.processed_files:
                return
            
            # 等待檔案完全寫入（避免處理正在下載的檔案）
            time.sleep(2)
            
            if file_path.exists() and file_path.stat().st_size > 0:
                self.processed_files.add(str(file_path))
                self.allocator.move_file(file_path)
    
    def on_moved(self, event):
        """檔案移動事件"""
        if not event.is_directory:
            file_path = Path(event.dest_path)
            
            if str(file_path) not in self.processed_files:
                time.sleep(1)
                if file_path.exists():
                    self.processed_files.add(str(file_path))
                    self.allocator.move_file(file_path)


def create_config_file():
    """創建設定檔案"""
    config_content = """# 檔案自動分類整理工具 - 設定檔
# 請根據您的需求修改以下設定

# 監控資料夾路徑（請使用絕對路徑）
WATCH_FOLDER = "C:\\Users\\%USERNAME%\\Downloads"

# 整理後的目標資料夾
TARGET_FOLDER = "C:\\Users\\%USERNAME%\\Documents\\OrganizedFiles"

# 檔名分隔符
SEPARATOR = "_"

# 支援的檔案類型（用逗號分隔）
SUPPORTED_EXTENSIONS = ".pdf,.docx,.xlsx,.pptx,.txt,.doc,.xls,.ppt,.jpg,.jpeg,.png,.gif,.bmp,.mp4,.avi,.mov,.mp3,.wav,.zip,.rar"

# 每日自動掃描時間（24小時制）
DAILY_SCAN_HOUR = 2
DAILY_SCAN_MINUTE = 0

# 範例檔名格式：
# "合同_財務部_2025Q3.pdf" → 資料夾結構：OrganizedFiles/合同/財務部/2025Q3.pdf
# "報告_人事_月報_202501.docx" → 資料夾結構：OrganizedFiles/報告/人事/月報_202501.docx
# "照片_旅遊_日本_2025.jpg" → 資料夾結構：OrganizedFiles/照片/旅遊/日本_2025.jpg
"""
    
    with open("config.txt", "w", encoding="utf-8") as f:
        f.write(config_content)


def load_config() -> Dict[str, str]:
    """載入設定檔"""
    config = {
        'WATCH_FOLDER': os.path.expanduser("~/Downloads"),
        'TARGET_FOLDER': os.path.expanduser("~/Documents/OrganizedFiles"),
        'SEPARATOR': "_",
        'SUPPORTED_EXTENSIONS': ".pdf,.docx,.xlsx,.pptx,.txt,.doc,.xls,.ppt,.jpg,.jpeg,.png,.gif,.bmp,.mp4,.avi,.mov,.mp3,.wav,.zip,.rar",
        'DAILY_SCAN_HOUR': "2",
        'DAILY_SCAN_MINUTE': "0"
    }
    
    if os.path.exists("config.txt"):
        try:
            with open("config.txt", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if "=" in line:
                            key, value = line.split("=", 1)
                            config[key.strip()] = value.strip().strip('"')
        except Exception as e:
            print(f"讀取設定檔錯誤：{e}")
    
    return config


def main():
    """主程式"""
    print("檔案自動分類整理工具")
    print("=" * 50)
    
    # 載入設定
    config = load_config()
    
    # 處理路徑中的環境變數
    watch_folder = os.path.expandvars(config['WATCH_FOLDER'])
    target_folder = os.path.expandvars(config['TARGET_FOLDER'])
    
    # 解析支援的檔案類型
    extensions = [ext.strip() for ext in config['SUPPORTED_EXTENSIONS'].split(",")]
    
    # 創建檔案分配器
    allocator = FileAllocator(
        watch_folder=watch_folder,
        target_folder=target_folder,
        separator=config['SEPARATOR'],
        supported_extensions=extensions
    )
    
    print(f"監控資料夾：{watch_folder}")
    print(f"目標資料夾：{target_folder}")
    print(f"支援檔案類型：{', '.join(extensions)}")
    
    # 詢問操作模式
    print("\n請選擇操作模式：")
    print("1. 掃描現有檔案並整理")
    print("2. 開始即時監控")
    print("3. 掃描 + 監控（推薦）")
    print("4. 檔名模式管理")
    print("5. 創建設定檔並退出")
    
    while True:
        choice = input("\n請輸入選項 (1-5): ").strip()
        
        if choice == "1":
            allocator.scan_and_organize()
            break
        elif choice == "2":
            # 設定每日掃描
            hour = int(config['DAILY_SCAN_HOUR'])
            minute = int(config['DAILY_SCAN_MINUTE'])
            allocator.schedule_daily_scan(hour, minute)
            
            print("開始即時監控... (按 Ctrl+C 停止)")
            allocator.start_monitoring()
            break
        elif choice == "3":
            # 先掃描現有檔案
            allocator.scan_and_organize()
            
            # 設定每日掃描
            hour = int(config['DAILY_SCAN_HOUR'])
            minute = int(config['DAILY_SCAN_MINUTE'])
            allocator.schedule_daily_scan(hour, minute)
            
            print("\n開始即時監控... (按 Ctrl+C 停止)")
            allocator.start_monitoring()
            break
        elif choice == "4":
            allocator.manage_patterns_interactive()
        elif choice == "5":
            create_config_file()
            print("設定檔 'config.txt' 已創建，請修改後重新執行程式")
            break
        else:
            print("無效選項，請重新輸入")


if __name__ == "__main__":
    main()
