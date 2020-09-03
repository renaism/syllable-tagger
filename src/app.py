import tkinter as tk
import tkinter.ttk as ttk
import style

from subapp.tabaugmentation import TabAugmentation
from subapp.tabtraining import TabTraining
from subapp.tabtesting import TabTesting
from subapp.tabsettings import TabSettings

class App(tk.Frame):
    def __init__(self, master, mode):
        super().__init__(master)
        self.master = master
        self.mode = mode
        self.master.minsize(width=style.WINDOW_MIN_WIDTH, height=style.WINDOW_MIN_HEIGHT)
        self.pack(expand=True, fill=tk.BOTH)
        self.initialize_widgets()


    def initialize_widgets(self):
        # Configure grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Parent for tabs
        self.tabs = ttk.Notebook(self)
        self.tabs.grid(row=0, column=0, sticky="nsew")

        if self.mode == "syl":
            # Settings tab
            self.tab_settings = TabSettings(self)
            self.tabs.add(self.tab_settings, sticky="nsew", text="Settings")

            # Augmentation tab
            self.tab_augmentation = TabAugmentation(self)
            self.tabs.add(self.tab_augmentation, sticky="nsew", text="Augmentation")

        # Training tab
        self.tab_train = TabTraining(self, mode=self.mode)
        self.tabs.add(self.tab_train, sticky="nsew", text="Training")

        # Testing tab
        self.tab_test = TabTesting(self, mode=self.mode)
        self.tabs.add(self.tab_test, sticky="nsew", text="Testing")

        self.tabs.select(0)
    

    def toggle_other_tabs(self, enabled):
        for tab in self.tabs.tabs():
            if self.tabs.index(tab) != self.tabs.index("current"):
                self.tabs.tab(tab, state=tk.NORMAL if enabled else tk.DISABLED)