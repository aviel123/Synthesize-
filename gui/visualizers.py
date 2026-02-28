import tkinter as tk
from tkinter import ttk
import numpy as np


class WaveformVisualizer(tk.Frame):
    """
    Dual-mode visualizer: toggles between waveform view and spectrum (FFT) view.
    Also displays Peak and RMS loudness meters below the canvas.
    """

    FREQ_BANDS = [
        (20,   80,   "#e74c3c", "Sub"),
        (80,   300,  "#e67e22", "Body"),
        (300,  3000, "#2ecc71", "Mid"),
        (3000, 8000, "#3498db", "Presence"),
        (8000, 20000,"#9b59b6", "Air"),
    ]

    def __init__(self, parent, height=140, bg="#1a1a2e", fg="lime"):
        super().__init__(parent, bg=bg)
        self.height = height
        self.bg = bg
        self.fg = fg
        self._sample_rate = 44100
        self._mode = tk.StringVar(value="wave")  # "wave" | "spectrum"
        self._audio_data = None

        # ── Toolbar ───────────────────────────────────────────────────────
        toolbar = tk.Frame(self, bg=bg)
        toolbar.pack(fill=tk.X)

        tk.Label(toolbar, text="View:", bg=bg, fg="#aaaaaa",
                 font=("Helvetica", 8)).pack(side=tk.LEFT, padx=(4, 2))
        for label, val in [("Waveform", "wave"), ("Spectrum", "spectrum")]:
            tk.Radiobutton(
                toolbar, text=label, variable=self._mode, value=val,
                bg=bg, fg="#cccccc", selectcolor="#333355",
                activebackground=bg, font=("Helvetica", 8),
                command=self._redraw
            ).pack(side=tk.LEFT)

        # ── Canvas ────────────────────────────────────────────────────────
        self.canvas = tk.Canvas(self, height=height, bg=bg, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # ── Loudness meters ───────────────────────────────────────────────
        meter_frame = tk.Frame(self, bg=bg)
        meter_frame.pack(fill=tk.X, padx=4, pady=(2, 4))

        self._peak_var = tk.StringVar(value="Peak: ---")
        self._rms_var  = tk.StringVar(value="RMS:  ---")

        tk.Label(meter_frame, textvariable=self._peak_var,
                 bg=bg, fg="#e74c3c", font=("Courier", 9, "bold"),
                 anchor=tk.W).pack(side=tk.LEFT, padx=(0, 20))
        tk.Label(meter_frame, textvariable=self._rms_var,
                 bg=bg, fg="#f39c12", font=("Courier", 9, "bold"),
                 anchor=tk.W).pack(side=tk.LEFT)

    # ── Public API ─────────────────────────────────────────────────────────

    def update_plot(self, audio_data, sample_rate=44100):
        self._audio_data = audio_data
        self._sample_rate = sample_rate
        self._update_meters(audio_data)
        self._redraw()

    # ── Internal ───────────────────────────────────────────────────────────

    def _to_mono(self, audio_data):
        if audio_data is None or (hasattr(audio_data, '__len__') and len(audio_data) == 0):
            return None
        if audio_data.ndim == 2:
            return np.mean(audio_data, axis=0)
        return audio_data

    def _update_meters(self, audio_data):
        from effects.limiter import measure_loudness
        try:
            peak_db, rms_db = measure_loudness(audio_data, self._sample_rate)
            peak_color = "#e74c3c" if peak_db > -3 else "#2ecc71"
            self._peak_var.set(f"Peak: {peak_db:+6.1f} dBFS")
            self._rms_var.set(f"RMS:  {rms_db:+6.1f} dBFS")
        except Exception:
            pass

    def _redraw(self):
        self.canvas.delete("all")
        data = self._to_mono(self._audio_data)
        if data is None:
            return
        if self._mode.get() == "spectrum":
            self._draw_spectrum(data)
        else:
            self._draw_waveform(data)

    def _canvas_size(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1: w = 760
        if h <= 1: h = self.height
        return w, h

    def _draw_waveform(self, data):
        w, h = self._canvas_size()

        # Draw centre line
        self.canvas.create_line(0, h // 2, w, h // 2, fill="#333333", width=1)

        step = max(1, len(data) // w)
        data_vis = data[::step][:w]

        center_y = h / 2
        scale_y  = h / 2 * 0.88

        coords = []
        for x, val in enumerate(data_vis):
            coords.append(x)
            coords.append(center_y - float(val) * scale_y)

        if len(coords) > 2:
            self.canvas.create_line(coords, fill=self.fg, width=1)

    def _draw_spectrum(self, data):
        """FFT magnitude spectrum with frequency-band colouring."""
        w, h = self._canvas_size()
        sr = self._sample_rate

        # Zero-pad to next power of 2 for speed, cap at 32768 points
        n_fft = min(32768, 2 ** int(np.ceil(np.log2(len(data)))))
        spectrum = np.abs(np.fft.rfft(data * np.hanning(len(data)), n=n_fft))
        freqs = np.fft.rfftfreq(n_fft, d=1.0 / sr)

        # Convert to dB (floor at -80 dB)
        spectrum_db = 20 * np.log10(np.maximum(spectrum, 1e-4))
        db_min, db_max = -80.0, 0.0

        # Map frequency axis: log scale 20Hz–20kHz
        f_min, f_max = 20.0, min(20000.0, sr / 2)

        def freq_to_x(f):
            return int(np.clip(
                (np.log10(f / f_min) / np.log10(f_max / f_min)) * w,
                0, w - 1
            ))

        # Rasterise spectrum to pixel columns (max in each column)
        pixel_db = np.full(w, db_min)
        for i, (f, mag) in enumerate(zip(freqs, spectrum_db)):
            if f < f_min or f > f_max:
                continue
            px = freq_to_x(f)
            if mag > pixel_db[px]:
                pixel_db[px] = mag

        # Colour by frequency band
        def band_color(freq_hz):
            for lo, hi, color, _ in self.FREQ_BANDS:
                if lo <= freq_hz < hi:
                    return color
            return "#888888"

        # Draw bars
        for px in range(w):
            db = pixel_db[px]
            bar_h = int((db - db_min) / (db_max - db_min) * h)
            bar_h = max(1, min(bar_h, h))
            f_hz = f_min * (f_max / f_min) ** (px / w)
            color = band_color(f_hz)
            self.canvas.create_line(px, h, px, h - bar_h, fill=color, width=1)

        # Frequency grid lines + labels
        for f_label in [50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000]:
            if f_label < f_min or f_label > f_max:
                continue
            px = freq_to_x(f_label)
            self.canvas.create_line(px, 0, px, h, fill="#333333", width=1)
            label = f"{f_label // 1000}k" if f_label >= 1000 else str(f_label)
            self.canvas.create_text(px, h - 8, text=label,
                                    fill="#666666", font=("Helvetica", 7), anchor=tk.S)

        # Band legend
        x_leg = 4
        for _, _, color, name in self.FREQ_BANDS:
            self.canvas.create_rectangle(x_leg, 4, x_leg + 8, 14, fill=color, outline="")
            self.canvas.create_text(x_leg + 10, 9, text=name,
                                    fill="#aaaaaa", font=("Helvetica", 7), anchor=tk.W)
            x_leg += 55
