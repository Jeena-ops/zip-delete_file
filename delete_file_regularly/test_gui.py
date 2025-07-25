#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檔案自動清理工具 - 測試版本
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path

# 簡單測試 GUI
def test_gui():
    root = tk.Tk()
    root.title("檔案清理工具測試")
    root.geometry("400x200")
    
    frame = ttk.Frame(root, padding="20")
    frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(frame, text="檔案自動清理工具", font=("TkDefaultFont", 14, "bold")).pack(pady=10)
    ttk.Label(frame, text="GUI 測試成功！", font=("TkDefaultFont", 10)).pack(pady=5)
    
    def test_import():
        try:
            import pystray
            import PIL
            import schedule
            from delete_file_regularly import FileCleanupTool
            messagebox.showinfo("成功", "所有模組導入成功！\n準備啟動完整版本...")
            root.destroy()
            # 啟動完整 GUI
            import file_cleanup_gui
            app = file_cleanup_gui.FileCleanupGUI()
            app.run()
        except ImportError as e:
            messagebox.showerror("錯誤", f"模組導入失敗：{e}")
        except Exception as e:
            messagebox.showerror("錯誤", f"啟動失敗：{e}")
    
    ttk.Button(frame, text="測試完整功能", command=test_import).pack(pady=10)
    ttk.Button(frame, text="退出", command=root.quit).pack(pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    test_gui()
