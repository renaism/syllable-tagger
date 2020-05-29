import tkinter as tk
import tkinter.ttk as ttk
import style

from subapp.tabaugmentation import TabAugmentation
from subapp.tabtraining import TabTraining
from subapp.tabtesting import TabTesting
from subapp.tabsettings import TabSettings

VERSION = "0.3a"

class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
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
        for tab in self.tabs.tabs():
            if self.tabs.index(tab) != self.tabs.index("current"):
                self.tabs.tab(tab, state=tk.NORMAL if enabled else tk.DISABLED)


if __name__ == "__main__":
    # Main window configuration
    root = tk.Tk()
    root.title(f"Indonesian Syllable Tagger v{VERSION}")
    app = App(root)
    app.mainloop()