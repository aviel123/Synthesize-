## 2024-05-23 - Reusable Tooltip Pattern
**Learning:** Tkinter `ttk.Scale` and `ttk.Label` widgets lack built-in tooltip support. `bbox("insert")` is unreliable for positioning tooltips relative to these widgets and can cause crashes.
**Action:** Use `winfo_rootx()` and `winfo_rooty()` for positioning tooltips relative to the widget's screen coordinates. Implement a reusable `ToolTip` class that binds to `<Enter>` and `<Leave>` events.
