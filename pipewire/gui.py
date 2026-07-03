#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox
import os
import subprocess
import glob

class HRTFTesterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("HRTF File Tester")
        self.root.geometry("550x400")

        self.file_dir = "wav"
        self.file_extension = "*.wav"
        self.target_link = "hrtf.wav"

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

        list_frame = ttk.LabelFrame(main_frame, text="Available WAV Files", padding="5")
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        listbox_frame = ttk.Frame(list_frame)
        listbox_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)

        self.listbox = tk.Listbox(listbox_frame, selectmode=tk.SINGLE)
        self.listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.listbox.bind('<Double-Button-1>', self.on_file_select)

        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.listbox.configure(yscrollcommand=scrollbar.set)

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

    def refresh_file_list(self):
        self.listbox.delete(0, tk.END)
        if not os.path.exists(self.file_dir):
            self.status_label.config(text=f"Directory '{self.file_dir}' not found!")
            return
        files = glob.glob(os.path.join(self.file_dir, self.file_extension))
        files.sort()
        for file_path in files:
            self.listbox.insert(tk.END, os.path.basename(file_path))
        self.status_label.config(text=f"Found {len(files)} WAV files")

    def on_file_select(self, event=None):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a file first.")
            return
        self.apply_file(self.listbox.get(selection[0]))

    def apply_file(self, filename):
        base_path = os.path.dirname(os.path.abspath(__file__))
        source_path = os.path.join(base_path, self.file_dir, filename)
        target_link = os.path.join(base_path, self.target_link)

        try:
            if os.path.exists(target_link) or os.path.islink(target_link):
                os.remove(target_link)
            os.symlink(source_path, target_link)

            self.status_label.config(text="Restarting pipewire...")
            result = subprocess.run(
                ["systemctl", "--user", "restart", "pipewire", "pipewire-pulse"],
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
        if os.path.islink(self.target_link):
            link_target = os.readlink(self.target_link)
            self.current_label.config(text=f"WAV: {os.path.basename(link_target)}")
        else:
            self.current_label.config(text="WAV: None")

def main():
    root = tk.Tk()
    app = HRTFTesterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
