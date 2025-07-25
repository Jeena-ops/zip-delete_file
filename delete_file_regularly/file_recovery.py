#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檔案恢復工具
功能：恢復被清理工具移動到回收站的檔案
支援：從回收站恢復檔案到原始位置
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


class FileRecoveryTool:
    """檔案恢復工具"""
    
    def __init__(self):
        """初始化恢復工具"""
        self.recycle_bin = Path("recycle_bin")
        self.recycle_bin.mkdir(exist_ok=True)
        self.recovery_log = self.recycle_bin / "recovery_log.json"
        
    def load_recovery_log(self) -> List[Dict]:
        """載入恢復日誌"""
        try:
            if self.recovery_log.exists():
                with open(self.recovery_log, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"載入恢復日誌失敗：{e}")
            return []
    
    def save_recovery_log(self, log_data: List[Dict]):
        """儲存恢復日誌"""
        try:
            with open(self.recovery_log, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"儲存恢復日誌失敗：{e}")
    
    def add_deleted_file(self, original_path: Path, file_size: int, deleted_time: datetime) -> str:
        """
        記錄被刪除的檔案
        
        Args:
            original_path: 原始檔案路徑
            file_size: 檔案大小
            deleted_time: 刪除時間
            
        Returns:
            str: 回收站中的檔案ID
        """
        # 生成唯一檔案ID
        file_id = f"{deleted_time.strftime('%Y%m%d_%H%M%S')}_{original_path.name}"
        
        # 移動檔案到回收站
        recycle_path = self.recycle_bin / file_id
        
        try:
            shutil.move(str(original_path), str(recycle_path))
            
            # 記錄到恢復日誌
            log_data = self.load_recovery_log()
            log_entry = {
                "file_id": file_id,
                "original_path": str(original_path),
                "recycle_path": str(recycle_path),
                "file_size": file_size,
                "deleted_time": deleted_time.isoformat(),
                "recovered": False
            }
            log_data.append(log_entry)
            self.save_recovery_log(log_data)
            
            return file_id
        except Exception as e:
            print(f"移動檔案到回收站失敗：{e}")
            return None
    
    def list_recoverable_files(self) -> List[Dict]:
        """列出可恢復的檔案"""
        log_data = self.load_recovery_log()
        recoverable_files = []
        
        for entry in log_data:
            if not entry.get("recovered", False):
                recycle_path = Path(entry["recycle_path"])
                if recycle_path.exists():
                    recoverable_files.append(entry)
        
        return recoverable_files
    
    def recover_file(self, file_id: str) -> bool:
        """
        恢復檔案
        
        Args:
            file_id: 檔案ID
            
        Returns:
            bool: 是否成功恢復
        """
        log_data = self.load_recovery_log()
        
        for entry in log_data:
            if entry["file_id"] == file_id and not entry.get("recovered", False):
                try:
                    recycle_path = Path(entry["recycle_path"])
                    original_path = Path(entry["original_path"])
                    
                    if not recycle_path.exists():
                        print(f"回收站中找不到檔案：{recycle_path}")
                        return False
                    
                    # 確保目標目錄存在
                    original_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # 如果原位置已有同名檔案，詢問是否覆蓋
                    if original_path.exists():
                        print(f"原位置已存在檔案：{original_path}")
                        return False
                    
                    # 移動檔案回原位置
                    shutil.move(str(recycle_path), str(original_path))
                    
                    # 更新恢復狀態
                    entry["recovered"] = True
                    entry["recovery_time"] = datetime.now().isoformat()
                    self.save_recovery_log(log_data)
                    
                    print(f"檔案已恢復：{original_path}")
                    return True
                    
                except Exception as e:
                    print(f"恢復檔案失敗：{e}")
                    return False
        
        print(f"找不到檔案ID：{file_id}")
        return False
    
    def permanent_delete(self, file_id: str) -> bool:
        """
        永久刪除檔案
        
        Args:
            file_id: 檔案ID
            
        Returns:
            bool: 是否成功刪除
        """
        log_data = self.load_recovery_log()
        
        for entry in log_data:
            if entry["file_id"] == file_id:
                try:
                    recycle_path = Path(entry["recycle_path"])
                    if recycle_path.exists():
                        recycle_path.unlink()
                    
                    # 標記為永久刪除
                    entry["permanently_deleted"] = True
                    entry["permanent_delete_time"] = datetime.now().isoformat()
                    self.save_recovery_log(log_data)
                    
                    print(f"檔案已永久刪除：{entry['original_path']}")
                    return True
                    
                except Exception as e:
                    print(f"永久刪除失敗：{e}")
                    return False
        
        return False
    
    def cleanup_recycle_bin(self, days_to_keep: int = 30):
        """
        清理回收站（永久刪除超過指定天數的檔案）
        
        Args:
            days_to_keep: 回收站保留天數
        """
        log_data = self.load_recovery_log()
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        for entry in log_data:
            if not entry.get("recovered", False) and not entry.get("permanently_deleted", False):
                deleted_time = datetime.fromisoformat(entry["deleted_time"])
                if deleted_time < cutoff_date:
                    self.permanent_delete(entry["file_id"])


class FileRecoveryGUI:
    """檔案恢復圖形介面"""
    
    def __init__(self):
        """初始化 GUI"""
        self.recovery_tool = FileRecoveryTool()
        self.root = tk.Tk()
        self.setup_window()
        self.create_widgets()
        self.refresh_file_list()
        self.update_space_info()
    
    def setup_window(self):
        """設定視窗"""
        self.root.title("檔案恢復與回收站管理工具")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)
    
    def create_widgets(self):
        """建立 GUI 元件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 標題
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        title_frame.columnconfigure(1, weight=1)
        
        title_label = ttk.Label(title_frame, text="檔案恢復與回收站管理工具", font=("TkDefaultFont", 14, "bold"))
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # 空間資訊
        self.space_info_var = tk.StringVar()
        space_label = ttk.Label(title_frame, textvariable=self.space_info_var, font=("TkDefaultFont", 10), foreground="blue")
        space_label.grid(row=0, column=1, sticky=tk.E)
        
        # 檔案列表框架
        list_frame = ttk.LabelFrame(main_frame, text="可恢復的檔案", padding="10")
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 建立樹狀檢視
        columns = ("檔案名稱", "原始路徑", "檔案大小", "刪除時間")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # 設定欄位標題
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200)
        
        # 設定特定欄位寬度
        self.tree.column("檔案名稱", width=250)
        self.tree.column("原始路徑", width=400)
        self.tree.column("檔案大小", width=100)
        self.tree.column("刪除時間", width=150)
        
        # 捲軸
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 按鈕框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Button(button_frame, text="重新整理", command=self.refresh_file_list).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="恢復選中檔案", command=self.recover_selected_file, style="Accent.TButton").grid(row=0, column=1, padx=(5, 5))
        ttk.Button(button_frame, text="永久刪除選中", command=self.permanent_delete_selected).grid(row=0, column=2, padx=(5, 5))
        ttk.Button(button_frame, text="批量永久刪除", command=self.batch_permanent_delete).grid(row=0, column=3, padx=(5, 5))
        ttk.Button(button_frame, text="清理回收站", command=self.cleanup_recycle_bin).grid(row=0, column=4, padx=(5, 0))
        
        # 狀態列
        self.status_var = tk.StringVar(value="就緒")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=3, column=0, sticky=tk.W, pady=(10, 0))
    
    def format_file_size(self, size_bytes: int) -> str:
        """格式化檔案大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def refresh_file_list(self):
        """重新整理檔案列表"""
        # 清除現有項目
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 載入可恢復檔案
        recoverable_files = self.recovery_tool.list_recoverable_files()
        
        for file_entry in recoverable_files:
            file_name = Path(file_entry["original_path"]).name
            original_path = file_entry["original_path"]
            file_size = self.format_file_size(file_entry["file_size"])
            deleted_time = datetime.fromisoformat(file_entry["deleted_time"]).strftime("%Y-%m-%d %H:%M:%S")
            
            # 插入到樹狀檢視
            item_id = self.tree.insert("", tk.END, values=(file_name, original_path, file_size, deleted_time))
            # 儲存 file_id 作為項目的標識
            self.tree.set(item_id, "#0", file_entry["file_id"])
        
        count = len(recoverable_files)
        self.status_var.set(f"找到 {count} 個可恢復的檔案")
        self.update_space_info()
    
    def update_space_info(self):
        """更新空間資訊"""
        recoverable_files = self.recovery_tool.list_recoverable_files()
        total_size = sum(file_entry["file_size"] for file_entry in recoverable_files)
        self.space_info_var.set(f"回收站占用空間：{self.format_file_size(total_size)}")
    
    def get_selected_file_id(self) -> Optional[str]:
        """取得選中檔案的ID"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "請先選擇一個檔案")
            return None
        
        item = selection[0]
        file_id = self.tree.set(item, "#0")
        return file_id
    
    def recover_selected_file(self):
        """恢復選中的檔案"""
        file_id = self.get_selected_file_id()
        if not file_id:
            return
        
        # 確認對話框
        result = messagebox.askyesno("確認恢復", "確定要將此檔案恢復到原始位置嗎？")
        if not result:
            return
        
        # 執行恢復
        success = self.recovery_tool.recover_file(file_id)
        
        if success:
            messagebox.showinfo("成功", "檔案已成功恢復到原始位置")
            self.refresh_file_list()
        else:
            messagebox.showerror("錯誤", "檔案恢復失敗，請檢查原始位置是否有同名檔案")
    
    def batch_permanent_delete(self):
        """批量永久刪除檔案"""
        recoverable_files = self.recovery_tool.list_recoverable_files()
        if not recoverable_files:
            messagebox.showinfo("提示", "回收站中沒有檔案")
            return
        
        # 創建批量刪除對話框
        batch_window = tk.Toplevel(self.root)
        batch_window.title("批量永久刪除")
        batch_window.geometry("500x400")
        batch_window.resizable(False, False)
        batch_window.transient(self.root)
        batch_window.grab_set()
        
        frame = ttk.Frame(batch_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="批量永久刪除選項", font=("TkDefaultFont", 12, "bold")).pack(pady=(0, 20))
        
        # 選項
        option_var = tk.StringVar(value="old")
        
        ttk.Radiobutton(frame, text="刪除超過 30 天的檔案", variable=option_var, value="old").pack(anchor=tk.W, pady=5)
        ttk.Radiobutton(frame, text="刪除超過 7 天的檔案", variable=option_var, value="week").pack(anchor=tk.W, pady=5)
        ttk.Radiobutton(frame, text="刪除所有檔案（清空回收站）", variable=option_var, value="all").pack(anchor=tk.W, pady=5)
        
        # 統計資訊
        stats_frame = ttk.LabelFrame(frame, text="統計資訊", padding="10")
        stats_frame.pack(fill=tk.X, pady=(20, 10))
        
        total_size = sum(f["file_size"] for f in recoverable_files)
        ttk.Label(stats_frame, text=f"總檔案數：{len(recoverable_files)} 個").pack(anchor=tk.W)
        ttk.Label(stats_frame, text=f"總占用空間：{self.format_file_size(total_size)}").pack(anchor=tk.W)
        
        # 計算不同時間範圍的檔案
        now = datetime.now()
        old_files = [f for f in recoverable_files if (now - datetime.fromisoformat(f["deleted_time"])).days > 30]
        week_files = [f for f in recoverable_files if (now - datetime.fromisoformat(f["deleted_time"])).days > 7]
        
        ttk.Label(stats_frame, text=f"超過 30 天：{len(old_files)} 個").pack(anchor=tk.W)
        ttk.Label(stats_frame, text=f"超過 7 天：{len(week_files)} 個").pack(anchor=tk.W)
        
        def execute_batch_delete():
            option = option_var.get()
            files_to_delete = []
            
            if option == "old":
                files_to_delete = old_files
                desc = "超過 30 天的檔案"
            elif option == "week":
                files_to_delete = week_files
                desc = "超過 7 天的檔案"
            else:  # all
                files_to_delete = recoverable_files
                desc = "所有檔案"
            
            if not files_to_delete:
                messagebox.showinfo("提示", "沒有符合條件的檔案")
                return
            
            total_size = sum(f["file_size"] for f in files_to_delete)
            result = messagebox.askyesno(
                "確認批量刪除",
                f"將永久刪除 {desc}：\n\n"
                f"檔案數量：{len(files_to_delete)} 個\n"
                f"釋放空間：{self.format_file_size(total_size)}\n\n"
                f"此操作無法復原，確定要繼續嗎？",
                icon="warning"
            )
            
            if result:
                success_count = 0
                for file_entry in files_to_delete:
                    if self.recovery_tool.permanent_delete(file_entry["file_id"]):
                        success_count += 1
                
                batch_window.destroy()
                messagebox.showinfo("完成", f"已永久刪除 {success_count} 個檔案\n釋放空間：{self.format_file_size(total_size)}")
                self.refresh_file_list()
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="執行刪除", command=execute_batch_delete).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="取消", command=batch_window.destroy).pack(side=tk.RIGHT)
    
    def permanent_delete_selected(self):
        """永久刪除選中的檔案"""
        file_id = self.get_selected_file_id()
        if not file_id:
            return
        
        # 確認對話框
        result = messagebox.askyesno(
            "確認永久刪除", 
            "警告：此操作將永久刪除檔案，無法復原！\n\n確定要繼續嗎？",
            icon="warning"
        )
        if not result:
            return
        
        # 執行永久刪除
        success = self.recovery_tool.permanent_delete(file_id)
        
        if success:
            messagebox.showinfo("完成", "檔案已永久刪除")
            self.refresh_file_list()
        else:
            messagebox.showerror("錯誤", "永久刪除失敗")
    
    def cleanup_recycle_bin(self):
        """清理回收站"""
        # 詢問保留天數
        days_window = tk.Toplevel(self.root)
        days_window.title("清理回收站")
        days_window.geometry("300x150")
        days_window.resizable(False, False)
        days_window.transient(self.root)
        days_window.grab_set()
        
        frame = ttk.Frame(days_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="回收站保留天數：").pack(pady=(0, 10))
        
        days_var = tk.StringVar(value="30")
        days_spinbox = ttk.Spinbox(frame, from_=1, to=365, textvariable=days_var, width=10)
        days_spinbox.pack(pady=(0, 10))
        
        ttk.Label(frame, text="超過此天數的檔案將被永久刪除").pack(pady=(0, 10))
        
        def confirm_cleanup():
            try:
                days = int(days_var.get())
                days_window.destroy()
                
                result = messagebox.askyesno(
                    "確認清理",
                    f"將永久刪除超過 {days} 天的所有檔案\n\n此操作無法復原，確定繼續嗎？",
                    icon="warning"
                )
                
                if result:
                    self.recovery_tool.cleanup_recycle_bin(days)
                    messagebox.showinfo("完成", "回收站清理完成")
                    self.refresh_file_list()
            except ValueError:
                messagebox.showerror("錯誤", "請輸入有效的天數")
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(side=tk.BOTTOM)
        
        ttk.Button(button_frame, text="確定", command=confirm_cleanup).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="取消", command=days_window.destroy).pack(side=tk.LEFT)
    
    def run(self):
        """執行應用程式"""
        self.root.mainloop()


def main():
    """主函數"""
    try:
        app = FileRecoveryGUI()
        app.run()
    except Exception as e:
        print(f"程式啟動失敗：{e}")


if __name__ == "__main__":
    main()
