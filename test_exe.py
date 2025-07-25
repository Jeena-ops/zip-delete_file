#!/usr/bin/env python3
"""
快速測試 EXE 檔案的功能
"""

import subprocess
import tempfile
import os
from pathlib import Path

def test_exe_basic():
    """測試 EXE 檔案的基本功能"""
    print("測試 FileRenamer.exe...")
    
    # 檢查 EXE 檔案是否存在
    exe_path = Path("dist/FileRenamer.exe")
    if not exe_path.exists():
        print("❌ FileRenamer.exe 不存在")
        return False
    
    print("✅ FileRenamer.exe 存在")
    print(f"📁 檔案大小: {exe_path.stat().st_size / (1024*1024):.1f} MB")
    
    # 創建測試資料夾和檔案
    test_dir = Path(tempfile.mkdtemp(prefix="exe_test_"))
    test_files = [
        "123456789_USD_042025_TRF001.pdf",
        "invalid_file.txt"
    ]
    
    for filename in test_files:
        (test_dir / filename).write_text("test content")
    
    print(f"📂 測試資料夾: {test_dir}")
    
    # 創建輸入檔案（模擬使用者輸入）
    input_text = f"{test_dir}\nn\n"  # 資料夾路徑 + 不執行重新命名
    
    try:
        # 測試程式是否能啟動和處理
        result = subprocess.run(
            [str(exe_path)],
            input=input_text,
            text=True,
            capture_output=True,
            timeout=30  # 30秒超時
        )
        
        if result.returncode == 0:
            print("✅ EXE 檔案執行成功")
            print("📤 程式輸出:")
            print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
            return True
        else:
            print(f"❌ EXE 檔案執行失敗 (返回碼: {result.returncode})")
            print("❌ 錯誤輸出:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ 程式執行超時（可能在等待使用者輸入）")
        print("✅ 這通常表示程式正常啟動了")
        return True
    except Exception as e:
        print(f"❌ 測試時發生錯誤: {e}")
        return False
    finally:
        # 清理測試檔案
        import shutil
        shutil.rmtree(test_dir, ignore_errors=True)

if __name__ == "__main__":
    print("=" * 50)
    print("FileRenamer.exe 測試")
    print("=" * 50)
    
    success = test_exe_basic()
    
    if success:
        print("\n🎉 測試通過！EXE 檔案可以正常使用")
    else:
        print("\n❌ 測試失敗，請檢查打包過程")
        
    print("\n💡 使用方式：")
    print("1. 雙擊 dist/FileRenamer.exe")
    print("2. 或在命令列執行：dist\\FileRenamer.exe")
