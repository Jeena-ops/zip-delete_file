
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
