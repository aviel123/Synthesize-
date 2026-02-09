## 2024-05-22 - Tooltip Positioning in Tkinter
**Learning:** `bbox("insert")` is not available on `ttk.Label` or `ttk.Scale` widgets, causing crashes when trying to position tooltips.
**Action:** Use `winfo_rootx()` and `winfo_rooty()` for generic widget positioning relative to the screen.
