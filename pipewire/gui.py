#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox
import os
import subprocess
import glob
from pathlib import Path

class HRTFTesterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("HRTF File Tester")
        self.root.geometry("550x450")
        
        # File type configurations
        self.file_configs = {
            "SOFA": {
                "dir": "sofa",
                "extension": "*.sofa",
                "target_link": "hrtf.sofa"
            },
            "WAV": {
                "dir": "wav", 
                "extension": "*.wav",
                "target_link": "hrtf.wav"
            }
        }
        
        self.service_name = "filter-chain"
        self.current_tab = "SOFA"
        
        self.setup_ui()
        self.refresh_file_list()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        title_label = ttk.Label(main_frame, text="HRTF File Tester", 
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        self.tabs = {}
        for file_type in ["SOFA", "WAV"]:
            self.create_tab(file_type)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        
        self.refresh_btn = ttk.Button(button_frame, text="Refresh List", 
                                     command=self.refresh_file_list)
        self.refresh_btn.grid(row=0, column=0, padx=(0, 5), sticky=(tk.W, tk.E))
        
        self.select_btn = ttk.Button(button_frame, text="Apply & Restart", 
                                    command=self.on_file_select)
        self.select_btn.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        
        self.quit_btn = ttk.Button(button_frame, text="Quit", 
                                  command=self.root.quit)
        self.quit_btn.grid(row=0, column=2, padx=(5, 0), sticky=(tk.W, tk.E))
        
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="5")
        status_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.current_label = ttk.Label(status_frame, text="", 
                                      font=("Arial", 9), foreground="blue")
        self.current_label.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        self.update_current_link_info()
        
    def create_tab(self, file_type):
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text=f"{file_type} Files")
        tab_frame.columnconfigure(0, weight=1)
        tab_frame.rowconfigure(0, weight=1)
        
        list_frame = ttk.LabelFrame(tab_frame, text=f"Available {file_type} Files", padding="5")
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 5))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        listbox_frame = ttk.Frame(list_frame)
        listbox_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)
        
        listbox = tk.Listbox(listbox_frame, selectmode=tk.SINGLE)
        listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        listbox.configure(yscrollcommand=scrollbar.set)
        listbox.bind('<Double-Button-1>', self.on_file_select)
        
        self.tabs[file_type] = {"frame": tab_frame, "listbox": listbox}
        
    def get_current_config(self):
        return self.file_configs[self.current_tab]
        
    def get_current_listbox(self):
        return self.tabs[self.current_tab]["listbox"]
        
    def on_tab_changed(self, event=None):
        selected_tab = self.notebook.select()
        tab_text = self.notebook.tab(selected_tab, "text")
        self.current_tab = tab_text.split()[0]
        self.refresh_file_list()
        self.update_current_link_info()
        
    def refresh_file_list(self):
        config = self.get_current_config()
        listbox = self.get_current_listbox()
        listbox.delete(0, tk.END)
        if not os.path.exists(config["dir"]):
            self.status_label.config(text=f"Directory '{config['dir']}' not found!")
            return
        files = glob.glob(os.path.join(config["dir"], config["extension"]))
        files.sort()
        for file_path in files:
            listbox.insert(tk.END, os.path.basename(file_path))
        self.status_label.config(text=f"Found {len(files)} {self.current_tab} files")
        
    def on_file_select(self, event=None):
        listbox = self.get_current_listbox()
        selection = listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a file first.")
            return
        self.apply_file(listbox.get(selection[0]))
        
    def apply_file(self, filename):
        config = self.get_current_config()
        source_path = os.path.join(config["dir"], filename)
        target_link = config["target_link"]
        
        try:
            if os.path.exists(target_link) or os.path.islink(target_link):
                os.remove(target_link)
            os.symlink(source_path, target_link)
            
            # Use systemctl to restart
            self.status_label.config(text=f"Restarting {self.service_name}...")
            result = subprocess.run(
                ["systemctl", "--user", "restart", self.service_name],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                self.status_label.config(text=f"✓ Applied {filename}")
            else:
                raise Exception(result.stderr)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply {filename}:\n{str(e)}")
            self.status_label.config(text="Error occurred")
            
        self.update_current_link_info()
        
    def update_current_link_info(self):
        info_parts = []
        for file_type, config in self.file_configs.items():
            target_link = config["target_link"]
            if os.path.islink(target_link):
                link_target = os.readlink(target_link)
                info_parts.append(f"{file_type}: {os.path.basename(link_target)}")
            else:
                info_parts.append(f"{file_type}: None")
        self.current_label.config(text=" | ".join(info_parts))

def main():
    root = tk.Tk()
    app = HRTFTesterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
