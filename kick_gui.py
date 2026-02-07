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

        # Controls Frame
        controls_frame = ttk.LabelFrame(main_frame, text="Synthesis Parameters", padding="10")
        controls_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # 1. Base Frequency (Body) - Note: In code it's fixed at 70Hz or 150Hz punch, let's expose specific tweaks if possible,
        # but the current generator has hardcoded frequencies.
        # For this task, I'll expose the parameters I just added + Duration.

        # Duration
        self.create_slider(controls_frame, "Duration (s)", 0.1, 1.0, 0.5, "duration")

        # Click/Noise Level
        self.create_slider(controls_frame, "Click/Noise Level (Euphoria)", 0.0, 3.0, 1.0, "click_level")

        # Click Decay
        self.create_slider(controls_frame, "Click Decay (ms)", 5.0, 100.0, 10.0, "click_decay")

        # Drive
        self.create_slider(controls_frame, "Saturation Drive (dB)", 0.0, 12.0, 4.5, "drive")

        # Reverb
        self.create_slider(controls_frame, "Reverb Amount", 0.0, 1.0, 0.0, "reverb")

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
            duration = self.duration_var.get()
            click_level = self.click_level_var.get()
            click_decay = self.click_decay_var.get()
            drive = self.drive_var.get()
            reverb = self.reverb_var.get()
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
                reverb_amount=reverb
            )
            generator.save(filename, audio)

            self.status_var.set(f"Saved to {filename}")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_var.set("Error generating kick.")

if __name__ == "__main__":
    root = tk.Tk()
    app = KickGeneratorGUI(root)
    root.mainloop()
