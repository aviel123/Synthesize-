"""Lightweight hover tooltip for any tkinter widget."""

import tkinter as tk


class Tooltip:
    """Show a small popup with *text* when the mouse hovers over *widget*.

    Parameters
    ----------
    widget:     The tkinter widget to attach the tooltip to.
    text:       Tooltip body text (may contain newlines).
    delay:      Milliseconds before the tooltip appears (default 500 ms).
    wraplength: Maximum pixel width before text wraps (default 240 px).
    """

    def __init__(self, widget, text: str, delay: int = 500,
                 wraplength: int = 240):
        self._widget = widget
        self._text = text
        self._delay = delay
        self._wraplength = wraplength
        self._tipwin = None
        self._job = None

        widget.bind("<Enter>",       self._on_enter, add="+")
        widget.bind("<Leave>",       self._on_leave, add="+")
        widget.bind("<ButtonPress>", self._on_leave, add="+")

    # ── Internal ────────────────────────────────────────────────────────

    def _on_enter(self, _event=None):
        self._schedule()

    def _on_leave(self, _event=None):
        self._cancel()
        self._hide()

    def _schedule(self):
        self._cancel()
        self._job = self._widget.after(self._delay, self._show)

    def _cancel(self):
        if self._job is not None:
            self._widget.after_cancel(self._job)
            self._job = None

    def _show(self):
        if self._tipwin:
            return
        w = self._widget
        x = w.winfo_rootx() + 16
        y = w.winfo_rooty() + w.winfo_height() + 4

        self._tipwin = tw = tk.Toplevel(w)
        tw.wm_overrideredirect(True)   # no title bar / border
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes("-topmost", True)

        tk.Label(
            tw,
            text=self._text,
            justify=tk.LEFT,
            background="#ffffcc",
            foreground="#222222",
            relief="solid",
            borderwidth=1,
            font=("TkDefaultFont", 9),
            wraplength=self._wraplength,
            padx=7,
            pady=5,
        ).pack()

    def _hide(self):
        if self._tipwin is not None:
            self._tipwin.destroy()
            self._tipwin = None
