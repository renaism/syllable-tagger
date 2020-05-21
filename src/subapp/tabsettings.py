import tkinter as tk
import style

from subapp.component import StatusBar, ConfigText
from config import *

class TabSettings(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        # Grid configuration
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, minsize=style.STATUS_HEIGHT)
        self.columnconfigure(0, weight=1)

        self.status_bar()
        self.main()
        self.fill()
    

    def status_bar(self):
        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=style.SECTION_PADDING, pady=style.SECTION_PADDING)
        self.status_bar.write("Ready\n")
    
    
    def main(self):
        self.frm_main = tk.Frame(self)
        self.frm_main.grid(row=0, column=0, sticky="nsew", padx=style.SECTION_PADDING, pady=style.ELEMENT_PADDING)
        self.frm_main.rowconfigure(1, weight=1)
        self.frm_main.columnconfigure(0, weight=1)

        self.frm_settings = tk.Frame(self.frm_main)
        self.frm_settings.grid(sticky="new", padx=style.SECTION_PADDING, pady=style.SECTION_PADDING)

        self.var_vowels = tk.StringVar()
        self.frm_vowels = ConfigText(self.frm_settings, "List of vowels", VOWELS_DEFAULT, self.var_vowels)
        self.frm_vowels.grid(sticky="nw")

        self.var_semi_vowels = tk.StringVar()
        self.frm_semi_vowels = ConfigText(self.frm_settings, "List of semi-vowels", SEMI_VOWELS_DEFAULT, self.var_semi_vowels)
        self.frm_semi_vowels.grid(sticky="nw")

        self.var_diphtongs = tk.StringVar()
        self.frm_diphtongs = ConfigText(self.frm_settings, "List of diphtongs", DIPHTONGS_DEFAULT, self.var_diphtongs)
        self.frm_diphtongs.grid(sticky="nw")

        # Buttons
        self.frm_buttons = tk.Frame(self.frm_main)
        self.frm_buttons.grid(sticky="se")

        tk.Button(self.frm_buttons, text="Apply", width=style.BUTTON_WIDTH, command=self.apply_settings).grid(row=0, column=1, sticky="ne", padx=style.ELEMENT_PADDING)
        tk.Button(self.frm_buttons, text="Revert", width=style.BUTTON_WIDTH, command=self.fill).grid(row=0, column=0, sticky="ne", padx=style.ELEMENT_PADDING)
    

    def fill(self):
        config = load_config()

        self.var_vowels.set(config["SYMBOLS"]["vowels"])
        self.var_semi_vowels.set(config["SYMBOLS"]["semi_vowels"])
        self.var_diphtongs.set(config["SYMBOLS"]["diphtongs"])

        self.frm_vowels.check_default()
        self.frm_semi_vowels.check_default()
        self.frm_diphtongs.check_default()
    

    def apply_settings(self):
        config = load_config()

        config["SYMBOLS"]["vowels"] = self.var_vowels.get()
        config["SYMBOLS"]["semi_vowels"] = self.var_semi_vowels.get()
        config["SYMBOLS"]["diphtongs"] = self.var_diphtongs.get()

        self.frm_vowels.check_default()
        self.frm_semi_vowels.check_default()
        self.frm_diphtongs.check_default()

        save_config(config)

        self.status_bar.write("Settings saved\n")
