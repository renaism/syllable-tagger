import tkinter as tk
import style

from subapp.component import StatusBar

class Tab(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master.master
        self.mode = self.master.mode
        self.status_bar = self.master.status_bar

        # Grid configuration
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, minsize=style.SIDEBAR_WIDTH)
        self.columnconfigure(1, weight=1)