import tkinter as tk

class ToolTip:
    """
    It creates a tooltip for a given widget as the mouse goes on it.
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None

        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)
        # Accessibility: Keyboard focus
        self.widget.bind("<FocusIn>", self.show_tip)
        self.widget.bind("<FocusOut>", self.hide_tip)

    def show_tip(self, event=None):
        "Display text in tooltip window"
        if self.tip_window or not self.text:
            return

        try:
            x = self.widget.winfo_rootx() + 25
            y = self.widget.winfo_rooty() + 20
        except Exception:
            return

        self.tip_window = tw = tk.Toplevel(self.widget)
        # Remove window decorations
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1)
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()
