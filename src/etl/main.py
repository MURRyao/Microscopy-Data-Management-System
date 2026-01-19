import tkinter as tk
from controller import ETLController


if __name__ == "__main__":
    root = tk.Tk()
    app = ETLController(root)
    root.mainloop()