#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檔案清理工具 - 系統托盤版本
功能：常駐系統托盤的檔案清理工具，支援一鍵開關和自動清理
"""

import os
import sys
import time
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
from pathlib import Path
import schedule
from delete_file_regularly import FileCleanupTool

try:
    import pystray
    from PIL import Image, ImageDraw, ImageFont
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False
    print("警告：無法載入 pystray 或 PIL，將無法使用系統托盤功能")
    print("請執行：pip install pystray pillow")


class CleanupTrayApp:
    """檔案清理托盤應用程序"""
    
    def __init__(self):
        self.settings_file = Path("tray_settings.json")
        self.load_settings()
        self.cleaner = FileCleanupTool("INFO", use_recycle_bin=True, use_archive=True)
        self.is_running = True
        self.auto_cleanup_enabled = False
        self.main_window = None
        self.tray_icon = None
        
        # 設定定時器
        self.setup_scheduler()
        
        if TRAY_AVAILABLE:
            self.create_tray_icon()
        else:
            self.show_main_window()
    
    def load_settings(self):
        """載入設定"""
        default_settings = {
            "cleanup_paths": [],
            "cleanup_days": 30,
            "include_subfolders": True,
            "auto_cleanup_enabled": False,
            "cleanup_schedule": "daily",
            "cleanup_time": "02:00",
            "cleanup_mode": "archive",  # archive, safe, permanent
            "startup_minimized": True
        }
        
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = {**default_settings, **json.load(f)}
            else:
                self.settings = default_settings
                self.save_settings()
        except Exception:
            self.settings = default_settings
    
    def save_settings(self):
        """儲存設定"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"儲存設定失敗：{e}")
    
    def create_tray_icon(self):
        """創建托盤圖示"""
        # 創建圖示圖像
        image = self.create_icon_image()
        
        # 創建菜單
        menu = pystray.Menu(
            pystray.MenuItem("📦 檔案清理工具", self.show_main_window, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("🚀 立即清理", self.quick_cleanup),
            pystray.MenuItem("📁 管理歸檔", self.open_archive_manager),
            pystray.MenuItem("🔄 管理回收站", self.open_recovery_tool),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("⚙️ 設定", self.show_settings),
            pystray.MenuItem("📊 統計資訊", self.show_statistics),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "🤖 自動清理", 
                self.toggle_auto_cleanup,
                checked=lambda item: self.auto_cleanup_enabled
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("❌ 退出", self.quit_app)
        )
        
        # 創建托盤圖示
        self.tray_icon = pystray.Icon(
            "file_cleanup",
            image,
            "檔案清理工具",
            menu
        )
    
    def create_icon_image(self, size=64):
        """創建托盤圖示圖像"""
        # 創建圓形圖示
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # 背景圓形
        margin = 4
        draw.ellipse(
            [margin, margin, size-margin, size-margin],
            fill=(52, 152, 219, 255),  # 藍色
            outline=(41, 128, 185, 255),
            width=2
        )
        
        # 繪製掃帚圖示（清理象徵）
        center = size // 2
        
        # 掃帚柄
        draw.line(
            [center-8, center+8, center+8, center-8],
            fill=(255, 255, 255, 255),
            width=3
        )
        
        # 掃帚頭
        draw.arc(
            [center+4, center-12, center+16, center],
            start=0, end=180,
            fill=(255, 255, 255, 255),
            width=3
        )
        
        return image
    
    def run(self):
        """運行應用程序"""
        if TRAY_AVAILABLE and self.tray_icon:
            # 啟動定時器執行緒
            timer_thread = threading.Thread(target=self.run_scheduler, daemon=True)
            timer_thread.start()
            
            # 運行托盤圖示
            self.tray_icon.run()
        else:
            self.show_main_window()
            self.main_window.mainloop()
    
    def run_scheduler(self):
        """運行定時任務"""
        while self.is_running:
            if self.auto_cleanup_enabled:
                schedule.run_pending()
            time.sleep(60)  # 每分鐘檢查一次
    
    def setup_scheduler(self):
        """設定定時清理"""
        schedule.clear()
        if self.settings["auto_cleanup_enabled"]:
            cleanup_time = self.settings["cleanup_time"]
            if self.settings["cleanup_schedule"] == "daily":
                schedule.every().day.at(cleanup_time).do(self.scheduled_cleanup)
            elif self.settings["cleanup_schedule"] == "weekly":
                schedule.every().week.at(cleanup_time).do(self.scheduled_cleanup)
    
    def scheduled_cleanup(self):
        """定時自動清理"""
        try:
            for path in self.settings["cleanup_paths"]:
                if Path(path).exists():
                    result = self.cleaner.cleanup_files(
                        path,
                        self.settings["cleanup_days"],
                        self.settings["include_subfolders"],
                        dry_run=False
                    )
                    
                    # 記錄清理結果
                    if result["successfully_deleted"] > 0:
                        self.log_cleanup_result(path, result)
        except Exception as e:
            print(f"自動清理失敗：{e}")
    
    def log_cleanup_result(self, path, result):
        """記錄清理結果"""
        log_file = Path("cleanup_log.txt")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now()}: 自動清理 {path}, "
                   f"處理 {result['successfully_deleted']} 個檔案\n")
    
    def show_main_window(self, icon=None, item=None):
        """顯示主視窗"""
        if self.main_window and self.main_window.winfo_exists():
            self.main_window.deiconify()
            self.main_window.lift()
            return
        
        self.create_main_window()
    
    def create_main_window(self):
        """創建主視窗"""
        self.main_window = tk.Toplevel() if hasattr(self, 'root') else tk.Tk()
        self.main_window.title("檔案清理工具 - 控制面板")
        self.main_window.geometry("700x500")
        self.main_window.minsize(600, 400)
        
        # 設定視窗關閉事件
        self.main_window.protocol("WM_DELETE_WINDOW", self.hide_main_window)
        
        # 創建筆記本控件
        notebook = ttk.Notebook(self.main_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 清理標籤頁
        self.create_cleanup_tab(notebook)
        
        # 設定標籤頁
        self.create_settings_tab(notebook)
        
        # 統計標籤頁
        self.create_statistics_tab(notebook)
        
        # 日誌標籤頁
        self.create_log_tab(notebook)
    
    def create_cleanup_tab(self, notebook):
        """創建清理標籤頁"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="🧹 檔案清理")
        
        # 標題
        title_label = ttk.Label(frame, text="檔案清理控制", font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # 路徑選擇框架
        path_frame = ttk.LabelFrame(frame, text="清理路徑", padding=10)
        path_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 路徑列表
        self.path_listbox = tk.Listbox(path_frame, height=4)
        self.path_listbox.pack(fill=tk.X, pady=(0, 5))
        
        # 路徑按鈕
        path_buttons = ttk.Frame(path_frame)
        path_buttons.pack(fill=tk.X)
        
        ttk.Button(path_buttons, text="➕ 新增路徑", command=self.add_path).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(path_buttons, text="➖ 移除路徑", command=self.remove_path).pack(side=tk.LEFT, padx=(0, 5))
        
        # 清理選項框架
        options_frame = ttk.LabelFrame(frame, text="清理選項", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 保留天數
        days_frame = ttk.Frame(options_frame)
        days_frame.pack(fill=tk.X, pady=2)
        ttk.Label(days_frame, text="保留天數：").pack(side=tk.LEFT)
        self.days_var = tk.StringVar(value=str(self.settings["cleanup_days"]))
        ttk.Entry(days_frame, textvariable=self.days_var, width=10).pack(side=tk.LEFT, padx=(5, 0))
        
        # 包含子資料夾
        self.subfolder_var = tk.BooleanVar(value=self.settings["include_subfolders"])
        ttk.Checkbutton(options_frame, text="包含子資料夾", variable=self.subfolder_var).pack(anchor=tk.W, pady=2)
        
        # 清理模式
        mode_frame = ttk.Frame(options_frame)
        mode_frame.pack(fill=tk.X, pady=2)
        ttk.Label(mode_frame, text="清理模式：").pack(side=tk.LEFT)
        self.mode_var = tk.StringVar(value=self.settings["cleanup_mode"])
        mode_combo = ttk.Combobox(mode_frame, textvariable=self.mode_var, values=["archive", "safe", "permanent"], 
                                 state="readonly", width=15)
        mode_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # 清理按鈕框架
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="🔍 預覽清理", command=self.preview_cleanup, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="🚀 開始清理", command=self.start_cleanup, 
                  style="Accent.TButton").pack(side=tk.LEFT)
        
        # 更新路徑列表
        self.update_path_list()
    
    def create_settings_tab(self, notebook):
        """創建設定標籤頁"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="⚙️ 設定")
        
        # 自動清理設定
        auto_frame = ttk.LabelFrame(frame, text="自動清理設定", padding=10)
        auto_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.auto_enabled_var = tk.BooleanVar(value=self.settings["auto_cleanup_enabled"])
        ttk.Checkbutton(auto_frame, text="啟用自動清理", variable=self.auto_enabled_var,
                       command=self.update_auto_cleanup).pack(anchor=tk.W, pady=2)
        
        # 清理時間
        time_frame = ttk.Frame(auto_frame)
        time_frame.pack(fill=tk.X, pady=5)
        ttk.Label(time_frame, text="清理時間：").pack(side=tk.LEFT)
        self.time_var = tk.StringVar(value=self.settings["cleanup_time"])
        ttk.Entry(time_frame, textvariable=self.time_var, width=10).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(time_frame, text="(24小時格式，例：14:30)").pack(side=tk.LEFT, padx=(5, 0))
        
        # 清理頻率
        freq_frame = ttk.Frame(auto_frame)
        freq_frame.pack(fill=tk.X, pady=5)
        ttk.Label(freq_frame, text="清理頻率：").pack(side=tk.LEFT)
        self.schedule_var = tk.StringVar(value=self.settings["cleanup_schedule"])
        schedule_combo = ttk.Combobox(freq_frame, textvariable=self.schedule_var, 
                                    values=["daily", "weekly"], state="readonly", width=15)
        schedule_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # 儲存設定按鈕
        ttk.Button(auto_frame, text="💾 儲存設定", command=self.save_all_settings).pack(pady=10)
        
        # 應用程序設定
        app_frame = ttk.LabelFrame(frame, text="應用程序設定", padding=10)
        app_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.startup_min_var = tk.BooleanVar(value=self.settings["startup_minimized"])
        ttk.Checkbutton(app_frame, text="啟動時最小化到托盤", variable=self.startup_min_var).pack(anchor=tk.W, pady=2)
        
        # 工具按鈕
        tools_frame = ttk.LabelFrame(frame, text="工具", padding=10)
        tools_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tool_buttons = ttk.Frame(tools_frame)
        tool_buttons.pack(fill=tk.X)
        
        ttk.Button(tool_buttons, text="📤 歸檔管理器", command=self.open_archive_manager).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(tool_buttons, text="🔄 回收站管理", command=self.open_recovery_tool).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(tool_buttons, text="📁 開啟設定檔案夾", command=self.open_settings_folder).pack(side=tk.LEFT)
    
    def create_statistics_tab(self, notebook):
        """創建統計標籤頁"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="📊 統計")
        
        # 統計資訊將在這裡顯示
        self.stats_text = tk.Text(frame, wrap=tk.WORD, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=scrollbar.set)
        
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)
        
        # 重新整理按鈕
        refresh_btn = ttk.Button(frame, text="🔄 重新整理", command=self.update_statistics)
        refresh_btn.pack(side=tk.BOTTOM, padx=10, pady=10)
        
        self.update_statistics()
    
    def create_log_tab(self, notebook):
        """創建日誌標籤頁"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="📝 日誌")
        
        # 日誌顯示區域
        self.log_text = tk.Text(frame, wrap=tk.WORD, state=tk.DISABLED)
        log_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)
        
        # 清除日誌按鈕
        clear_btn = ttk.Button(frame, text="🗑️ 清除日誌", command=self.clear_log)
        clear_btn.pack(side=tk.BOTTOM, padx=10, pady=10)
        
        self.load_log()
    
    def add_path(self):
        """新增清理路徑"""
        path = filedialog.askdirectory(title="選擇要清理的資料夾")
        if path and path not in self.settings["cleanup_paths"]:
            self.settings["cleanup_paths"].append(path)
            self.update_path_list()
            self.save_settings()
    
    def remove_path(self):
        """移除清理路徑"""
        selection = self.path_listbox.curselection()
        if selection:
            index = selection[0]
            del self.settings["cleanup_paths"][index]
            self.update_path_list()
            self.save_settings()
    
    def update_path_list(self):
        """更新路徑列表"""
        self.path_listbox.delete(0, tk.END)
        for path in self.settings["cleanup_paths"]:
            self.path_listbox.insert(tk.END, path)
    
    def preview_cleanup(self):
        """預覽清理"""
        self.run_cleanup(dry_run=True)
    
    def start_cleanup(self):
        """開始清理"""
        if messagebox.askyesno("確認", "確定要開始清理嗎？"):
            self.run_cleanup(dry_run=False)
    
    def run_cleanup(self, dry_run=True):
        """執行清理"""
        if not self.settings["cleanup_paths"]:
            messagebox.showwarning("警告", "請先新增清理路徑")
            return
        
        try:
            days = int(self.days_var.get())
            mode = self.mode_var.get()
            
            # 更新清理器設定
            use_archive = mode == "archive"
            use_recycle_bin = mode == "safe"
            self.cleaner = FileCleanupTool("INFO", use_recycle_bin, use_archive)
            
            # 執行清理
            total_files = 0
            total_size = 0
            
            for path in self.settings["cleanup_paths"]:
                if Path(path).exists():
                    result = self.cleaner.cleanup_files(
                        path, days, self.subfolder_var.get(), dry_run
                    )
                    total_files += result["successfully_deleted"]
                    total_size += result["total_size_freed"]
            
            # 顯示結果
            action = "預覽" if dry_run else "清理"
            size_text = self.cleaner.format_file_size(total_size)
            messagebox.showinfo("完成", f"{action}完成！\n處理檔案：{total_files} 個\n處理大小：{size_text}")
            
        except ValueError:
            messagebox.showerror("錯誤", "請輸入有效的保留天數")
        except Exception as e:
            messagebox.showerror("錯誤", f"清理失敗：{e}")
    
    def update_auto_cleanup(self):
        """更新自動清理設定"""
        self.auto_cleanup_enabled = self.auto_enabled_var.get()
        if self.auto_cleanup_enabled:
            self.setup_scheduler()
    
    def save_all_settings(self):
        """儲存所有設定"""
        try:
            self.settings["cleanup_days"] = int(self.days_var.get())
            self.settings["include_subfolders"] = self.subfolder_var.get()
            self.settings["cleanup_mode"] = self.mode_var.get()
            self.settings["auto_cleanup_enabled"] = self.auto_enabled_var.get()
            self.settings["cleanup_time"] = self.time_var.get()
            self.settings["cleanup_schedule"] = self.schedule_var.get()
            self.settings["startup_minimized"] = self.startup_min_var.get()
            
            self.save_settings()
            self.setup_scheduler()
            messagebox.showinfo("成功", "設定已儲存")
        except ValueError:
            messagebox.showerror("錯誤", "請檢查輸入的數值")
    
    def update_statistics(self):
        """更新統計資訊"""
        stats = []
        stats.append("=== 檔案清理工具統計資訊 ===\n")
        stats.append(f"更新時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # 設定統計
        stats.append("📋 當前設定：\n")
        stats.append(f"  清理路徑數量：{len(self.settings['cleanup_paths'])}\n")
        stats.append(f"  保留天數：{self.settings['cleanup_days']} 天\n")
        stats.append(f"  清理模式：{self.settings['cleanup_mode']}\n")
        stats.append(f"  自動清理：{'啟用' if self.settings['auto_cleanup_enabled'] else '停用'}\n\n")
        
        # 歸檔統計
        if Path("archived_files").exists():
            stats.append("📦 歸檔統計：\n")
            archive_files = list(Path("archived_files").glob("*.zip"))
            stats.append(f"  歸檔檔案數量：{len(archive_files)}\n")
            
            total_size = sum(f.stat().st_size for f in archive_files)
            stats.append(f"  歸檔總大小：{self.cleaner.format_file_size(total_size)}\n\n")
        
        # 回收站統計
        if Path("recycle_bin").exists():
            stats.append("🗑️ 回收站統計：\n")
            recycle_files = list(Path("recycle_bin").glob("*"))
            # 排除日誌檔案
            recycle_files = [f for f in recycle_files if f.suffix != '.json']
            stats.append(f"  回收站檔案數量：{len(recycle_files)}\n")
            
            if recycle_files:
                total_size = sum(f.stat().st_size for f in recycle_files if f.is_file())
                stats.append(f"  回收站總大小：{self.cleaner.format_file_size(total_size)}\n")
        
        # 更新顯示
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, ''.join(stats))
        self.stats_text.config(state=tk.DISABLED)
    
    def load_log(self):
        """載入日誌"""
        log_file = Path("cleanup_log.txt")
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                
                self.log_text.config(state=tk.NORMAL)
                self.log_text.delete(1.0, tk.END)
                self.log_text.insert(tk.END, log_content)
                self.log_text.config(state=tk.DISABLED)
            except Exception as e:
                print(f"載入日誌失敗：{e}")
    
    def clear_log(self):
        """清除日誌"""
        if messagebox.askyesno("確認", "確定要清除所有日誌嗎？"):
            log_file = Path("cleanup_log.txt")
            if log_file.exists():
                log_file.unlink()
            
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)
            self.log_text.config(state=tk.DISABLED)
    
    def hide_main_window(self):
        """隱藏主視窗"""
        if self.main_window:
            self.main_window.withdraw()
    
    def show_settings(self, icon=None, item=None):
        """顯示設定"""
        self.show_main_window()
        # TODO: 切換到設定標籤頁
    
    def show_statistics(self, icon=None, item=None):
        """顯示統計"""
        self.show_main_window()
        # TODO: 切換到統計標籤頁
    
    def quick_cleanup(self, icon=None, item=None):
        """快速清理"""
        if not self.settings["cleanup_paths"]:
            if TRAY_AVAILABLE and self.tray_icon:
                self.tray_icon.notify("請先設定清理路徑", "檔案清理工具")
            return
        
        try:
            # 執行快速清理
            total_files = 0
            mode = self.settings["cleanup_mode"]
            use_archive = mode == "archive"
            use_recycle_bin = mode == "safe"
            cleaner = FileCleanupTool("INFO", use_recycle_bin, use_archive)
            
            for path in self.settings["cleanup_paths"]:
                if Path(path).exists():
                    result = cleaner.cleanup_files(
                        path, self.settings["cleanup_days"], 
                        self.settings["include_subfolders"], False
                    )
                    total_files += result["successfully_deleted"]
            
            # 通知結果
            if TRAY_AVAILABLE and self.tray_icon:
                self.tray_icon.notify(f"清理完成：處理 {total_files} 個檔案", "檔案清理工具")
            
        except Exception as e:
            if TRAY_AVAILABLE and self.tray_icon:
                self.tray_icon.notify(f"清理失敗：{e}", "檔案清理工具")
    
    def toggle_auto_cleanup(self, icon=None, item=None):
        """切換自動清理"""
        self.auto_cleanup_enabled = not self.auto_cleanup_enabled
        self.settings["auto_cleanup_enabled"] = self.auto_cleanup_enabled
        self.save_settings()
        
        if self.auto_cleanup_enabled:
            self.setup_scheduler()
            if TRAY_AVAILABLE and self.tray_icon:
                self.tray_icon.notify("自動清理已啟用", "檔案清理工具")
        else:
            schedule.clear()
            if TRAY_AVAILABLE and self.tray_icon:
                self.tray_icon.notify("自動清理已停用", "檔案清理工具")
    
    def open_archive_manager(self, icon=None, item=None):
        """開啟歸檔管理器"""
        try:
            os.system("python file_archive_manager.py")
        except Exception as e:
            print(f"開啟歸檔管理器失敗：{e}")
    
    def open_recovery_tool(self, icon=None, item=None):
        """開啟回收站工具"""
        try:
            os.system("python file_recovery.py")
        except Exception as e:
            print(f"開啟回收站工具失敗：{e}")
    
    def open_settings_folder(self):
        """開啟設定檔案夾"""
        try:
            os.startfile(Path.cwd())
        except Exception as e:
            print(f"開啟設定檔案夾失敗：{e}")
    
    def quit_app(self, icon=None, item=None):
        """退出應用程序"""
        self.is_running = False
        if self.tray_icon:
            self.tray_icon.stop()
        if self.main_window:
            self.main_window.quit()


def main():
    """主程式"""
    app = CleanupTrayApp()
    
    try:
        app.run()
    except KeyboardInterrupt:
        print("程式被使用者中斷")
    except Exception as e:
        print(f"程式執行錯誤：{e}")
    finally:
        app.is_running = False


if __name__ == "__main__":
    main()
