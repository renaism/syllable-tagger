import tkinter as tk
from app import App

APPNAME    = "Indonesian Syllable Tagger"
APPVERSION = "0.5b" 

if __name__ == "__main__":
    # Main window configuration
    root = tk.Tk()
    root.title(f"{APPNAME} v{APPVERSION}")
    app = App(master=root, mode="syl")
    app.mainloop()