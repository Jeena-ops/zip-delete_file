# 📅 檔案清理自動化工具 v2.0 - 完整使用指南

## 🌟 功能概述

這是一個功能強大的檔案自動清理工具，支援多種清理方式和自動排程功能。無論您需要定期清理下載資料夾、暫存檔案，還是管理大型專案的舊檔案，這個工具都能滿足您的需求。

### 🚀 主要特點

- **📦 多種清理方式**：壓縮歸檔、回收站、永久刪除
- **⏰ 自動排程**：每日、每週、間隔執行
- **🖥️ 圖形界面**：直觀的任務管理和監控
- **🔧 Windows 服務**：開機自動啟動（可選）
- **📊 詳細日誌**：完整的操作記錄和統計
- **🛡️ 安全機制**：預覽模式、權限檢查、錯誤處理

## 📋 系統需求

- **作業系統**：Windows 7/8/10/11
- **Python**：3.7 或更高版本
- **磁碟空間**：至少 50MB 可用空間
- **權限**：讀寫目標資料夾的權限

## 🚀 快速開始

### 方法一：使用 PowerShell（推薦）

```powershell
# 1. 下載或複製所有檔案到資料夾
# 2. 開啟 PowerShell，切換到工具目錄
cd "C:\path\to\file-cleanup-tool"

# 3. 執行安裝腳本
.\setup.ps1 -Install

# 4. 啟動 GUI
.\setup.ps1 -Start
```

### 方法二：使用批次檔

```batch
# 雙擊執行 launcher_auto.bat
# 選擇選項 1 啟動排程器 GUI
```

### 方法三：命令列

```bash
# 安裝依賴
pip install -r requirements_scheduler.txt

# 創建範例配置
python scheduler.py --create-config

# 啟動 GUI
python scheduler_gui.py
```

## 📖 使用指南

### 🎯 自動排程清理（推薦）

#### 使用圖形界面設定

1. **啟動 GUI**：執行 `python scheduler_gui.py`
2. **新增任務**：點擊「新增任務」按鈕
3. **設定任務**：
   - 任務名稱：例如「清理下載資料夾」
   - 資料夾路徑：選擇要清理的資料夾
   - 保留天數：例如 30 天
   - 清理方式：選擇壓縮歸檔（推薦）
   - 排程設定：例如每日 02:00 執行
4. **啟動排程器**：點擊「啟動排程器」
5. **監控執行**：在日誌區域查看執行狀態

#### 快速設定範例

**清理下載資料夾**：
- 路徑：`C:\Users\YourName\Downloads`
- 保留：30 天
- 方式：壓縮歸檔
- 排程：每日 02:00

**清理暫存檔案**：
- 路徑：`C:\Windows\Temp`
- 保留：7 天
- 方式：永久刪除
- 排程：每週日 03:00

### 🔧 進階配置

#### 手動編輯配置檔案

```json
{
  "enabled": true,
  "tasks": [
    {
      "name": "清理下載資料夾",
      "path": "C:\\Users\\YourName\\Downloads",
      "days_to_keep": 30,
      "include_subfolders": true,
      "action": "archive",
      "schedule": {
        "type": "daily",
        "time": "02:00"
      },
      "enabled": true
    }
  ],
  "global_settings": {
    "use_recycle_bin": true,
    "use_archive": true,
    "log_level": "INFO",
    "max_log_days": 30
  }
}
```

#### 排程類型說明

**每日執行**：
```json
{
  "type": "daily",
  "time": "02:00"
}
```

**每週執行**：
```json
{
  "type": "weekly",
  "day": "sunday",
  "time": "03:00"
}
```

**間隔執行**：
```json
{
  "type": "interval",
  "value": 6,
  "unit": "hours"
}
```

### 📦 清理方式詳解

#### 1. 壓縮歸檔模式（推薦）

**特點**：
- ✅ 大幅節省磁碟空間（通常節省 50-90%）
- ✅ 檔案可完整恢復
- ✅ 保持原始目錄結構
- ✅ 自動按日期分組

**適用場景**：
- 文檔資料夾
- 專案檔案
- 日誌檔案
- 媒體檔案

**操作**：
```bash
python delete_file_regularly.py --archive
```

#### 2. 回收站模式

**特點**：
- ✅ 檔案可恢復
- ✅ 操作安全
- ❌ 仍占用磁碟空間
- ❌ 需要手動清理回收站

**適用場景**：
- 重要檔案的清理
- 不確定是否需要的檔案
- 測試清理規則

**操作**：
```bash
python delete_file_regularly.py
```

#### 3. 永久刪除模式

**特點**：
- ✅ 立即釋放磁碟空間
- ❌ 檔案無法恢復
- ⚠️ 操作不可逆

**適用場景**：
- 暫存檔案
- 快取檔案
- 已確認不需要的檔案

**操作**：
```bash
python delete_file_regularly.py --no-recycle-bin
```

## 🔧 Windows 服務安裝

### 安裝服務（需管理員權限）

```powershell
# 以管理員身份開啟 PowerShell
python service.py --install
```

### 管理服務

```powershell
# 啟動服務
python service.py --start

# 停止服務
python service.py --stop

# 查看狀態
python service.py --status

# 移除服務
python service.py --remove
```

### 服務特點

- 🚀 開機自動啟動
- 🔄 背景運行，無需登入
- 📊 完整日誌記錄
- 🛡️ 系統級權限

## 📊 監控和管理

### 日誌檔案位置

- **排程器日誌**：`logs/scheduler_YYYYMMDD.log`
- **清理日誌**：`logs/file_cleanup_YYYYMMDD.log`
- **服務日誌**：`logs/service.log`

### 恢復和歸檔管理

#### 恢復回收站檔案

```bash
python file_recovery.py
```

#### 管理壓縮歸檔

```bash
python file_archive_manager.py
```

### 檢查排程器狀態

```bash
# 查看所有任務狀態
python scheduler.py --status

# 立即執行指定任務
python scheduler.py --run-task "任務名稱"
```

## 🛠️ 常見問題解決

### Q: Python 找不到或版本過舊

**解決方案**：
1. 從 [python.org](https://www.python.org/) 下載 Python 3.7+
2. 安裝時勾選「Add Python to PATH」
3. 重新開啟命令提示字元

### Q: 缺少依賴套件

**解決方案**：
```bash
# 安裝基本依賴
pip install schedule

# 安裝完整依賴（包括 GUI）
pip install -r requirements_scheduler.txt
```

### Q: GUI 無法啟動

**可能原因和解決方案**：
1. **tkinter 未安裝**：
   ```bash
   # Windows 通常內建，如果沒有：
   pip install tk
   ```

2. **缺少其他依賴**：
   ```bash
   pip install pillow pystray
   ```

### Q: 服務安裝失敗

**解決方案**：
1. **確認管理員權限**：右鍵選擇「以系統管理員身分執行」
2. **安裝 pywin32**：
   ```bash
   pip install pywin32
   ```

### Q: 排程器不執行任務

**檢查項目**：
1. 確認任務已啟用
2. 檢查排程時間設定
3. 確認資料夾路徑存在
4. 查看日誌檔案中的錯誤訊息

### Q: 權限不足錯誤

**解決方案**：
1. 確認對目標資料夾有寫入權限
2. 以管理員身份執行程式
3. 檢查檔案是否被其他程式占用

## 📅 使用場景範例

### 場景一：個人電腦日常維護

**需求**：定期清理下載資料夾和暫存檔案

**設定**：
```json
{
  "tasks": [
    {
      "name": "清理下載資料夾",
      "path": "C:\\Users\\YourName\\Downloads",
      "days_to_keep": 30,
      "action": "archive",
      "schedule": {"type": "daily", "time": "02:00"}
    },
    {
      "name": "清理暫存檔案",
      "path": "C:\\Windows\\Temp",
      "days_to_keep": 7,
      "action": "delete",
      "schedule": {"type": "weekly", "day": "sunday", "time": "03:00"}
    }
  ]
}
```

### 場景二：開發環境管理

**需求**：清理編譯產生的檔案和日誌

**設定**：
```json
{
  "tasks": [
    {
      "name": "清理編譯檔案",
      "path": "C:\\Projects",
      "days_to_keep": 14,
      "action": "delete",
      "schedule": {"type": "daily", "time": "01:00"}
    },
    {
      "name": "歸檔日誌檔案",
      "path": "C:\\Logs",
      "days_to_keep": 30,
      "action": "archive",
      "schedule": {"type": "weekly", "day": "saturday", "time": "23:00"}
    }
  ]
}
```

### 場景三：伺服器維護

**需求**：定期清理伺服器日誌和暫存檔案

**設定**：
- 安裝為 Windows 服務
- 每 6 小時清理一次
- 使用壓縮歸檔保留重要日誌

## 🔗 其他資源

### 相關檔案說明

- `delete_file_regularly.py`：核心清理功能
- `scheduler.py`：排程器引擎
- `scheduler_gui.py`：圖形界面
- `service.py`：Windows 服務支援
- `setup.ps1`：PowerShell 安裝腳本
- `launcher_auto.bat`：批次檔啟動器

### 配置檔案

- `scheduler_config.json`：排程任務配置
- `tray_settings.json`：托盤程式設定
- `requirements_scheduler.txt`：Python 依賴列表

### 日誌和資料

- `logs/`：所有日誌檔案
- `recycle_bin/`：回收站檔案
- `archived_files/`：壓縮歸檔檔案

## 📞 技術支援

如果遇到問題，請：

1. 檢查日誌檔案中的錯誤訊息
2. 確認 Python 和依賴套件版本
3. 參考本文檔的常見問題部分
4. 檢查檔案權限和路徑設定

---

*檔案清理自動化工具 v2.0 - 讓檔案管理變得簡單高效！* 🚀
