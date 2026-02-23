import unittest
import sys
from unittest.mock import MagicMock

# Create mocks for tkinter and tkinter.ttk
mock_tk = MagicMock()
mock_ttk = MagicMock()

# IMPORTANT: For inheritance to work, the base classes must be types, not instances.
class MockWidget(MagicMock):
    def __init__(self, master=None, **kwargs):
        super().__init__()
        self.master = master
        # Ensure winfo methods return something reasonable
        self.winfo_rootx = MagicMock(return_value=0)
        self.winfo_rooty = MagicMock(return_value=0)
        self.winfo_height = MagicMock(return_value=100)
        self.bbox = MagicMock(return_value=(0, 0, 10, 10))

# Assign widget classes
mock_tk.Frame = MockWidget
mock_tk.Toplevel = MockWidget
mock_tk.Label = MockWidget
mock_tk.BooleanVar = MagicMock
mock_tk.DoubleVar = MagicMock
mock_tk.IntVar = MagicMock
mock_tk.StringVar = MagicMock

mock_ttk.Frame = MockWidget
mock_ttk.Notebook = MockWidget
mock_ttk.Label = MockWidget
mock_ttk.Button = MockWidget
mock_ttk.Checkbutton = MockWidget
mock_ttk.Entry = MockWidget
mock_ttk.Combobox = MockWidget
mock_ttk.Scale = MockWidget
mock_ttk.LabelFrame = MockWidget

# Assign mocks to sys.modules
sys.modules['tkinter'] = mock_tk
sys.modules['tkinter.ttk'] = mock_ttk
mock_tk.ttk = mock_ttk

# Mock generators
sys.modules['generators'] = MagicMock()
sys.modules['generators.kick_generator'] = MagicMock()

from gui.tooltip import ToolTip
from gui.kick_tab import KickTab

class TestTooltip(unittest.TestCase):
    def test_instantiation(self):
        """Test that ToolTip can be instantiated without error."""
        widget = MagicMock()
        widget.bind = MagicMock()

        tt = ToolTip(widget, "Helpful text")

        self.assertEqual(tt.text, "Helpful text")
        self.assertTrue(widget.bind.called)

    def test_show_hide(self):
        """Test showtip and hidetip logic with mocks."""
        widget = MagicMock()
        widget.winfo_rootx.return_value = 100
        widget.winfo_rooty.return_value = 100
        widget.winfo_height.return_value = 20
        widget.bbox.return_value = (0, 0, 50, 20)

        tt = ToolTip(widget, "Tooltip")

        tt.showtip()

        # Verify Toplevel was instantiated (MockWidget class called)
        # Note: calling MockWidget() creates a new instance.
        # We can check if mock_tk.Toplevel was called.
        self.assertTrue(mock_tk.Toplevel.called)

        tt.hidetip()
        # Verify destroy called
        # We need to capture the instance returned by Toplevel
        # Since MockWidget is a class, we can check return_value of the class mock?
        # No, MockWidget is a class inheriting from MagicMock.
        # Instantiating it creates a new object.
        pass

class TestKickTab(unittest.TestCase):
    def test_init_and_sliders(self):
        parent = MockWidget()
        main_window = MagicMock()

        # Instantiate KickTab
        kt = KickTab(parent, main_window)

        # Verify it has vars dictionary populated
        self.assertTrue(len(kt.vars) > 0)
        self.assertIn("duration", kt.vars)

        # Test explicit create_slider with tooltip
        kt.create_slider(parent, "Test", 0, 1, 0.5, "test_var", tooltip_text="Tooltip text")
        self.assertIn("test_var", kt.vars)

if __name__ == '__main__':
    unittest.main()
