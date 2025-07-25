#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檔案歸檔管理工具
功能：管理壓縮歸檔的檔案，提供瀏覽、提取、刪除功能
"""

import os
import sys
import json
import zipfile
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import threading


class FileArchiveManager:
    """檔案歸檔管理器"""
    
    def __init__(self):
        self.archive_folder = Path("archived_files")
        self.archive_log = self.archive_folder / "archive_log.json"
        self.setup_ui()
        self.load_archive_data()
    
    def setup_ui(self):
        """設定使用者介面"""
        self.root = tk.Tk()
        self.root.title("檔案歸檔管理器 v1.0")
        self.root.geometry("800x600")
        
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 標題
        title_label = ttk.Label(main_frame, text="📦 檔案歸檔管理器", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # 歸檔統計資訊
        self.info_frame = ttk.LabelFrame(main_frame, text="歸檔統計", padding=10)
        self.info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 統計標籤
        self.total_archives_label = ttk.Label(self.info_frame, text="總歸檔數量：載入中...")
        self.total_archives_label.pack(anchor=tk.W)
        
        self.total_files_label = ttk.Label(self.info_frame, text="總檔案數量：載入中...")
        self.total_files_label.pack(anchor=tk.W)
        
        self.original_size_label = ttk.Label(self.info_frame, text="原始大小：載入中...")
        self.original_size_label.pack(anchor=tk.W)
        
        self.compressed_size_label = ttk.Label(self.info_frame, text="壓縮後大小：載入中...")
        self.compressed_size_label.pack(anchor=tk.W)
        
        self.space_saved_label = ttk.Label(self.info_frame, text="節省空間：載入中...")
        self.space_saved_label.pack(anchor=tk.W)
        
        # 搜尋框架
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="搜尋檔案：").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_changed)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        refresh_btn = ttk.Button(search_frame, text="🔄 重新整理", command=self.refresh_data)
        refresh_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # 檔案列表框架
        list_frame = ttk.LabelFrame(main_frame, text="歸檔檔案列表", padding=5)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 創建 Treeview
        columns = ("archive", "original_path", "size", "archived_time", "status")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # 設定欄位標題
        self.tree.heading("archive", text="歸檔檔案")
        self.tree.heading("original_path", text="原始路徑")
        self.tree.heading("size", text="檔案大小")
        self.tree.heading("archived_time", text="歸檔時間")
        self.tree.heading("status", text="狀態")
        
        # 設定欄位寬度
        self.tree.column("archive", width=150)
        self.tree.column("original_path", width=300)
        self.tree.column("size", width=100)
        self.tree.column("archived_time", width=150)
        self.tree.column("status", width=100)
        
        # 滾動條
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 包裝 Treeview 和滾動條
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 按鈕框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # 左側按鈕
        left_buttons = ttk.Frame(button_frame)
        left_buttons.pack(side=tk.LEFT)
        
        extract_btn = ttk.Button(left_buttons, text="📤 提取選中檔案", command=self.extract_selected)
        extract_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        extract_all_btn = ttk.Button(left_buttons, text="📦 提取整個歸檔", command=self.extract_archive)
        extract_all_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        view_btn = ttk.Button(left_buttons, text="👁️ 查看歸檔內容", command=self.view_archive_contents)
        view_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 右側按鈕
        right_buttons = ttk.Frame(button_frame)
        right_buttons.pack(side=tk.RIGHT)
        
        delete_btn = ttk.Button(right_buttons, text="🗑️ 刪除歸檔", command=self.delete_archive)
        delete_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        cleanup_btn = ttk.Button(right_buttons, text="🧹 清理空歸檔", command=self.cleanup_empty_archives)
        cleanup_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # 進度條（隱藏）
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, mode='determinate')
        
        # 狀態列
        self.status_var = tk.StringVar(value="就緒")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_label.pack(fill=tk.X, pady=(5, 0))
    
    def load_archive_data(self):
        """載入歸檔資料"""
        try:
            if not self.archive_log.exists():
                self.archive_data = []
                self.update_statistics()
                return
            
            with open(self.archive_log, 'r', encoding='utf-8') as f:
                self.archive_data = json.load(f)
            
            self.populate_tree()
            self.update_statistics()
            self.status_var.set(f"已載入 {len(self.archive_data)} 個歸檔記錄")
            
        except Exception as e:
            messagebox.showerror("錯誤", f"載入歸檔資料失敗：{e}")
            self.archive_data = []
    
    def populate_tree(self, data=None):
        """填充樹狀列表"""
        # 清空現有項目
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if data is None:
            data = self.archive_data
        
        for entry in data:
            # 檢查檔案狀態
            archive_path = Path(entry.get("archive_path", ""))
            if archive_path.exists():
                status = "✅ 可用"
            else:
                status = "❌ 遺失"
            
            # 格式化大小
            size_text = self.format_file_size(entry.get("original_size", 0))
            
            # 格式化時間
            archived_time = entry.get("archived_time", "")
            if archived_time:
                try:
                    dt = datetime.fromisoformat(archived_time)
                    time_text = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    time_text = archived_time[:16]  # 截取前16個字符
            else:
                time_text = "未知"
            
            # 插入項目
            self.tree.insert("", tk.END, values=(
                archive_path.name if archive_path.exists() else "遺失",
                entry.get("original_path", ""),
                size_text,
                time_text,
                status
            ), tags=(entry.get("archive_path", ""),))
    
    def update_statistics(self):
        """更新統計資訊"""
        if not self.archive_data:
            self.total_archives_label.config(text="總歸檔數量：0")
            self.total_files_label.config(text="總檔案數量：0")
            self.original_size_label.config(text="原始大小：0 B")
            self.compressed_size_label.config(text="壓縮後大小：0 B")
            self.space_saved_label.config(text="節省空間：0%")
            return
        
        # 統計歸檔檔案
        archives = set()
        total_original_size = 0
        total_compressed_size = 0
        
        for entry in self.archive_data:
            archive_path = entry.get("archive_path", "")
            if archive_path:
                archives.add(archive_path)
                total_original_size += entry.get("original_size", 0)
        
        # 計算壓縮後總大小
        for archive_path in archives:
            path = Path(archive_path)
            if path.exists():
                total_compressed_size += path.stat().st_size
        
        # 計算節省的空間
        if total_original_size > 0:
            space_saved_percent = (1 - total_compressed_size / total_original_size) * 100
        else:
            space_saved_percent = 0
        
        # 更新標籤
        self.total_archives_label.config(text=f"總歸檔數量：{len(archives)} 個檔案")
        self.total_files_label.config(text=f"總檔案數量：{len(self.archive_data)} 個")
        self.original_size_label.config(text=f"原始大小：{self.format_file_size(total_original_size)}")
        self.compressed_size_label.config(text=f"壓縮後大小：{self.format_file_size(total_compressed_size)}")
        self.space_saved_label.config(text=f"節省空間：{space_saved_percent:.1f}%")
    
    def format_file_size(self, size_bytes: int) -> str:
        """格式化檔案大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def on_search_changed(self, *args):
        """搜尋變更事件"""
        search_text = self.search_var.get().lower()
        if not search_text:
            self.populate_tree()
            return
        
        # 過濾資料
        filtered_data = []
        for entry in self.archive_data:
            original_path = entry.get("original_path", "").lower()
            archive_path = entry.get("archive_path", "").lower()
            if search_text in original_path or search_text in archive_path:
                filtered_data.append(entry)
        
        self.populate_tree(filtered_data)
    
    def refresh_data(self):
        """重新整理資料"""
        self.status_var.set("正在重新整理...")
        self.load_archive_data()
    
    def get_selected_item(self):
        """獲取選中的項目"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "請先選擇一個檔案")
            return None
        
        item = self.tree.item(selection[0])
        archive_path = item['tags'][0] if item['tags'] else ""
        
        # 找到對應的歸檔記錄
        for entry in self.archive_data:
            if entry.get("archive_path") == archive_path:
                return entry
        
        return None
    
    def extract_selected(self):
        """提取選中的檔案"""
        entry = self.get_selected_item()
        if not entry:
            return
        
        # 選擇提取位置
        extract_dir = filedialog.askdirectory(title="選擇提取位置")
        if not extract_dir:
            return
        
        self._extract_file_thread(entry, extract_dir)
    
    def extract_archive(self):
        """提取整個歸檔檔案"""
        entry = self.get_selected_item()
        if not entry:
            return
        
        archive_path = Path(entry.get("archive_path", ""))
        if not archive_path.exists():
            messagebox.showerror("錯誤", "歸檔檔案不存在")
            return
        
        # 選擇提取位置
        extract_dir = filedialog.askdirectory(title="選擇提取位置")
        if not extract_dir:
            return
        
        self._extract_archive_thread(archive_path, extract_dir)
    
    def _extract_file_thread(self, entry, extract_dir):
        """在背景執行緒中提取單個檔案"""
        def extract():
            try:
                self.status_var.set("正在提取檔案...")
                self.progress_bar.pack(fill=tk.X, pady=(5, 0))
                self.progress_var.set(0)
                
                archive_path = Path(entry.get("archive_path", ""))
                internal_path = entry.get("archive_internal_path", "")
                original_path = entry.get("original_path", "")
                
                if not archive_path.exists():
                    messagebox.showerror("錯誤", "歸檔檔案不存在")
                    return
                
                # 提取檔案
                with zipfile.ZipFile(archive_path, 'r') as zipf:
                    # 使用原始檔案名稱
                    extract_file_path = Path(extract_dir) / Path(original_path).name
                    
                    # 確保目標目錄存在
                    extract_file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # 提取檔案
                    with zipf.open(internal_path) as source, open(extract_file_path, 'wb') as target:
                        shutil.copyfileobj(source, target)
                    
                    self.progress_var.set(100)
                
                # 更新歸檔記錄
                entry["extracted"] = True
                entry["extract_time"] = datetime.now().isoformat()
                self.save_archive_log()
                
                messagebox.showinfo("成功", f"檔案已提取到：\n{extract_file_path}")
                self.status_var.set("提取完成")
                
            except Exception as e:
                messagebox.showerror("錯誤", f"提取檔案失敗：{e}")
                self.status_var.set("提取失敗")
            finally:
                self.progress_bar.pack_forget()
                self.progress_var.set(0)
        
        threading.Thread(target=extract, daemon=True).start()
    
    def _extract_archive_thread(self, archive_path, extract_dir):
        """在背景執行緒中提取整個歸檔"""
        def extract():
            try:
                self.status_var.set("正在提取歸檔...")
                self.progress_bar.pack(fill=tk.X, pady=(5, 0))
                
                with zipfile.ZipFile(archive_path, 'r') as zipf:
                    file_list = zipf.namelist()
                    total_files = len(file_list)
                    
                    for i, file_path in enumerate(file_list):
                        self.progress_var.set((i / total_files) * 100)
                        zipf.extract(file_path, extract_dir)
                    
                    self.progress_var.set(100)
                
                messagebox.showinfo("成功", f"歸檔已提取到：\n{extract_dir}")
                self.status_var.set("提取完成")
                
            except Exception as e:
                messagebox.showerror("錯誤", f"提取歸檔失敗：{e}")
                self.status_var.set("提取失敗")
            finally:
                self.progress_bar.pack_forget()
                self.progress_var.set(0)
        
        threading.Thread(target=extract, daemon=True).start()
    
    def view_archive_contents(self):
        """查看歸檔內容"""
        entry = self.get_selected_item()
        if not entry:
            return
        
        archive_path = Path(entry.get("archive_path", ""))
        if not archive_path.exists():
            messagebox.showerror("錯誤", "歸檔檔案不存在")
            return
        
        try:
            # 創建新視窗顯示歸檔內容
            content_window = tk.Toplevel(self.root)
            content_window.title(f"歸檔內容 - {archive_path.name}")
            content_window.geometry("600x400")
            
            # 創建文字區域
            text_frame = ttk.Frame(content_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            text_area = tk.Text(text_frame, wrap=tk.WORD)
            scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_area.yview)
            text_area.configure(yscrollcommand=scrollbar.set)
            
            text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # 讀取歸檔內容
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                file_list = zipf.namelist()
                info_list = zipf.infolist()
                
                text_area.insert(tk.END, f"歸檔檔案：{archive_path}\n")
                text_area.insert(tk.END, f"檔案數量：{len(file_list)}\n")
                text_area.insert(tk.END, "=" * 60 + "\n\n")
                
                total_original = 0
                total_compressed = 0
                
                for info in info_list:
                    original_size = info.file_size
                    compressed_size = info.compress_size
                    compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
                    
                    total_original += original_size
                    total_compressed += compressed_size
                    
                    text_area.insert(tk.END, f"檔案：{info.filename}\n")
                    text_area.insert(tk.END, f"原始大小：{self.format_file_size(original_size)}\n")
                    text_area.insert(tk.END, f"壓縮大小：{self.format_file_size(compressed_size)}\n")
                    text_area.insert(tk.END, f"壓縮率：{compression_ratio:.1f}%\n")
                    text_area.insert(tk.END, f"修改時間：{datetime(*info.date_time)}\n")
                    text_area.insert(tk.END, "-" * 40 + "\n")
                
                # 總計資訊
                overall_compression = (1 - total_compressed / total_original) * 100 if total_original > 0 else 0
                text_area.insert(tk.END, f"\n總計：\n")
                text_area.insert(tk.END, f"原始總大小：{self.format_file_size(total_original)}\n")
                text_area.insert(tk.END, f"壓縮總大小：{self.format_file_size(total_compressed)}\n")
                text_area.insert(tk.END, f"整體壓縮率：{overall_compression:.1f}%\n")
            
            text_area.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("錯誤", f"查看歸檔內容失敗：{e}")
    
    def delete_archive(self):
        """刪除歸檔"""
        entry = self.get_selected_item()
        if not entry:
            return
        
        archive_path = Path(entry.get("archive_path", ""))
        
        # 確認刪除
        result = messagebox.askyesno(
            "確認刪除", 
            f"確定要刪除歸檔檔案嗎？\n\n{archive_path}\n\n此操作無法復原！"
        )
        
        if not result:
            return
        
        try:
            # 刪除實際檔案
            if archive_path.exists():
                archive_path.unlink()
            
            # 從記錄中移除相關項目
            self.archive_data = [e for e in self.archive_data if e.get("archive_path") != str(archive_path)]
            self.save_archive_log()
            
            # 重新整理顯示
            self.populate_tree()
            self.update_statistics()
            
            messagebox.showinfo("成功", "歸檔已刪除")
            self.status_var.set("歸檔已刪除")
            
        except Exception as e:
            messagebox.showerror("錯誤", f"刪除歸檔失敗：{e}")
    
    def cleanup_empty_archives(self):
        """清理空的或損壞的歸檔"""
        cleaned_count = 0
        
        try:
            # 檢查所有歸檔檔案
            archives_to_remove = []
            
            for entry in self.archive_data:
                archive_path = Path(entry.get("archive_path", ""))
                
                should_remove = False
                
                # 檢查檔案是否存在
                if not archive_path.exists():
                    should_remove = True
                else:
                    # 檢查是否為有效的ZIP檔案
                    try:
                        with zipfile.ZipFile(archive_path, 'r') as zipf:
                            if len(zipf.namelist()) == 0:
                                should_remove = True
                    except:
                        should_remove = True
                
                if should_remove:
                    archives_to_remove.append(entry)
                    if archive_path.exists():
                        archive_path.unlink()
                    cleaned_count += 1
            
            # 從記錄中移除
            for entry in archives_to_remove:
                self.archive_data.remove(entry)
            
            if cleaned_count > 0:
                self.save_archive_log()
                self.populate_tree()
                self.update_statistics()
            
            messagebox.showinfo("清理完成", f"已清理 {cleaned_count} 個無效歸檔")
            self.status_var.set(f"清理完成，移除了 {cleaned_count} 個無效歸檔")
            
        except Exception as e:
            messagebox.showerror("錯誤", f"清理歸檔失敗：{e}")
    
    def save_archive_log(self):
        """儲存歸檔日誌"""
        try:
            with open(self.archive_log, 'w', encoding='utf-8') as f:
                json.dump(self.archive_data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            messagebox.showerror("錯誤", f"儲存歸檔日誌失敗：{e}")
    
    def run(self):
        """執行應用程式"""
        self.root.mainloop()


def main():
    """主程式"""
    try:
        # 檢查歸檔資料夾是否存在
        archive_folder = Path("archived_files")
        if not archive_folder.exists():
            print("找不到歸檔資料夾，請先執行檔案清理工具建立歸檔")
            input("按任意鍵退出...")
            return
        
        # 啟動管理器
        manager = FileArchiveManager()
        manager.run()
        
    except Exception as e:
        print(f"程式執行時發生錯誤：{e}")
        input("按任意鍵退出...")


if __name__ == "__main__":
    main()
