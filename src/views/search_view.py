import tkinter as tk
from tkinter import ttk

class SearchView(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.term_var = tk.StringVar()
        self.create_widgets()

    def create_widgets(self):
        top = ttk.Frame(self)
        top.pack(fill='x', padx=8, pady=6)
        entry = ttk.Entry(top, textvariable=self.term_var)
        entry.pack(side='left', fill='x', expand=True)
        btn = ttk.Button(top, text='Search', command=self.on_search)
        btn.pack(side='left', padx=(6,0))

    def on_search(self):
        # placeholder
        term = self.term_var.get()
        print('Search for', term)
