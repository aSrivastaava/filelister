import os
import sys
import threading
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from src.core import file_ops


class ListingView(ttk.Frame):
    def __init__(self, master, initial_path=None, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.path_var = tk.StringVar()
        if initial_path:
            self.path_var.set(initial_path)
        self.create_widgets()

    def create_widgets(self):
        top = ttk.Frame(self)
        top.pack(fill=tk.X, padx=8, pady=6)

        entry = ttk.Entry(top, textvariable=self.path_var)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,6))

        browse = ttk.Button(top, text='Browse...', command=self.browse)
        browse.pack(side=tk.LEFT)

        refresh = ttk.Button(top, text='Refresh', command=self.refresh)
        refresh.pack(side=tk.LEFT, padx=(6,0))

        self.status_var = tk.StringVar()
        status = ttk.Label(self, textvariable=self.status_var)
        status.pack(fill=tk.X, padx=8, pady=(0,6))

        columns = ('type', 'size', 'modified')
        self.tree = ttk.Treeview(self, columns=columns, show='tree headings')
        self.tree.heading('#0', text='Name')
        self.tree.heading('type', text='Type')
        self.tree.heading('size', text='Size')
        self.tree.heading('modified', text='Modified')
        self.tree.column('type', width=100)
        self.tree.column('size', width=120, anchor='e')
        self.tree.column('modified', width=160)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        self.tree.bind('<Double-1>', self.on_double)
        self.tree.bind('<<TreeviewOpen>>', self.on_open)

    def browse(self):
        path = filedialog.askdirectory()
        if path:
            self.path_var.set(path)
            self.load_path(path)

    def refresh(self):
        p = self.path_var.get()
        if not p:
            messagebox.showinfo('Info', 'Please select a directory first')
            return
        self.load_path(p)

    def set_status(self, text):
        self.status_var.set(text)
        self.update_idletasks()

    def load_path(self, path):
        self.root_path = path
        # clear
        try:
            self.tree.delete(*self.tree.get_children())
        except Exception:
            for c in self.tree.get_children():
                try:
                    self.tree.delete(c)
                except Exception:
                    pass
        self.set_status('Listing...')
        t = threading.Thread(target=self._list_top, args=(path,))
        t.daemon = True
        t.start()

    def _list_top(self, path):
        items = file_ops.list_dir(path)
        def insert():
            for name, full, is_dir, size, mtime in items:
                nid = name
                if is_dir:
                    try:
                        self.tree.insert('', 'end', nid, text=name, values=('Directory', '', ''))
                        self.tree.insert(nid, 'end', nid + '__dummy', text='')
                    except Exception:
                        pass
                else:
                    try:
                        self.tree.insert('', 'end', nid, text=name, values=('File', file_ops.format_size(size), file_ops.format_mtime(mtime)))
                    except Exception:
                        pass
            self.set_status(f'Listed {len(items)} items')
        self.after(0, insert)

    def on_open(self, event):
        item = self.tree.focus()
        if not item:
            return
        children = self.tree.get_children(item)
        if children and any(c.endswith('__dummy') for c in children):
            for c in children:
                if c.endswith('__dummy'):
                    try:
                        self.tree.delete(c)
                    except Exception:
                        pass
            full = os.path.join(self.root_path, item)
            t = threading.Thread(target=self._populate, args=(item, full))
            t.daemon = True
            t.start()

    def _populate(self, node_id, full_path):
        items = file_ops.list_dir(full_path)
        def insert():
            for name, full, is_dir, size, mtime in items:
                child_rel = os.path.join(node_id, name) if node_id else name
                if is_dir:
                    try:
                        if not self.tree.exists(child_rel):
                            self.tree.insert(node_id, 'end', child_rel, text=name, values=('Directory', '', ''))
                            self.tree.insert(child_rel, 'end', child_rel + '__dummy', text='')
                    except Exception:
                        pass
                else:
                    try:
                        if not self.tree.exists(child_rel):
                            self.tree.insert(node_id, 'end', child_rel, text=name, values=('File', file_ops.format_size(size), file_ops.format_mtime(mtime)))
                    except Exception:
                        pass
        self.after(0, insert)

    def on_double(self, event):
        item = self.tree.focus()
        if not item:
            return
        typ = self.tree.set(item, 'type')
        full = os.path.join(self.root_path, item)
        if typ == 'File':
            try:
                if sys.platform.startswith('win'):
                    os.startfile(full)
                else:
                    import subprocess
                    subprocess.Popen(['xdg-open', full])
            except Exception as e:
                messagebox.showerror('Open file', f'Could not open file: {e}')
