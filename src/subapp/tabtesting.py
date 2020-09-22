from subapp.tab import Tab

import sys
import traceback
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
    def __init__(self, master, mode):
        super().__init__(master)
        self.mode = mode

        self.test_files = []
        self.ngram_files = []
        self.ngram_aug_files = []

        self.var_output_fname = tk.StringVar()
        self.var_output_fdir = tk.StringVar()

        self.var_n = tk.StringVar()
        self.var_n.set(5)
        self.var_lower_case = tk.BooleanVar()

        self.var_state_elim = tk.BooleanVar()
        self.var_state_elim.set(True)
        self.var_stemming = tk.BooleanVar()

        self.var_augmentation = tk.BooleanVar()
        self.var_aug_w = tk.StringVar()
        self.var_aug_w.set(0.1)

        self.var_aug_prob = tk.BooleanVar()
        self.var_aug_prob_flip = tk.BooleanVar()
        self.var_aug_prob_transpose = tk.BooleanVar()
        self.var_smoothing = tk.StringVar()

        self.var_gkn_b = tk.StringVar()
        self.var_gkn_b.set(3)
        self.var_kn_d = tk.StringVar()
        self.var_kn_d.set(0.75)
        self.var_sb_alpha = tk.StringVar()
        self.var_sb_alpha.set(0.4)

        self.var_validation = tk.BooleanVar()
        self.var_validation.set(True)
        self.var_save_log = tk.BooleanVar()
        self.var_save_log.set(True)
        self.var_save_result = tk.BooleanVar()
        self.var_save_result.set(True)
        self.var_timestamp = tk.BooleanVar()
        self.var_timestamp.set(True)
        self.var_no_phoneme_sym = tk.BooleanVar()
        self.var_no_phoneme_sym.set(True)

        self.sidebar()
        self.main()
        
        if self.mode == "syl":
            self.toggle_augmentation()
            self.toggle_aug_prob()
    

    def sidebar(self):
        self.frm_sidebar = tk.LabelFrame(self, text="Params")
        self.frm_sidebar.grid(row=0, column=0, sticky="nsew", padx=style.SECTION_PADDING, pady=style.SECTION_PADDING)

        # Main params
        tk.Label(self.frm_sidebar, text="n").grid(row=0, column=0, sticky="nw")

        self.sbx_n = tk.Spinbox(self.frm_sidebar, textvariable=self.var_n, from_=1, to=99, width=style.DIGIT_ENTRY_WIDTH)
        self.sbx_n.grid(row=0, column=1, sticky="ne")
        
        self.cbt_lower_case = tk.Checkbutton(self.frm_sidebar, variable=self.var_lower_case, text="Ensure lower case")
        self.cbt_lower_case.grid(sticky="nw") 

        if self.mode == "syl":
            self.cbt_state_elim = tk.Checkbutton(self.frm_sidebar, variable=self.var_state_elim, text="State-elimination")
        elif self.mode == "g2p":
            self.cbt_state_elim = tk.Checkbutton(self.frm_sidebar, variable=self.var_state_elim, text="Phonotactic rules")
        
        self.cbt_state_elim.grid(columnspan=2, sticky="nw")

        if self.mode == "g2p":
            self.cbt_stemming = tk.Checkbutton(self.frm_sidebar, variable=self.var_stemming, text="Stemming")
            self.cbt_stemming.grid(sticky="nw") 

        if self.mode == "syl":
            # n-gram aug params
            self.cbt_augmentation = tk.Checkbutton(self.frm_sidebar, variable=self.var_augmentation, command=self.toggle_augmentation, text="Augmented n-gram")
            self.cbt_augmentation.grid(columnspan=2, sticky="nw")

            self.frm_aug_params = tk.Frame(self.frm_sidebar)
            self.frm_aug_params.columnconfigure(1, weight=1)
            self.frm_aug_params.grid(columnspan=2, sticky="new")
            
            tk.Label(self.frm_aug_params, text="Aug. weight").grid(row=0, column=0, sticky="nw")
            
            self.ent_aug_w = tk.Entry(self.frm_aug_params, textvariable=self.var_aug_w, width=style.DIGIT_ENTRY_WIDTH)
            self.ent_aug_w.grid(row=0, column=1, stick="ne")

            # Augmented probabiliy params
            self.cbt_aug_prob = tk.Checkbutton(self.frm_sidebar, variable=self.var_aug_prob, command=self.toggle_aug_prob, text="Augmented probability")
            self.cbt_aug_prob.grid(columnspan=2, sticky="nw")

            self.frm_aug_prob = tk.Frame(self.frm_sidebar)
            self.frm_aug_prob.columnconfigure(1, weight=1)
            self.frm_aug_prob.grid(columnspan=2, sticky="new")

            self.cbt_augmentation = tk.Checkbutton(self.frm_aug_prob, variable=self.var_aug_prob_flip, text="Flipped onsets")
            self.cbt_augmentation.grid(columnspan=2, sticky="nw")

            self.cbt_augmentation = tk.Checkbutton(self.frm_aug_prob, variable=self.var_aug_prob_transpose, text="Transposed nucleus")
            self.cbt_augmentation.grid(columnspan=2, sticky="nw")

        # Smoothing params
        tk.Label(self.frm_sidebar, text="Smoothing").grid(columnspan=2, sticky="nw")
        
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

        self.sbx_gkn_b = tk.Spinbox(self.frm_smoothings["GKN"], textvariable=self.var_gkn_b, from_=1, to=99, width=style.DIGIT_ENTRY_WIDTH)
        self.sbx_gkn_b.grid(row=0, column=1, sticky="ne")

        # KN params
        self.frm_smoothings["KN"] = tk.Frame(self.frm_smoothing_params)

        tk.Label(self.frm_smoothings["KN"], text="D").grid(row=0, column=0, sticky="nw")

        self.ent_kn_d = tk.Entry(self.frm_smoothings["KN"], textvariable=self.var_kn_d, width=style.DIGIT_ENTRY_WIDTH)
        self.ent_kn_d.grid(row=0, column=1, sticky="ne")

        # Stupid Backoff params
        self.frm_smoothings["Stupid Backoff"] = tk.Frame(self.frm_smoothing_params)

        tk.Label(self.frm_smoothings["Stupid Backoff"], text="Alpha").grid(row=0, column=0, sticky="nw")

        self.ent_sb_alpha = tk.Entry(self.frm_smoothings["Stupid Backoff"], textvariable=self.var_sb_alpha, width=style.DIGIT_ENTRY_WIDTH)
        self.ent_sb_alpha.grid(row=0, column=1, sticky="ne")

        self.cbx_smoothing_changed(None)

        # Additional params
        self.cbt_validation = tk.Checkbutton(self.frm_sidebar, variable=self.var_validation, text="Validation")
        self.cbt_validation.grid(columnspan=2, sticky="nw")

        self.cbt_save_log = tk.Checkbutton(self.frm_sidebar, variable=self.var_save_log, text="Save log")
        self.cbt_save_log.grid(columnspan=2, sticky="nw")

        self.cbt_ave_result = tk.Checkbutton(self.frm_sidebar, variable=self.var_save_result, text="Save result")
        self.cbt_ave_result.grid(columnspan=2, sticky="nw")

        self.cbt_var_timestamp = tk.Checkbutton(self.frm_sidebar, variable=self.var_timestamp, text="Timestamp")
        self.cbt_var_timestamp.grid(columnspan=2, sticky="nw")

        if self.mode == "g2p":
            self.cbt_no_phoneme_sym = tk.Checkbutton(self.frm_sidebar, variable=self.var_no_phoneme_sym, text="Inc. no-phoneme symbol (*)")
            self.cbt_no_phoneme_sym.grid(columnspan=2, sticky="nw")
    

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
            self.frm_aug_params.grid(row=4, columnspan=2, sticky="new")
        else:
            self.frm_ngram_aug_file.grid_remove()
            self.frm_aug_params.grid_remove()
    

    def toggle_aug_prob(self):
        if self.var_aug_prob.get():
            self.frm_aug_prob.grid(row=6, columnspan=2, sticky="new")
        else:
            self.frm_aug_prob.grid_remove()
    

    def cbx_smoothing_changed(self, event):
        smoothing = self.cbx_smoothing.get()

        for k, v in self.frm_smoothings.items():
            if k == smoothing:
                v.grid(sticky="new")
                v.columnconfigure(1, weight=1)
            else:
                v.grid_remove()
    

    def auto_output_fname(self):
        fname = ""

        if self.mode == "syl":
            if self.var_state_elim.get():
                fname += "se_"
        
        elif self.mode == "g2p":
            if self.var_state_elim.get():
                fname += "rules_"

            if self.var_stemming.get():
                fname += "stem_"

        fname += f"{SMOOTHING_METHOD_KEY[self.var_smoothing.get()]}_n={self.var_n.get()}"
        
        if self.var_smoothing.get() == "GKN":
            fname += f"_B={self.var_gkn_b.get()}"
        elif self.var_smoothing.get() == "KN":
            fname += f"_D={self.var_kn_d.get()}"
        elif self.var_smoothing.get() == "Stupid Backoff":
            fname += f"_a={self.var_sb_alpha.get()}"
        
        if self.var_augmentation.get():
            fname += f"_aug_w={self.var_aug_w.get()}"

        self.var_output_fname.set(fname)


    def get_var_range(self, str_range, var_name, var_min=1, var_max=99):
        valid = True
        var_range = str_range.split("-")

        if len(var_range) < 1:
            self.status_bar.write(f"[!] {var_name} can not be empty\n")
            valid = False
        elif len(var_range) > 2:
            self.status_bar.write(f"[!] {var_name} range is not valid\n")
            valid = False
        else:
            for i in range(len(var_range)):
                try:
                    var_range[i] = int(var_range[i])
                except ValueError:
                    self.status_bar.write(f"[!] {var_name} is not a valid integer number\n")
                    valid = False
                    break
            
            if valid:
                var_start = var_range[0]
                var_end   = var_range[len(var_range)-1]
                
                if var_start > var_end:
                    var_start, var_end = var_end, var_start
                
                if var_start < var_min:
                    self.status_bar.write(f"[!] {var_name} can not be smaller than {var_min}\n")
                    valid = False
                
                if var_end > var_max:
                    self.status_bar.write(f"[!] {var_name} can not be bigger than {var_max}\n")
                    valid = False
        
        if valid:
            return range(var_start, var_end+1)
                

    def btn_start_click(self):
        valid = True

        # Validations
        self.n_range = self.get_var_range(self.var_n.get(), "n")

        if not self.n_range:
            valid = False

        if self.var_augmentation.get():
            try:
                aug_w = float(self.var_aug_w.get())
            except ValueError:
                self.status_bar.write("[!] Aug. w is not a valid decimal number\n")
                valid = False

        if self.var_smoothing.get() == "GKN":
            self.gkn_b_range = self.get_var_range(self.var_gkn_b.get(), "B")

            if not self.gkn_b_range:
                valid = False
        elif self.var_smoothing.get() == "KN":
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

        for n in self.n_range:
            if self.var_smoothing.get() == "GKN":
                smoothing_param_range = self.gkn_b_range
            else:
                smoothing_param_range = range(0, 1)
            
            for smoothing_param in smoothing_param_range:
                prob_args= {
                    "method": SMOOTHING_METHOD_KEY[self.var_smoothing.get()],
                    "with_aug": self.var_augmentation.get(),
                    "aug_prob": self.var_aug_prob.get(),
                    "aug_prob_methods": {
                        "flip_onsets": self.var_aug_prob_flip.get(),
                        "transpose_nucleus": self.var_aug_prob_transpose.get()
                    }
                }

                if self.var_augmentation.get():
                    prob_args["aug_w"] = float(self.var_aug_w.get())

                if self.var_smoothing.get() == "GKN":
                    prob_args["d_ceil"] = smoothing_param
                elif self.var_smoothing.get() == "KN":
                    prob_args["d"] = float(self.var_kn_d.get())
                elif self.var_smoothing.get() == "Stupid Backoff":
                    prob_args["alpha"] = float(self.var_sb_alpha.get())

                try:
                    syllabify_folds(
                        data_test_fnames=self.test_files,
                        n_gram_fnames=self.ngram_files,
                        n=n,
                        prob_args=prob_args,
                        n_gram_aug_fnames=self.ngram_aug_files,
                        lower_case=self.var_lower_case.get(),
                        output_fname=self.var_output_fname.get(),
                        output_fdir=self.var_output_fdir.get(),
                        state_elim=self.var_state_elim.get(),
                        stemming=self.var_stemming.get(),
                        mode=self.mode,
                        char_strips="" if self.var_no_phoneme_sym.get() else "*",
                        validation=self.var_validation.get(),
                        save_log=self.var_save_log.get(),
                        save_result_=self.var_save_result.get(),
                        timestamp=self.var_timestamp.get()
                    )
                except Exception as e:
                    print(f"Error:\n{e}")
                    print(traceback.format_exc())

        sys.stdout = old_stdout

        self.master.toggle_other_tabs(True)
        self.btn_start.config(state=tk.NORMAL)
        self.btn_cancel.config(state=tk.DISABLED)
            
