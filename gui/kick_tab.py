import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import json
import random as _random
from generators.kick_generator import TranceKickGenerator
from gui.envelope_editor import EnvelopeEditor
from gui.tooltip import Tooltip

# ---------------------------------------------------------------------------
# Presets – tuned for professional trance kick styles
# ---------------------------------------------------------------------------
KICK_PRESETS = {
    "Buzzism Euphoria": {
        "duration": 0.6, "body_freq": 55.0, "punch_semitones": 24,
        "punch_decay": 40.0, "body_decay": 500.0,
        "click_level": 0.8, "click_decay": 7.0, "click_width": 0.3,
        "drive": 4.0, "reverb": 0.0, "delay": 0.0,
        "distortion_amount": 0.0, "distortion_type": "hard_clip",
        "oversample": 2, "phase": 0.0,
    },
    "Classic Trance": {
        "duration": 0.5, "body_freq": 60.0, "punch_semitones": 20,
        "punch_decay": 35.0, "body_decay": 400.0,
        "click_level": 1.0, "click_decay": 10.0, "click_width": 0.0,
        "drive": 5.0, "reverb": 0.0, "delay": 0.0,
        "distortion_amount": 0.0, "distortion_type": "hard_clip",
        "oversample": 1, "phase": 0.0,
    },
    "Deep Underground": {
        "duration": 0.8, "body_freq": 48.0, "punch_semitones": 18,
        "punch_decay": 50.0, "body_decay": 700.0,
        "click_level": 0.6, "click_decay": 5.0, "click_width": 0.0,
        "drive": 3.0, "reverb": 0.1, "delay": 0.0,
        "distortion_amount": 0.0, "distortion_type": "hard_clip",
        "oversample": 2, "phase": 0.0,
    },
    "Hard Trance": {
        "duration": 0.4, "body_freq": 65.0, "punch_semitones": 30,
        "punch_decay": 30.0, "body_decay": 250.0,
        "click_level": 1.5, "click_decay": 12.0, "click_width": 0.2,
        "drive": 7.0, "reverb": 0.0, "delay": 0.0,
        "distortion_amount": 0.25, "distortion_type": "hard_clip",
        "oversample": 1, "phase": 0.0,
    },
    "Hard Techno": {
        "duration": 0.45, "body_freq": 58.0, "punch_semitones": 32,
        "punch_decay": 22.0, "body_decay": 180.0,
        "click_level": 2.2, "click_decay": 14.0, "click_width": 0.4,
        "drive": 9.0, "reverb": 0.0, "delay": 0.0,
        "distortion_amount": 0.65, "distortion_type": "hard_clip",
        "oversample": 2, "phase": 0.0,
    },
    "Industrial Foldback": {
        "duration": 0.5, "body_freq": 50.0, "punch_semitones": 36,
        "punch_decay": 28.0, "body_decay": 300.0,
        "click_level": 1.8, "click_decay": 18.0, "click_width": 0.5,
        "drive": 6.0, "reverb": 0.05, "delay": 0.0,
        "distortion_amount": 0.75, "distortion_type": "foldback",
        "oversample": 2, "phase": 0.0,
    },
    "Metallic Wavefold": {
        "duration": 0.5, "body_freq": 62.0, "punch_semitones": 28,
        "punch_decay": 25.0, "body_decay": 220.0,
        "click_level": 1.6, "click_decay": 10.0, "click_width": 0.3,
        "drive": 5.0, "reverb": 0.0, "delay": 0.0,
        "distortion_amount": 0.55, "distortion_type": "wavefolder",
        "oversample": 2, "phase": 0.0,
    },
}


class KickTab(ttk.Frame):
    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self.vars = {}
        self._distortion_type_var = tk.StringVar(value="hard_clip")
        self._lfo_target_var      = tk.StringVar(value="none")
        self._lfo_waveform_var    = tk.StringVar(value="sine")
        self._ab_slots = {"A": None, "B": None}   # preset snapshots

        # Internal notebook
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        synth_frame = ttk.Frame(notebook, padding="14 10")
        notebook.add(synth_frame, text="Synthesis")

        fx_frame = ttk.Frame(notebook, padding="14 10")
        notebook.add(fx_frame, text="Effects")

        bass_frame_tab = ttk.Frame(notebook, padding="14 10")
        notebook.add(bass_frame_tab, text="Bassline & Export")

        # ── Synthesis Tab ──────────────────────────────────────────────────

        # Presets row
        preset_frame = ttk.Frame(synth_frame)
        preset_frame.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(preset_frame, text="Preset:", width=20).pack(side=tk.LEFT)
        self._preset_var = tk.StringVar(value="Buzzism Euphoria")
        preset_cb = ttk.Combobox(
            preset_frame, textvariable=self._preset_var,
            values=list(KICK_PRESETS.keys()), state="readonly", width=20
        )
        preset_cb.pack(side=tk.LEFT, padx=4)
        preset_cb.bind("<<ComboboxSelected>>", self._load_preset)
        ttk.Button(preset_frame, text="Load", command=self._load_preset).pack(side=tk.LEFT)

        ttk.Separator(synth_frame, orient="horizontal").pack(fill=tk.X, pady=6)

        # Quality / Oversampling
        q_frame = ttk.Frame(synth_frame)
        q_frame.pack(fill=tk.X, pady=3)
        ttk.Label(q_frame, text="Quality Mode:", width=25).pack(side=tk.LEFT)
        self.vars["oversample"] = tk.IntVar(value=2)
        ttk.Combobox(q_frame, textvariable=self.vars["oversample"],
                     values=[1, 2], state="readonly", width=5).pack(side=tk.LEFT)
        ttk.Label(q_frame, text="(1=Std, 2=HQ Oversampled)").pack(side=tk.LEFT, padx=5)

        # Body & Pitch group
        self._section_header(synth_frame, "Body & Pitch")
        self.create_slider(synth_frame, "Body Frequency (Hz)", 35.0, 90.0,  55.0,  "body_freq",
            tooltip="Fundamental pitch of the sine-wave body.\n"
                    "Lower = deeper sub-bass (35 Hz).\n"
                    "Higher = snappier techno kick (90 Hz).")
        self.create_slider(synth_frame, "Body Decay (ms)",     100.0, 800.0, 500.0, "body_decay",
            tooltip="How long the body tone sustains before silence.\n"
                    "Short (100 ms) = punchy techno.\n"
                    "Long (700+ ms) = deep underground trance tail.")
        self.create_slider(synth_frame, "Punch Start (semitones)", 8.0, 40.0, 24.0, "punch_semitones",
            tooltip="How many semitones above Body Frequency the pitch\n"
                    "sweep starts. Larger = more dramatic downward glide.\n"
                    "24 st = 2 octaves above body freq.")
        self.create_slider(synth_frame, "Punch Decay (ms)",    10.0,  80.0,  40.0, "punch_decay",
            tooltip="Speed of the pitch sweep from Punch Start down\n"
                    "to Body Frequency.\n"
                    "Short = snappy attack click. Long = pitched tom feel.")
        self.create_slider(synth_frame, "Duration (s)",         0.3,   1.2,   0.6,  "duration",
            tooltip="Total length of the generated WAV sample.\n"
                    "Shorter = tighter, punchy kick.\n"
                    "Longer = more sustain / room for reverb tail.")
        self.create_slider(synth_frame, "Start Phase (deg)",    0.0,  360.0,  0.0,  "phase",
            tooltip="Starting phase of the sine oscillator in degrees.\n"
                    "0° = normal polarity.\n"
                    "180° = phase-inverted (useful for mono-compat checks).")

        # Envelope visualizer (linked to punch_decay, body_decay, duration)
        self._section_header(synth_frame, "Amplitude Envelope")
        self._env_editor = EnvelopeEditor(
            synth_frame,
            vars_dict={
                "punch_decay": self.vars["punch_decay"],
                "body_decay":  self.vars["body_decay"],
                "duration":    self.vars["duration"],
            },
        )
        self._env_editor.pack(fill=tk.X, pady=4)

        # Transient group
        self._section_header(synth_frame, "Transient")
        self.create_slider(synth_frame, "Click/Noise Level",    0.0,  3.0,   0.8,  "click_level",
            tooltip="Amplitude of the noise-burst transient layered\n"
                    "at the attack. Higher = more crack and presence.\n"
                    "0 = pure sine body only.")
        self.create_slider(synth_frame, "Click Decay (ms)",     1.0,  50.0,  7.0,  "click_decay",
            tooltip="How fast the click/noise layer fades.\n"
                    "Very short (1–3 ms) = transient pop only.\n"
                    "Longer = noise sweep into the body.")
        self.create_slider(synth_frame, "Click Width (Stereo)", 0.0,  2.0,   0.3,  "click_width",
            tooltip="Stereo width of the click/noise layer.\n"
                    "0 = mono centre. 1+ = wide stereo transient.\n"
                    "Body remains mono; only the click is widened.")

        # ── Effects Tab ───────────────────────────────────────────────────
        self.create_slider(fx_frame, "Saturation Drive (dB)", 0.0, 12.0, 4.0, "drive",
            tooltip="Soft-saturation gain applied before the limiter.\n"
                    "Adds harmonic warmth and perceived loudness.\n"
                    "2–5 dB = subtle glue. 8+ dB = aggressive saturation.")
        self.create_slider(fx_frame, "Reverb Amount",         0.0,  1.0, 0.0, "reverb",
            tooltip="Amount of room reverb mixed with the dry signal.\n"
                    "Keep low (0–0.1) for club kicks — reverb eats punch.\n"
                    "Useful for experimental or cinematic kicks.")
        self.create_slider(fx_frame, "Delay Amount",          0.0,  1.0, 0.0, "delay",
            tooltip="Short delay effect mix level.\n"
                    "Usually 0 for standard kick drums.\n"
                    "Subtle delay can add width or tempo-synced echo.")

        self._section_header(fx_frame, "Distortion")

        dist_type_frame = ttk.Frame(fx_frame)
        dist_type_frame.pack(fill=tk.X, pady=3)
        ttk.Label(dist_type_frame, text="Distortion Type:", width=25).pack(side=tk.LEFT)
        ttk.Combobox(
            dist_type_frame, textvariable=self._distortion_type_var,
            values=["hard_clip", "foldback", "wavefolder", "bitcrush"],
            state="readonly", width=14,
        ).pack(side=tk.LEFT)

        self.create_slider(fx_frame, "Distortion Amount", 0.0, 1.0, 0.0, "distortion_amount",
            tooltip="Intensity of the chosen distortion algorithm.\n"
                    "0 = clean bypass. 0.3 = subtle grit. 1 = fully clipped.\n"
                    "Pair with Distortion Type for different timbres.")

        self._section_header(fx_frame, "LFO (body modulation)")

        lfo_target_frame = ttk.Frame(fx_frame)
        lfo_target_frame.pack(fill=tk.X, pady=3)
        ttk.Label(lfo_target_frame, text="LFO Target:", width=25).pack(side=tk.LEFT)
        ttk.Combobox(
            lfo_target_frame, textvariable=self._lfo_target_var,
            values=["none", "body_freq", "drive"],
            state="readonly", width=12,
        ).pack(side=tk.LEFT)

        lfo_wave_frame = ttk.Frame(fx_frame)
        lfo_wave_frame.pack(fill=tk.X, pady=3)
        ttk.Label(lfo_wave_frame, text="LFO Waveform:", width=25).pack(side=tk.LEFT)
        ttk.Combobox(
            lfo_wave_frame, textvariable=self._lfo_waveform_var,
            values=["sine", "square", "saw", "triangle"],
            state="readonly", width=12,
        ).pack(side=tk.LEFT)

        self.create_slider(fx_frame, "LFO Rate (Hz)",  0.05, 20.0, 2.0, "lfo_rate_hz",
            tooltip="Oscillation speed of the LFO in cycles per second.\n"
                    "0.5–2 Hz = slow wobble / wub-wub effect.\n"
                    "10–20 Hz = fast tremolo / ring-mod character.")
        self.create_slider(fx_frame, "LFO Depth",      0.0,   1.0, 0.0, "lfo_depth",
            tooltip="How much the LFO modulates the target parameter.\n"
                    "0 = LFO is off (no modulation).\n"
                    "0.2–0.5 = subtle movement. 1.0 = full sweep.")

        # ── Bassline Tab ──────────────────────────────────────────────────
        bass_frame = ttk.LabelFrame(bass_frame_tab,
                                    text="Bassline & Sidechain (VST/DAW Integration)",
                                    padding="10")
        bass_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.vars["bass"] = tk.BooleanVar(value=False)
        ttk.Checkbutton(bass_frame, text="Generate Bassline Loop (138 BPM)",
                        variable=self.vars["bass"]).pack(anchor=tk.W)

        self.create_slider(bass_frame, "Bass Frequency (Hz)", 30.0, 100.0, 55.0, "bass_freq",
            tooltip="Root frequency of the generated bassline loop.\n"
                    "Should complement Body Frequency (e.g. same note or 5th).\n"
                    "30–50 Hz = sub bass. 60–100 Hz = mid bass.")
        self.create_slider(bass_frame, "Sidechain Depth",      0.0,   1.0,  0.8,  "sc_depth",
            tooltip="Depth of kick-triggered sidechain volume ducking\n"
                    "applied to the bassline. 0 = no ducking. 1 = full cut.\n"
                    "0.7–0.9 = classic pumping trance/techno feel.")

        ttk.Button(bass_frame, text="Export Sidechain Trigger (Click)",
                   command=self.export_trigger).pack(pady=5)

        # ── Bottom button rows ─────────────────────────────────────────────
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=(8, 2))
        self.generate_btn = ttk.Button(btn_frame, text="  Generate Kick  ",
                                       command=self.generate)
        self.generate_btn.pack(side=tk.LEFT, padx=5, ipady=4)
        ttk.Button(btn_frame, text="Randomize 🎲",
                   command=self.randomize).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save Preset…",
                   command=self.save_preset).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Load Preset…",
                   command=self.load_preset_file).pack(side=tk.LEFT, padx=5)

        # A/B comparison row
        ab_frame = ttk.Frame(self)
        ab_frame.pack(fill=tk.X, pady=(2, 10))
        ttk.Label(ab_frame, text="A/B Compare:", width=12).pack(side=tk.LEFT, padx=(5, 2))
        self._ab_a_btn = ttk.Button(ab_frame, text="◀ A", width=5,
                                    command=lambda: self._ab_load("A"))
        self._ab_a_btn.pack(side=tk.LEFT, padx=2)
        ttk.Button(ab_frame, text="→ A", width=5,
                   command=lambda: self._ab_store("A")).pack(side=tk.LEFT, padx=2)
        ttk.Separator(ab_frame, orient="vertical").pack(side=tk.LEFT, fill=tk.Y,
                                                         padx=6, pady=2)
        ttk.Button(ab_frame, text="→ B", width=5,
                   command=lambda: self._ab_store("B")).pack(side=tk.LEFT, padx=2)
        self._ab_b_btn = ttk.Button(ab_frame, text="◀ B", width=5,
                                    command=lambda: self._ab_load("B"))
        self._ab_b_btn.pack(side=tk.LEFT, padx=2)
        self._ab_status_lbl = ttk.Label(ab_frame, text="A: empty  B: empty",
                                        foreground="#888888")
        self._ab_status_lbl.pack(side=tk.LEFT, padx=8)

        # Load the default preset
        self._load_preset()

    # ── Helpers ────────────────────────────────────────────────────────────

    def _section_header(self, parent, title):
        """Bold section title with a full-width separator line to the right."""
        frm = ttk.Frame(parent)
        frm.pack(fill=tk.X, pady=(10, 3))
        ttk.Label(frm, text=title,
                  font=("TkDefaultFont", 9, "bold")).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Separator(frm, orient="horizontal").pack(
            side=tk.LEFT, fill=tk.X, expand=True, pady=4)

    _UNIT_MAP = {
        "freq": "Hz", "rate": "Hz", "hz": "Hz",
        "decay": "ms", "duration": "s",
        "drive": "dB", "semitones": "st", "phase": "°",
    }

    def _unit_for(self, var_name):
        vn = var_name.lower()
        for key, unit in self._UNIT_MAP.items():
            if key in vn:
                return unit
        return ""

    def create_slider(self, parent, label_text, min_val, max_val, default_val,
                      var_name, tooltip: str = ""):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)

        lbl = ttk.Label(frame, text=label_text, width=26)
        lbl.pack(side=tk.LEFT)

        # Smart decimal places based on parameter range
        span = max_val - min_val
        if span >= 100:
            fmt = "{:.0f}"
        elif span >= 5:
            fmt = "{:.1f}"
        else:
            fmt = "{:.2f}"

        unit = self._unit_for(var_name)

        var = tk.DoubleVar(value=default_val)
        scale = ttk.Scale(frame, from_=min_val, to=max_val,
                          orient=tk.HORIZONTAL, variable=var, length=200)
        scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 2))

        def _fmt(v):
            s = fmt.format(float(v))
            return f"{s} {unit}" if unit else s

        val_lbl = ttk.Label(frame, text=_fmt(default_val), width=9, anchor="e")
        val_lbl.pack(side=tk.LEFT, padx=(0, 4))

        scale.config(command=lambda v: val_lbl.config(text=_fmt(v)))

        if tooltip:
            Tooltip(lbl,   tooltip)
            Tooltip(scale, tooltip)

        self.vars[var_name] = var

    def _load_preset(self, event=None):
        name = self._preset_var.get()
        preset = KICK_PRESETS.get(name)
        if not preset:
            return
        for key, val in preset.items():
            if key == "distortion_type":
                self._distortion_type_var.set(val)
            elif key == "lfo_target":
                self._lfo_target_var.set(val)
            elif key == "lfo_waveform":
                self._lfo_waveform_var.set(val)
            elif key in self.vars:
                self.vars[key].set(val)

    # ── Preset Import / Export ─────────────────────────────────────────────

    def _current_params(self):
        """Collect all current slider/control values into a plain dict."""
        params = {}
        for key, var in self.vars.items():
            params[key] = var.get()
        params["distortion_type"]  = self._distortion_type_var.get()
        params["lfo_target"]       = self._lfo_target_var.get()
        params["lfo_waveform"]     = self._lfo_waveform_var.get()
        params["_preset_name"]     = self._preset_var.get()
        return params

    def save_preset(self):
        """Save the current parameters to a JSON file chosen by the user."""
        path = filedialog.asksaveasfilename(
            title="Save Kick Preset",
            defaultextension=".json",
            filetypes=[("Kick Preset", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "w") as f:
                json.dump(self._current_params(), f, indent=2)
            self.main_window.status_var.set(f"Preset saved: {path}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def load_preset_file(self):
        """Load parameters from a previously saved JSON preset file."""
        path = filedialog.askopenfilename(
            title="Load Kick Preset",
            filetypes=[("Kick Preset", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path) as f:
                params = json.load(f)
            for key, val in params.items():
                if key.startswith("_"):
                    continue
                if key == "distortion_type":
                    self._distortion_type_var.set(val)
                elif key == "lfo_target":
                    self._lfo_target_var.set(val)
                elif key == "lfo_waveform":
                    self._lfo_waveform_var.set(val)
                elif key in self.vars:
                    self.vars[key].set(val)
            name = params.get("_preset_name", "")
            if name:
                self._preset_var.set(name)
            self.main_window.status_var.set(f"Preset loaded: {path}")
        except Exception as e:
            messagebox.showerror("Load Error", str(e))

    # ── Randomize ──────────────────────────────────────────────────────────

    def randomize(self):
        """Randomize synthesis parameters within musically sensible bounds."""
        rng = _random.Random()

        # Body & Pitch (musically grounded)
        self.vars["body_freq"].set(rng.uniform(40.0, 72.0))
        self.vars["body_decay"].set(rng.uniform(200.0, 700.0))
        self.vars["punch_semitones"].set(rng.uniform(12.0, 36.0))
        self.vars["punch_decay"].set(rng.uniform(15.0, 65.0))
        self.vars["duration"].set(rng.uniform(0.35, 0.85))
        self.vars["phase"].set(0.0)   # keep phase deterministic

        # Transient
        self.vars["click_level"].set(rng.uniform(0.3, 2.0))
        self.vars["click_decay"].set(rng.uniform(3.0, 20.0))
        self.vars["click_width"].set(rng.uniform(0.0, 0.5))

        # Effects
        self.vars["drive"].set(rng.uniform(2.0, 10.0))
        self.vars["reverb"].set(rng.uniform(0.0, 0.12) if rng.random() < 0.25 else 0.0)
        self.vars["delay"].set(0.0)

        # Distortion (35 % chance, biased toward lower amounts)
        if rng.random() < 0.35:
            self.vars["distortion_amount"].set(rng.uniform(0.1, 0.55))
            self._distortion_type_var.set(
                rng.choice(["hard_clip", "hard_clip", "foldback", "wavefolder"]))
        else:
            self.vars["distortion_amount"].set(0.0)

        # LFO (20 % chance of body_freq wub)
        if rng.random() < 0.20:
            self._lfo_target_var.set("body_freq")
            self._lfo_waveform_var.set(rng.choice(["sine", "triangle"]))
            self.vars["lfo_rate_hz"].set(rng.uniform(0.5, 6.0))
            self.vars["lfo_depth"].set(rng.uniform(0.05, 0.25))
        else:
            self._lfo_target_var.set("none")
            self.vars["lfo_depth"].set(0.0)

        self._preset_var.set("— Randomized —")
        self.main_window.status_var.set("Randomized! Press Generate to hear.")

    # ── A/B Comparison ─────────────────────────────────────────────────────

    def _ab_store(self, slot):
        """Snapshot the current parameters into slot A or B."""
        self._ab_slots[slot] = self._current_params()
        self._ab_update_status()
        self.main_window.status_var.set(
            f"Stored to {slot} — press ◀ {slot} to recall anytime.")

    def _ab_load(self, slot):
        """Restore parameters from slot A or B."""
        params = self._ab_slots.get(slot)
        if params is None:
            self.main_window.status_var.set(
                f"Slot {slot} is empty — press → {slot} to store first.")
            return
        for key, val in params.items():
            if key.startswith("_"):
                continue
            if key == "distortion_type":
                self._distortion_type_var.set(val)
            elif key == "lfo_target":
                self._lfo_target_var.set(val)
            elif key == "lfo_waveform":
                self._lfo_waveform_var.set(val)
            elif key in self.vars:
                self.vars[key].set(val)
        pname = params.get("_preset_name", "")
        if pname:
            self._preset_var.set(pname)
        self.main_window.status_var.set(f"Loaded {slot}.")

    def _ab_update_status(self):
        filled = {k: ("● filled" if v else "○ empty")
                  for k, v in self._ab_slots.items()}
        self._ab_status_lbl.config(
            text=f"A: {filled['A']}   B: {filled['B']}")
        # Highlight buttons that have data
        self._ab_a_btn.config(
            style="Accent.TButton" if self._ab_slots["A"] else "TButton")
        self._ab_b_btn.config(
            style="Accent.TButton" if self._ab_slots["B"] else "TButton")

    # ── Actions ────────────────────────────────────────────────────────────

    def export_trigger(self):
        try:
            generator = TranceKickGenerator()
            generator.save_sidechain_trigger("sidechain_trigger.wav")
            messagebox.showinfo("Success", "Exported sidechain_trigger.wav")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def generate(self):
        self.generate_btn.config(state="disabled")
        self.main_window.status_var.set("Generating Kick...")
        self.main_window.start_progress()

        # Snapshot all params before spawning thread
        oversample       = self.vars["oversample"].get()
        body_freq        = self.vars["body_freq"].get()
        body_decay       = self.vars["body_decay"].get()
        punch_semi       = int(round(self.vars["punch_semitones"].get()))
        punch_decay      = self.vars["punch_decay"].get()
        duration         = self.vars["duration"].get()
        phase            = self.vars["phase"].get()
        click_level      = self.vars["click_level"].get()
        click_decay      = self.vars["click_decay"].get()
        click_width      = self.vars["click_width"].get()
        drive            = self.vars["drive"].get()
        reverb           = self.vars["reverb"].get()
        delay            = self.vars["delay"].get()
        distortion_amt   = self.vars["distortion_amount"].get()
        distortion_mode  = self._distortion_type_var.get()
        lfo_target       = self._lfo_target_var.get()
        lfo_waveform     = self._lfo_waveform_var.get()
        lfo_rate_hz      = self.vars["lfo_rate_hz"].get()
        lfo_depth        = self.vars["lfo_depth"].get()
        generate_bass    = self.vars["bass"].get()
        bass_freq        = self.vars["bass_freq"].get()
        sc_depth         = self.vars["sc_depth"].get()

        filename = self.main_window.filename_var.get()
        if not filename.endswith('.wav'):
            filename += '.wav'

        smoke_params = None
        if hasattr(self.main_window, 'smoke_tab'):
            smoke_params = self.main_window.smoke_tab.get_params()

        def _run():
            try:
                gen = TranceKickGenerator(duration=duration)
                audio = gen.generate(
                    body_freq=body_freq,
                    punch_semitones=punch_semi,
                    punch_decay_ms=punch_decay,
                    body_decay_ms=body_decay,
                    click_level=click_level,
                    click_decay_ms=click_decay,
                    click_width=click_width,
                    drive_db=drive,
                    reverb_amount=reverb,
                    delay_amount=delay,
                    distortion_amount=distortion_amt,
                    distortion_mode=distortion_mode,
                    lfo_target=lfo_target,
                    lfo_waveform=lfo_waveform,
                    lfo_rate_hz=lfo_rate_hz,
                    lfo_depth=lfo_depth,
                    generate_bass=generate_bass,
                    bass_freq=bass_freq,
                    sc_depth=sc_depth,
                    oversample=oversample,
                    phase_deg=phase,
                    smoke_params=smoke_params,
                )
                gen.save(filename, audio)

                def _done():
                    self.main_window.stop_progress()
                    self.main_window.status_var.set(f"Saved to {filename}")
                    if hasattr(self.main_window, 'visualizer'):
                        self.main_window.visualizer.update_plot(audio)
                    self.generate_btn.config(state="normal")
                self.after(0, _done)

            except Exception as e:
                def _err(exc=e):
                    self.main_window.stop_progress()
                    messagebox.showerror("Generation Error", str(exc))
                    self.main_window.status_var.set("Error generating kick.")
                    self.generate_btn.config(state="normal")
                self.after(0, _err)

        threading.Thread(target=_run, daemon=True).start()
