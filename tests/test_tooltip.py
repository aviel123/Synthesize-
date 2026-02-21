import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 1. Mock tkinter modules BEFORE importing gui code
mock_tk = MagicMock()
mock_ttk = MagicMock()
sys.modules['tkinter'] = mock_tk
sys.modules['tkinter.ttk'] = mock_ttk
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()

# IMPORTANT: Link sys.modules['tkinter'].ttk to sys.modules['tkinter.ttk']
# This ensures that 'from tkinter import ttk' returns the same mock object
# as 'import tkinter.ttk', preserving our modifications to mock_ttk.Frame
mock_tk.ttk = mock_ttk

# 2. Setup mock classes for inheritance
class MockFrame:
    def __init__(self, *args, **kwargs):
        pass
    def pack(self, *args, **kwargs):
        pass
    def add(self, *args, **kwargs):
        pass

mock_ttk.Frame = MockFrame
mock_ttk.LabelFrame = MockFrame
mock_ttk.Notebook = MockFrame

# 3. Import the modules to test
try:
    from gui.kick_tab import KickTab
    from gui.tooltip import ToolTip
except ImportError as e:
    print(f"ImportError during setup: {e}")
    sys.exit(1)

class TestTooltipIntegration(unittest.TestCase):
    def test_tooltip_instantiation(self):
        """Test that ToolTip can be instantiated with a mock widget."""
        mock_widget = MagicMock()
        mock_widget.winfo_rootx.return_value = 100
        mock_widget.winfo_rooty.return_value = 100

        tt = ToolTip(mock_widget, "Test text")

        # Verify it bound events
        mock_widget.bind.assert_any_call("<Enter>", tt.enter)
        mock_widget.bind.assert_any_call("<Leave>", tt.leave)

        # Test showtip (simulated)
        tt.showtip()
        # gui.tooltip.tk refers to mock_tk
        mock_tk.Toplevel.assert_called_with(mock_widget)

    def test_kick_tab_instantiation(self):
        """Test that KickTab initializes and calls create_slider with tooltips."""
        parent = MagicMock()
        main_window = MagicMock()

        # We need to mock ToolTip class to verify it gets called
        with patch('gui.kick_tab.ToolTip') as MockToolTip:
            tab = KickTab(parent, main_window)

            # Verify ToolTip was instantiated multiple times (at least once per slider with tooltip)
            self.assertTrue(MockToolTip.call_count > 0, "ToolTip should have been instantiated")

            # Check a specific call, e.g. for Duration
            found_duration = False
            for call in MockToolTip.call_args_list:
                args, _ = call
                if len(args) > 1 and "Length of the kick" in args[1]:
                    found_duration = True
                    break

            self.assertTrue(found_duration, "Did not find ToolTip for Duration")

if __name__ == '__main__':
    unittest.main()
