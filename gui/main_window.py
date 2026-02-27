import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from gui.kick_tab import KickTab
from gui.clap_tab import ClapTab
from gui.combo_tab import ComboTab
from gui.smoke_tab import SmokeTab
from gui.visualizers import WaveformVisualizer
from gui.sequencer_tab import SequencerTab

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Euphoria Trance Drum Designer")
        self.root.geometry("860x680")
        self.root.minsize(760, 560)

        # Style
        style = ttk.Style()
        style.theme_use('clam')

        # Main Container
        main_container = ttk.Frame(root, padding="12 8")
        main_container.pack(fill=tk.BOTH, expand=True)

        # ── Header ──────────────────────────────────────────────────────
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(
            header_frame,
            text="Euphoria Trance Drum Designer",
            font=("Helvetica", 15, "bold"),
        ).pack(side=tk.LEFT)

        # File output inline with header (right side)
        self.filename_var = tk.StringVar(value="output.wav")
        ttk.Label(header_frame, text="Output:").pack(side=tk.RIGHT, padx=(8, 2))
        ttk.Button(header_frame, text="Browse…",
                   command=self._browse_output).pack(side=tk.RIGHT, padx=(0, 4))
        ttk.Entry(header_frame, textvariable=self.filename_var,
                  width=26).pack(side=tk.RIGHT, padx=(0, 4))

        ttk.Separator(main_container, orient="horizontal").pack(fill=tk.X, pady=(4, 8))

        # ── Visualizer ──────────────────────────────────────────────────
        self.visualizer = WaveformVisualizer(main_container, height=130)
        self.visualizer.pack(fill=tk.X, expand=False, pady=(0, 6))

        # ── Status bar ──────────────────────────────────────────────────
        status_bar = ttk.Frame(main_container, relief="sunken")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var = tk.StringVar(value="Ready.")
        ttk.Label(
            status_bar, textvariable=self.status_var,
            foreground="#2a7a2a", anchor="w", padding="4 2",
        ).pack(fill=tk.X)

        # ── Tabs ────────────────────────────────────────────────────────
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

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

        # Step Sequencer Tab
        self.sequencer_tab = SequencerTab(self.notebook, self)
        self.notebook.add(self.sequencer_tab, text="Sequencer")

    def _browse_output(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
            initialfile=self.filename_var.get(),
        )
        if path:
            self.filename_var.set(path)

if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
