import tkinter as tk
from tkinter import ttk
import os
import glob
import subprocess
import sys
import pystray
from PIL import Image
import psutil
import win32gui
import win32con
import win32api
import wmi  # For WiFi control
import winsound  # For volume control (basic)
from datetime import datetime

class CustomShell:
    def __init__(self, root):
        self.root = root
        self.root.title("Custom Shell")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#E5F1FB')

        # Taskbar
        self.taskbar = tk.Frame(root, bg='#2B2B2B', height=48)
        self.taskbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Start Button
        self.start_button = tk.Button(self.taskbar, text="⊞", font=("Segoe UI", 12), bg='#2B2B2B', fg='white', 
                                      command=self.toggle_apps_menu)
        self.start_button.pack(side=tk.LEFT, padx=5)

        # Pinned Apps
        self.pinned_frame = tk.Frame(self.taskbar, bg='#2B2B2B')
        self.pinned_frame.pack(side=tk.LEFT)
        self.load_pinned_apps()

        # System Tray
        self.setup_system_tray()

        # Apps Menu
        self.apps_menu = tk.Toplevel(root)
        self.apps_menu.withdraw()
        self.apps_menu.overrideredirect(True)
        self.apps_menu.geometry(f"300x400+0+{self.root.winfo_screenheight()-448}")
        self.apps_menu.configure(bg='#2B2B2B')
        self.apps_listbox = tk.Listbox(self.apps_menu, bg='#2B2B2B', fg='white', font=("Segoe UI", 10), 
                                       borderwidth=0, highlightthickness=0)
        self.apps_listbox.pack(fill=tk.BOTH, expand=True)
        self.apps_listbox.bind('<<ListboxSelect>>', self.launch_app)
        self.populate_apps_menu()

        # Quick Settings
        self.quick_settings = tk.Toplevel(root)
        self.quick_settings.withdraw()
        self.quick_settings.overrideredirect(True)
        self.quick_settings.geometry(f"300x400+{self.root.winfo_screenwidth()-300}+{self.root.winfo_screenheight()-448}")
        self.quick_settings.configure(bg='#2B2B2B')
        self.setup_quick_settings()

    def setup_system_tray(self):
        tray_frame = tk.Frame(self.taskbar, bg='#2B2B2B')
        tray_frame.pack(side=tk.RIGHT)

        # Clock
        self.clock = tk.Label(tray_frame, text=datetime.now().strftime("%H:%M"), bg='#2B2B2B', fg='white', 
                              font=("Segoe UI", 10))
        self.clock.pack(side=tk.RIGHT, padx=5)
        self.clock.bind("<Button-1>", lambda e: self.toggle_quick_settings())
        self.root.after(1000, self.update_clock)

        # WiFi Button
        self.wifi_button = tk.Button(tray_frame, text="WiFi", bg='#2B2B2B', fg='white', 
                                     command=self.toggle_wifi)
        self.wifi_button.pack(side=tk.RIGHT, padx=2)

        # Volume Button
        self.volume_button = tk.Button(tray_frame, text="Vol", bg='#2B2B2B', fg='white', 
                                       command=self.toggle_volume)
        self.volume_button.pack(side=tk.RIGHT, padx=2)

        # Power Button (placeholder)
        tk.Button(tray_frame, text="Pwr", bg='#2B2B2B', fg='white', command=self.shutdown).pack(side=tk.RIGHT, padx=2)

    def setup_quick_settings(self):
        # Quick Settings Buttons
        tk.Button(self.quick_settings, text="Wi-Fi", bg='#2B2B2B', fg='white', width=10, height=5, 
                  command=self.toggle_wifi).place(x=20, y=20)
        tk.Button(self.quick_settings, text="Bluetooth", bg='#2B2B2B', fg='white', width=10, height=5).place(x=110, y=20)
        tk.Button(self.quick_settings, text="Hotspot", bg='#2B2B2B', fg='white', width=10, height=5).place(x=200, y=20)
        tk.Button(self.quick_settings, text="Airplane", bg='#2B2B2B', fg='white', width=10, height=5).place(x=20, y=110)
        tk.Button(self.quick_settings, text="Accessibility", bg='#2B2B2B', fg='white', width=10, height=5).place(x=110, y=110)

        # Power Options
        tk.Button(self.quick_settings, text="Lock", bg='#2B2B2B', fg='white', width=10, 
                  command=self.lock_screen).place(x=20, y=340)
        tk.Button(self.quick_settings, text="Sign Out", bg='#2B2B2B', fg='white', width=10, 
                  command=self.sign_out).place(x=110, y=340)
        tk.Button(self.quick_settings, text="Power", bg='#2B2B2B', fg='white', width=10, 
                  command=self.shutdown).place(x=200, y=340)

    def load_pinned_apps(self):
        pinned_path = os.path.join(os.getenv('APPDATA'), r"Microsoft\Internet Explorer\Quick Launch\User Pinned\TaskBar")
        if os.path.exists(pinned_path):
            for lnk in glob.glob(os.path.join(pinned_path, "*.lnk")):
                name = os.path.splitext(os.path.basename(lnk))[0]
                btn = tk.Button(self.pinned_frame, text=name, bg='#2B2B2B', fg='white', 
                                command=lambda path=lnk: subprocess.Popen(['start', path], shell=True))
                btn.pack(side=tk.LEFT, padx=2)

    def populate_apps_menu(self):
        directories = [
            r"C:\Program Files",
            r"C:\Program Files (x86)",
            os.path.join(os.getenv('APPDATA'), r"Microsoft\Windows\Start Menu\Programs"),
            r"C:\Users\Public\Desktop",
            os.path.expanduser("~/Desktop")
        ]
        for dir in directories:
            if os.path.exists(dir):
                for root, _, files in os.walk(dir):
                    for file in files:
                        if file.endswith(('.exe', '.lnk')):
                            self.apps_listbox.insert(tk.END, (os.path.splitext(file)[0], os.path.join(root, file)))

    def launch_app(self, event):
        selection = self.apps_listbox.curselection()
        if selection:
            app = self.apps_listbox.get(selection[0])
            subprocess.Popen(['start', app[1]], shell=True)
            self.apps_menu.withdraw()

    def toggle_apps_menu(self):
        if self.apps_menu.winfo_viewable():
            self.apps_menu.withdraw()
        else:
            self.apps_menu.deiconify()
            self.quick_settings.withdraw()

    def toggle_quick_settings(self):
        if self.quick_settings.winfo_viewable():
            self.quick_settings.withdraw()
        else:
            self.quick_settings.deiconify()
            self.apps_menu.withdraw()

    def update_clock(self):
        self.clock.config(text=datetime.now().strftime("%H:%M"))
        self.root.after(1000, self.update_clock)

    def toggle_wifi(self):
        try:
            c = wmi.WMI()
            for adapter in c.Win32_NetworkAdapter(NetConnectionID="Wi-Fi"):
                if adapter.NetEnabled:
                    adapter.Disable()
                    self.wifi_button.config(text="WiFi Off")
                    self.quick_settings.winfo_children()[0].config(text="Wi-Fi Off")
                else:
                    adapter.Enable()
                    self.wifi_button.config(text="WiFi On")
                    self.quick_settings.winfo_children()[0].config(text="Wi-Fi On")
        except Exception as e:
            tk.messagebox.showerror("Error", f"WiFi toggle failed: {e}")

    def toggle_volume(self):
        # Basic mute/unmute (no fine control without additional libraries)
        try:
            # This is a simple toggle; for real volume control, you'd need pyaudio or similar
            win32api.keybd_event(win32con.VK_VOLUME_MUTE, 0)
            self.volume_button.config(text="Vol" if self.volume_button["text"] == "Vol Off" else "Vol Off")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Volume toggle failed: {e}")

    def lock_screen(self):
        subprocess.Popen("rundll32.exe user32.dll,LockWorkStation")

    def shutdown(self):
        subprocess.Popen("shutdown /s /t 0")

    def sign_out(self):
        subprocess.Popen("shutdown /l")

if __name__ == "__main__":
    root = tk.Tk()
    app = CustomShell(root)
    root.mainloop()
