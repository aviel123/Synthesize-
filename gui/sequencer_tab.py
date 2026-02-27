import tkinter as tk
from tkinter import ttk, filedialog
import threading
import numpy as np


class SequencerTab(ttk.Frame):
    """
    16/32-step drum sequencer.

    Rows: Kick · Clap · HiHat
    Playback uses sounddevice (pip install sounddevice).
    Export Loop renders the full pattern to a WAV file.
    """

    ROWS = [
        ("Kick",  "#e74c3c"),
        ("Clap",  "#3498db"),
        ("HiHat", "#2ecc71"),
    ]
    MAX_STEPS = 32

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self._playing     = False
        self._play_thread = None
        self._audio_cache = None
        self._step_buttons    = {}                              # (row, step) -> tk.Button
        self._pattern         = {                              # (row, step) -> bool
            (r, s): False
            for r in range(len(self.ROWS))
            for s in range(self.MAX_STEPS)
        }

        self._build_ui()
        self._set_default_pattern()

    # ── UI construction ─────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Header bar ──
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=10, pady=8)

        ttk.Label(header, text="BPM:").pack(side=tk.LEFT)
        self._bpm_var = tk.DoubleVar(value=138.0)
        ttk.Scale(header, from_=60, to=200, variable=self._bpm_var,
                  orient=tk.HORIZONTAL, length=120).pack(side=tk.LEFT, padx=4)
        self._bpm_lbl = ttk.Label(header, text="138", width=4)
        self._bpm_lbl.pack(side=tk.LEFT, padx=(0, 12))
        self._bpm_var.trace_add("write",
            lambda *_: self._bpm_lbl.config(text=f"{self._bpm_var.get():.0f}"))

        ttk.Label(header, text="Steps:").pack(side=tk.LEFT)
        self._steps_var = tk.IntVar(value=16)
        ttk.Combobox(header, textvariable=self._steps_var,
                     values=[16, 32], state="readonly", width=4).pack(
            side=tk.LEFT, padx=(4, 14))
        self._steps_var.trace_add("write", lambda *_: self._update_step_visibility())

        self._play_btn = ttk.Button(header, text="▶  Play", command=self._toggle_play)
        self._play_btn.pack(side=tk.LEFT, padx=(0, 6))

        ttk.Button(header, text="Export Loop…",
                   command=self._export_loop).pack(side=tk.LEFT, padx=4)
        ttk.Button(header, text="Clear",
                   command=self._clear_pattern).pack(side=tk.LEFT, padx=4)

        # ── Step grid ──
        grid_outer = tk.Frame(self, bg="#1a1a2e")
        grid_outer.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)

        for r, (row_name, color) in enumerate(self.ROWS):
            tk.Label(grid_outer, text=row_name, width=6, anchor=tk.E,
                     bg="#1a1a2e", fg=color,
                     font=("Helvetica", 9, "bold")).grid(
                row=r * 2, column=0, padx=(0, 6), pady=3, sticky=tk.E)

            for s in range(self.MAX_STEPS):
                # Shade every group-of-4 slightly differently
                base_bg = "#2a2a4e" if (s // 4) % 2 == 0 else "#24244a"
                btn = tk.Button(
                    grid_outer, width=2, height=1,
                    bg=base_bg, relief="flat", bd=1, cursor="hand2",
                    command=lambda rr=r, ss=s: self._toggle_step(rr, ss),
                )
                btn.grid(row=r * 2, column=s + 1, padx=1, pady=2)
                self._step_buttons[(r, s)] = btn

        # ── Playhead indicators ──
        ind_frame = tk.Frame(grid_outer, bg="#1a1a2e")
        ind_frame.grid(
            row=len(self.ROWS) * 2, column=1,
            columnspan=self.MAX_STEPS, sticky=tk.EW, pady=4)
        self._step_indicators = []
        for s in range(self.MAX_STEPS):
            ind = tk.Label(ind_frame, width=2, height=1,
                           bg="#1a1a2e", relief="flat")
            ind.pack(side=tk.LEFT, padx=1)
            self._step_indicators.append(ind)

        # ── Beat numbers ──
        for beat in range(8):
            tk.Label(grid_outer, text=f"{beat + 1}",
                     bg="#1a1a2e", fg="#444466",
                     font=("Helvetica", 7)).grid(
                row=len(self.ROWS) * 2 + 1,
                column=beat * 4 + 1, columnspan=4, sticky=tk.W, pady=(0, 4))

        self._update_step_visibility()

    # ── Pattern logic ───────────────────────────────────────────────────────

    def _update_step_visibility(self):
        steps = self._steps_var.get()
        for r in range(len(self.ROWS)):
            for s in range(self.MAX_STEPS):
                btn = self._step_buttons[(r, s)]
                if s < steps:
                    btn.grid()
                else:
                    btn.grid_remove()
        for s in range(self.MAX_STEPS):
            if s < steps:
                self._step_indicators[s].pack(side=tk.LEFT, padx=1)
            else:
                self._step_indicators[s].pack_forget()

    def _toggle_step(self, row, step):
        key = (row, step)
        self._pattern[key] = not self._pattern[key]
        active = self._pattern[key]
        grp = (step // 4) % 2
        off_bg = "#2a2a4e" if grp == 0 else "#24244a"
        self._step_buttons[key].config(
            bg=self.ROWS[row][1] if active else off_bg)

    def _set_default_pattern(self):
        """Classic 4-on-the-floor + snare-on-2&4 + off-beat hi-hat."""
        for s in [0, 4, 8, 12]:          # Kick
            self._toggle_step(0, s)
        for s in [4, 12]:                # Clap
            self._toggle_step(1, s)
        for s in range(0, 16, 2):        # HiHat
            self._toggle_step(2, s)

    def _clear_pattern(self):
        for r in range(len(self.ROWS)):
            for s in range(self.MAX_STEPS):
                if self._pattern[(r, s)]:
                    self._toggle_step(r, s)

    # ── Playback ────────────────────────────────────────────────────────────

    def _toggle_play(self):
        if self._playing:
            self._playing = False
            self._play_btn.config(text="▶  Play")
            self._clear_indicators()
            self.main_window.status_var.set("Stopped.")
        else:
            self._playing = True
            self._play_btn.config(text="■  Stop")
            self._audio_cache = None   # rebuild on each play session
            t = threading.Thread(target=self._playback_loop, daemon=True)
            t.start()

    def _clear_indicators(self):
        for ind in self._step_indicators:
            ind.config(bg="#1a1a2e")

    def _playback_loop(self):
        try:
            import sounddevice as sd
        except ImportError:
            self.after(0, lambda: self.main_window.status_var.set(
                "sounddevice not found — install with: pip install sounddevice"))
            self._playing = False
            self.after(0, lambda: self._play_btn.config(text="▶  Play"))
            return

        SR = 44100
        self.after(0, lambda: self.main_window.status_var.set(
            "Building audio clips…"))
        self._audio_cache = self._prebuild_audio(SR)
        self.after(0, lambda: self.main_window.status_var.set("Playing…"))

        step = 0
        while self._playing:
            bpm   = self._bpm_var.get()
            steps = self._steps_var.get()
            step_dur = 60.0 / bpm / 4       # one 16th note in seconds
            n_samp   = int(step_dur * SR)

            mix = np.zeros(n_samp, dtype=np.float32)
            for r in range(len(self.ROWS)):
                if self._pattern.get((r, step % steps), False):
                    clip = self._audio_cache.get(r, np.zeros(1, np.float32))
                    n = min(len(clip), n_samp)
                    mix[:n] += clip[:n]

            mix = np.clip(mix, -1.0, 1.0)

            s_now = step % steps

            def _highlight(s=s_now):
                self._clear_indicators()
                if s < len(self._step_indicators):
                    self._step_indicators[s].config(bg="#f39c12")

            self.after(0, _highlight)
            sd.play(mix, SR)
            sd.wait()
            step += 1

        self.after(0, self._clear_indicators)

    # ── Audio synthesis ─────────────────────────────────────────────────────

    def _prebuild_audio(self, sr):
        from generators.kick_generator        import TranceKickGenerator
        from generators.clap_generator        import ClapGenerator
        from generators.advanced_noise_generator import AdvancedNoiseGenerator

        cache = {}

        # Kick — use current kick-tab settings if available
        try:
            kt = getattr(self.main_window, "kick_tab", None)
            if kt is not None:
                dur   = kt.vars["duration"].get()
                bf    = kt.vars["body_freq"].get()
                psemi = int(round(kt.vars["punch_semitones"].get()))
                pdec  = kt.vars["punch_decay"].get()
                bdec  = kt.vars["body_decay"].get()
                drive = kt.vars["drive"].get()
                dist_amt  = kt.vars.get("distortion_amount",
                                        tk.DoubleVar(value=0.0)).get()
                dist_mode = kt._distortion_type_var.get()
                kg = TranceKickGenerator(sample_rate=sr, duration=dur)
                kick = kg.generate(
                    body_freq=bf, punch_semitones=psemi,
                    punch_decay_ms=pdec, body_decay_ms=bdec,
                    drive_db=drive,
                    distortion_amount=dist_amt, distortion_mode=dist_mode,
                )
            else:
                kg   = TranceKickGenerator(sample_rate=sr, duration=0.4)
                kick = kg.generate()
            if kick.ndim == 2:
                kick = np.mean(kick, axis=0)
            cache[0] = (kick * 0.85).astype(np.float32)
        except Exception:
            cache[0] = np.zeros(int(sr * 0.4), dtype=np.float32)

        # Clap
        try:
            cg   = ClapGenerator(sample_rate=sr)
            clap = cg.generate()
            if clap.ndim == 2:
                clap = np.mean(clap, axis=0)
            cache[1] = (clap * 0.70).astype(np.float32)
        except Exception:
            cache[1] = np.zeros(int(sr * 0.5), dtype=np.float32)

        # HiHat — short white noise burst with exponential decay
        try:
            ng    = AdvancedNoiseGenerator(sample_rate=sr)
            hihat = ng.generate_noise("white", duration=0.07)
            decay = np.exp(-np.linspace(0, 18, len(hihat)))
            cache[2] = (hihat * decay * 0.35).astype(np.float32)
        except Exception:
            cache[2] = np.zeros(int(sr * 0.07), dtype=np.float32)

        return cache

    # ── Export ──────────────────────────────────────────────────────────────

    def _export_loop(self):
        import scipy.io.wavfile as wav

        path = filedialog.asksaveasfilename(
            title="Export Loop as WAV",
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
        )
        if not path:
            return

        SR    = 44100
        bpm   = self._bpm_var.get()
        steps = self._steps_var.get()
        step_dur      = 60.0 / bpm / 4
        total_samples = int(step_dur * steps * SR)
        mix           = np.zeros(total_samples, dtype=np.float32)

        audio_cache = self._prebuild_audio(SR)

        for s in range(steps):
            offset = int(s * step_dur * SR)
            for r in range(len(self.ROWS)):
                if self._pattern.get((r, s), False):
                    clip = audio_cache.get(r, np.zeros(1, np.float32))
                    n = min(len(clip), total_samples - offset)
                    if n > 0:
                        mix[offset:offset + n] += clip[:n]

        mix = np.clip(mix, -1.0, 1.0)
        wav.write(path, SR, (mix * 32767).astype(np.int16))
        self.main_window.status_var.set(f"Loop exported → {path}")
