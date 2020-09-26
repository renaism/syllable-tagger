import tkinter as tk
import tkinter.ttk as ttk
import style
import os

from subapp.tabaugmentation import TabAugmentation
from subapp.tabtraining import TabTraining
from subapp.tabtesting import TabTesting
from subapp.tabsettings import TabSettings

from subapp.component import StatusBar

class App(tk.Frame):
    def __init__(self, master, mode):
        super().__init__(master)
        self.master = master
        self.mode = mode
        self.master.minsize(width=style.WINDOW_MIN_WIDTH, height=style.WINDOW_MIN_HEIGHT)
        self.master.iconbitmap(os.path.dirname(os.path.realpath(__file__)) + "/icon.ico")
        self.pack(expand=True, fill=tk.BOTH)
        self.initialize_widgets()


    def initialize_widgets(self):
        # Configure grid
        self.paned_window = tk.PanedWindow(self, orient=tk.VERTICAL)
        self.paned_window.pack(expand=True, fill=tk.BOTH, side=tk.TOP)
        
        # Parent for tabs
        self.tabs = ttk.Notebook(self.paned_window)
        
        self.paned_window.add(self.tabs)
        self.paned_window.paneconfig(self.tabs, height=style.WINDOW_MIN_HEIGHT-style.STATUS_HEIGHT, sticky="nsew")

        # Status bar
        self.status_bar = StatusBar(self.paned_window)

        self.paned_window.add(self.status_bar)
        self.paned_window.paneconfig(self.status_bar, height=style.STATUS_HEIGHT, minsize=style.STATUS_HEIGHT, sticky="nsew")
        self.status_bar.write("Ready\n")

        if self.mode == "syl":
            # Settings tab
            self.tab_settings = TabSettings(self.paned_window)
            self.tabs.add(self.tab_settings, sticky="nsew", text="Settings")

            # Augmentation tab
            self.tab_augmentation = TabAugmentation(self.paned_window)
            self.tabs.add(self.tab_augmentation, sticky="nsew", text="Augmentation")

        # Training tab
        self.tab_train = TabTraining(self.paned_window)
        self.tabs.add(self.tab_train, sticky="nsew", text="Training")

        # Testing tab
        self.tab_test = TabTesting(self.paned_window)
        self.tabs.add(self.tab_test, sticky="nsew", text="Testing")

        self.tabs.select(0)
    

    def toggle_other_tabs(self, enabled):
        for tab in self.tabs.tabs():
            if self.tabs.index(tab) != self.tabs.index("current"):
                self.tabs.tab(tab, state=tk.NORMAL if enabled else tk.DISABLED)