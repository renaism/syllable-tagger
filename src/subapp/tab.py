import tkinter as tk
import style

from subapp.component import StatusBar

class Tab(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        # Grid configuration
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, minsize=style.STATUS_HEIGHT)
        self.columnconfigure(0, minsize=style.SIDEBAR_WIDTH)
        self.columnconfigure(1, weight=1)

        self.status_bar()
    

    def status_bar(self):
        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=style.SECTION_PADDING, pady=style.SECTION_PADDING)
        self.status_bar.write("Ready\n")