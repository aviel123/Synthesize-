import tkinter as tk
from tkinter import ttk


class ToolTip:
    """
    A simple tooltip class for tkinter widgets.
    """
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip = None
        self._after_id = None
        self.widget.bind("<Enter>", self.schedule_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def schedule_tooltip(self, event=None):
        self._after_id = self.widget.after(self.delay, self.show_tooltip)

    def show_tooltip(self, event=None):
        self._after_id = None
        if self.tooltip:
            return

        # Calculate position using winfo_rootx/y to avoid crashes with ttk widgets
        try:
            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        except Exception:
            # Fallback if winfo fails (unlikely if widget is mapped)
            x = self.widget.winfo_pointerx() + 20
            y = self.widget.winfo_pointery() + 20

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        # Use tk.Label for consistent styling (yellow bg, black fg) across themes
        label = tk.Label(
            self.tooltip,
            text=self.text,
            background="#ffffe0",
            foreground="black",
            relief="solid",
            borderwidth=1,
            padx=5,
            pady=2
        )
        label.pack()

    def hide_tooltip(self, event=None):
        if self._after_id:
            self.widget.after_cancel(self._after_id)
            self._after_id = None

        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
