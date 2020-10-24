import tkinter as tk
from app import App

APPNAME    = "INASYLLG2P"
APPVERSION = "0.6b" 

if __name__ == "__main__":
    # Main window configuration
    root = tk.Tk()
    root.name = APPNAME
    root.version = APPVERSION
    
    root.title(f"{root.name}")
    app = App(master=root, mode="both")
    app.mainloop()