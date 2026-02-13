## 2024-05-23 - Robust Tooltip Positioning in Tkinter
**Learning:** Using `bbox("insert")` to position tooltips crashes on widgets without a text cursor (like `ttk.Scale` or `ttk.Frame`). Only text-input widgets support the "insert" index.
**Action:** Always use `winfo_rootx()` and `winfo_rooty()` to calculate screen coordinates for positioning overlays relative to generic widgets. This ensures the tooltip appears correctly regardless of the widget type.
