import tkinter as tk
import style
import utility as util

from tkinter.filedialog import askopenfilenames, askdirectory
from tkinter.scrolledtext import ScrolledText

class FileList(tk.LabelFrame):
    def __init__(self, master, title, file_list, file_types):
        super().__init__(master, text=title)
        self.columnconfigure(0, weight=1)

        self.file_list = file_list
        self.file_types = file_types
        self.update_listing()

        self.frm_btn_container = tk.Frame(self)
        self.frm_btn_container.grid(row=1, column=0, sticky="nw", pady=style.ELEMENT_PADDING)

        tk.Button(self.frm_btn_container, text="Add File(s)", command=self.add_files).grid(row=0, column=0, padx=style.ELEMENT_PADDING)
        tk.Button(self.frm_btn_container, text="Remove All", command=self.remove_all_file).grid(row=0, column=1, padx=style.ELEMENT_PADDING)
    

    def update_listing(self, init=False):
        if hasattr(self, "frm_listing"):
            self.frm_listing.destroy()
        
        self.frm_listing = tk.Frame(self)
        self.frm_listing.grid(row=0, column=0, sticky="new")
        self.frm_listing.columnconfigure(1, weight=1)
        
        for i, fpath in enumerate(self.file_list):
            tk.Label(self.frm_listing, text=f"{i+1}.").grid(row=i, column=0, sticky="nw")

            ent_fpath = tk.Entry(self.frm_listing)
            ent_fpath.grid(row=i, column=1, sticky="nsew")
            ent_fpath.insert(0, fpath)
            ent_fpath.xview(tk.END)
            ent_fpath.config(state="readonly")

            tk.Button(self.frm_listing, text="\u274C", command=lambda x=i : self.remove_file(x)).grid(row=i, column=2, sticky="ne")
    

    def add_files(self):
        new_files = list(askopenfilenames(filetypes=self.file_types))

        self.file_list += new_files
        self.update_listing()


    def remove_file(self, i):
        self.file_list.pop(i)
        self.update_listing()
    

    def remove_all_file(self):
        self.file_list.clear()
        self.update_listing()


class FileOutput(tk.Frame):
    def __init__(self, master, title, fname, fdir, auto_func):
        super().__init__(master)
        self.fname = fname
        self.fdir = fdir
        self.columnconfigure(1, weight=1)

        tk.Label(self, text=title).grid(row=0, column=0, columnspan=2, sticky="nw")

        tk.Label(self, text="File name:").grid(row=1, column=0, sticky="w")
        tk.Entry(self, textvariable=fname).grid(row=1, column=1, sticky="nsew", padx=style.ELEMENT_PADDING, pady=style.ELEMENT_PADDING)
        tk.Button(self, text="Auto", width=style.BUTTON_WIDTH, command=auto_func).grid(row=1, column=2, sticky="nsew", pady=style.ELEMENT_PADDING)

        tk.Label(self, text="Directory:").grid(row=2, column=0, sticky="w")
        tk.Entry(self, textvariable=fdir).grid(row=2, column=1, sticky="nsew", padx=style.ELEMENT_PADDING, pady=style.ELEMENT_PADDING)
        tk.Button(self, text="Browse", width=style.BUTTON_WIDTH, command=self.browse_fdir).grid(row=2, column=2, sticky="nsew", pady=style.ELEMENT_PADDING)
    

    def browse_fdir(self):
        new_dir = askdirectory(mustexist=True)

        if new_dir != '':
            self.fdir.set(new_dir)


class StatusBar(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.repeat_line = False

        self.status_text = ScrolledText(self, width=0, height=0, state=tk.DISABLED)
        self.status_text.pack(expand=True, fill=tk.BOTH)
    
    def write(self, string):
        self.status_text.config(state=tk.NORMAL)

        if self.repeat_line:
            self.status_text.delete("end-1c linestart", "end-1c lineend")
            self.repeat_line = False
        
        self.status_text.insert(tk.END, string)

        if len(string) > 0 and string[-1] == "\r":
            self.repeat_line = True
        
        self.status_text.config(state=tk.DISABLED)
        self.status_text.see(tk.END)


class ConfigText(tk.Frame):
    def __init__(self, master, title, def_var, var):
        super().__init__(master)
        self.master = master
        self.def_var = util.tags_to_str(def_var)
        self.var = var

        # List of vowels
        tk.Label(self, text=title).grid(row=0, column=0, columnspan=2, sticky="nw")
        
        self.var_custom = tk.BooleanVar()
        tk.Radiobutton(self, text="Default", variable=self.var_custom, value=False, command=self.toggle).grid(row=1, column=0, sticky="nw")
        tk.Radiobutton(self, text="Custom", variable=self.var_custom, value=True, command=self.toggle).grid(row=1, column=1, sticky="nw")

        self.ent_var = tk.Entry(self, textvariable=self.var, width=style.TEXT_ENTRY_WIDTH)
        self.ent_var.grid(row=2, column=0, columnspan=2, sticky="nw")

        self.toggle()


    def toggle(self):
        if self.var_custom.get():
            self.ent_var.config(state=tk.NORMAL)
        else:
            self.var.set(self.def_var)
            self.ent_var.config(state=tk.DISABLED)
    

    def check_default(self):
        self.var_custom.set(self.var.get() != self.def_var)
        self.toggle()
