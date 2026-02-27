import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import json
from generators.kick_generator import TranceKickGenerator
from gui.envelope_editor import EnvelopeEditor

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
        self._lfo_target_var   = tk.StringVar(value="none")
        self._lfo_waveform_var = tk.StringVar(value="sine")

        # Internal notebook
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        synth_frame = ttk.Frame(notebook, padding="10")
        notebook.add(synth_frame, text="Synthesis")

        fx_frame = ttk.Frame(notebook, padding="10")
        notebook.add(fx_frame, text="Effects")

        bass_frame_tab = ttk.Frame(notebook, padding="10")
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
        ttk.Label(synth_frame, text="── Body & Pitch ──", foreground="gray").pack(anchor=tk.W, pady=(8, 2))
        self.create_slider(synth_frame, "Body Frequency (Hz)", 35.0, 90.0,  55.0,  "body_freq")
        self.create_slider(synth_frame, "Body Decay (ms)",     100.0, 800.0, 500.0, "body_decay")
        self.create_slider(synth_frame, "Punch Start (semitones)", 8.0, 40.0, 24.0, "punch_semitones")
        self.create_slider(synth_frame, "Punch Decay (ms)",    10.0,  80.0,  40.0, "punch_decay")
        self.create_slider(synth_frame, "Duration (s)",         0.3,   1.2,   0.6,  "duration")
        self.create_slider(synth_frame, "Start Phase (deg)",    0.0,  360.0,  0.0,  "phase")

        # Envelope visualizer (linked to punch_decay, body_decay, duration)
        ttk.Label(synth_frame, text="── Amplitude Envelope ──",
                  foreground="gray").pack(anchor=tk.W, pady=(8, 2))
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
        ttk.Label(synth_frame, text="── Transient ──", foreground="gray").pack(anchor=tk.W, pady=(8, 2))
        self.create_slider(synth_frame, "Click/Noise Level",    0.0,  3.0,   0.8,  "click_level")
        self.create_slider(synth_frame, "Click Decay (ms)",     1.0,  50.0,  7.0,  "click_decay")
        self.create_slider(synth_frame, "Click Width (Stereo)", 0.0,  2.0,   0.3,  "click_width")

        # ── Effects Tab ───────────────────────────────────────────────────
        self.create_slider(fx_frame, "Saturation Drive (dB)", 0.0, 12.0, 4.0, "drive")
        self.create_slider(fx_frame, "Reverb Amount",         0.0,  1.0, 0.0, "reverb")
        self.create_slider(fx_frame, "Delay Amount",          0.0,  1.0, 0.0, "delay")

        ttk.Separator(fx_frame, orient="horizontal").pack(fill=tk.X, pady=8)
        ttk.Label(fx_frame, text="── Distortion ──", foreground="gray").pack(anchor=tk.W, pady=(0, 4))

        dist_type_frame = ttk.Frame(fx_frame)
        dist_type_frame.pack(fill=tk.X, pady=3)
        ttk.Label(dist_type_frame, text="Distortion Type:", width=25).pack(side=tk.LEFT)
        ttk.Combobox(
            dist_type_frame, textvariable=self._distortion_type_var,
            values=["hard_clip", "foldback", "wavefolder", "bitcrush"],
            state="readonly", width=14,
        ).pack(side=tk.LEFT)

        self.create_slider(fx_frame, "Distortion Amount", 0.0, 1.0, 0.0, "distortion_amount")

        ttk.Separator(fx_frame, orient="horizontal").pack(fill=tk.X, pady=8)
        ttk.Label(fx_frame, text="── LFO (body modulation) ──",
                  foreground="gray").pack(anchor=tk.W, pady=(0, 4))

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

        self.create_slider(fx_frame, "LFO Rate (Hz)",  0.05, 20.0, 2.0, "lfo_rate_hz")
        self.create_slider(fx_frame, "LFO Depth",      0.0,   1.0, 0.0, "lfo_depth")

        # ── Bassline Tab ──────────────────────────────────────────────────
        bass_frame = ttk.LabelFrame(bass_frame_tab,
                                    text="Bassline & Sidechain (VST/DAW Integration)",
                                    padding="10")
        bass_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.vars["bass"] = tk.BooleanVar(value=False)
        ttk.Checkbutton(bass_frame, text="Generate Bassline Loop (138 BPM)",
                        variable=self.vars["bass"]).pack(anchor=tk.W)

        self.create_slider(bass_frame, "Bass Frequency (Hz)", 30.0, 100.0, 55.0, "bass_freq")
        self.create_slider(bass_frame, "Sidechain Depth",      0.0,   1.0,  0.8,  "sc_depth")

        ttk.Button(bass_frame, text="Export Sidechain Trigger (Click)",
                   command=self.export_trigger).pack(pady=5)

        # Bottom button bar: Generate | Save Preset | Load Preset
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=10)
        self.generate_btn = ttk.Button(btn_frame, text="Generate Kick", command=self.generate)
        self.generate_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save Preset…", command=self.save_preset).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Load Preset…", command=self.load_preset_file).pack(side=tk.LEFT, padx=5)

        # Load the default preset
        self._load_preset()

    # ── Helpers ────────────────────────────────────────────────────────────

    def create_slider(self, parent, label_text, min_val, max_val, default_val, var_name):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=3)

        ttk.Label(frame, text=label_text, width=25).pack(side=tk.LEFT)

        var = tk.DoubleVar(value=default_val)
        scale = ttk.Scale(frame, from_=min_val, to=max_val,
                          orient=tk.HORIZONTAL, variable=var, length=200)
        scale.pack(side=tk.LEFT, fill=tk.X, expand=True)

        val_lbl = ttk.Label(frame, text=f"{default_val:.1f}", width=7)
        val_lbl.pack(side=tk.LEFT, padx=5)

        def update_label(v):
            val_lbl.config(text=f"{float(v):.1f}")
        scale.config(command=update_label)

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
                    self.main_window.status_var.set(f"Saved to {filename}")
                    if hasattr(self.main_window, 'visualizer'):
                        self.main_window.visualizer.update_plot(audio)
                    self.generate_btn.config(state="normal")
                self.after(0, _done)

            except Exception as e:
                def _err():
                    messagebox.showerror("Error", str(e))
                    self.main_window.status_var.set("Error generating kick.")
                    self.generate_btn.config(state="normal")
                self.after(0, _err)

        threading.Thread(target=_run, daemon=True).start()
