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
    def __init__(self, master, mode="both"):
        super().__init__(master)
        self.master = master
        self.mode = mode

        self.master.minsize(width=style.WINDOW_MIN_WIDTH, height=style.WINDOW_MIN_HEIGHT)
        self.master.iconbitmap(os.path.dirname(os.path.realpath(__file__)) + "/icon.ico")
        self.pack(expand=True, fill=tk.BOTH)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.var_mode = tk.StringVar()
        self.var_mode.set(self.mode if self.mode != "both" else "syl")

        if self.mode == "both":
            self.frm_selector = tk.Frame(self)
            self.frm_selector.grid(row=0, sticky="new")

            tk.Label(self.frm_selector, text="Mode: ").grid(row=0, column=0, sticky="nw")
            self.rbtn_syl = tk.Radiobutton(self.frm_selector, text="SYL", variable=self.var_mode, value="syl", command=self.select_mode)
            self.rbtn_syl.grid(row=0, column=1, sticky="nw")
            self.rbtn_g2p = tk.Radiobutton(self.frm_selector, text="G2P", variable=self.var_mode, value="g2p", command=self.select_mode)
            self.rbtn_g2p.grid(row=0, column=2, sticky="nw")
        
        # Version text
        tk.Label(self, text=f"Version {master.version}").grid(row=0, column=1, sticky="ne")
        
        # Paned window, for tab area and status bar
        self.frm_paned_window_wrapper = tk.Frame(self)
        self.frm_paned_window_wrapper.grid(row=1, sticky="nsew", columnspan=2)

        self.paned_window = tk.PanedWindow(self.frm_paned_window_wrapper, orient=tk.VERTICAL)
        self.paned_window.pack(expand=True, fill=tk.BOTH, side=tk.TOP)
        
        # App wrapper
        self.frm_app_wrapper = tk.Frame(self.paned_window)
        self.paned_window.add(self.frm_app_wrapper)
        self.paned_window.paneconfig(self.frm_app_wrapper, height=style.WINDOW_MIN_HEIGHT-style.STATUS_HEIGHT, sticky="nsew")

        # Status bar
        self.status_bar = StatusBar(self.paned_window)
        self.paned_window.add(self.status_bar)
        self.paned_window.paneconfig(self.status_bar, height=style.STATUS_HEIGHT, minsize=style.STATUS_HEIGHT, sticky="nsew")

        # Main app
        self.frm_app_wrapper.status_bar = self.status_bar
        self.frm_app_wrapper.columnconfigure(0, weight=1)
        self.frm_app_wrapper.rowconfigure(0, weight=1)

        if self.mode == "syl" or self.mode == "both":
            self.app_syl = SubApp(self.frm_app_wrapper, self, mode="syl")
        
        if self.mode == "g2p" or self.mode == "both":
            self.app_g2p = SubApp(self.frm_app_wrapper, self, mode="g2p")
        
        self.select_mode()
    

    def select_mode(self):
        if self.var_mode.get() == "syl":
            if self.mode == "both":
                self.app_g2p.grid_remove()
            
            self.app_syl.grid(sticky="nsew")
        
        elif self.var_mode.get() == "g2p":
            if self.mode == "both":
                self.app_syl.grid_remove()
            
            self.app_g2p.grid(sticky="nsew")


class SubApp(tk.Frame):
    def __init__(self, master, app, mode):
        super().__init__(master)
        self.master = master
        self.app = app
        self.status_bar = self.app.status_bar
        self.mode = mode
        
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.tabs = ttk.Notebook(self)
        self.tabs.grid(sticky="nsew")

        if self.mode == "syl":
            # Settings tab
            self.tab_settings = TabSettings(self)
            self.tabs.add(self.tab_settings, sticky="nsew", text="Settings")

            # Augmentation tab
            self.tab_augmentation = TabAugmentation(self)
            self.tabs.add(self.tab_augmentation, sticky="nsew", text="Augmentation")

        # Training tab
        self.tab_train = TabTraining(self)
        self.tabs.add(self.tab_train, sticky="nsew", text="Training")

        # Testing tab
        self.tab_test = TabTesting(self)
        self.tabs.add(self.tab_test, sticky="nsew", text="Testing")

        self.tabs.select(0)


    def toggle_other_tabs(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED

        for tab in self.tabs.tabs():
            if self.tabs.index(tab) != self.tabs.index("current"):
                self.tabs.tab(tab, state=state)
        
        if self.app.mode == "both":
            self.app.rbtn_syl.config(state=state)
            self.app.rbtn_g2p.config(state=state)