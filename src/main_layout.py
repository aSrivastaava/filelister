import tkinter as tk
from tkinter import ttk
from src.views.listing_view import ListingView
from src.views.search_view import SearchView


class MainLayout(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('File Lister')
        self.geometry('900x600')
        self.create_widgets()

    def create_widgets(self):
        # simple notebook to switch between listing and search
        nb = ttk.Notebook(self)
        nb.pack(fill='both', expand=True)

        self.listing = ListingView(nb)
        nb.add(self.listing, text='Listing')

        self.search = SearchView(nb)
        nb.add(self.search, text='Search')


if __name__ == '__main__':
    app = MainLayout()
    app.mainloop()
