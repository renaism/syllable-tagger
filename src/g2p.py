import tkinter as tk
from app import App

APPNAME    = "Indonesian G2P"
APPVERSION = "0.1a" 

if __name__ == "__main__":
    # Main window configuration
    root = tk.Tk()
    root.title(f"{APPNAME} v{APPVERSION}")
    app = App(master=root, mode="g2p")
    app.mainloop()