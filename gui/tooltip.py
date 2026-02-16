import tkinter as tk


class ToolTip:
    """
    It creates a tooltip for a given widget as the mouse goes on it.
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<FocusIn>", self.enter)
        self.widget.bind("<FocusOut>", self.leave)

    def enter(self, event=None):
        if self.tooltip_window or not self.text:
            return

        # Calculate position
        try:
            x = self.widget.winfo_rootx() + 25
            y = self.widget.winfo_rooty() + 20
        except Exception:
            return

        # Create Toplevel window
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        # Style and Label - using tk.Label for background support
        label = tk.Label(
            self.tooltip_window, text=self.text, justify='left',
            background="#ffffe0", relief='solid', borderwidth=1,
            font=("tahoma", "8", "normal")
        )
        label.pack(ipadx=1)

    def leave(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
