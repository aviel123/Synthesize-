import tkinter as tk
import numpy as np


class EnvelopeEditor(tk.Frame):
    """
    Interactive amplitude-envelope visualizer for the kick generator.

    Draws the combined punch + body exponential decay curve on a Canvas.
    Two vertical drag handles let the user scrub punch_decay_ms (orange)
    and body_decay_ms (blue) directly – the linked tk.DoubleVars are kept
    in sync so the sliders update instantly.

    linked_vars expects keys: 'punch_decay', 'body_decay', 'duration'
    """

    HANDLE_HIT = 12   # px either side of a handle that counts as a click

    def __init__(self, parent, vars_dict, bg="#1a1a2e"):
        super().__init__(parent, bg=bg)
        self.bg = bg
        self._vars = vars_dict
        self._dragging = None   # "punch" | "body"
        self._w = 400
        self._h = 90

        self.canvas = tk.Canvas(self, height=90, bg=bg, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>",   self._on_press)
        self.canvas.bind("<B1-Motion>",       self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Configure>",       lambda _e: self._redraw())

        # Redraw whenever any linked slider changes
        for key in ("punch_decay", "body_decay", "duration"):
            if key in self._vars:
                self._vars[key].trace_add("write", lambda *_: self.after(0, self._redraw))

    # ── helpers ────────────────────────────────────────────────────────────

    def _params(self):
        dur       = self._vars["duration"].get()    if "duration"    in self._vars else 0.6
        punch_ms  = self._vars["punch_decay"].get() if "punch_decay" in self._vars else 40.0
        body_ms   = self._vars["body_decay"].get()  if "body_decay"  in self._vars else 500.0
        return max(dur, 0.1), punch_ms, body_ms

    def _t_to_x(self, t_sec, dur):
        return int(t_sec / dur * self._w)

    def _x_to_ms(self, x, dur):
        return (x / max(self._w, 1)) * dur * 1000.0

    # ── drawing ────────────────────────────────────────────────────────────

    def _redraw(self):
        c = self.canvas
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w <= 1 or h <= 1:
            return
        self._w, self._h = w, h

        dur, punch_ms, body_ms = self._params()

        # Compute combined envelope
        t = np.linspace(0, dur, w)
        punch_tau = (punch_ms / 1000.0) * 1.2
        body_k    = 7.0 / max(body_ms / 1000.0, 1e-4)
        env       = 0.85 * np.exp(-t / max(punch_tau, 1e-6)) \
                  + 0.90 * np.exp(-body_k * t)
        peak = env[0] if env[0] > 0 else 1.0
        env_n = np.clip(env / peak, 0.0, 1.0)

        # Horizontal grid
        for yf in (0.25, 0.5, 0.75):
            y = int(yf * h)
            c.create_line(0, y, w, y, fill="#222244", dash=(4, 4))

        # Envelope curve
        coords = []
        for px in range(w):
            coords.extend([px, int((1.0 - env_n[px]) * (h - 2)) + 1])
        if len(coords) >= 4:
            c.create_line(coords, fill="#44bb77", width=2, smooth=True)

        # ── Punch handle (orange) ──
        px = max(2, min(self._t_to_x(punch_ms / 1000.0, dur), w - 2))
        c.create_line(px, 0, px, h, fill="#f39c12", width=2, dash=(6, 3))
        c.create_oval(px - 5, h // 2 - 5, px + 5, h // 2 + 5,
                      fill="#f39c12", outline="white", width=1)
        c.create_text(px, 4, text="Punch", fill="#f39c12",
                      font=("Helvetica", 7, "bold"), anchor=tk.N)
        c.create_text(px, h - 2, text=f"{punch_ms:.0f}ms", fill="#f39c12",
                      font=("Helvetica", 7), anchor=tk.S)

        # ── Body handle (blue) ──
        bx = max(px + 8, min(self._t_to_x(body_ms / 1000.0, dur), w - 2))
        c.create_line(bx, 0, bx, h, fill="#3498db", width=2, dash=(6, 3))
        c.create_oval(bx - 5, h // 2 - 5, bx + 5, h // 2 + 5,
                      fill="#3498db", outline="white", width=1)
        c.create_text(bx, 4, text="Body", fill="#3498db",
                      font=("Helvetica", 7, "bold"), anchor=tk.N)
        c.create_text(bx, h - 12, text=f"{body_ms:.0f}ms", fill="#3498db",
                      font=("Helvetica", 7), anchor=tk.S)

        # Axis labels
        c.create_text(2,     h - 2, text="0",           fill="#555555",
                      font=("Helvetica", 7), anchor=tk.SW)
        c.create_text(w - 2, h - 2, text=f"{dur*1000:.0f}ms", fill="#555555",
                      font=("Helvetica", 7), anchor=tk.SE)

    # ── interaction ────────────────────────────────────────────────────────

    def _on_press(self, event):
        dur, punch_ms, body_ms = self._params()
        px = self._t_to_x(punch_ms / 1000.0, dur)
        bx = self._t_to_x(body_ms  / 1000.0, dur)
        if abs(event.x - px) <= self.HANDLE_HIT:
            self._dragging = "punch"
        elif abs(event.x - bx) <= self.HANDLE_HIT:
            self._dragging = "body"

    def _on_drag(self, event):
        if self._dragging is None:
            return
        dur, punch_ms, body_ms = self._params()
        ms = self._x_to_ms(event.x, dur)

        if self._dragging == "punch":
            ms = max(10.0, min(ms, 80.0))
            ms = min(ms, body_ms - 5.0)
            if "punch_decay" in self._vars:
                self._vars["punch_decay"].set(ms)

        elif self._dragging == "body":
            ms = max(100.0, min(ms, 800.0))
            ms = max(ms, punch_ms + 5.0)
            if "body_decay" in self._vars:
                self._vars["body_decay"].set(ms)

    def _on_release(self, _event):
        self._dragging = None
