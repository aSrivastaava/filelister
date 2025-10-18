import tkinter as tk
from tkinter import ttk
from src.views.listing_view import ListingView
from src.views.search_view import SearchView


class MainLayout(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('File Lister')
        self.geometry('1000x650')
        self.style = ttk.Style(self)
        # try a modern theme
        for t in ('clam', 'alt', 'default'):
            try:
                self.style.theme_use(t)
                break
            except Exception:
                continue

        self.dark = False
        self.create_widgets()

    def create_widgets(self):
        # main area: left sidebar + right content
        pan = ttk.Panedwindow(self, orient='horizontal')
        pan.pack(fill='both', expand=True, padx=8, pady=(8,6))

        # left sidebar
        sidebar = ttk.Frame(pan, width=220, padding=(8,8))
        pan.add(sidebar, weight=0)

        title = ttk.Label(sidebar, text='📁 File Lister', font=('Segoe UI', 14, 'bold'))
        title.pack(anchor='w', pady=(0,8))

        # quick filters
        ttk.Label(sidebar, text='Quick filters', font=('Segoe UI', 10, 'underline')).pack(anchor='w', pady=(6,4))
        btn_all = ttk.Button(sidebar, text='All items', command=lambda: self.status_var.set('All items'))
        btn_all.pack(fill='x', pady=2)
        btn_dirs = ttk.Button(sidebar, text='Directories', command=lambda: self.status_var.set('Directories'))
        btn_dirs.pack(fill='x', pady=2)
        btn_files = ttk.Button(sidebar, text='Files', command=lambda: self.status_var.set('Files'))
        btn_files.pack(fill='x', pady=2)

        ttk.Separator(sidebar, orient='horizontal').pack(fill='x', pady=8)
        ttk.Label(sidebar, text='Recent', font=('Segoe UI', 10, 'underline')).pack(anchor='w', pady=(0,4))
        # empty recent placeholder
        ttk.Label(sidebar, text='(no recent folders)', foreground='#666').pack(anchor='w')

        # right content
        content = ttk.Frame(pan, padding=(4,0))
        pan.add(content, weight=1)

        # toolbar in content
        toolbar = ttk.Frame(content, padding=(6,6))
        toolbar.pack(side='top', fill='x')

        run_btn = ttk.Button(toolbar, text='🔍 Browse', command=self.on_browse)
        run_btn.pack(side='left')

        refresh_btn = ttk.Button(toolbar, text='⟳ Refresh', command=self.on_refresh)
        refresh_btn.pack(side='left', padx=(6,0))

        theme_btn = ttk.Button(toolbar, text='🌙 Toggle Theme', command=self.toggle_theme)
        theme_btn.pack(side='right')

        # notebook for views inside content
        nb = ttk.Notebook(content)
        nb.pack(fill='both', expand=True, padx=6, pady=(6,0))

        self.listing = ListingView(nb)
        nb.add(self.listing, text='Listing')

        self.search = SearchView(nb)
        nb.add(self.search, text='Search')

        # status bar
        self.status_var = tk.StringVar(value='Ready')
        status = ttk.Label(self, textvariable=self.status_var, relief='sunken', anchor='w', padding=4)
        status.pack(side='bottom', fill='x')

    def on_browse(self):
        # delegate to listing view
        self.listing.browse()

    def on_refresh(self):
        self.listing.refresh()

    def toggle_theme(self):
        # simple theme toggle: invert colors via style map for Treeview
        self.dark = not self.dark
        if self.dark:
            self.style.configure('Treeview', background='#2b2b2b', foreground='#eaeaea', fieldbackground='#2b2b2b')
            self.style.configure('Treeview.Heading', background='#3b3b3b', foreground='#ffffff')
            self.status_var.set('Dark theme')
        else:
            self.style.configure('Treeview', background='#ffffff', foreground='#000000', fieldbackground='#ffffff')
            self.style.configure('Treeview.Heading', background='#f0f0f0', foreground='#000000')
            self.status_var.set('Light theme')


if __name__ == '__main__':
    app = MainLayout()
    app.mainloop()
