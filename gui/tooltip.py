import tkinter as tk
from tkinter import ttk

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return

        # Calculate position using winfo_rootx/y to avoid crashes
        try:
            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        except Exception:
            # Fallback if winfo_rootx fails (e.g. widget not managed yet)
            x, y = self.widget.winfo_pointerxy()
            y += 20

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        # self.tooltip_window.wm_geometry(f"+{x}+{y}")
        self.tooltip_window.geometry(f"+{x}+{y}")

        # Use a label for the tooltip text
        # Styling: light yellow background, solid border
        label = tk.Label(self.tooltip_window, text=self.text, background="#ffffe0", relief="solid", borderwidth=1, padx=5, pady=2, font=("Helvetica", 9))
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
