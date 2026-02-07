import tkinter as tk
from gui.main_window import MainWindow

if __name__ == "__main__":
    root = tk.Tk()
    # Set icon if available?
    app = MainWindow(root)
    root.mainloop()
