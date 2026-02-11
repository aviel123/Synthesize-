## 2024-05-23 - Tooltip Implementation and Theming
**Learning:** `ttk.Label` inherits system theme colors which can lead to unreadable tooltips (e.g., white text on light yellow background) in dark mode. `bbox("insert")` on `ttk` widgets can cause crashes.
**Action:** Use `tk.Label` with explicit `background` and `foreground` colors for tooltips to ensure readability. Use `winfo_rootx()` and `winfo_rooty()` for positioning.
