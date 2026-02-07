import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from scipy.io import wavfile
from generators.clap_generator import ClapGenerator
from utils.security import validate_filename

class ClapTab(ttk.Frame):
    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        # self.pack(fill=tk.BOTH, expand=True) # Managed by Notebook
        self.vars = {}

        # --- Synthesis Controls ---
        frame = ttk.LabelFrame(self, text="Clap Parameters", padding="10")
        frame.pack(fill=tk.X, expand=True, pady=10)

        self.create_slider(frame, "Transient Level", 0.0, 2.0, 1.0, "transient_level")
        self.create_slider(frame, "Reflections (Count)", 1.0, 10.0, 5.0, "reflections") # int cast later
        self.create_slider(frame, "Reflection Spacing (ms)", 1.0, 20.0, 8.0, "spacing")
        self.create_slider(frame, "Tail Length (ms)", 10.0, 300.0, 100.0, "tail_length")
        self.create_slider(frame, "Stereo Width", 0.0, 1.0, 0.5, "width")

        # Generate Button for this tab
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=10)
        generate_btn = ttk.Button(btn_frame, text="Generate Clap", command=self.generate)
        generate_btn.pack(side=tk.LEFT, padx=5)

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
            # Get values
            transient = self.vars["transient_level"].get()
            reflections = int(self.vars["reflections"].get())
            spacing = self.vars["spacing"].get()
            tail = self.vars["tail_length"].get()
            width = self.vars["width"].get()

            filename = self.main_window.filename_var.get()

            # Auto-rename if needed to avoid overwriting kick
            if filename == "output.wav" or filename.endswith("kick.wav"):
                filename = "clap_output.wav"
                self.main_window.filename_var.set(filename)

            if not filename.endswith('.wav'):
                filename += '.wav'

            # Validate filename
            is_valid, error_msg = validate_filename(filename)
            if not is_valid:
                messagebox.showerror("Invalid Filename", error_msg)
                return

            self.main_window.status_var.set("Generating Clap...")
            self.update_idletasks()

            # Run generation
            generator = ClapGenerator()
            audio = generator.generate(
                transient_level=transient,
                tail_length_ms=tail,
                reflections=reflections,
                spacing_ms=spacing,
                stereo_width=width
            )

            # Save
            # Transpose if stereo
            if audio.ndim == 2:
                audio_save = audio.T
            else:
                audio_save = audio

            scaled = np.int16(audio_save * 32767)
            wavfile.write(filename, 44100, scaled)

            self.main_window.status_var.set(f"Saved to {filename}")

            # Update Visualizer if present
            if hasattr(self.main_window, 'visualizer'):
                self.main_window.visualizer.update_plot(audio)

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.main_window.status_var.set("Error generating clap.")
