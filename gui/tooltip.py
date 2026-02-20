import tkinter as tk

class ToolTip:
    """
    Creates a tooltip for a given widget as the mouse hovers above it.
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.id = None
        self.x = self.y = 0

        # Bind events
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)

        # Accessibility: Also bind to FocusIn/FocusOut for keyboard navigation
        # Note: Not all widgets can take focus by default.
        self.widget.bind("<FocusIn>", self.enter)
        self.widget.bind("<FocusOut>", self.leave)

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(500, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        if self.tip_window or not self.text:
            return

        x = 0
        y = 0

        # Calculate position
        try:
            # Position the tooltip below and to the right of the widget
            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
        except Exception:
            # Fallback if winfo fails
            return

        # Create a Toplevel window
        self.tip_window = tw = tk.Toplevel(self.widget)
        # Remove window decorations
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        # Use tk.Label for background color support (ttk.Label doesn't always support bg)
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()
