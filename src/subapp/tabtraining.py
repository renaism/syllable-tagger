from subapp.tab import Tab

import sys
import traceback
import os.path
import threading
import time
import tkinter as tk
import style

from tkinter.filedialog import askopenfilenames, askdirectory
from subapp.component import FileList, FileOutput, StatusBar
from subapp.core import build_ngram

class TabTraining(Tab):
    def __init__(self, master, mode):
        super().__init__(master)
        self.mode = mode

        self.train_files = []

        self.var_output_fname = tk.StringVar()
        self.var_output_fdir = tk.StringVar()
        
        self.sidebar()
        self.main()
        #self.status_bar()


    def sidebar(self):
        self.frm_sidebar = tk.LabelFrame(self, text="Params")
        self.frm_sidebar.grid(row=0, column=0, sticky="nsew", padx=style.SECTION_PADDING, pady=style.SECTION_PADDING)

        tk.Label(self.frm_sidebar, text="Maximum n").grid(row=0, column=0, sticky="nw")

        self.var_n = tk.IntVar()
        self.var_n.set(5)
        self.ent_n = tk.Spinbox(self.frm_sidebar, textvariable=self.var_n, from_=1, to=10, width=style.DIGIT_ENTRY_WIDTH)
        self.ent_n.grid(row=0, column=1, sticky="ne")

        self.var_lower_case = tk.BooleanVar()
        self.cbt_lower_case = tk.Checkbutton(self.frm_sidebar, variable=self.var_lower_case, text="Ensure lower case")
        self.cbt_lower_case.grid(row=1, column=0, sticky="nw")

        self.var_cont_count = tk.BooleanVar()
        self.var_cont_count.set(True)
        self.cbt_cont_count = tk.Checkbutton(self.frm_sidebar, variable=self.var_cont_count, text="Continuation count")
        self.cbt_cont_count.grid(row=2, column=0, columnspan=2, sticky="nw")

        self.var_follow_count = tk.BooleanVar()
        self.var_follow_count.set(True)
        self.cbt_follow_count = tk.Checkbutton(self.frm_sidebar, variable=self.var_follow_count, text="Follow count")
        self.cbt_follow_count.grid(row=3, column=0, columnspan=2, sticky="nw")

    
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
        self.frm_train_file.grid(row=0, column=0, sticky="nsew")
      
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

        self.btn_start = tk.Button(self.frm_op_btn_container, width=style.BUTTON_WIDTH, text="Start", command=self.btn_start_click)
        self.btn_start.grid(row=0, column=1, sticky="e")

        self.btn_cancel = tk.Button(self.frm_op_btn_container, width=style.BUTTON_WIDTH, text="Cancel", state=tk.DISABLED)
        #self.btn_cancel.grid(row=0, column=0, sticky="e")
    

    def status_bar(self):
        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=style.SECTION_PADDING, pady=style.SECTION_PADDING)
        self.status_bar.write("Ready\n")


    def auto_output_fname(self):
        self.var_output_fname.set(f"{self.var_n.get()}_gram")
    
    
    def btn_start_click(self):
        valid = True

        # Validations
        if len(self.train_files) < 1:
            self.status_bar.write("[!] No train file selected.\n")
            valid = False
        
        if self.var_output_fname.get() == '':
            self.status_bar.write("[!] File name can not be empty.\n")
            valid = False
        
        if self.var_output_fdir.get() == '':
            self.status_bar.write("[!] Directory is not selected yet.\n")
            valid = False
        elif not os.path.isdir(self.var_output_fdir.get()):
            self.status_bar.write("[!] Directory is not exists/valid.\n")
            valid = False
        
        self.status_bar.write("\n")

        if valid:
            threading.Thread(target=self.build_ngram_worker).start()
    

    def build_ngram_worker(self):
        self.master.toggle_other_tabs(False)
        self.btn_start.config(state=tk.DISABLED)
        self.btn_cancel.config(state=tk.NORMAL)
        
        old_stdout = sys.stdout
        sys.stdout = self.status_bar

        try:
            build_ngram(
                n_max=int(self.var_n.get()),
                data_train_fnames=self.train_files,
                output_fname=self.var_output_fname.get(),
                output_fdir=self.var_output_fdir.get(),
                lower_case=self.var_lower_case.get(),
                build_cont_fdist=self.var_cont_count.get(),
                build_follow_fdist=self.var_follow_count.get(),
                mode=self.mode
            )
        except Exception as e:
            print(f"Error:\n{e}")
            print(traceback.format_exc())

        sys.stdout = old_stdout

        self.master.toggle_other_tabs(True)
        self.btn_start.config(state=tk.NORMAL)
        self.btn_cancel.config(state=tk.DISABLED)