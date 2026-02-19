import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from scipy.io import wavfile
from generators.kick_generator import TranceKickGenerator
from generators.clap_generator import ClapGenerator
from utils.validators import InputValidator

class ComboTab(ttk.Frame):
    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        # self.pack(fill=tk.BOTH, expand=True) # Managed by Notebook
        self.vars = {}

        # Title
        ttk.Label(self, text="Combo Pattern Generator (4-Bar Loop)", font=("Helvetica", 12)).pack(pady=10)

        # Instructions
        desc = "Generates a 138 BPM Trance Loop:\nKick on 1, 2, 3, 4\nClap on 2, 4 (and ghost notes)"
        ttk.Label(self, text=desc, justify=tk.CENTER).pack(pady=10)

        # Controls
        frame = ttk.LabelFrame(self, text="Pattern Settings", padding="10")
        frame.pack(fill=tk.X, expand=True, pady=10)

        self.create_slider(frame, "Swing (%)", 0.0, 50.0, 0.0, "swing")
        self.create_slider(frame, "Kick Volume", 0.0, 1.0, 0.9, "kick_vol")
        self.create_slider(frame, "Clap Volume", 0.0, 1.0, 0.8, "clap_vol")

        # Generate Button
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=20)
        generate_btn = ttk.Button(btn_frame, text="Generate Combo Loop", command=self.generate)
        generate_btn.pack(side=tk.TOP, padx=5)

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
        try:
            self.main_window.status_var.set("Generating Combo Loop...")
            self.update_idletasks()

            # 1. Generate Kick (Using current Kick Tab settings)
            # Retrieve settings from KickTab (need access)
            # Access main_window -> kick_tab -> vars
            kt_vars = self.main_window.kick_tab.vars

            # Use duration from Kick Tab
            kick_duration = kt_vars["duration"].get()
            kick_gen = TranceKickGenerator(duration=kick_duration)

            kick_audio = kick_gen.generate(
                click_level=kt_vars["click_level"].get(),
                click_decay_ms=kt_vars["click_decay"].get(),
                drive_db=kt_vars["drive"].get(),
                reverb_amount=kt_vars["reverb"].get(),
                delay_amount=kt_vars["delay"].get(),
                oversample=kt_vars["oversample"].get(),
                click_width=kt_vars["click_width"].get(),
                phase_deg=kt_vars["phase"].get()
            )

            # 2. Generate Clap (Using current Clap Tab settings)
            clap_gen = ClapGenerator()
            ct_vars = self.main_window.clap_tab.vars
            clap_audio = clap_gen.generate(
                transient_level=ct_vars["transient_level"].get(),
                tail_length_ms=ct_vars["tail_length"].get(),
                reflections=int(ct_vars["reflections"].get()),
                spacing_ms=ct_vars["spacing"].get(),
                stereo_width=ct_vars["width"].get()
            )

            # 3. Create Pattern
            bpm = 138.0
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

            # Pattern Grid (1 = Kick, 2 = Clap, 3 = Both)
            # Standard Trance: Kick on every beat, Clap on 2 and 4 (beats 1, 3, 5, 7... 0-indexed)
            # Beats: 0 1 2 3 ... 15
            # Kicks: 0, 1, 2, 3 ... 15
            # Claps: 1, 3, 5, 7 ... 15 (Backbeat)

            kick_vol = self.vars["kick_vol"].get()
            clap_vol = self.vars["clap_vol"].get()

            # Add Swing later?

            for beat in range(total_beats):
                pos = beat * beat_samples

                # Add Kick (Every Beat)
                if is_stereo:
                    k_len = kick_audio.shape[1]
                else:
                    k_len = len(kick_audio)

                end = pos + k_len
                if end > loop_len: end = loop_len

                if is_stereo:
                    loop[:, pos:end] += kick_audio[:, :end-pos] * kick_vol
                else:
                    loop[pos:end] += kick_audio[:end-pos] * kick_vol

                # Add Clap (Every other beat: 1, 3, 5...)
                # Beats are 0, 1, 2, 3 -> Clap on 1 and 3 (Backbeat in 4/4 if 0=1)
                # Actually beat 1 (0-indexed) is 2nd beat.
                if beat % 2 == 1:
                    # Offset slightly for "human" feel or swing?
                    clap_pos = pos
                    if is_stereo:
                         c_len = clap_audio.shape[1]
                    else:
                         c_len = len(clap_audio)

                    end_c = clap_pos + c_len
                    if end_c > loop_len: end_c = loop_len

                    if is_stereo:
                        loop[:, clap_pos:end_c] += clap_audio[:, :end_c-clap_pos] * clap_vol
                    else:
                        loop[clap_pos:end_c] += clap_audio[:end_c-clap_pos] * clap_vol

            # Normalize
            max_val = np.max(np.abs(loop))
            if max_val > 0:
                loop = loop / max_val * 0.95

            # Save
            filename = self.main_window.filename_var.get()
            if filename == "output.wav" or filename.endswith("kick.wav") or filename.endswith("clap_output.wav"):
                filename = "combo_loop.wav"
                self.main_window.filename_var.set(filename)

            if not filename.endswith("combo.wav") and not filename.endswith(".wav"):
                filename += "_combo.wav"

            filename = InputValidator.sanitize_filename(filename)

            if loop.ndim == 2:
                loop_save = loop.T
            else:
                loop_save = loop

            scaled = np.int16(loop_save * 32767)
            wavfile.write(filename, 44100, scaled)

            self.main_window.status_var.set(f"Saved Combo to {filename}")

            # Visualizer
            if hasattr(self.main_window, 'visualizer'):
                self.main_window.visualizer.update_plot(loop)

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.main_window.status_var.set("Error generating combo.")
