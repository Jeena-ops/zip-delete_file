# 🚀 將檔案清理大師上傳到 GitHub 完整指南

## 📋 **準備工作**

### **1. 確保已安裝 Git**
```bash
# 檢查 Git 是否已安裝
git --version

# 如果未安裝，請下載：https://git-scm.com/
```

### **2. 配置 Git 用戶資訊**
```bash
# 設置你的 GitHub 用戶名和郵箱
git config --global user.name "你的用戶名"
git config --global user.email "你的郵箱@example.com"
```

### **3. 檢查 SSH 密鑰（推薦）**
```bash
# 檢查是否已有 SSH 密鑰
ls -al ~/.ssh

# 如果沒有，生成新的 SSH 密鑰
ssh-keygen -t ed25519 -C "你的郵箱@example.com"

# 將公鑰添加到 GitHub
cat ~/.ssh/id_ed25519.pub
# 複製輸出內容，到 GitHub Settings > SSH keys 添加
```

---

## 🎯 **上傳步驟**

### **步驟 1：創建 .gitignore 文件**
```bash
# 創建 .gitignore 避免上傳不必要的文件
```

### **步驟 2：初始化並添加文件**
```bash
# 1. 進入項目目錄
cd c:\ccode\project

# 2. 初始化 Git 倉庫（如果還沒有）
git init

# 3. 添加所有文件
git add .

# 4. 創建第一次提交
git commit -m "初始提交：檔案清理大師完整版本

包含功能：
- 核心檔案清理系統
- 系統托盤應用
- 壓縮歸檔功能
- EXE 打包配置
- 網頁版介面
- 完整部署指南"
```

### **步驟 3：在 GitHub 創建新倉庫**
1. 登錄 [GitHub.com](https://github.com)
2. 點擊右上角 "+" → "New repository"
3. 輸入倉庫名稱：`file-cleanup-master` 或 `檔案清理大師`
4. 選擇 "Public"（公開）或 "Private"（私人）
5. **不要**勾選 "Initialize with README"
6. 點擊 "Create repository"

### **步驟 4：連接本地倉庫到 GitHub**
```bash
# 添加遠端倉庫（替換成你的 GitHub 用戶名）
git remote add origin https://github.com/你的用戶名/file-cleanup-master.git

# 或使用 SSH（推薦）
git remote add origin git@github.com:你的用戶名/file-cleanup-master.git

# 推送到 GitHub
git push -u origin main
```

---

## 🔧 **Git Bash 完整命令序列**

打開 Git Bash，複製貼上以下命令：

```bash
# 1. 進入項目目錄
cd /c/ccode/project

# 2. 檢查當前狀態
git status

# 3. 添加所有文件
git add .

# 4. 創建提交
git commit -m "檔案清理大師 v1.0 - 完整功能版本

✨ 新功能：
- 智能檔案清理系統
- 壓縮歸檔節省 50%+ 空間
- 系統托盤常駐程序
- 一鍵 EXE 打包
- 網頁版多人使用
- 完整部署方案

🎯 支援功能：
- Windows 系統托盤整合
- 多種清理模式
- 自動壓縮歸檔
- 雙重部署方案（EXE + Web）
- 專業級使用者介面"

# 5. 添加遠端倉庫（記得替換你的用戶名）
git remote add origin https://github.com/你的用戶名/file-cleanup-master.git

# 6. 推送到 GitHub
git push -u origin main
```

---

## 📁 **建議的 .gitignore 內容**

在根目錄創建 `.gitignore` 文件：

```gitignore
# Python 編譯文件
__pycache__/
*.py[cod]
*$py.class
*.so

# 分發 / 打包
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# 單元測試
htmlcov/
.tox/
.coverage
.coverage.*
.cache
.pytest_cache/

# 環境變量
.env
.venv
env/
venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# 系統文件
.DS_Store
Thumbs.db
*.log

# 臨時文件
temp/
tmp/
*.tmp
*.temp

# 大型二進制文件
*.exe
*.msi
*.zip
*.rar
*.7z

# 本地配置
config.local.py
settings.local.py
```

---

## 🎉 **完成後的效果**

上傳成功後，你的 GitHub 倉庫將包含：

### **📂 專案結構展示**
```
file-cleanup-master/
├── 📁 delete_file_regularly/     # 核心清理系統
├── 📄 web_app.py                # 網頁版應用
├── 📄 cleanup_tray.py           # 系統托盤程序
├── 📄 create_exe.py             # EXE 打包器
├── 📄 start_web.bat             # 網頁版啟動器
├── 📄 quick_build.bat           # 一鍵打包
├── 📄 DEPLOYMENT_GUIDE.md       # 部署指南
├── 📄 GITHUB_UPLOAD_GUIDE.md    # 上傳指南
└── 📄 README.md                 # 項目說明
```

### **🌟 項目特色**
- ⭐ **完整的開源檔案清理解決方案**
- 🎯 **雙重部署模式**（EXE + Web）
- 🔧 **專業級程式碼品質**
- 📚 **完整的文檔和指南**
- 🚀 **即用型部署腳本**

---

## 🔄 **後續更新流程**

當你修改代碼後，使用以下命令更新 GitHub：

```bash
# 1. 添加修改的文件
git add .

# 2. 創建新提交
git commit -m "更新功能：描述你的修改"

# 3. 推送到 GitHub
git push origin main
```

---

## 🛠️ **故障排除**

### **常見問題 1：推送被拒絕**
```bash
# 解決方案：先拉取遠端更新
git pull origin main --allow-unrelated-histories
git push origin main
```

### **常見問題 2：認證失敗**
```bash
# 使用 GitHub Personal Access Token
# 1. 到 GitHub Settings > Developer settings > Personal access tokens
# 2. 創建新 token
# 3. 使用 token 代替密碼
```

### **常見問題 3：大文件上傳失敗**
```bash
# 移除大文件並重新提交
git rm --cached large_file.exe
git commit -m "移除大文件"
git push origin main
```

---

## 🎯 **推薦的倉庫設置**

### **README.md 內容建議**
```markdown
# 📁 檔案清理大師 File Cleanup Master

> 🚀 專業級檔案清理工具，支援系統托盤和網頁版

## ✨ 主要功能
- 🗂️ 智能檔案清理
- 📦 自動壓縮歸檔
- 🎯 系統托盤常駐
- 🌐 網頁版多人使用
- 📱 跨平台支援

## 🚀 快速開始
1. 下載 EXE 版本：直接運行 `檔案清理大師.exe`
2. 網頁版：運行 `start_web.bat` 啟動伺服器

## 📖 詳細文檔
- [部署指南](DEPLOYMENT_GUIDE.md)
- [上傳指南](GITHUB_UPLOAD_GUIDE.md)
```

### **發布 Release**
```bash
# 創建標籤
git tag -a v1.0 -m "檔案清理大師 v1.0 正式版"
git push origin v1.0

# 然後在 GitHub 網頁上創建 Release
```

---

## 🎉 **立即開始上傳**

**複製以下命令到 Git Bash：**

```bash
cd /c/ccode/project
git add .
git commit -m "檔案清理大師完整版 - 支援 EXE 和網頁版部署"
# 記得替換下面的用戶名
git remote add origin https://github.com/你的用戶名/file-cleanup-master.git
git push -u origin main
```

完成後，你的專業檔案清理工具就可以分享給全世界了！ 🌍✨
