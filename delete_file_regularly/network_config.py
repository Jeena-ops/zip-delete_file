#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
網絡配置管理工具
讓檔案清理大師網頁版能被所有人訪問
"""

import socket
import subprocess
import sys
from pathlib import Path

def get_local_ip():
    """獲取本機IP地址"""
    try:
        # 連接到外部地址來獲取本機IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def check_firewall_status():
    """檢查Windows防火牆狀態"""
    try:
        result = subprocess.run(
            ['netsh', 'advfirewall', 'show', 'allprofiles', 'state'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        return "ON" in result.stdout.upper()
    except Exception:
        return None

def add_firewall_rule():
    """添加防火牆規則允許5000端口"""
    try:
        # 檢查是否已存在規則
        check_cmd = [
            'netsh', 'advfirewall', 'firewall', 'show', 'rule', 
            'name="檔案清理大師網頁版"'
        ]
        result = subprocess.run(check_cmd, capture_output=True, text=True, encoding='utf-8')
        
        if "檔案清理大師網頁版" not in result.stdout:
            # 添加新規則
            add_cmd = [
                'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                'name=檔案清理大師網頁版',
                'dir=in',
                'action=allow',
                'protocol=TCP',
                'localport=5000'
            ]
            
            result = subprocess.run(add_cmd, capture_output=True, text=True)
            return result.returncode == 0
        else:
            return True  # 規則已存在
    except Exception as e:
        print(f"❌ 防火牆配置失敗: {e}")
        return False

def create_network_launcher():
    """創建支持網絡訪問的啟動腳本"""
    local_ip = get_local_ip()
    
    launcher_content = f'''@echo off
chcp 65001 >nul
echo 🌐 檔案清理大師 - 網頁版啟動器
echo ================================================
echo.

echo 📡 檢測網絡配置...
echo 本機IP地址: {local_ip}
echo.

echo 🔥 檢查防火牆設置...
'''

    # 檢查Python是否安裝
    launcher_content += '''
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤: 未找到Python
    echo 請先安裝Python 3.7或更新版本
    pause
    exit /b 1
)

echo ✅ Python已安裝

echo 📦 檢查依賴包...
python -c "import flask, werkzeug" >nul 2>&1
if errorlevel 1 (
    echo 🔧 正在安裝必要的依賴包...
    pip install flask werkzeug pillow schedule
    if errorlevel 1 (
        echo ❌ 依賴包安裝失敗
        pause
        exit /b 1
    )
)

echo ✅ 所有依賴已就緒

echo.
echo 🚀 啟動網頁伺服器...
echo ================================================
'''

    launcher_content += f'''echo.
echo 📌 訪問地址:
echo    本機訪問: http://localhost:5000
echo    網絡訪問: http://{local_ip}:5000
echo.
echo 💡 讓其他人訪問的方法:
echo    1. 確保防火牆允許5000端口
echo    2. 告訴其他人訪問: http://{local_ip}:5000
echo    3. 如果在公司/學校網絡，可能需要IT管理員協助
echo.
echo 🛑 按 Ctrl+C 停止伺服器
echo ================================================
echo.

rem 自動打開瀏覽器
timeout /t 3 /nobreak >nul
start http://localhost:5000

rem 啟動Flask應用
python web_app.py

pause
'''
    
    with open("start_network_web.bat", "w", encoding="utf-8") as f:
        f.write(launcher_content)
    
    return local_ip

def show_network_info():
    """顯示網絡配置信息"""
    local_ip = get_local_ip()
    firewall_status = check_firewall_status()
    
    print("🌐 網絡配置信息")
    print("=" * 50)
    print(f"📍 本機IP地址: {local_ip}")
    print(f"🔥 防火牆狀態: {'開啟' if firewall_status else '關閉' if firewall_status is False else '未知'}")
    print()
    
    print("📌 訪問地址:")
    print(f"   本機訪問: http://localhost:5000")
    print(f"   網絡訪問: http://{local_ip}:5000")
    print()
    
    print("🌍 讓其他人訪問的方法:")
    print("1. 📱 同一WiFi網絡下的設備:")
    print(f"   直接訪問: http://{local_ip}:5000")
    print()
    print("2. 🖥️ 其他網絡的設備:")
    print("   需要進行端口轉發或使用公網IP")
    print("   (需要路由器管理員權限)")
    print()
    print("3. ☁️ 最簡單的方法:")
    print("   部署到雲端伺服器 (如阿里雲、騰訊雲)")
    print()
    
    if firewall_status:
        print("⚠️ 檢測到防火牆已開啟")
        print("如果其他人無法訪問，請運行:")
        print("   python network_config.py --add-firewall-rule")
        print()

def main():
    """主函數"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--add-firewall-rule':
            print("🔥 正在配置防火牆規則...")
            if add_firewall_rule():
                print("✅ 防火牆規則添加成功")
            else:
                print("❌ 防火牆規則添加失敗，請以管理員身份運行")
            return
        elif sys.argv[1] == '--create-launcher':
            local_ip = create_network_launcher()
            print(f"✅ 網絡啟動腳本已創建: start_network_web.bat")
            print(f"📡 其他人可通過 http://{local_ip}:5000 訪問")
            return
    
    show_network_info()
    
    print("🛠️ 可用命令:")
    print("   python network_config.py --add-firewall-rule  # 添加防火牆規則")
    print("   python network_config.py --create-launcher     # 創建網絡啟動腳本")

if __name__ == '__main__':
    main()
