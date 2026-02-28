import tkinter as tk
from tkinter import ttk, messagebox

class SmokeTab(ttk.Frame):
    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        # Layout is managed by the parent Notebook
        self.vars = {}

        # --- Main Frame ---
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Enable/Disable
        self.vars["enabled"] = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="Enable Smoke Layer", variable=self.vars["enabled"]).pack(anchor=tk.W, pady=5)

        # Presets Dropdown
        ttk.Label(main_frame, text="Preset:").pack(anchor=tk.W)
        self.preset_var = tk.StringVar(value="Armin Euphoria Smoke")
        presets = ["Armin Euphoria Smoke", "Vintage Analog Hiss", "Harsh Digital Noise", "Subtle Air"]
        preset_cb = ttk.Combobox(main_frame, textvariable=self.preset_var, values=presets, state="readonly")
        preset_cb.pack(fill=tk.X, pady=5)
        preset_cb.bind("<<ComboboxSelected>>", self.load_preset)

        # Parameters Frame
        params_frame = ttk.LabelFrame(main_frame, text="Smoke Parameters", padding="10")
        params_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Character
        char_frame = ttk.Frame(params_frame)
        char_frame.pack(fill=tk.X, pady=5)
        ttk.Label(char_frame, text="Character:", width=15).pack(side=tk.LEFT)
        self.vars["character"] = tk.StringVar(value="soft")
        char_cb = ttk.Combobox(char_frame, textvariable=self.vars["character"], values=["soft", "harsh", "analog", "digital"], state="readonly")
        char_cb.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Sliders
        self.create_slider(params_frame, "Level (dB)", -60.0, 0.0, -12.0, "level")
        self.create_slider(params_frame, "Density (%)", 0.0, 100.0, 60.0, "density")
        self.create_slider(params_frame, "HP Freq (Hz)", 1000.0, 15000.0, 6000.0, "hp_freq")
        self.create_slider(params_frame, "LP Freq (Hz)", 5000.0, 20000.0, 16000.0, "lp_freq")
        self.create_slider(params_frame, "Start Delay (ms)", 0.0, 200.0, 15.0, "delay")
        self.create_slider(params_frame, "Fade In (ms)", 0.0, 500.0, 120.0, "fade_in")
        self.create_slider(params_frame, "Fade Out (ms)", 0.0, 1000.0, 350.0, "fade_out")
        self.create_slider(params_frame, "Stereo Width (%)", 0.0, 100.0, 85.0, "width")

    def create_slider(self, parent, label_text, min_val, max_val, default_val, var_name):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)

        lbl = ttk.Label(frame, text=label_text, width=20)
        lbl.pack(side=tk.LEFT)

        var = tk.DoubleVar(value=default_val)
        scale = ttk.Scale(frame, from_=min_val, to=max_val, orient=tk.HORIZONTAL, variable=var, length=200)
        scale.pack(side=tk.LEFT, fill=tk.X, expand=True)

        val_lbl = ttk.Label(frame, text=f"{default_val:.1f}", width=6)
        val_lbl.pack(side=tk.LEFT, padx=5)

        def update_label(v):
            val_lbl.config(text=f"{float(v):.1f}")
        scale.config(command=update_label)

        self.vars[var_name] = var

    def load_preset(self, event=None):
        name = self.preset_var.get()
        # Hardcoded presets for now
        data = {}
        if name == "Armin Euphoria Smoke":
            data = {"level": -15, "density": 60, "character": "soft", "hp_freq": 7000, "lp_freq": 16000, "delay": 15, "fade_in": 120, "fade_out": 350, "width": 85}
        elif name == "Vintage Analog Hiss":
            data = {"level": -18, "density": 40, "character": "analog", "hp_freq": 5000, "lp_freq": 14000, "delay": 0, "fade_in": 10, "fade_out": 200, "width": 50}
        elif name == "Harsh Digital Noise":
            data = {"level": -10, "density": 80, "character": "harsh", "hp_freq": 9000, "lp_freq": 20000, "delay": 5, "fade_in": 50, "fade_out": 150, "width": 100}
        elif name == "Subtle Air":
            data = {"level": -24, "density": 30, "character": "soft", "hp_freq": 12000, "lp_freq": 18000, "delay": 0, "fade_in": 200, "fade_out": 400, "width": 60}

        # Apply
        for key, val in data.items():
            if key in self.vars:
                self.vars[key].set(val)

    def get_params(self):
        params = {}
        for key, var in self.vars.items():
            params[key] = var.get()
        return params
