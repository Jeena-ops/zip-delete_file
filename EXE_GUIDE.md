# 檔案批次重新命名工具 - EXE 版本

## 🎉 成功打包為可執行檔！

您的 Python 程式已經成功打包為 Windows 可執行檔 (.exe)，現在可以在任何 Windows 電腦上運行，無需安裝 Python。

## 📁 檔案說明

- **`dist/FileRenamer.exe`** - 主要可執行檔（約 7.3 MB）
- **`version_info.txt`** - 版本資訊檔案
- **`FileRenamer.spec`** - PyInstaller 配置檔案
- **`build_exe.py`** - 打包腳本
- **`build_exe.bat`** - Windows 批次打包腳本

## 🚀 如何使用 EXE 檔案

### 方法一：直接執行
1. 雙擊 `dist/FileRenamer.exe`
2. 按照提示輸入資料夾路徑
3. 預覽重新命名結果
4. 確認後執行實際重新命名

### 方法二：命令列執行
```cmd
cd path/to/your/files
C:\path\to\FileRenamer.exe
```

## 📋 版本資訊

- **版本**：1.0.0.0
- **檔案說明**：檔案批次重新命名工具
- **產品名稱**：File Batch Renamer
- **版權**：Copyright © 2025

## 🔧 重新打包 (如需要)

如果您需要修改程式後重新打包：

### 使用 Python 腳本：
```bash
python build_exe.py
```

### 使用 Windows 批次檔：
```cmd
build_exe.bat
```

### 手動使用 PyInstaller：
```bash
pyinstaller --onefile --name FileRenamer --version-file version_info.txt rename_files.py
```

## 📦 分發指南

### 單一檔案分發
- 只需複製 `dist/FileRenamer.exe` 即可
- 不需要其他檔案或 Python 環境
- 檔案大小：約 7.3 MB

### 完整分發包
如果要分發完整套件，建議包含：
- `FileRenamer.exe` - 主程式
- `README.md` - 使用說明
- `範例檔案/` - 測試用範例檔案

## 🛠️ 自定義打包選項

### 修改版本資訊
編輯 `version_info.txt` 檔案來修改：
- 公司名稱
- 產品名稱
- 版本號碼
- 版權資訊
- 檔案說明

### 修改 EXE 設定
編輯 `FileRenamer.spec` 檔案來修改：
- 程式名稱
- 圖示 (添加 `icon='icon.ico'`)
- 控制台模式 (`console=True/False`)
- 隱藏導入的模組

### 添加圖示
1. 準備 `.ico` 格式的圖示檔案
2. 在 `FileRenamer.spec` 中添加：
   ```python
   icon='your_icon.ico'
   ```
3. 重新打包

## ⚡ 性能優化

### 減小檔案大小
```bash
# 使用 UPX 壓縮（如果已安裝）
pyinstaller --onefile --upx-dir=/path/to/upx --name FileRenamer rename_files.py

# 排除不需要的模組
pyinstaller --onefile --exclude-module tkinter --name FileRenamer rename_files.py
```

### 加快啟動速度
- 使用 `--onedir` 替代 `--onefile`（會產生資料夾而非單一檔案）
- 在 spec 檔案中設定 `optimize=2`

## 🔍 故障排除

### 常見問題

1. **EXE 檔案無法執行**
   - 檢查防毒軟體是否阻攔
   - 確認在相容的 Windows 版本上運行

2. **缺少模組錯誤**
   - 在 spec 檔案的 `hiddenimports` 中添加缺少的模組

3. **檔案太大**
   - 使用 `--exclude-module` 排除不需要的模組
   - 考慮使用虛擬環境打包

4. **啟動速度慢**
   - 使用 `--onedir` 模式
   - 將常用程式放在 SSD 上

## 📱 系統需求

- **作業系統**：Windows 7 或更新版本
- **架構**：64位元 Windows
- **記憶體**：至少 100 MB 可用空間
- **磁碟空間**：約 10 MB

## 🆕 更新版本

當您更新程式時：
1. 修改 `version_info.txt` 中的版本號
2. 更新 Python 程式碼
3. 重新執行打包腳本
4. 測試新的 EXE 檔案

---

**恭喜！您的程式現在可以作為獨立的可執行檔分發和使用了！** 🎊
