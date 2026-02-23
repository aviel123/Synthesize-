## 2024-05-22 - Tkinter Label styling constraints
**Learning:** `ttk.Label` widgets do not support direct background color configuration (it depends on the theme), which limits the ability to create standard yellow tooltips.
**Action:** Use standard `tk.Label` instead of `ttk.Label` when specific background colors are required for UI elements like tooltips or notifications.

## 2024-05-22 - Reusable ToolTip Pattern
**Learning:** Created a reusable `ToolTip` class that can be easily attached to any widget.
**Action:** Import `gui.tooltip.ToolTip` and instantiate `ToolTip(widget, "text")` to add helpful context.
