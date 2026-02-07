import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from generators.kick_generator import TranceKickGenerator
from utils.tooltip import ToolTip

class KickTab(ttk.Frame):
    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        # self.pack(fill=tk.BOTH, expand=True) # Managed by Notebook
        self.vars = {}

        # Notebook for Kick internal Tabs
        notebook = ttk.Notebook(self)
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
        self.vars["oversample"] = tk.IntVar(value=1)
        q_combo = ttk.Combobox(q_frame, textvariable=self.vars["oversample"], values=[1, 2], state="readonly", width=5)
        q_combo.pack(side=tk.LEFT)
        ttk.Label(q_frame, text="(1=Std, 2=High/Oversampled)").pack(side=tk.LEFT, padx=5)

        self.create_slider(synth_frame, "Duration (s)", 0.1, 1.0, 0.5,
                           "duration", "Length of the kick in seconds")
        self.create_slider(synth_frame, "Start Phase (deg)", 0.0, 360.0, 0.0,
                           "phase",
                           "Adjusts the starting phase alignment of the "
                           "sub/punch (0-360)")
        self.create_slider(synth_frame, "Click/Noise Level", 0.0, 3.0, 1.0,
                           "click_level",
                           "Volume of the high-frequency noise layer")
        self.create_slider(synth_frame, "Click Decay (ms)", 5.0, 100.0, 10.0,
                           "click_decay",
                           "Length of the noise envelope in milliseconds")
        self.create_slider(synth_frame, "Click Width (Stereo)", 0.0, 2.0, 0.0,
                           "click_width",
                           "Stereo width of the noise layer "
                           "(0=Mono, >1=Wide)")

        # --- Effects Tab ---
        self.create_slider(fx_frame, "Saturation Drive (dB)", 0.0, 12.0, 4.5,
                           "drive", "Amount of soft-clipping distortion")
        self.create_slider(fx_frame, "Reverb Amount", 0.0, 1.0, 0.0,
                           "reverb", "Mix level of the reverb tail")
        self.create_slider(fx_frame, "Delay Amount", 0.0, 1.0, 0.0,
                           "delay", "Mix level of the stereo delay")

        # --- Bassline Tab ---
        bass_frame = ttk.LabelFrame(
            bass_frame_tab,
            text="Bassline & Sidechain (VST/DAW Integration)",
            padding="10"
        )
        bass_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Checkbox for Bassline
        self.vars["bass"] = tk.BooleanVar(value=False)
        bass_chk = ttk.Checkbutton(
            bass_frame,
            text="Generate Bassline Loop (138 BPM)",
            variable=self.vars["bass"]
        )
        bass_chk.pack(anchor=tk.W)

        # Bass Freq
        self.create_slider(bass_frame, "Bass Frequency (Hz)", 30.0, 100.0,
                           55.0, "bass_freq",
                           "Pitch of the accompanying bassline")
        # Sidechain Depth
        self.create_slider(bass_frame, "Sidechain Depth", 0.0, 1.0, 0.8,
                           "sc_depth",
                           "Amount of volume reduction on the bassline "
                           "when the kick hits")

        # Export Trigger Button
        trigger_btn = ttk.Button(bass_frame, text="Export Sidechain Trigger (Click)", command=self.export_trigger)
        trigger_btn.pack(pady=5)

        # Generate Button for this tab
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=10)
        generate_btn = ttk.Button(btn_frame, text="Generate Kick", command=self.generate)
        generate_btn.pack(side=tk.LEFT, padx=5)

    def create_slider(self, parent, label_text, min_val, max_val, default_val,
                      var_name, tooltip_text=None):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)

        lbl = ttk.Label(frame, text=label_text, width=25)
        lbl.pack(side=tk.LEFT)

        if tooltip_text:
            ToolTip(lbl, tooltip_text)

        var = tk.DoubleVar(value=default_val)
        scale = ttk.Scale(frame, from_=min_val, to=max_val, orient=tk.HORIZONTAL, variable=var, length=200)
        scale.pack(side=tk.LEFT, fill=tk.X, expand=True)

        val_lbl = ttk.Label(frame, text=f"{default_val:.2f}", width=6)
        val_lbl.pack(side=tk.LEFT, padx=5)

        def update_label(v):
            val_lbl.config(text=f"{float(v):.2f}")
        scale.config(command=update_label)

        self.vars[var_name] = var

    def export_trigger(self):
        try:
            generator = TranceKickGenerator()
            generator.save_sidechain_trigger("sidechain_trigger.wav")
            messagebox.showinfo("Success", "Exported sidechain_trigger.wav")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def generate(self):
        try:
            # Get values
            oversample = self.vars["oversample"].get()
            duration = self.vars["duration"].get()
            phase = self.vars["phase"].get()
            click_level = self.vars["click_level"].get()
            click_decay = self.vars["click_decay"].get()
            click_width = self.vars["click_width"].get()
            drive = self.vars["drive"].get()
            reverb = self.vars["reverb"].get()
            delay = self.vars["delay"].get()

            # Bassline params
            generate_bass = self.vars["bass"].get()
            bass_freq = self.vars["bass_freq"].get()
            sc_depth = self.vars["sc_depth"].get()

            filename = self.main_window.filename_var.get()

            if not filename.endswith('.wav'):
                filename += '.wav'

            self.main_window.status_var.set("Generating Kick...")
            self.update_idletasks()

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

            self.main_window.status_var.set(f"Saved to {filename}")

            # Update Visualizer if present
            if hasattr(self.main_window, 'visualizer'):
                self.main_window.visualizer.update_plot(audio)

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.main_window.status_var.set("Error generating kick.")
