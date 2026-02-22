## 2025-02-19 - Tkinter Headless Testing
**Learning:** Testing `tkinter` GUI components in a headless environment requires careful mocking, especially for inheritance. `MagicMock` instances cannot be used as base classes; `sys.modules['tkinter.ttk'].Frame` must be set to a dummy class (e.g., `class MockWidget: ...`) rather than a `MagicMock` instance.
**Action:** When creating headless tests for Tkinter apps, define a `MockWidget` class that implements dummy methods (`pack`, `grid`, `bind`) and assign it to `tk.Frame`, `ttk.Frame`, etc., in the mocked module.
