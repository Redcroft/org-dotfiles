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
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="HRTF File Tester", 
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Create tabs
        self.tabs = {}
        for file_type in ["SOFA", "WAV"]:
            self.create_tab(file_type)
        
        # Button frame (shared across tabs)
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        
        # Buttons
        self.refresh_btn = ttk.Button(button_frame, text="Refresh List", 
                                     command=self.refresh_file_list)
        self.refresh_btn.grid(row=0, column=0, padx=(0, 5), sticky=(tk.W, tk.E))
        
        self.select_btn = ttk.Button(button_frame, text="Select & Test", 
                                    command=self.on_file_select)
        self.select_btn.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        
        self.quit_btn = ttk.Button(button_frame, text="Quit", 
                                  command=self.root.quit)
        self.quit_btn.grid(row=0, column=2, padx=(5, 0), sticky=(tk.W, tk.E))
        
        # Status frame (shared)
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="5")
        status_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Current link info
        self.current_label = ttk.Label(status_frame, text="", 
                                      font=("Arial", 9), foreground="blue")
        self.current_label.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        self.update_current_link_info()
        
    def create_tab(self, file_type):
        """Create a tab for the specified file type"""
        # Create tab frame
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text=f"{file_type} Files")
        tab_frame.columnconfigure(0, weight=1)
        tab_frame.rowconfigure(0, weight=1)
        
        # File list frame
        list_frame = ttk.LabelFrame(tab_frame, text=f"Available {file_type} Files", padding="5")
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 5))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Listbox with scrollbar
        listbox_frame = ttk.Frame(list_frame)
        listbox_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)
        
        listbox = tk.Listbox(listbox_frame, selectmode=tk.SINGLE)
        listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", 
                                 command=listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        listbox.configure(yscrollcommand=scrollbar.set)
        
        # Bind double-click
        listbox.bind('<Double-Button-1>', self.on_file_select)
        
        # Store tab components
        self.tabs[file_type] = {
            "frame": tab_frame,
            "listbox": listbox
        }
        
    def get_current_config(self):
        """Get configuration for currently selected tab"""
        return self.file_configs[self.current_tab]
        
    def get_current_listbox(self):
        """Get listbox for currently selected tab"""
        return self.tabs[self.current_tab]["listbox"]
        
    def on_tab_changed(self, event=None):
        """Handle tab change"""
        selected_tab = self.notebook.select()
        tab_text = self.notebook.tab(selected_tab, "text")
        self.current_tab = tab_text.split()[0]  # Get "SOFA" from "SOFA Files"
        self.refresh_file_list()
        self.update_current_link_info()
        
    def refresh_file_list(self):
        """Refresh the list of files for current tab"""
        config = self.get_current_config()
        listbox = self.get_current_listbox()
        
        listbox.delete(0, tk.END)
        
        if not os.path.exists(config["dir"]):
            self.status_label.config(text=f"Directory '{config['dir']}' not found!")
            return
            
        files = glob.glob(os.path.join(config["dir"], config["extension"]))
        files.sort()
        
        if not files:
            self.status_label.config(text=f"No {config['extension']} files found in '{config['dir']}'")
            return
            
        for file_path in files:
            filename = os.path.basename(file_path)
            listbox.insert(tk.END, filename)
            
        self.status_label.config(text=f"Found {len(files)} {self.current_tab} files")
        
    def on_file_select(self, event=None):
        """Handle file selection"""
        listbox = self.get_current_listbox()
        selection = listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", f"Please select a {self.current_tab} file first.")
            return
            
        selected_file = listbox.get(selection[0])
        self.apply_file(selected_file)
        
    def apply_file(self, filename):
        """Apply the selected file"""
        config = self.get_current_config()
        source_path = os.path.join(config["dir"], filename)
        target_link = config["target_link"]
        
        try:
            # Remove existing symlink if it exists
            if os.path.exists(target_link) or os.path.islink(target_link):
                os.remove(target_link)
                
            # Create new symlink
            os.symlink(source_path, target_link)
            self.status_label.config(text=f"Symlinked: {filename}")
            
            # Restart the systemd service
            result = subprocess.run(
                ["systemctl", "--user", "restart", self.service_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.status_label.config(text=f"✓ Applied {filename} and restarted service")
                messagebox.showinfo("Success", 
                                  f"Successfully applied {filename}\nService restarted successfully!")
            else:
                self.status_label.config(text=f"⚠ Applied {filename} but service restart failed")
                messagebox.showwarning("Partial Success", 
                                     f"Applied {filename} successfully,\nbut service restart failed:\n{result.stderr}")
                
        except subprocess.TimeoutExpired:
            self.status_label.config(text=f"⚠ Applied {filename} but service restart timed out")
            messagebox.showwarning("Timeout", 
                                 f"Applied {filename} successfully,\nbut service restart timed out")
        except OSError as e:
            self.status_label.config(text=f"Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to apply {filename}:\n{str(e)}")
        except Exception as e:
            self.status_label.config(text=f"Unexpected error: {str(e)}")
            messagebox.showerror("Error", f"Unexpected error:\n{str(e)}")
            
        self.update_current_link_info()
        
    def update_current_link_info(self):
        """Update the current symlink information for both file types"""
        info_parts = []
        
        for file_type, config in self.file_configs.items():
            target_link = config["target_link"]
            if os.path.islink(target_link):
                link_target = os.readlink(target_link)
                info_parts.append(f"{file_type}: {os.path.basename(link_target)}")
            elif os.path.exists(target_link):
                info_parts.append(f"{file_type}: {target_link} (regular file)")
            else:
                info_parts.append(f"{file_type}: None")
                
        self.current_label.config(text=" | ".join(info_parts))

def main():
    root = tk.Tk()
    app = HRTFTesterGUI(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
