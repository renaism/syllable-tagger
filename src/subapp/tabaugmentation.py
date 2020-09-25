from subapp.tab import Tab

import sys
import traceback
import os.path
import threading
import time
import tkinter as tk
import tkinter.ttk as ttk
import style

from tkinter.filedialog import askopenfilenames, askopenfilename, askdirectory
from subapp.component import FileList, FileOutput
from subapp.core import augment_folds

from config import *

class TabAugmentation(Tab):
    def __init__(self, master):
        super().__init__(master)

        self.train_files = []

        self.var_validation_fname = tk.StringVar()

        self.var_output_fname = tk.StringVar()
        self.var_output_fdir = tk.StringVar()

        self.var_lower_case = tk.BooleanVar()
        self.var_flip_onsets = tk.BooleanVar()
        self.var_swap_consonants = tk.BooleanVar()
        self.var_transpose_nucleus = tk.BooleanVar()
        self.var_distinct = tk.BooleanVar()
        self.var_distinct.set(True)
        self.var_validation = tk.BooleanVar()

        self.sidebar()
        self.main()

        self.toggle_validation()
    

    def sidebar(self):
        self.frm_sidebar = tk.LabelFrame(self, text="Options")
        self.frm_sidebar.grid(row=0, column=0, sticky="nsew", padx=style.SECTION_PADDING, pady=style.SECTION_PADDING)

        self.cbt_lower_case = tk.Checkbutton(self.frm_sidebar, variable=self.var_lower_case, text="Ensure lower case")
        self.cbt_lower_case.grid(sticky="nw")
        
        tk.Label(self.frm_sidebar, text="Methods").grid(sticky="nw")
        
        self.cbt_flip_onsets = tk.Checkbutton(self.frm_sidebar, variable=self.var_flip_onsets, text="Flip onsets")
        self.cbt_flip_onsets.grid(sticky="nw")

        self.cbt_swap_consonants = tk.Checkbutton(self.frm_sidebar, variable=self.var_swap_consonants, text="Swap consonants")
        self.cbt_swap_consonants.grid(sticky="nw")

        self.cbt_transpose_nucleus = tk.Checkbutton(self.frm_sidebar, variable=self.var_transpose_nucleus, text="Transpose nucleus")
        self.cbt_transpose_nucleus.grid(sticky="nw")

        tk.Label(self.frm_sidebar, text="Other settings").grid(sticky="nw")

        self.cbt_distinct = tk.Checkbutton(self.frm_sidebar, variable=self.var_distinct, text="Distinct")
        self.cbt_distinct.grid(sticky="nw")

        self.cbt_validation = tk.Checkbutton(self.frm_sidebar, variable=self.var_validation, command=self.toggle_validation, text="Validation")
        self.cbt_validation.grid(sticky="nw")


    def main(self):
        self.frm_main = tk.Frame(self)
        self.frm_main.grid(row=0, column=1, sticky="nsew", padx=style.SECTION_PADDING, pady=style.SECTION_PADDING)
        self.frm_main.rowconfigure(1, weight=1)
        self.frm_main.columnconfigure(0, weight=1)

        # Train file area
        self.frm_train_file = FileList(
            master=self.frm_main,
            title="Train file",
            file_list=self.train_files,
            file_types=[("Text Files", "*.txt"), ("CSV Files", "*.csv"), ("All Files", "*")]
        )
        self.frm_train_file.grid(sticky="nsew")

        self.frm_validation_file = tk.LabelFrame(self.frm_main, text="Validation file")
        self.frm_validation_file.grid(sticky="new")
        self.frm_validation_file.columnconfigure(1, weight=1)

        # Validation file
        tk.Label(self.frm_validation_file, text="File name:").grid(row=0, column=0, sticky="w")
        self.ent_validation_file = tk.Entry(self.frm_validation_file, state="readonly", textvariable=self.var_validation_fname)
        self.ent_validation_file.grid(row=0, column=1, sticky="nsew", padx=style.ELEMENT_PADDING, pady=style.ELEMENT_PADDING)
        tk.Button(self.frm_validation_file, text="Browse", width=style.BUTTON_WIDTH, command=self.browse_validation_fname).grid(row=0, column=2, sticky="nsew", padx=style.ELEMENT_PADDING, pady=style.ELEMENT_PADDING)
      
        # Output area
        self.frm_file_output = FileOutput(
            master=self.frm_main,
            title="Save n-gram as",
            fname=self.var_output_fname,
            fdir=self.var_output_fdir,
            auto_func=self.auto_output_fname
        )
        self.frm_file_output.grid(row=1, column=0, sticky="sew")

        # Operation buttons
        self.frm_op_btn_container = tk.Frame(self.frm_main)
        self.frm_op_btn_container.grid(row=3, column=0, sticky="e", pady=style.ELEMENT_PADDING)

        self.btn_start = tk.Button(self.frm_op_btn_container, text="Start", width=style.BUTTON_WIDTH, command=self.btn_start_click)
        self.btn_start.grid(row=0, column=1, sticky="e")

        self.btn_cancel = tk.Button(self.frm_op_btn_container, text="Cancel", width=style.BUTTON_WIDTH, state=tk.DISABLED)
        #self.btn_cancel.grid(row=0, column=0, sticky="e", padx=style.ELEMENT_PADDING)
    

    def toggle_validation(self):
        if self.var_validation.get():
            self.frm_validation_file.grid(sticky="new")
        else:
            self.frm_validation_file.grid_remove()
    

    def browse_validation_fname(self):
        fname = askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*")])

        self.ent_validation_file.config(state=tk.NORMAL)
        self.var_validation_fname.set(fname)
        self.ent_validation_file.config(state="readonly")


    def auto_output_fname(self):
        fname = "train_aug"

        ops = []
        
        if self.var_flip_onsets.get():
            ops.append("fo")

        if self.var_swap_consonants.get():
            ops.append("sc")
        
        if self.var_transpose_nucleus.get():
            ops.append("tn")
        
        for i, op in enumerate(ops):
            if i == 0:
                fname += "["
            else:
                fname += "+"
            
            fname += op

            if i == len(ops)-1:
                fname += "]"
        
        if self.var_distinct.get():
            fname += "_dct"

        if self.var_validation.get():
            fname += "_val"

        self.var_output_fname.set(fname)
    

    def btn_start_click(self):
        valid = True

        # Validations
        if len(self.train_files) < 1:
            self.status_bar.write("[!] No train file selected.\n")
            valid = False
        
        if not self.var_flip_onsets.get() and not self.var_swap_consonants.get() and not self.var_transpose_nucleus.get():
            self.status_bar.write("[!] No augmentation method selected.\n")

        if self.var_output_fname.get() == '':
            self.status_bar.write("[!] File name can not be empty.\n")
            valid = False

        if self.var_validation.get() and self.var_validation_fname.get() == "":
            self.status_bar.write("[!] No validation file selected.")
            valid = False

        if self.var_output_fdir.get() == "":
            self.status_bar.write("[!] Directory is not selected yet.\n")
            valid = False
        elif not os.path.isdir(self.var_output_fdir.get()):
            self.status_bar.write("[!] Directory is not exists/valid.\n")
            valid = False
        
        self.status_bar.write("\n")

        if valid:
            threading.Thread(target=self.augment_folds_worker).start()
    

    def augment_folds_worker(self):
        self.master.toggle_other_tabs(False)
        self.btn_start.config(state=tk.DISABLED)
        self.btn_cancel.config(state=tk.NORMAL)
        
        old_stdout = sys.stdout
        sys.stdout = self.status_bar

        try:
            augment_folds(
                data_train_fnames=self.train_files,
                output_fname=self.var_output_fname.get(),
                output_fdir=self.var_output_fdir.get(),
                lower_case=self.var_lower_case.get(),
                flip_onsets_=self.var_flip_onsets.get(),
                swap_consonants_=self.var_swap_consonants.get(),
                transpose_nucleus_=self.var_transpose_nucleus.get(),
                distinct=self.var_distinct.get(),
                validation=self.var_validation.get(),
                validation_fname=self.var_validation_fname.get()
            )
        except Exception as e:
            print(f"Error:\n{e}")
            print(traceback.format_exc())

        sys.stdout = old_stdout

        self.master.toggle_other_tabs(True)
        self.btn_start.config(state=tk.NORMAL)
        self.btn_cancel.config(state=tk.DISABLED)