import tkinter as tk
from tkinter import ttk, messagebox
import os
from gui.kick_tab import KickTab
from gui.clap_tab import ClapTab
from gui.combo_tab import ComboTab
from gui.smoke_tab import SmokeTab
from gui.visualizers import WaveformVisualizer

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Euphoria Trance Drum Designer")
        self.root.geometry("800x600")

        # Style
        style = ttk.Style()
        style.theme_use('clam')

        # Main Container
        main_container = ttk.Frame(root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(main_container, text="Trance Drum Designer", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=(0, 10))

        # File Output Frame (Shared)
        file_frame = ttk.Frame(main_container)
        file_frame.pack(fill=tk.X, pady=10)

        ttk.Label(file_frame, text="Output Filename:").pack(side=tk.LEFT)
        self.filename_var = tk.StringVar(value="output.wav")
        entry = ttk.Entry(file_frame, textvariable=self.filename_var, width=30)
        entry.pack(side=tk.LEFT, padx=10)

        # Status
        self.status_var = tk.StringVar()
        status_label = ttk.Label(main_container, textvariable=self.status_var, foreground="green")
        status_label.pack(side=tk.BOTTOM, pady=10)

        # Visualizer
        self.visualizer = WaveformVisualizer(main_container, height=120)
        self.visualizer.pack(fill=tk.X, expand=False, pady=10)

        # Tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        # Kick Tab
        self.kick_tab = KickTab(self.notebook, self)
        self.notebook.add(self.kick_tab, text="Kick Generator")

        # Clap Tab
        self.clap_tab = ClapTab(self.notebook, self)
        self.notebook.add(self.clap_tab, text="Clap Generator")

        # Smoke Tab
        self.smoke_tab = SmokeTab(self.notebook, self)
        self.notebook.add(self.smoke_tab, text="Smoke / Noise")

        # Combo/Pattern Tab
        self.combo_tab = ComboTab(self.notebook, self)
        self.notebook.add(self.combo_tab, text="Pattern/Combo")

if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
