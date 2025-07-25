#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能檔案分類工具 - 自動打包腳本
將程式打包成獨立的可執行檔
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def check_pyinstaller():
    """檢查 PyInstaller 是否已安裝"""
    try:
        import PyInstaller
        print("✓ PyInstaller 已安裝")
        return True
    except ImportError:
        print("✗ PyInstaller 未安裝")
        print("請執行：pip install pyinstaller")
        return False


def clean_build_files():
    """清理之前的建置檔案"""
    print("\n正在清理之前的建置檔案...")
    
    dirs_to_clean = ['dist', 'build', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  - 已刪除 {dir_name}/")


def build_exe():
    """使用 PyInstaller 建置可執行檔"""
    print("\n正在打包程式...")
    
    # 使用 spec 檔案進行打包
    cmd = ['pyinstaller', '--clean', 'SmartFileAllocator.spec']
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"打包失敗：{e}")
        print(f"錯誤輸出：{e.stderr}")
        return False


def get_file_size(file_path):
    """獲取檔案大小（格式化）"""
    size_bytes = os.path.getsize(file_path)
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def create_distribution_package():
    """創建分發套件"""
    exe_path = Path('dist/SmartFileAllocator.exe')
    
    if not exe_path.exists():
        print("❌ 找不到建置的可執行檔")
        return False
    
    # 創建分發資料夾
    dist_folder = Path('SmartFileAllocator_v2.0')
    if dist_folder.exists():
        shutil.rmtree(dist_folder)
    
    dist_folder.mkdir()
    
    # 複製主要檔案
    shutil.copy2(exe_path, dist_folder / 'SmartFileAllocator.exe')
    
    # 創建說明檔案
    readme_content = """# 智能檔案自動分類工具 v2.0

## 🚀 快速開始

1. 雙擊 `SmartFileAllocator.exe` 啟動程式
2. 首次使用選擇「5」創建設定檔
3. 修改 `config.txt` 設定監控和目標資料夾
4. 重新執行程式，選擇「3」開始使用（推薦）

## 📋 主要功能

- 🧠 **智能學習**：自動識別檔名格式模式
- 📁 **動態分類**：根據檔名自動創建資料夾結構
- 👁️ **即時監控**：持續監控新檔案並自動分類
- ⚙️ **模式管理**：查看和管理已學習的檔名格式

## 📄 檔名格式範例

```
合同_財務部_2025Q3.pdf         → 合同/財務部/2025Q3.pdf
報告_月報_人事部_202501.xlsx   → 報告/月報/人事部/202501.xlsx
發票_ABC公司_50000_20250115.pdf → 發票/ABC公司/50000/20250115.pdf
照片_會議_會議室A_20250125.jpg → 照片/會議/會議室A/20250125.jpg
```

## 🔧 設定說明

程式會自動創建 `config.txt` 設定檔，您可以修改：

- 監控資料夾路徑
- 目標整理資料夾
- 支援的檔案類型
- 每日自動掃描時間

## 💡 使用技巧

1. **檔名規範**：使用一致的分隔符（預設為 `_`）
2. **分類邏輯**：按重要性排序：類型_部門_時間_詳細描述
3. **首次使用**：建議先測試少量檔案
4. **模式管理**：可以查看和自定義檔名格式

## 📞 技術支援

- 程式會自動記錄日誌到 `logs/` 資料夾
- 學習到的模式保存在 `learned_patterns.json`
- 如遇問題請檢查日誌檔案

## 🔍 系統需求

- Windows 7 或更新版本
- 至少 50MB 可用磁碟空間
- 對目標資料夾的寫入權限

---
智能檔案自動分類工具 v2.0
Copyright © 2025 Smart File Solutions
"""
    
    with open(dist_folder / 'README.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    # 創建範例設定檔
    example_config = """# 智能檔案自動分類工具 - 設定檔範例
# 請根據您的需求修改以下設定

# 監控資料夾路徑（請修改為您的實際路徑）
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

# 檔名格式範例：
# "合同_財務部_2025Q3.pdf" → 資料夾結構：OrganizedFiles/合同/財務部/2025Q3.pdf
# "報告_人事_月報_202501.docx" → 資料夾結構：OrganizedFiles/報告/人事/月報_202501.docx
# "照片_旅遊_日本_2025.jpg" → 資料夾結構：OrganizedFiles/照片/旅遊/日本_2025.jpg
"""
    
    with open(dist_folder / 'config_example.txt', 'w', encoding='utf-8') as f:
        f.write(example_config)
    
    # 創建範例檔案資料夾
    examples_folder = dist_folder / '範例檔案'
    examples_folder.mkdir()
    
    example_files = [
        "合同_財務部_2025Q3.pdf",
        "報告_月報_人事部_202501.xlsx",
        "發票_ABC公司_50000_20250115.pdf",
        "照片_會議_會議室A_20250125.jpg",
        "專案_網站改版_設計_v1.docx"
    ]
    
    for filename in example_files:
        example_file = examples_folder / filename
        example_file.write_text(f"這是範例檔案：{filename}\n\n將此檔案放入監控資料夾中測試自動分類功能。")
    
    print(f"\n✅ 分發套件已創建：{dist_folder}")
    print(f"📁 套件大小：{get_file_size(exe_path)}")
    
    return True


def main():
    """主函數"""
    print("智能檔案自動分類工具 - 打包成 EXE")
    print("=" * 60)
    
    # 檢查 PyInstaller
    if not check_pyinstaller():
        return False
    
    # 檢查必要檔案
    required_files = ['allocate_file.py', 'SmartFileAllocator.spec', 'version_info.txt']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"\n錯誤：缺少必要檔案：{missing_files}")
        return False
    
    # 清理建置檔案
    clean_build_files()
    
    # 建置可執行檔
    if build_exe():
        exe_path = Path('dist/SmartFileAllocator.exe')
        
        if exe_path.exists():
            print("\n" + "=" * 60)
            print("打包完成！")
            print("=" * 60)
            print(f"可執行檔位置：{exe_path}")
            print(f"檔案大小：{get_file_size(exe_path)}")
            
            # 創建分發套件
            if create_distribution_package():
                print("\n🎉 分發套件創建完成！")
                print("\n📦 分發內容：")
                print("  - SmartFileAllocator.exe     (主程式)")
                print("  - README.txt                 (使用說明)")
                print("  - config_example.txt         (設定範例)")
                print("  - 範例檔案/                  (測試檔案)")
                print("\n💡 使用方式：")
                print("  1. 將整個 SmartFileAllocator_v2.0 資料夾複製給使用者")
                print("  2. 使用者雙擊 SmartFileAllocator.exe 即可使用")
                print("  3. 無需安裝 Python 或任何依賴套件")
                
            return True
        else:
            print("\n錯誤：找不到建置的可執行檔")
            return False
    else:
        print("\n打包失敗！")
        return False


if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n按 Enter 鍵退出...")
        input()
        sys.exit(1)
    
    print("\n按 Enter 鍵退出...")
    input()
