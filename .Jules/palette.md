## 2026-02-12 - Tkinter Tooltip Positioning
**Learning:** `bbox("insert")` is not supported on non-text widgets like `ttk.Label` and `ttk.Scale`, causing potential crashes or incorrect positioning.
**Action:** When implementing tooltips or floating UI elements, always use `winfo_rootx()` and `winfo_rooty()` to position them relative to the screen coordinates of the widget.
