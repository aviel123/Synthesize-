import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from kick_generator import TranceKickGenerator

class KickGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Euphoria Trance Kick Generator")
        self.root.geometry("600x500")

        # Style
        style = ttk.Style()
        style.theme_use('clam')

        # Main Frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="Trance Kick Designer (Armin Style)", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=(0, 20))

        # Notebook for Tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        # Tab 1: Synthesis
        synth_frame = ttk.Frame(notebook, padding="10")
        notebook.add(synth_frame, text="Synthesis")

        # Tab 2: Effects
        fx_frame = ttk.Frame(notebook, padding="10")
        notebook.add(fx_frame, text="Effects")

        # Tab 3: Bassline/Export
        bass_frame_tab = ttk.Frame(notebook, padding="10")
        notebook.add(bass_frame_tab, text="Bassline & Export")

        # --- Synthesis Tab ---

        # Quality/Oversampling
        q_frame = ttk.Frame(synth_frame)
        q_frame.pack(fill=tk.X, pady=5)
        ttk.Label(q_frame, text="Quality Mode:", width=25).pack(side=tk.LEFT)
        self.oversample_var = tk.IntVar(value=1)
        q_combo = ttk.Combobox(q_frame, textvariable=self.oversample_var, values=[1, 2], state="readonly", width=5)
        q_combo.pack(side=tk.LEFT)
        ttk.Label(q_frame, text="(1=Std, 2=High/Oversampled)").pack(side=tk.LEFT, padx=5)

        self.create_slider(synth_frame, "Duration (s)", 0.1, 1.0, 0.5, "duration")

        # Phase
        self.create_slider(synth_frame, "Start Phase (deg)", 0.0, 360.0, 0.0, "phase")

        # Click/Noise Level
        self.create_slider(synth_frame, "Click/Noise Level", 0.0, 3.0, 1.0, "click_level")

        # Click Decay
        self.create_slider(synth_frame, "Click Decay (ms)", 5.0, 100.0, 10.0, "click_decay")

        # Stereo Width (Click)
        self.create_slider(synth_frame, "Click Width (Stereo)", 0.0, 2.0, 0.0, "click_width")

        # --- Effects Tab ---

        # Drive
        self.create_slider(fx_frame, "Saturation Drive (dB)", 0.0, 12.0, 4.5, "drive")

        # Reverb
        self.create_slider(fx_frame, "Reverb Amount", 0.0, 1.0, 0.0, "reverb")

        # Delay
        self.create_slider(fx_frame, "Delay Amount", 0.0, 1.0, 0.0, "delay")

        # --- Bassline Tab ---
        bass_frame = ttk.LabelFrame(bass_frame_tab, text="Bassline & Sidechain (VST/DAW Integration)", padding="10")
        bass_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Checkbox for Bassline
        self.bass_var = tk.BooleanVar(value=False)
        bass_chk = ttk.Checkbutton(bass_frame, text="Generate Bassline Loop (138 BPM)", variable=self.bass_var)
        bass_chk.pack(anchor=tk.W)

        # Bass Freq
        self.create_slider(bass_frame, "Bass Frequency (Hz)", 30.0, 100.0, 55.0, "bass_freq")

        # Sidechain Depth
        self.create_slider(bass_frame, "Sidechain Depth", 0.0, 1.0, 0.8, "sc_depth")

        # Export Trigger Button
        trigger_btn = ttk.Button(bass_frame, text="Export Sidechain Trigger (Click)", command=self.export_trigger)
        trigger_btn.pack(pady=5)

        # File Output Frame
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=20)

        ttk.Label(file_frame, text="Output Filename:").pack(side=tk.LEFT)
        self.filename_var = tk.StringVar(value="euphoria_kick.wav")
        entry = ttk.Entry(file_frame, textvariable=self.filename_var, width=30)
        entry.pack(side=tk.LEFT, padx=10)

        # Actions
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        generate_btn = ttk.Button(btn_frame, text="Generate & Save", command=self.generate)
        generate_btn.pack(side=tk.LEFT, padx=5)

        # Status
        self.status_var = tk.StringVar()
        status_label = ttk.Label(main_frame, textvariable=self.status_var, foreground="green")
        status_label.pack(pady=10)

        # Store slider vars
        self.vars = {}

    def create_slider(self, parent, label_text, min_val, max_val, default_val, var_name):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)

        lbl = ttk.Label(frame, text=label_text, width=25)
        lbl.pack(side=tk.LEFT)

        var = tk.DoubleVar(value=default_val)
        scale = ttk.Scale(frame, from_=min_val, to=max_val, orient=tk.HORIZONTAL, variable=var, length=200)
        scale.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Value label
        val_lbl = ttk.Label(frame, text=f"{default_val:.2f}", width=6)
        val_lbl.pack(side=tk.LEFT, padx=5)

        # Update value label on change
        def update_label(v):
            val_lbl.config(text=f"{float(v):.2f}")

        scale.config(command=update_label)

        # Store using setattr to access later via self.var_name? No, create a dict.
        setattr(self, f"{var_name}_var", var)

    def generate(self):
        try:
            # Get values
            oversample = self.oversample_var.get()
            duration = self.duration_var.get()
            phase = self.phase_var.get()
            click_level = self.click_level_var.get()
            click_decay = self.click_decay_var.get()
            click_width = self.click_width_var.get()
            drive = self.drive_var.get()
            reverb = self.reverb_var.get()
            delay = self.delay_var.get()

            # Bassline params
            generate_bass = self.bass_var.get()
            bass_freq = self.bass_freq_var.get()
            sc_depth = self.sc_depth_var.get()

            filename = self.filename_var.get()

            if not filename.endswith('.wav'):
                filename += '.wav'

            self.status_var.set("Generating...")
            self.root.update()

            # Run generation
            generator = TranceKickGenerator(duration=duration)
            audio = generator.generate(
                click_level=click_level,
                click_decay_ms=click_decay,
                drive_db=drive,
                reverb_amount=reverb,
                delay_amount=delay,
                generate_bass=generate_bass,
                bass_freq=bass_freq,
                sc_depth=sc_depth,
                oversample=oversample,
                click_width=click_width,
                phase_deg=phase
            )
            generator.save(filename, audio)

            self.status_var.set(f"Saved to {filename}")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_var.set("Error generating kick.")

    def export_trigger(self):
        try:
            generator = TranceKickGenerator()
            generator.save_sidechain_trigger("sidechain_trigger.wav")
            messagebox.showinfo("Success", "Exported sidechain_trigger.wav")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = KickGeneratorGUI(root)
    root.mainloop()
