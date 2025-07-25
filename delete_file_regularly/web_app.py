#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檔案清理工具 - 網頁版本
基於Flask的Web界面，支援瀏覽器訪問
"""

from flask import Flask, render_template, request, jsonify, send_file, session
import os
import json
import zipfile
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import secrets

# 導入核心清理工具
from delete_file_regularly import FileCleanupTool

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# 配置
UPLOAD_FOLDER = 'web_temp'
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# 確保臨時目錄存在
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)

class WebFileCleanup:
    """網頁版檔案清理工具"""
    
    def __init__(self):
        self.sessions = {}  # 儲存會話數據
    
    def create_session(self):
        """創建新的清理會話"""
        session_id = secrets.token_hex(8)
        self.sessions[session_id] = {
            'created': datetime.now(),
            'files': [],
            'settings': {},
            'results': {}
        }
        return session_id
    
    def cleanup_old_sessions(self):
        """清理舊會話"""
        cutoff = datetime.now() - timedelta(hours=1)
        expired = [sid for sid, data in self.sessions.items() 
                  if data['created'] < cutoff]
        for sid in expired:
            del self.sessions[sid]

web_cleanup = WebFileCleanup()

@app.route('/')
def index():
    """主頁面"""
    return render_template('index.html')

@app.route('/api/scan', methods=['POST'])
def scan_files():
    """掃描檔案API"""
    try:
        data = request.get_json()
        folder_path = data.get('folder_path', '')
        days_to_keep = int(data.get('days_to_keep', 7))
        include_subfolders = data.get('include_subfolders', True)
        
        # 驗證路徑
        if not folder_path or not Path(folder_path).exists():
            return jsonify({'error': '無效的資料夾路徑'}), 400
        
        # 創建清理工具
        cleaner = FileCleanupTool("INFO", use_recycle_bin=False, use_archive=True)
        
        # 掃描檔案
        result = cleaner.cleanup_files(
            folder_path, days_to_keep, include_subfolders, dry_run=True
        )
        
        # 轉換結果格式
        files_info = []
        if hasattr(cleaner, '_last_expired_files'):
            for file_info in cleaner._last_expired_files:
                files_info.append({
                    'path': str(file_info['path']),
                    'size': file_info['size'],
                    'size_formatted': cleaner.format_file_size(file_info['size']),
                    'modified_time': file_info['modified_time'].isoformat(),
                    'modified_formatted': file_info['modified_time'].strftime('%Y-%m-%d %H:%M:%S')
                })
        
        # 創建會話
        session_id = web_cleanup.create_session()
        web_cleanup.sessions[session_id]['files'] = files_info
        web_cleanup.sessions[session_id]['settings'] = {
            'folder_path': folder_path,
            'days_to_keep': days_to_keep,
            'include_subfolders': include_subfolders
        }
        
        return jsonify({
            'session_id': session_id,
            'total_files': len(files_info),
            'total_size': sum(f['size'] for f in files_info),
            'total_size_formatted': cleaner.format_file_size(sum(f['size'] for f in files_info)),
            'files': files_info[:20]  # 只返回前20個檔案用於預覽
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cleanup', methods=['POST'])
def cleanup_files():
    """執行清理API"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        cleanup_mode = data.get('cleanup_mode', 'archive')  # archive, recycle, permanent
        
        if session_id not in web_cleanup.sessions:
            return jsonify({'error': '無效的會話ID'}), 400
        
        session_data = web_cleanup.sessions[session_id]
        settings = session_data['settings']
        
        # 創建清理工具
        use_archive = cleanup_mode == 'archive'
        use_recycle = cleanup_mode == 'recycle'
        cleaner = FileCleanupTool("INFO", use_recycle_bin=use_recycle, use_archive=use_archive)
        
        # 執行清理
        result = cleaner.cleanup_files(
            settings['folder_path'],
            settings['days_to_keep'],
            settings['include_subfolders'],
            dry_run=False
        )
        
        # 保存結果
        web_cleanup.sessions[session_id]['results'] = {
            'mode': cleanup_mode,
            'total_found': result['total_found'],
            'successfully_deleted': result['successfully_deleted'],
            'failed_deletions': result['failed_deletions'],
            'total_size_freed': result['total_size_freed'],
            'total_size_freed_formatted': cleaner.format_file_size(result['total_size_freed'])
        }
        
        return jsonify({
            'success': True,
            'result': web_cleanup.sessions[session_id]['results']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download_archive/<session_id>')
def download_archive(session_id):
    """下載歸檔檔案"""
    try:
        if session_id not in web_cleanup.sessions:
            return jsonify({'error': '無效的會話ID'}), 400
        
        # 找到最新的歸檔檔案
        archive_folder = Path("archived_files")
        today = datetime.now().strftime('%Y%m%d')
        archive_name = f"archived_files_{today}.zip"
        archive_path = archive_folder / archive_name
        
        if archive_path.exists():
            return send_file(archive_path, as_attachment=True, download_name=archive_name)
        else:
            return jsonify({'error': '歸檔檔案不存在'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """獲取統計資訊"""
    try:
        stats = {
            'active_sessions': len(web_cleanup.sessions),
            'archive_folder_size': 0,
            'recycle_folder_size': 0,
            'total_archives': 0
        }
        
        # 計算歸檔資料夾大小
        archive_folder = Path("archived_files")
        if archive_folder.exists():
            for file in archive_folder.glob("*.zip"):
                stats['archive_folder_size'] += file.stat().st_size
                stats['total_archives'] += 1
        
        # 計算回收站大小
        recycle_folder = Path("recycle_bin")
        if recycle_folder.exists():
            for file in recycle_folder.glob("*"):
                if file.is_file():
                    stats['recycle_folder_size'] += file.stat().st_size
        
        # 格式化大小
        cleaner = FileCleanupTool("INFO")
        stats['archive_folder_size_formatted'] = cleaner.format_file_size(stats['archive_folder_size'])
        stats['recycle_folder_size_formatted'] = cleaner.format_file_size(stats['recycle_folder_size'])
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def create_web_templates():
    """創建網頁模板"""
    
    # 創建templates目錄
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    # 創建靜態文件目錄
    static_dir = Path("static")
    static_dir.mkdir(exist_ok=True)
    
    # 主頁面HTML
    index_html = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>檔案清理大師 - 網頁版</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        .hero-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 3rem 0;
        }
        .feature-card {
            border: none;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }
        .feature-card:hover {
            transform: translateY(-5px);
        }
        .progress-container {
            display: none;
        }
        .file-list {
            max-height: 400px;
            overflow-y: auto;
        }
        .stats-card {
            background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }
    </style>
</head>
<body>
    <!-- 導航欄 -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="#">
                <i class="bi bi-trash3"></i> 檔案清理大師
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="#features">功能特色</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#cleanup">開始清理</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#stats">統計資訊</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- 主標題區 -->
    <section class="hero-section text-center">
        <div class="container">
            <h1 class="display-4 mb-4"><i class="bi bi-magic"></i> 檔案清理大師</h1>
            <p class="lead mb-4">智能清理過期檔案，支援壓縮歸檔，安全可靠，一鍵操作</p>
            <a href="#cleanup" class="btn btn-light btn-lg">
                <i class="bi bi-play-circle"></i> 立即開始
            </a>
        </div>
    </section>

    <!-- 功能特色 -->
    <section id="features" class="py-5">
        <div class="container">
            <h2 class="text-center mb-5">功能特色</h2>
            <div class="row">
                <div class="col-md-4 mb-4">
                    <div class="card feature-card h-100">
                        <div class="card-body text-center">
                            <i class="bi bi-archive display-4 text-primary mb-3"></i>
                            <h5 class="card-title">壓縮歸檔</h5>
                            <p class="card-text">將過期檔案壓縮存檔，節省50%以上空間，需要時可隨時恢復。</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4 mb-4">
                    <div class="card feature-card h-100">
                        <div class="card-body text-center">
                            <i class="bi bi-shield-check display-4 text-success mb-3"></i>
                            <h5 class="card-title">安全可靠</h5>
                            <p class="card-text">完整的預覽功能，清楚顯示將要處理的檔案，避免誤刪重要資料。</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4 mb-4">
                    <div class="card feature-card h-100">
                        <div class="card-body text-center">
                            <i class="bi bi-lightning display-4 text-warning mb-3"></i>
                            <h5 class="card-title">簡單易用</h5>
                            <p class="card-text">網頁界面操作簡單，無需安裝軟體，任何人都可以輕鬆使用。</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- 清理工具 -->
    <section id="cleanup" class="py-5 bg-light">
        <div class="container">
            <h2 class="text-center mb-5">檔案清理工具</h2>
            
            <!-- 設置表單 -->
            <div class="row justify-content-center">
                <div class="col-lg-8">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="bi bi-gear"></i> 清理設置</h5>
                        </div>
                        <div class="card-body">
                            <form id="cleanupForm">
                                <div class="mb-3">
                                    <label for="folderPath" class="form-label">資料夾路徑 *</label>
                                    <input type="text" class="form-control" id="folderPath" 
                                           placeholder="例如: C:\\Users\\用戶名\\Downloads" required>
                                    <div class="form-text">請輸入要清理的資料夾完整路徑</div>
                                </div>
                                
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="daysToKeep" class="form-label">保留天數</label>
                                            <input type="number" class="form-control" id="daysToKeep" 
                                                   value="7" min="0" max="3650">
                                            <div class="form-text">超過此天數的檔案將被清理</div>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="cleanupMode" class="form-label">清理模式</label>
                                            <select class="form-select" id="cleanupMode">
                                                <option value="archive">壓縮歸檔（推薦）</option>
                                                <option value="recycle">移至回收站</option>
                                                <option value="permanent">永久刪除</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" id="includeSubfolders" checked>
                                        <label class="form-check-label" for="includeSubfolders">
                                            包含子資料夾
                                        </label>
                                    </div>
                                </div>
                                
                                <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                                    <button type="button" class="btn btn-primary" id="scanBtn">
                                        <i class="bi bi-search"></i> 掃描檔案
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 進度條 -->
            <div class="progress-container mt-4">
                <div class="text-center mb-3">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">處理中...</span>
                    </div>
                    <p class="mt-2">正在處理，請稍候...</p>
                </div>
                <div class="progress">
                    <div class="progress-bar" role="progressbar" style="width: 0%"></div>
                </div>
            </div>

            <!-- 掃描結果 -->
            <div id="scanResults" class="mt-4" style="display: none;">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="bi bi-list-ul"></i> 掃描結果</h5>
                    </div>
                    <div class="card-body">
                        <div class="row mb-3">
                            <div class="col-md-4">
                                <div class="text-center">
                                    <h4 id="totalFiles" class="text-primary">0</h4>
                                    <small class="text-muted">找到檔案</small>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="text-center">
                                    <h4 id="totalSize" class="text-success">0 B</h4>
                                    <small class="text-muted">總大小</small>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="text-center">
                                    <button type="button" class="btn btn-danger" id="cleanupBtn">
                                        <i class="bi bi-trash3"></i> 執行清理
                                    </button>
                                </div>
                            </div>
                        </div>
                        
                        <div class="file-list">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>檔案路徑</th>
                                        <th>大小</th>
                                        <th>修改時間</th>
                                    </tr>
                                </thead>
                                <tbody id="fileList">
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 清理結果 -->
            <div id="cleanupResults" class="mt-4" style="display: none;">
                <div class="card border-success">
                    <div class="card-header bg-success text-white">
                        <h5 class="mb-0"><i class="bi bi-check-circle"></i> 清理完成</h5>
                    </div>
                    <div class="card-body">
                        <div class="row text-center">
                            <div class="col-md-3">
                                <h4 id="processedFiles" class="text-success">0</h4>
                                <small class="text-muted">已處理檔案</small>
                            </div>
                            <div class="col-md-3">
                                <h4 id="savedSpace" class="text-info">0 B</h4>
                                <small class="text-muted">節省空間</small>
                            </div>
                            <div class="col-md-3">
                                <h4 id="failedFiles" class="text-warning">0</h4>
                                <small class="text-muted">失敗檔案</small>
                            </div>
                            <div class="col-md-3">
                                <button type="button" class="btn btn-primary" id="downloadBtn" style="display: none;">
                                    <i class="bi bi-download"></i> 下載歸檔
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- 統計資訊 -->
    <section id="stats" class="py-5">
        <div class="container">
            <h2 class="text-center mb-5">系統統計</h2>
            <div class="row">
                <div class="col-md-3 mb-4">
                    <div class="card stats-card text-center">
                        <div class="card-body">
                            <i class="bi bi-activity display-4 mb-3"></i>
                            <h4 id="activeSessions">0</h4>
                            <p class="mb-0">活躍會話</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3 mb-4">
                    <div class="card stats-card text-center">
                        <div class="card-body">
                            <i class="bi bi-archive display-4 mb-3"></i>
                            <h4 id="totalArchives">0</h4>
                            <p class="mb-0">歸檔檔案</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3 mb-4">
                    <div class="card stats-card text-center">
                        <div class="card-body">
                            <i class="bi bi-hdd display-4 mb-3"></i>
                            <h4 id="archiveSize">0 B</h4>
                            <p class="mb-0">歸檔大小</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3 mb-4">
                    <div class="card stats-card text-center">
                        <div class="card-body">
                            <i class="bi bi-recycle display-4 mb-3"></i>
                            <h4 id="recycleSize">0 B</h4>
                            <p class="mb-0">回收站大小</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- 頁腳 -->
    <footer class="bg-dark text-white text-center py-4">
        <div class="container">
            <p class="mb-0">&copy; 2025 檔案清理大師. 智能清理，安全可靠.</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="/static/app.js"></script>
</body>
</html>'''
    
    with open(templates_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(index_html)
    
    print("✅ 網頁模板已創建")

def create_web_javascript():
    """創建JavaScript文件"""
    
    static_dir = Path("static")
    static_dir.mkdir(exist_ok=True)
    
    js_content = '''
// 檔案清理大師 - JavaScript
let currentSession = null;

// 頁面載入完成後初始化
document.addEventListener('DOMContentLoaded', function() {
    loadStats();
    setupEventListeners();
});

function setupEventListeners() {
    document.getElementById('scanBtn').addEventListener('click', scanFiles);
    document.getElementById('cleanupBtn').addEventListener('click', cleanupFiles);
    document.getElementById('downloadBtn').addEventListener('click', downloadArchive);
}

function scanFiles() {
    const folderPath = document.getElementById('folderPath').value;
    const daysToKeep = document.getElementById('daysToKeep').value;
    const includeSubfolders = document.getElementById('includeSubfolders').checked;
    
    if (!folderPath) {
        alert('請輸入資料夾路徑');
        return;
    }
    
    showProgress();
    
    fetch('/api/scan', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            folder_path: folderPath,
            days_to_keep: parseInt(daysToKeep),
            include_subfolders: includeSubfolders
        })
    })
    .then(response => response.json())
    .then(data => {
        hideProgress();
        if (data.error) {
            alert('錯誤: ' + data.error);
            return;
        }
        
        currentSession = data.session_id;
        displayScanResults(data);
    })
    .catch(error => {
        hideProgress();
        alert('掃描失敗: ' + error);
    });
}

function cleanupFiles() {
    if (!currentSession) {
        alert('請先掃描檔案');
        return;
    }
    
    const cleanupMode = document.getElementById('cleanupMode').value;
    
    if (cleanupMode === 'permanent') {
        if (!confirm('確定要永久刪除這些檔案嗎？此操作無法復原！')) {
            return;
        }
    }
    
    showProgress();
    
    fetch('/api/cleanup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: currentSession,
            cleanup_mode: cleanupMode
        })
    })
    .then(response => response.json())
    .then(data => {
        hideProgress();
        if (data.error) {
            alert('錯誤: ' + data.error);
            return;
        }
        
        displayCleanupResults(data.result);
        loadStats(); // 更新統計
    })
    .catch(error => {
        hideProgress();
        alert('清理失敗: ' + error);
    });
}

function downloadArchive() {
    if (!currentSession) {
        alert('沒有可下載的歸檔');
        return;
    }
    
    window.open('/api/download_archive/' + currentSession);
}

function displayScanResults(data) {
    document.getElementById('totalFiles').textContent = data.total_files;
    document.getElementById('totalSize').textContent = data.total_size_formatted;
    
    const fileList = document.getElementById('fileList');
    fileList.innerHTML = '';
    
    data.files.forEach(file => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td title="${file.path}">${truncatePath(file.path, 50)}</td>
            <td>${file.size_formatted}</td>
            <td>${file.modified_formatted}</td>
        `;
        fileList.appendChild(row);
    });
    
    if (data.files.length < data.total_files) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td colspan="3" class="text-center text-muted">
                ... 還有 ${data.total_files - data.files.length} 個檔案未顯示
            </td>
        `;
        fileList.appendChild(row);
    }
    
    document.getElementById('scanResults').style.display = 'block';
}

function displayCleanupResults(result) {
    document.getElementById('processedFiles').textContent = result.successfully_deleted;
    document.getElementById('savedSpace').textContent = result.total_size_freed_formatted;
    document.getElementById('failedFiles').textContent = result.failed_deletions;
    
    // 如果是歸檔模式，顯示下載按鈕
    if (result.mode === 'archive' && result.successfully_deleted > 0) {
        document.getElementById('downloadBtn').style.display = 'block';
    }
    
    document.getElementById('cleanupResults').style.display = 'block';
}

function loadStats() {
    fetch('/api/stats')
    .then(response => response.json())
    .then(data => {
        if (!data.error) {
            document.getElementById('activeSessions').textContent = data.active_sessions;
            document.getElementById('totalArchives').textContent = data.total_archives;
            document.getElementById('archiveSize').textContent = data.archive_folder_size_formatted;
            document.getElementById('recycleSize').textContent = data.recycle_folder_size_formatted;
        }
    })
    .catch(error => {
        console.error('載入統計失敗:', error);
    });
}

function showProgress() {
    document.querySelector('.progress-container').style.display = 'block';
    animateProgressBar();
}

function hideProgress() {
    document.querySelector('.progress-container').style.display = 'none';
}

function animateProgressBar() {
    const progressBar = document.querySelector('.progress-bar');
    let width = 0;
    const interval = setInterval(function() {
        if (width >= 90) {
            clearInterval(interval);
        } else {
            width += Math.random() * 10;
            progressBar.style.width = Math.min(width, 90) + '%';
        }
    }, 200);
}

function truncatePath(path, maxLength) {
    if (path.length <= maxLength) {
        return path;
    }
    return '...' + path.substring(path.length - maxLength + 3);
}

// 定時更新統計
setInterval(loadStats, 30000); // 每30秒更新一次
'''
    
    with open(static_dir / "app.js", "w", encoding="utf-8") as f:
        f.write(js_content)
    
    print("✅ JavaScript文件已創建")

def create_web_launcher():
    """創建網頁版啟動腳本"""
    
    launcher_content = '''@echo off
chcp 65001 >nul
title 檔案清理大師 - 網頁版啟動器

echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                          🌐 檔案清理大師 網頁版                            ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

echo 🔍 檢查環境...

REM 檢查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤：未找到 Python
    echo 請先安裝 Python: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python 可用

REM 檢查Flask
pip show flask >nul 2>&1
if errorlevel 1 (
    echo ⚠️  正在安裝 Flask...
    pip install flask
)
echo ✅ Flask 可用

echo.
echo 🚀 啟動網頁伺服器...
echo.
echo 📱 使用方法:
echo   • 伺服器啟動後會自動開啟瀏覽器
echo   • 如果沒有自動開啟，請手動訪問: http://localhost:5000
echo   • 按 Ctrl+C 可停止伺服器
echo.

REM 啟動Flask應用
start "" http://localhost:5000
python web_app.py

pause
'''
    
    with open("start_web.bat", "w", encoding="utf-8") as f:
        f.write(launcher_content)
    
    print("✅ 網頁版啟動腳本已創建: start_web.bat")

if __name__ == '__main__':
    # 創建模板和靜態文件
    create_web_templates()
    create_web_javascript()
    create_web_launcher()
    
    print("🌐 網頁版本準備完成！")
    print("使用方法：")
    print("  本機使用：雙擊 start_web.bat")
    print("  網絡共享：雙擊 start_network_web.bat")
    
    # 如果直接運行此腳本，啟動伺服器（允許外部訪問）
    print("🚀 啟動網絡伺服器...")
    print("🌍 允許外部設備訪問...")
    app.run(debug=False, host='0.0.0.0', port=5000)
