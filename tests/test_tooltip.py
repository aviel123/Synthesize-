import unittest
import sys
from unittest.mock import MagicMock

# Create mocks for tkinter and ttk BEFORE importing gui modules
mock_tk = MagicMock()
mock_ttk = MagicMock()
mock_filedialog = MagicMock()
mock_messagebox = MagicMock()

# Setup module mocks
sys.modules['tkinter'] = mock_tk
sys.modules['tkinter.ttk'] = mock_ttk
sys.modules['tkinter.filedialog'] = mock_filedialog
sys.modules['tkinter.messagebox'] = mock_messagebox

# Ensure ttk classes that are inherited from are actual classes
class MockWidget:
    def __init__(self, master=None, **kwargs):
        pass
    def pack(self, **kwargs):
        pass
    def grid(self, **kwargs):
        pass
    def add(self, widget, **kwargs):
        pass
    def bind(self, event, handler):
        pass

mock_ttk.Frame = MockWidget
mock_ttk.Notebook = MockWidget
mock_ttk.LabelFrame = MockWidget

# Also mock tk.Frame just in case
mock_tk.Frame = MockWidget
mock_tk.Toplevel = MagicMock() # Toplevel is usually just instantiated
mock_tk.Label = MagicMock()

class TestToolTip(unittest.TestCase):
    def setUp(self):
        # Reset mocks
        mock_tk.reset_mock()
        mock_ttk.reset_mock()

    def test_tooltip_instantiation(self):
        # This checks if the module exists and class works
        try:
            from gui.tooltip import ToolTip
        except ImportError:
            self.fail("Could not import gui.tooltip")

        widget = MagicMock()
        # Mock geometry methods
        widget.winfo_rootx.return_value = 100
        widget.winfo_rooty.return_value = 100

        tt = ToolTip(widget, "Test text")

        # Verify bindings
        calls = widget.bind.call_args_list
        bound_events = [c[0][0] for c in calls]
        self.assertIn("<Enter>", bound_events)
        self.assertIn("<Leave>", bound_events)

        # Test show_tip
        tt.show_tip()
        # Should create a Toplevel
        mock_tk.Toplevel.assert_called()

        # Test hide_tip
        tt.hide_tip()
        # Should destroy the Toplevel
        mock_window = mock_tk.Toplevel.return_value
        mock_window.destroy.assert_called()

    def test_kick_tab_integration(self):
        # Verify KickTab imports and runs
        try:
            from gui.kick_tab import KickTab
        except ImportError as e:
            self.fail(f"Failed to import KickTab: {e}")

        parent = MagicMock()
        main_window = MagicMock()

        # Instantiate
        kt = KickTab(parent, main_window)
        # Check if instantiated correctly
        self.assertTrue(kt)

        # Check create_slider
        # We can't check if ToolTip is used inside without inspecting the code or mocking ToolTip
        # But this ensures no runtime errors
        kt.create_slider(parent, "Test Slider", 0, 10, 5, "test_var")

if __name__ == '__main__':
    unittest.main()
