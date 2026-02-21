## 2025-02-18 - Tooltip Positioning in Tkinter
**Learning:** `bbox('insert')` crashes on widgets like `ttk.Scale` or `ttk.Frame` that don't support text insertion.
**Action:** Always use `winfo_rootx()` and `winfo_rooty()` for positioning popups relative to arbitrary widgets.

## 2025-02-18 - Headless Testing of Tkinter GUI
**Learning:** `tkinter.ttk` module resolution behaves unexpectedly when mocked in `sys.modules`. `from tkinter import ttk` retrieves `tkinter.ttk` from the `tkinter` package mock, not `sys.modules['tkinter.ttk']` directly.
**Action:** When mocking tkinter for headless tests, explicitly set `mock_tk.ttk = mock_ttk` to alias the mocks.
