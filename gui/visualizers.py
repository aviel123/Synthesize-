import tkinter as tk
from tkinter import ttk
import numpy as np

class WaveformVisualizer(tk.Frame):
    def __init__(self, parent, height=100, bg="black", fg="lime"):
        super().__init__(parent)
        self.height = height
        self.bg = bg
        self.fg = fg

        self.canvas = tk.Canvas(self, height=height, bg=bg)
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def update_plot(self, audio_data):
        self.canvas.delete("all")

        if audio_data is None or len(audio_data) == 0:
            return

        # Normalize for display
        # Handle stereo
        if audio_data.ndim == 2:
            # Mix down to mono for visualization or show one channel
            data = np.mean(audio_data, axis=0)
        else:
            data = audio_data

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width <= 1:
            # Not drawn yet, use requested width if packed
            width = self.winfo_width()
            if width <= 1: width = 800 # Fallback

        # Downsample to width
        step = max(1, len(data) // width)
        data_vis = data[::step]

        # Scale to canvas height
        # Center is height/2
        center_y = height / 2
        scale_y = height / 2 * 0.9 # 90% height

        coords = []
        for x, val in enumerate(data_vis):
            # Map x to canvas width
            # x_coord = x * (width / len(data_vis))
            # Or just pixel by pixel if step is correct
            x_coord = x
            y_coord = center_y - (val * scale_y)
            coords.append(x_coord)
            coords.append(y_coord)

        if len(coords) > 2:
            self.canvas.create_line(coords, fill=self.fg, width=1)
