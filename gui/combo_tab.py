import tkinter as tk
from tkinter import ttk, messagebox
import threading
import numpy as np
from scipy.io import wavfile
from generators.kick_generator import TranceKickGenerator
from generators.clap_generator import ClapGenerator

class ComboTab(ttk.Frame):
    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self.vars = {}

        # Title
        ttk.Label(self, text="Combo Pattern Generator (4-Bar Loop)", font=("Helvetica", 12)).pack(pady=10)

        # Instructions
        desc = "Generates a Trance Loop:\nKick on 1, 2, 3, 4\nClap on 2, 4 (and ghost notes)"
        ttk.Label(self, text=desc, justify=tk.CENTER).pack(pady=10)

        # Controls
        frame = ttk.LabelFrame(self, text="Pattern Settings", padding="10")
        frame.pack(fill=tk.X, expand=True, pady=10)

        self.create_slider(frame, "BPM", 100.0, 180.0, 138.0, "bpm")
        self.create_slider(frame, "Swing (%)", 0.0, 50.0, 0.0, "swing")
        self.create_slider(frame, "Kick Volume", 0.0, 1.0, 0.9, "kick_vol")
        self.create_slider(frame, "Clap Volume", 0.0, 1.0, 0.8, "clap_vol")

        # Generate Button
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=20)
        self.generate_btn = ttk.Button(btn_frame, text="Generate Combo Loop", command=self.generate)
        self.generate_btn.pack(side=tk.TOP, padx=5)

    def create_slider(self, parent, label_text, min_val, max_val, default_val, var_name):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)

        lbl = ttk.Label(frame, text=label_text, width=25)
        lbl.pack(side=tk.LEFT)

        var = tk.DoubleVar(value=default_val)
        scale = ttk.Scale(frame, from_=min_val, to=max_val, orient=tk.HORIZONTAL, variable=var, length=200)
        scale.pack(side=tk.LEFT, fill=tk.X, expand=True)

        val_lbl = ttk.Label(frame, text=f"{default_val:.2f}", width=6)
        val_lbl.pack(side=tk.LEFT, padx=5)

        def update_label(v):
            val_lbl.config(text=f"{float(v):.2f}")
        scale.config(command=update_label)

        self.vars[var_name] = var

    def generate(self):
        self.generate_btn.config(state="disabled")
        self.main_window.status_var.set("Generating Combo Loop...")

        # Collect all parameters before spawning thread
        bpm = self.vars["bpm"].get()
        kick_vol = self.vars["kick_vol"].get()
        clap_vol = self.vars["clap_vol"].get()

        kt_vars = self.main_window.kick_tab.vars
        kick_params = {
            "duration": kt_vars["duration"].get(),
            "click_level": kt_vars["click_level"].get(),
            "click_decay": kt_vars["click_decay"].get(),
            "drive": kt_vars["drive"].get(),
            "reverb": kt_vars["reverb"].get(),
            "delay": kt_vars["delay"].get(),
            "oversample": kt_vars["oversample"].get(),
            "click_width": kt_vars["click_width"].get(),
            "phase": kt_vars["phase"].get(),
        }

        ct_vars = self.main_window.clap_tab.vars
        clap_params = {
            "transient_level": ct_vars["transient_level"].get(),
            "tail_length": ct_vars["tail_length"].get(),
            "reflections": int(ct_vars["reflections"].get()),
            "spacing": ct_vars["spacing"].get(),
            "width": ct_vars["width"].get(),
        }

        filename = self.main_window.filename_var.get()
        if filename in ("output.wav",) or filename.endswith("kick.wav") or filename.endswith("clap_output.wav"):
            filename = "combo_loop.wav"
            self.main_window.filename_var.set(filename)
        if not filename.endswith(".wav"):
            filename += "_combo.wav"

        def _run():
            try:
                # 1. Generate Kick
                kick_gen = TranceKickGenerator(duration=kick_params["duration"])
                kick_audio = kick_gen.generate(
                    click_level=kick_params["click_level"],
                    click_decay_ms=kick_params["click_decay"],
                    drive_db=kick_params["drive"],
                    reverb_amount=kick_params["reverb"],
                    delay_amount=kick_params["delay"],
                    oversample=kick_params["oversample"],
                    click_width=kick_params["click_width"],
                    phase_deg=kick_params["phase"]
                )

                # 2. Generate Clap
                clap_gen = ClapGenerator()
                clap_audio = clap_gen.generate(
                    transient_level=clap_params["transient_level"],
                    tail_length_ms=clap_params["tail_length"],
                    reflections=clap_params["reflections"],
                    spacing_ms=clap_params["spacing"],
                    stereo_width=clap_params["width"]
                )

                # 3. Create Pattern
                beat_ms = 60000.0 / bpm
                beat_samples = int(beat_ms * 44100 / 1000.0)

                # 4 Bars = 16 Beats
                total_beats = 16
                loop_len = beat_samples * total_beats

                # Determine channels (stereo if either is stereo)
                is_stereo = (kick_audio.ndim == 2 or clap_audio.ndim == 2)

                if is_stereo:
                    loop = np.zeros((2, loop_len))
                    if kick_audio.ndim == 1:
                        kick_audio = np.vstack((kick_audio, kick_audio))
                    if clap_audio.ndim == 1:
                        clap_audio = np.vstack((clap_audio, clap_audio))
                else:
                    loop = np.zeros(loop_len)

                for beat in range(total_beats):
                    pos = beat * beat_samples

                    # Add Kick (Every Beat)
                    k_len = kick_audio.shape[1] if is_stereo else len(kick_audio)
                    end = min(pos + k_len, loop_len)

                    if is_stereo:
                        loop[:, pos:end] += kick_audio[:, :end-pos] * kick_vol
                    else:
                        loop[pos:end] += kick_audio[:end-pos] * kick_vol

                    # Add Clap (Backbeat: beats 1, 3, 5...)
                    if beat % 2 == 1:
                        c_len = clap_audio.shape[1] if is_stereo else len(clap_audio)
                        end_c = min(pos + c_len, loop_len)

                        if is_stereo:
                            loop[:, pos:end_c] += clap_audio[:, :end_c-pos] * clap_vol
                        else:
                            loop[pos:end_c] += clap_audio[:end_c-pos] * clap_vol

                # Normalize
                max_val = np.max(np.abs(loop))
                if max_val > 0:
                    loop = loop / max_val * 0.95

                # Save
                loop_save = loop.T if loop.ndim == 2 else loop
                scaled = np.int16(loop_save * 32767)
                wavfile.write(filename, 44100, scaled)

                def _done():
                    self.main_window.status_var.set(f"Saved Combo to {filename}")
                    if hasattr(self.main_window, 'visualizer'):
                        self.main_window.visualizer.update_plot(loop)
                    self.generate_btn.config(state="normal")

                self.after(0, _done)

            except Exception as e:
                def _err():
                    messagebox.showerror("Error", str(e))
                    self.main_window.status_var.set("Error generating combo.")
                    self.generate_btn.config(state="normal")
                self.after(0, _err)

        threading.Thread(target=_run, daemon=True).start()
