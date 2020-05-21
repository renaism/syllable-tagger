from subapp.tab import Tab

import sys
import os.path
import threading
import time
import tkinter as tk
import tkinter.ttk as ttk
import style

from tkinter.filedialog import askopenfilenames, askdirectory
from subapp.component import FileList, FileOutput, StatusBar
from subapp.core import syllabify_folds

SMOOTHING_METHOD_KEY = {
    "GKN": "gkn",
    "KN": "kn",
    "Stupid Backoff": "stupid_backoff"
} 

class TabTesting(Tab):
    def __init__(self, master):
        super().__init__(master)

        self.test_files = []
        self.ngram_files = []
        self.ngram_aug_files = []

        self.var_output_fname = tk.StringVar()
        self.var_output_fdir = tk.StringVar()

        self.sidebar()
        self.main()
        #self.status_bar()
    

    def sidebar(self):
        self.frm_sidebar = tk.LabelFrame(self, text="Params")
        self.frm_sidebar.grid(row=0, column=0, sticky="nsew", padx=style.SECTION_PADDING, pady=style.SECTION_PADDING)

        # Main params
        tk.Label(self.frm_sidebar, text="n").grid(row=0, column=0, sticky="nw")

        self.var_n = tk.IntVar()
        self.var_n.set(5)
        self.sbx_n = tk.Spinbox(self.frm_sidebar, textvariable=self.var_n, from_=1, to=10, width=style.DIGIT_ENTRY_WIDTH)
        self.sbx_n.grid(row=0, column=1, sticky="ne")
        
        self.var_lower_case = tk.BooleanVar()
        self.var_lower_case.set(True)
        self.cbt_lower_case = tk.Checkbutton(self.frm_sidebar, variable=self.var_lower_case, text="Ensure lower case")
        self.cbt_lower_case.grid(sticky="nw") 

        self.var_state_elim = tk.BooleanVar()
        self.var_state_elim.set(True)
        self.cbt_state_elim = tk.Checkbutton(self.frm_sidebar, variable=self.var_state_elim, text="State-elimination")
        self.cbt_state_elim.grid(columnspan=2, sticky="nw")

        self.var_augmentation = tk.BooleanVar()
        self.var_augmentation.set(False)
        self.cbt_augmentation = tk.Checkbutton(self.frm_sidebar, variable=self.var_augmentation, command=self.toggle_augmentation, text="Augmented n-gram")
        self.cbt_augmentation.grid(columnspan=2, sticky="nw")

        self.frm_aug_params = tk.Frame(self.frm_sidebar)
        self.frm_aug_params.columnconfigure(1, weight=1)
        
        tk.Label(self.frm_aug_params, text="Aug. weight").grid(row=0, column=0, sticky="nw")
        
        self.var_aug_w = tk.StringVar()
        self.var_aug_w.set(0.1)
        self.ent_aug_w = tk.Entry(self.frm_aug_params, textvariable=self.var_aug_w, width=style.DIGIT_ENTRY_WIDTH)
        self.ent_aug_w.grid(row=0, column=1, stick="ne")

        tk.Label(self.frm_sidebar, text="Smoothing").grid(row=3, columnspan=2, sticky="nw")
        
        self.var_smoothing = tk.StringVar()
        self.cbx_smoothing = ttk.Combobox(
            self.frm_sidebar,
            state="readonly",
            textvariable=self.var_smoothing,
            values=["GKN", "KN", "Stupid Backoff"],
            width=15
        )
        self.cbx_smoothing.bind("<<ComboboxSelected>>", self.cbx_smoothing_changed)
        self.cbx_smoothing.set("GKN")
        self.cbx_smoothing.grid(columnspan=2, sticky="new")

        self.frm_smoothing_params = tk.Frame(self.frm_sidebar)
        self.frm_smoothing_params.grid(columnspan=2, sticky="new", pady=style.ELEMENT_PADDING)
        self.frm_smoothing_params.columnconfigure(0, weight=1)

        self.frm_smoothings = {}
        
        # GKN params (default)
        self.frm_smoothings["GKN"] = tk.Frame(self.frm_smoothing_params)

        tk.Label(self.frm_smoothings["GKN"], text="B").grid(row=0, column=0, sticky="nw")

        self.var_gkn_b = tk.IntVar()
        self.var_gkn_b.set(3)
        self.sbx_gkn_b = tk.Spinbox(self.frm_smoothings["GKN"], from_=1, to=100, textvariable=self.var_gkn_b, width=style.DIGIT_ENTRY_WIDTH)
        self.sbx_gkn_b.grid(row=0, column=1, sticky="ne")

        # KN params
        self.frm_smoothings["KN"] = tk.Frame(self.frm_smoothing_params)

        tk.Label(self.frm_smoothings["KN"], text="D").grid(row=0, column=0, sticky="nw")

        self.var_kn_d = tk.StringVar()
        self.var_kn_d.set(0.75)
        self.ent_kn_d = tk.Entry(self.frm_smoothings["KN"], textvariable=self.var_kn_d, width=style.DIGIT_ENTRY_WIDTH)
        self.ent_kn_d.grid(row=0, column=1, sticky="ne")

        # Stupid Backoff params
        self.frm_smoothings["Stupid Backoff"] = tk.Frame(self.frm_smoothing_params)

        tk.Label(self.frm_smoothings["Stupid Backoff"], text="Alpha").grid(row=0, column=0, sticky="nw")

        self.var_sb_alpha = tk.StringVar()
        self.var_sb_alpha.set(0.4)
        self.ent_sb_alpha = tk.Entry(self.frm_smoothings["Stupid Backoff"], textvariable=self.var_sb_alpha, width=style.DIGIT_ENTRY_WIDTH)
        self.ent_sb_alpha.grid(row=0, column=1, sticky="ne")

        self.cbx_smoothing_changed(None)

        # Additional params
        self.var_validation = tk.BooleanVar()
        self.var_validation.set(True)
        self.cbt_validation = tk.Checkbutton(self.frm_sidebar, variable=self.var_validation, text="Validation")
        self.cbt_validation.grid(columnspan=2, sticky="nw")

        self.var_save_log = tk.BooleanVar()
        self.var_save_log.set(True)
        self.cbt_save_log = tk.Checkbutton(self.frm_sidebar, variable=self.var_save_log, text="Save log")
        self.cbt_save_log.grid(columnspan=2, sticky="nw")

        self.var_save_result = tk.BooleanVar()
        self.var_save_result.set(True)
        self.cbt_ave_result = tk.Checkbutton(self.frm_sidebar, variable=self.var_save_result, text="Save result")
        self.cbt_ave_result.grid(columnspan=2, sticky="nw")

        self.var_timestamp = tk.BooleanVar()
        self.var_timestamp.set(True)
        self.cbt_var_timestamp = tk.Checkbutton(self.frm_sidebar, variable=self.var_timestamp, text="Timestamp")
        self.cbt_var_timestamp.grid(columnspan=2, sticky="nw")
    

    def main(self):
        self.frm_main = tk.Frame(self)
        self.frm_main.grid(row=0, column=1, sticky="nsew", padx=style.SECTION_PADDING, pady=style.SECTION_PADDING)
        self.frm_main.rowconfigure(2, weight=1)
        self.frm_main.columnconfigure([0, 1], weight=1)

        # Test file area
        self.frm_test_file = FileList(
            master=self.frm_main,
            title="Test file",
            file_list=self.test_files,
            file_types=[("Text Files", "*.txt"), ("CSV Files", "*.csv"), ("All Files", "*")]
        )
        self.frm_test_file.grid(row=0, column=0, sticky="nsew")
        
        # n-gram file area
        self.frm_ngram_file = FileList(
            master=self.frm_main,
            title="n-gram file",
            file_list=self.ngram_files,
            file_types=[("JSON Files", "*.json"), ("All Files", "*")]
        )
        self.frm_ngram_file.grid(row=0, column=1, sticky="nsew")
        
        # Augmented n-gram file area
        self.frm_ngram_aug_file = FileList(
            master=self.frm_main,
            title="Augmented n-gram file",
            file_list=self.ngram_aug_files,
            file_types=[("JSON Files", "*.json"), ("All Files", "*")]
        )

        # Output area
        self.frm_file_output = FileOutput(
            master=self.frm_main,
            title="Save result as",
            fname=self.var_output_fname,
            fdir=self.var_output_fdir,
            auto_func=self.auto_output_fname
        )
        self.frm_file_output.grid(row=2, column=0, columnspan=2, sticky="sew")

        # Operatiom buttons
        self.frm_op_btn_container = tk.Frame(self.frm_main)
        self.frm_op_btn_container.grid(row=3, column=0, columnspan=2, sticky="e", pady=style.ELEMENT_PADDING)

        self.btn_start = tk.Button(self.frm_op_btn_container, width=style.BUTTON_WIDTH, text="Start", command=self.btn_start_click)
        self.btn_start.grid(row=0, column=1, sticky="e")

        self.btn_cancel = tk.Button(self.frm_op_btn_container, width=style.BUTTON_WIDTH, text="Cancel", state=tk.DISABLED)
        #self.btn_cancel.grid(row=0, column=0, sticky="e")
    

    def status_bar(self):
        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=style.SECTION_PADDING, pady=style.SECTION_PADDING)
        self.status_bar.write("Ready\n")
    

    def toggle_augmentation(self):
        if self.var_augmentation.get():
            self.frm_ngram_aug_file.grid(row=1, column=1, sticky="nsew", padx=style.ELEMENT_PADDING, pady=style.ELEMENT_PADDING)
            self.frm_aug_params.grid(row=2, columnspan=2, sticky="new")
        else:
            self.frm_ngram_aug_file.grid_remove()
            self.frm_aug_params.grid_remove()
    

    def cbx_smoothing_changed(self, event):
        smoothing = self.cbx_smoothing.get()

        for k, v in self.frm_smoothings.items():
            if k == smoothing:
                v.grid(sticky="new")
                v.columnconfigure(1, weight=1)
            else:
                v.grid_remove()
    

    def auto_output_fname(self):
        fname = f"{SMOOTHING_METHOD_KEY[self.var_smoothing.get()]}_n={self.var_n.get()}"
        
        if self.var_smoothing.get() == "GKN":
            fname += f"_B={self.var_gkn_b.get()}"
        elif self.var_smoothing.get() == "KN":
            fname += f"_D={self.var_kn_d.get()}"
        elif self.var_smoothing.get() == "Stupid Backoff":
            fname += f"_a={self.var_sb_alpha.get()}"
        
        if self.var_augmentation.get():
            fname += f"_aug_w={self.var_aug_w.get()}"

        self.var_output_fname.set(fname)

    
    def btn_start_click(self):
        valid = True

        # Validations
        if self.var_augmentation.get():
            try:
                aug_w = float(self.var_aug_w.get())
            except ValueError:
                self.status_bar.write("[!] Aug. w is not a valid decimal number\n")
                valid = False

        if self.var_smoothing.get() == "KN":
            try:
                d = float(self.var_kn_d.get())
            except ValueError:
                self.status_bar.write("[!] D is not a valid decimal number\n")
                valid = False
        elif self.var_smoothing.get() == "Stupid Backoff":
            try:
                alpha = float(self.var_sb_alpha.get())
            except ValueError:
                self.status_bar.write("[!] Alpha is not a valid decimal number\n")
                valid = False
        
        if len(self.test_files) < 1:
            self.status_bar.write("[!] No test file selected.\n")
            valid = False

        if len(self.ngram_files) < 1:
            self.status_bar.write("[!] No n-gram file selected.\n")
            valid = False
        
        if len(self.test_files) != len(self.ngram_files):
            self.status_bar.write("[!] Number of test file and n-gram file does not match.\n")
            valid = False
        
        if self.var_augmentation.get() and len(self.test_files) != len(self.ngram_aug_files):
            self.status_bar.write("[!] Number of test file and augmented n-gram file does not match.\n")
            valid = False
        
        if self.var_save_log.get() or self.var_save_result.get():
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
            threading.Thread(target=self.syllabify_folds_worker).start()
    

    def syllabify_folds_worker(self):
        self.master.toggle_other_tabs(False)
        self.btn_start.config(state=tk.DISABLED)
        self.btn_cancel.config(state=tk.NORMAL)

        old_stdout = sys.stdout
        sys.stdout = self.status_bar

        prob_args= {
            "method": SMOOTHING_METHOD_KEY[self.var_smoothing.get()],
            "with_aug": self.var_augmentation.get()
        }

        if self.var_augmentation.get():
            prob_args["aug_w"] = float(self.var_aug_w.get())

        if self.var_smoothing.get() == "GKN":
            prob_args["d_ceil"] = self.var_gkn_b.get()
        elif self.var_smoothing.get() == "KN":
            prob_args["d"] = float(self.var_kn_d.get())
        elif self.var_smoothing.get() == "Stupid Backoff":
            prob_args["alpha"] = float(self.var_sb_alpha.get())

        try:
            syllabify_folds(
                data_test_fnames=self.test_files,
                n_gram_fnames=self.ngram_files,
                n=self.var_n.get(),
                prob_args=prob_args,
                n_gram_aug_fnames=self.ngram_aug_files,
                lower_case=self.var_lower_case.get(),
                output_fname=self.var_output_fname.get(),
                output_fdir=self.var_output_fdir.get(),
                state_elim=self.var_state_elim.get(),
                validation=self.var_validation.get(),
                save_log=self.var_save_log.get(),
                save_result_=self.var_save_result.get(),
                timestamp=self.var_timestamp.get()
            )
        except Exception as e:
            print(f"Error:\n{e}")

        sys.stdout = old_stdout

        self.master.toggle_other_tabs(True)
        self.btn_start.config(state=tk.NORMAL)
        self.btn_cancel.config(state=tk.DISABLED)
            
