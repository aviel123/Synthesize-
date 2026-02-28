import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import config
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

        # Restore persisted session
        self._cfg = config.load()
        self.root.geometry(self._cfg.get("window_geometry", "860x680"))
        self.root.minsize(760, 560)

        # Style
        style = ttk.Style()
        style.theme_use(self._cfg.get("theme", "clam"))

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
        self.filename_var = tk.StringVar(
            value=self._cfg.get("output_filename", "output.wav")
        )
        self.filename_var.trace_add("write", self._on_filename_change)

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
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Progress bar (hidden until a generation is running)
        self.progress = ttk.Progressbar(
            status_bar, mode="indeterminate", length=160
        )
        self.progress.pack(side=tk.RIGHT, padx=(4, 6), pady=2)

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

        # Restore last active tab
        last_tab = self._cfg.get("last_tab", 0)
        try:
            self.notebook.select(last_tab)
        except Exception:
            pass
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

        # Persist window geometry on close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # ── Keyboard shortcuts ───────────────────────────────────────────
        self.root.bind_all("<Control-g>", self._shortcut_generate)
        self.root.bind_all("<Control-G>", self._shortcut_generate)
        self.root.bind_all("<Control-r>", self._shortcut_randomize)
        self.root.bind_all("<Control-R>", self._shortcut_randomize)
        self.root.bind_all("<Control-s>", self._shortcut_save_preset)
        self.root.bind_all("<Control-S>", self._shortcut_save_preset)
        self.root.bind_all("<F5>",        self._shortcut_generate)

    # ── Progress helpers (called from generator tabs) ─────────────────

    def start_progress(self) -> None:
        """Show the indeterminate progress bar and start animation."""
        self.progress.start(12)

    def stop_progress(self) -> None:
        """Stop and hide the progress bar."""
        self.progress.stop()

    # ── Internal callbacks ────────────────────────────────────────────

    def _browse_output(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
            initialfile=self.filename_var.get(),
        )
        if path:
            self.filename_var.set(path)

    def _on_filename_change(self, *_):
        config.set("output_filename", self.filename_var.get())

    def _on_tab_change(self, *_):
        try:
            config.set("last_tab", self.notebook.index(self.notebook.select()))
        except Exception:
            pass

    def _on_close(self):
        config.save({"window_geometry": self.root.geometry()})
        self.root.destroy()

    # ── Keyboard shortcut handlers ────────────────────────────────────

    def _shortcut_generate(self, _event=None):
        """Ctrl+G / F5 — generate on the currently visible tab."""
        try:
            tab_idx = self.notebook.index(self.notebook.select())
        except Exception:
            return
        tabs = [self.kick_tab, self.clap_tab, None, self.combo_tab, None]
        if tab_idx < len(tabs) and tabs[tab_idx] is not None:
            tabs[tab_idx].generate()

    def _shortcut_randomize(self, _event=None):
        """Ctrl+R — randomize kick parameters (only on Kick tab)."""
        try:
            tab_idx = self.notebook.index(self.notebook.select())
        except Exception:
            return
        if tab_idx == 0:
            self.kick_tab.randomize()

    def _shortcut_save_preset(self, _event=None):
        """Ctrl+S — save kick preset (only on Kick tab)."""
        try:
            tab_idx = self.notebook.index(self.notebook.select())
        except Exception:
            return
        if tab_idx == 0:
            self.kick_tab.save_preset()


if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
