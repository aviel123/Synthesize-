## 2024-05-23 - Tooltip Positioning in Tkinter
**Learning:** `bbox("insert")` is unreliable for `ttk.Label` and `ttk.Scale` widgets as they lack an insertion cursor, leading to crashes or incorrect coordinates.
**Action:** Always use `winfo_rootx()` and `winfo_rooty()` for positioning overlay windows relative to these widgets.
