#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檔案自動清理工具 - GUI 版本
功能：圖形化介面的檔案清理工具，支援系統托盤和定時清理
支援：Windows 平台，長時間運行
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
import json
import schedule
from delete_file_regularly import FileCleanupTool

try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False


class FileCleanupGUI:
    """檔案清理工具 GUI 版本"""
    
    def __init__(self):
        """初始化 GUI"""
        self.root = tk.Tk()
        self.setup_window()
        self.load_settings()
        self.create_widgets()
        self.cleaner = FileCleanupTool("INFO")
        self.tray = None
        self.is_running = True
        self.auto_cleanup_enabled = False
        self.setup_tray()
        
    def setup_window(self):
        """設定主視窗"""
        self.root.title("檔案自動清理工具 v2.0")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # 設定視窗圖示（如果可用）
        try:
            self.root.iconbitmap(default='cleanup.ico')
        except:
            pass
        
        # 設定視窗關閉事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def load_settings(self):
        """載入設定"""
        self.settings_file = Path("cleanup_settings.json")
        self.default_settings = {
            "last_folder": "",
            "default_days": 30,
            "include_subfolders": True,
            "auto_cleanup": False,
            "cleanup_schedule": "daily",
            "cleanup_time": "02:00",
            "minimize_to_tray": True
        }
        
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
            else:
                self.settings = self.default_settings.copy()
        except:
            self.settings = self.default_settings.copy()
    
    def save_settings(self):
        """儲存設定"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("錯誤", f"無法儲存設定：{e}")
    
    def create_widgets(self):
        """建立 GUI 元件"""
        # 創建主要框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 設定網格權重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 建立筆記本（分頁）
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        main_frame.rowconfigure(0, weight=1)
        
        # 手動清理分頁
        self.create_manual_tab()
        
        # 自動清理分頁
        self.create_auto_tab()
        
        # 日誌分頁
        self.create_log_tab()
        
        # 狀態列
        self.create_status_bar(main_frame)
        
        # 控制按鈕
        self.create_control_buttons(main_frame)
    
    def create_manual_tab(self):
        """建立手動清理分頁"""
        manual_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(manual_frame, text="手動清理")
        
        # 資料夾選擇
        ttk.Label(manual_frame, text="目標資料夾：").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        folder_frame = ttk.Frame(manual_frame)
        folder_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        folder_frame.columnconfigure(0, weight=1)
        
        self.folder_var = tk.StringVar(value=self.settings.get("last_folder", ""))
        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_var, font=("Consolas", 9))
        self.folder_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(folder_frame, text="瀏覽", command=self.browse_folder).grid(row=0, column=1)
        
        # 保留天數
        ttk.Label(manual_frame, text="保留天數：").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        days_frame = ttk.Frame(manual_frame)
        days_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.days_var = tk.StringVar(value=str(self.settings.get("default_days", 30)))
        self.days_spinbox = ttk.Spinbox(days_frame, from_=0, to=3650, textvariable=self.days_var, width=10)
        self.days_spinbox.grid(row=0, column=0, padx=(0, 10))
        
        ttk.Label(days_frame, text="天（超過此天數的檔案將被刪除）").grid(row=0, column=1, sticky=tk.W)
        
        # 選項
        options_frame = ttk.LabelFrame(manual_frame, text="清理選項", padding="10")
        options_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.include_sub_var = tk.BooleanVar(value=self.settings.get("include_subfolders", True))
        ttk.Checkbutton(options_frame, text="包含子資料夾", variable=self.include_sub_var).grid(row=0, column=0, sticky=tk.W)
        
        # 操作按鈕
        button_frame = ttk.Frame(manual_frame)
        button_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(button_frame, text="預覽清理", command=self.preview_cleanup, style="Accent.TButton").grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="執行清理", command=self.execute_cleanup).grid(row=0, column=1, padx=(5, 0))
        
        # 結果顯示
        result_frame = ttk.LabelFrame(manual_frame, text="清理結果", padding="10")
        result_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        manual_frame.rowconfigure(6, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        self.result_text = scrolledtext.ScrolledText(result_frame, height=10, font=("Consolas", 9))
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def create_auto_tab(self):
        """建立自動清理分頁"""
        auto_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(auto_frame, text="自動清理")
        
        # 自動清理開關
        ttk.Label(auto_frame, text="自動清理功能：", font=("TkDefaultFont", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        self.auto_enabled_var = tk.BooleanVar(value=self.settings.get("auto_cleanup", False))
        auto_switch = ttk.Checkbutton(auto_frame, text="啟用自動清理", variable=self.auto_enabled_var, command=self.toggle_auto_cleanup)
        auto_switch.grid(row=1, column=0, sticky=tk.W, pady=(0, 20))
        
        # 自動清理設定
        settings_frame = ttk.LabelFrame(auto_frame, text="自動清理設定", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 排程設定
        ttk.Label(settings_frame, text="清理頻率：").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.schedule_var = tk.StringVar(value=self.settings.get("cleanup_schedule", "daily"))
        schedule_combo = ttk.Combobox(settings_frame, textvariable=self.schedule_var, 
                                    values=["daily", "weekly", "monthly"], state="readonly", width=15)
        schedule_combo.grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        # 時間設定
        ttk.Label(settings_frame, text="清理時間：").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        time_frame = ttk.Frame(settings_frame)
        time_frame.grid(row=3, column=0, sticky=tk.W, pady=(0, 10))
        
        self.time_var = tk.StringVar(value=self.settings.get("cleanup_time", "02:00"))
        time_entry = ttk.Entry(time_frame, textvariable=self.time_var, width=10)
        time_entry.grid(row=0, column=0, padx=(0, 5))
        ttk.Label(time_frame, text="(格式: HH:MM)").grid(row=0, column=1, sticky=tk.W)
        
        # 自動清理記錄
        log_frame = ttk.LabelFrame(auto_frame, text="自動清理記錄", padding="10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        auto_frame.rowconfigure(3, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.auto_log_text = scrolledtext.ScrolledText(log_frame, height=15, font=("Consolas", 9))
        self.auto_log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 載入自動清理記錄
        self.load_auto_log()
    
    def create_log_tab(self):
        """建立日誌分頁"""
        log_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(log_frame, text="系統日誌")
        
        # 日誌控制
        control_frame = ttk.Frame(log_frame)
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(control_frame, text="重新整理", command=self.refresh_log).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(control_frame, text="清除日誌", command=self.clear_log).grid(row=0, column=1, padx=(5, 0))
        
        # 日誌顯示
        log_display_frame = ttk.LabelFrame(log_frame, text="系統日誌", padding="10")
        log_display_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.rowconfigure(1, weight=1)
        log_display_frame.columnconfigure(0, weight=1)
        log_display_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_display_frame, height=20, font=("Consolas", 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 載入日誌
        self.refresh_log()
    
    def create_status_bar(self, parent):
        """建立狀態列"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        status_frame.columnconfigure(1, weight=1)
        
        self.status_var = tk.StringVar(value="就緒")
        ttk.Label(status_frame, text="狀態：").grid(row=0, column=0, sticky=tk.W)
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
        self.status_label.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # 自動清理狀態
        self.auto_status_var = tk.StringVar()
        self.auto_status_label = ttk.Label(status_frame, textvariable=self.auto_status_var, foreground="green")
        self.auto_status_label.grid(row=0, column=2, sticky=tk.E)
        self.update_auto_status()
    
    def create_control_buttons(self, parent):
        """建立控制按鈕"""
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Button(control_frame, text="最小化到托盤", command=self.minimize_to_tray).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(control_frame, text="設定", command=self.open_settings).grid(row=0, column=1, padx=(5, 5))
        ttk.Button(control_frame, text="關於", command=self.show_about).grid(row=0, column=2, padx=(5, 5))
        ttk.Button(control_frame, text="退出", command=self.quit_app).grid(row=0, column=3, padx=(5, 0))
    
    def browse_folder(self):
        """瀏覽資料夾"""
        folder = filedialog.askdirectory(
            title="選擇要清理的資料夾",
            initialdir=self.folder_var.get() or os.path.expanduser("~")
        )
        if folder:
            self.folder_var.set(folder)
            self.settings["last_folder"] = folder
            self.save_settings()
    
    def preview_cleanup(self):
        """預覽清理"""
        self.run_cleanup(dry_run=True)
    
    def execute_cleanup(self):
        """執行清理"""
        if not self.validate_inputs():
            return
        
        # 確認對話框
        result = messagebox.askyesno(
            "確認清理",
            "確定要執行檔案清理嗎？\n\n警告：刪除的檔案無法復原！",
            icon="warning"
        )
        
        if result:
            self.run_cleanup(dry_run=False)
    
    def validate_inputs(self):
        """驗證輸入"""
        folder = self.folder_var.get().strip()
        if not folder:
            messagebox.showerror("錯誤", "請選擇目標資料夾")
            return False
        
        if not Path(folder).exists():
            messagebox.showerror("錯誤", "目標資料夾不存在")
            return False
        
        try:
            days = int(self.days_var.get())
            if days < 0:
                messagebox.showerror("錯誤", "保留天數不能為負數")
                return False
        except ValueError:
            messagebox.showerror("錯誤", "請輸入有效的天數")
            return False
        
        return True
    
    def run_cleanup(self, dry_run=True):
        """執行清理（在背景執行緒中）"""
        if not self.validate_inputs():
            return
        
        # 更新狀態
        action = "預覽" if dry_run else "執行"
        self.status_var.set(f"正在{action}清理...")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"開始{action}清理...\n")
        self.root.update()
        
        # 在背景執行緒中執行
        def cleanup_thread():
            try:
                folder = self.folder_var.get().strip()
                days = int(self.days_var.get())
                include_sub = self.include_sub_var.get()
                
                # 執行清理
                result = self.cleaner.cleanup_files(folder, days, include_sub, dry_run)
                
                # 更新 UI
                self.root.after(0, lambda: self.display_cleanup_result(result, dry_run))
                
            except Exception as e:
                error_msg = f"清理過程中發生錯誤：{e}"
                self.root.after(0, lambda: self.display_error(error_msg))
        
        threading.Thread(target=cleanup_thread, daemon=True).start()
    
    def display_cleanup_result(self, result, dry_run):
        """顯示清理結果"""
        action = "預覽" if dry_run else "清理"
        
        # 清除之前的結果
        self.result_text.delete(1.0, tk.END)
        
        # 顯示結果摘要
        self.result_text.insert(tk.END, f"{action}結果摘要\n")
        self.result_text.insert(tk.END, "=" * 50 + "\n")
        self.result_text.insert(tk.END, f"發現過期檔案：{result['total_found']} 個\n")
        
        if not dry_run:
            self.result_text.insert(tk.END, f"成功刪除：{result['successfully_deleted']} 個\n")
            self.result_text.insert(tk.END, f"刪除失敗：{result['failed_deletions']} 個\n")
            self.result_text.insert(tk.END, f"釋放空間：{self.cleaner.format_file_size(result['total_size_freed'])}\n")
        
        self.result_text.insert(tk.END, "=" * 50 + "\n\n")
        
        # 顯示詳細檔案清單
        if result['total_found'] > 0:
            if dry_run:
                self.result_text.insert(tk.END, "預覽要刪除的檔案：\n")
            else:
                self.result_text.insert(tk.END, "已刪除的檔案：\n")
            
            files_to_show = result.get('deleted_files', []) if not dry_run else []
            if dry_run:
                # 從 cleaner 獲取找到的檔案
                folder = self.folder_var.get().strip()
                days = int(self.days_var.get())
                include_sub = self.include_sub_var.get()
                try:
                    validated_path = self.cleaner.validate_path(folder)
                    expired_files = self.cleaner.find_expired_files(validated_path, days, include_sub)
                    files_to_show = expired_files
                except:
                    files_to_show = []
            
            for i, file_info in enumerate(files_to_show[:50], 1):  # 限制顯示50個
                file_path = file_info['path']
                file_size = self.cleaner.format_file_size(file_info['size'])
                modified_time = file_info['modified_time'].strftime('%Y-%m-%d %H:%M')
                
                self.result_text.insert(tk.END, f"{i:3d}. {file_path.name}\n")
                self.result_text.insert(tk.END, f"     路徑: {file_path}\n")
                self.result_text.insert(tk.END, f"     大小: {file_size}, 修改時間: {modified_time}\n\n")
            
            if len(files_to_show) > 50:
                self.result_text.insert(tk.END, f"... 還有 {len(files_to_show) - 50} 個檔案未顯示\n")
        
        # 顯示失敗的檔案
        if not dry_run and result['failed_files']:
            self.result_text.insert(tk.END, "\n刪除失敗的檔案：\n")
            for failed in result['failed_files']:
                self.result_text.insert(tk.END, f"- {failed['file']['path']}\n")
                self.result_text.insert(tk.END, f"  錯誤：{failed['error']}\n\n")
        
        # 更新狀態
        self.status_var.set(f"{action}完成")
        
        # 捲動到頂部
        self.result_text.see(1.0)
    
    def display_error(self, error_msg):
        """顯示錯誤"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"錯誤：{error_msg}\n")
        self.status_var.set("發生錯誤")
        messagebox.showerror("錯誤", error_msg)
    
    def toggle_auto_cleanup(self):
        """切換自動清理"""
        self.auto_cleanup_enabled = self.auto_enabled_var.get()
        self.settings["auto_cleanup"] = self.auto_cleanup_enabled
        self.save_settings()
        self.update_auto_status()
        
        if self.auto_cleanup_enabled:
            self.setup_auto_cleanup()
            self.add_auto_log("自動清理已啟用")
        else:
            self.add_auto_log("自動清理已停用")
    
    def setup_auto_cleanup(self):
        """設定自動清理排程"""
        # 清除現有排程
        schedule.clear()
        
        # 設定新排程
        schedule_type = self.schedule_var.get()
        cleanup_time = self.time_var.get()
        
        try:
            if schedule_type == "daily":
                schedule.every().day.at(cleanup_time).do(self.auto_cleanup_job)
            elif schedule_type == "weekly":
                schedule.every().week.at(cleanup_time).do(self.auto_cleanup_job)
            elif schedule_type == "monthly":
                schedule.every(30).days.at(cleanup_time).do(self.auto_cleanup_job)
            
            self.add_auto_log(f"排程已設定：{schedule_type} 於 {cleanup_time}")
        except Exception as e:
            self.add_auto_log(f"排程設定失敗：{e}")
    
    def auto_cleanup_job(self):
        """自動清理工作"""
        if not self.auto_cleanup_enabled:
            return
        
        try:
            folder = self.settings.get("last_folder", "")
            if not folder or not Path(folder).exists():
                self.add_auto_log("自動清理失敗：未設定有效的目標資料夾")
                return
            
            days = self.settings.get("default_days", 30)
            include_sub = self.settings.get("include_subfolders", True)
            
            # 執行清理
            result = self.cleaner.cleanup_files(folder, days, include_sub, dry_run=False)
            
            # 記錄結果
            log_msg = f"自動清理完成 - 刪除 {result['successfully_deleted']} 個檔案，"
            log_msg += f"釋放 {self.cleaner.format_file_size(result['total_size_freed'])}"
            if result['failed_deletions'] > 0:
                log_msg += f"，{result['failed_deletions']} 個檔案刪除失敗"
            
            self.add_auto_log(log_msg)
            
        except Exception as e:
            self.add_auto_log(f"自動清理發生錯誤：{e}")
    
    def add_auto_log(self, message):
        """新增自動清理日誌"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        # 更新 GUI
        def update_gui():
            self.auto_log_text.insert(tk.END, log_entry)
            self.auto_log_text.see(tk.END)
        
        if threading.current_thread() == threading.main_thread():
            update_gui()
        else:
            self.root.after(0, update_gui)
        
        # 儲存到檔案
        try:
            auto_log_file = Path("auto_cleanup.log")
            with open(auto_log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except:
            pass
    
    def load_auto_log(self):
        """載入自動清理日誌"""
        try:
            auto_log_file = Path("auto_cleanup.log")
            if auto_log_file.exists():
                with open(auto_log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.auto_log_text.insert(tk.END, content)
                    self.auto_log_text.see(tk.END)
        except:
            pass
    
    def update_auto_status(self):
        """更新自動清理狀態"""
        if self.auto_cleanup_enabled:
            schedule_type = self.schedule_var.get()
            cleanup_time = self.time_var.get()
            self.auto_status_var.set(f"自動清理：啟用 ({schedule_type} {cleanup_time})")
        else:
            self.auto_status_var.set("自動清理：停用")
    
    def refresh_log(self):
        """重新整理日誌"""
        self.log_text.delete(1.0, tk.END)
        
        try:
            log_file = Path("logs") / f"file_cleanup_{datetime.now().strftime('%Y%m%d')}.log"
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.log_text.insert(tk.END, content)
                    self.log_text.see(tk.END)
            else:
                self.log_text.insert(tk.END, "今日尚無日誌記錄\n")
        except Exception as e:
            self.log_text.insert(tk.END, f"無法載入日誌：{e}\n")
    
    def clear_log(self):
        """清除日誌顯示"""
        result = messagebox.askyesno("確認", "確定要清除日誌顯示嗎？\n（不會刪除日誌檔案）")
        if result:
            self.log_text.delete(1.0, tk.END)
    
    def setup_tray(self):
        """設定系統托盤"""
        if not TRAY_AVAILABLE:
            return
        
        # 創建托盤圖示
        def create_image():
            # 創建簡單的圖示
            image = Image.new('RGB', (64, 64), color='white')
            draw = ImageDraw.Draw(image)
            draw.rectangle([10, 10, 54, 54], fill='blue', outline='black', width=2)
            draw.text((25, 28), "C", fill='white', anchor="mm")
            return image
        
        # 托盤選單
        def on_show(icon, item):
            self.show_window()
        
        def on_quit(icon, item):
            self.quit_app()
        
        menu = pystray.Menu(
            pystray.MenuItem("顯示主視窗", on_show, default=True),
            pystray.MenuItem("退出", on_quit)
        )
        
        self.tray = pystray.Icon("FileCleanup", create_image(), "檔案清理工具", menu)
    
    def minimize_to_tray(self):
        """最小化到系統托盤"""
        if TRAY_AVAILABLE and self.tray:
            self.root.withdraw()  # 隱藏主視窗
            
            # 在背景執行緒中運行托盤
            def run_tray():
                self.tray.run()
            
            threading.Thread(target=run_tray, daemon=True).start()
        else:
            messagebox.showwarning("警告", "系統托盤功能不可用\n請安裝 pystray 和 Pillow 套件")
    
    def show_window(self):
        """顯示主視窗"""
        self.root.deiconify()  # 顯示視窗
        self.root.lift()       # 置頂
        self.root.focus_force() # 獲得焦點
        
        if TRAY_AVAILABLE and self.tray:
            self.tray.stop()   # 停止托盤
    
    def open_settings(self):
        """開啟設定視窗"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("設定")
        settings_window.geometry("400x300")
        settings_window.resizable(False, False)
        
        # 設定內容
        frame = ttk.Frame(settings_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="程式設定", font=("TkDefaultFont", 12, "bold")).pack(pady=(0, 20))
        
        # 最小化到托盤選項
        minimize_var = tk.BooleanVar(value=self.settings.get("minimize_to_tray", True))
        ttk.Checkbutton(frame, text="關閉視窗時最小化到系統托盤", variable=minimize_var).pack(anchor=tk.W, pady=5)
        
        # 按鈕
        button_frame = ttk.Frame(frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))
        
        def save_settings():
            self.settings["minimize_to_tray"] = minimize_var.get()
            self.save_settings()
            settings_window.destroy()
            messagebox.showinfo("提示", "設定已儲存")
        
        ttk.Button(button_frame, text="儲存", command=save_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="取消", command=settings_window.destroy).pack(side=tk.RIGHT)
    
    def show_about(self):
        """顯示關於對話框"""
        messagebox.showinfo(
            "關於",
            "檔案自動清理工具 v2.0\n\n"
            "功能特色：\n"
            "• 圖形化介面，操作簡單\n"
            "• 支援自動清理排程\n"
            "• 系統托盤運行\n"
            "• 完整的日誌記錄\n"
            "• 安全的預覽模式\n\n"
            "支援平台：Windows\n"
            "開發語言：Python + tkinter"
        )
    
    def on_closing(self):
        """視窗關閉事件"""
        if self.settings.get("minimize_to_tray", True) and TRAY_AVAILABLE:
            self.minimize_to_tray()
        else:
            self.quit_app()
    
    def quit_app(self):
        """退出應用程式"""
        result = messagebox.askyesno("確認退出", "確定要退出檔案清理工具嗎？")
        if result:
            self.is_running = False
            self.save_settings()
            
            if TRAY_AVAILABLE and self.tray:
                self.tray.stop()
            
            self.root.quit()
            self.root.destroy()
    
    def run_scheduler(self):
        """執行排程檢查"""
        def scheduler_thread():
            while self.is_running:
                try:
                    if self.auto_cleanup_enabled:
                        schedule.run_pending()
                    time.sleep(60)  # 每分鐘檢查一次
                except:
                    pass
        
        threading.Thread(target=scheduler_thread, daemon=True).start()
    
    def run(self):
        """執行應用程式"""
        # 啟動排程器
        self.run_scheduler()
        
        # 如果啟用自動清理，設定排程
        if self.auto_cleanup_enabled:
            self.setup_auto_cleanup()
        
        # 執行主迴圈
        self.root.mainloop()


def main():
    """主函數"""
    try:
        app = FileCleanupGUI()
        app.run()
    except Exception as e:
        messagebox.showerror("錯誤", f"程式啟動失敗：{e}")


if __name__ == "__main__":
    main()
