import tkinter as tk
import numpy as np

class WaveformVisualizer(tk.Frame):
    def __init__(self, parent, height=150, bg="black"):
        super().__init__(parent)
        self.height = height
        self.bg = bg

        # Colors matching the HTML designer
        self.grid_color = "#0a2a0a"
        self.center_line_color = "#1a4a1a"
        self.fill_color = "#001100"  # Very dark green to simulate transparent fill
        self.glow_colors = [
            ("#003300", 6), # Outer glow (darkest, widest)
            ("#006600", 4), # Mid glow
            ("#00ff00", 2)  # Core (brightest, thinnest)
        ]

        self.canvas = tk.Canvas(self, height=height, bg=bg, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.bind("<Configure>", self._on_resize)
        self.current_data = None

    def _on_resize(self, event):
        if self.current_data is not None:
            self.draw_plot(self.current_data)
        else:
            self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("grid")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        # Draw vertical lines
        for i in range(1, 11):
            x = (w / 10) * i
            self.canvas.create_line(x, 0, x, h, fill=self.grid_color, tags="grid")

        # Draw horizontal lines
        for i in range(1, 11):
            y = (h / 10) * i
            self.canvas.create_line(0, y, w, y, fill=self.grid_color, tags="grid")

        # Draw center line
        self.canvas.create_line(0, h/2, w, h/2, fill=self.center_line_color, width=2, tags="grid")

    def update_plot(self, audio_data):
        self.current_data = audio_data
        self.draw_plot(audio_data)

    def draw_plot(self, audio_data):
        self.canvas.delete("all")
        self.draw_grid()

        if audio_data is None or len(audio_data) == 0:
            return

        # Handle stereo (mix to mono)
        if audio_data.ndim == 2:
            data = np.mean(audio_data, axis=0)
        else:
            data = audio_data

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        if w <= 1:
            return # Canvas not ready

        # Downsample
        # To show "real oscillations", we need enough points.
        # But too many points is slow.
        # Step size to fit data into width
        step = max(1, len(data) // w)

        # We want at least one point per pixel if possible
        data_vis = data[::step]

        # Normalize/Scale
        # Assume audio is -1.0 to 1.0.
        # Center is h/2. Scale is h/2 * 0.9 (headroom)
        center_y = h / 2
        scale_y = h / 2 * 0.95

        coords = []

        # Generate coordinates
        # Map indices to x coordinates
        for i, val in enumerate(data_vis):
            x = i * (w / len(data_vis))
            y = center_y - (val * scale_y)
            coords.extend([x, y])

        if len(coords) < 4:
            return

        # 1. Draw Fill (Polygon)
        # Close the shape by going to the center line at the end and start
        fill_coords = coords + [w, center_y, 0, center_y]
        self.canvas.create_polygon(fill_coords, fill=self.fill_color, outline="", tags="wave")

        # 2. Draw Glow Lines
        # Draw from widest/darkest to thinnest/brightest
        for color, width in self.glow_colors:
            self.canvas.create_line(coords, fill=color, width=width, tags="wave", capstyle=tk.ROUND, joinstyle=tk.ROUND)
