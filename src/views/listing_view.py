import os
import sys
import threading
import subprocess
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from src.core import file_ops


class ListingView(ttk.Frame):
    def __init__(self, master, initial_path=None, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.path_var = tk.StringVar()
        self._current_filter = ''
        if initial_path:
            self.path_var.set(initial_path)
        self.create_widgets()

    def create_widgets(self):
        top = ttk.Frame(self)
        top.pack(fill=tk.X, padx=8, pady=6)
        # path entry and filter
        entry = ttk.Entry(top, textvariable=self.path_var)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,6))

        browse = ttk.Button(top, text='Browse...', command=self.browse)
        browse.pack(side=tk.LEFT)

        refresh = ttk.Button(top, text='Refresh', command=self.refresh)
        refresh.pack(side=tk.LEFT, padx=(6,0))

        # filter box
        filter_lbl = ttk.Label(top, text='Filter:')
        filter_lbl.pack(side=tk.LEFT, padx=(8,2))
        self.filter_var = tk.StringVar()
        filter_entry = ttk.Entry(top, textvariable=self.filter_var, width=24)
        filter_entry.pack(side=tk.LEFT)
        filter_entry.bind('<KeyRelease>', lambda e: self.apply_filter())

        self.status_var = tk.StringVar()
        status = ttk.Label(self, textvariable=self.status_var)
        status.pack(fill=tk.X, padx=8, pady=(0,6))

        columns = ('type', 'size', 'modified')
        self.tree = ttk.Treeview(self, columns=columns, show='tree headings', selectmode='browse')
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
        # style: alternating row colors
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure('Treeview', rowheight=22, font=('Segoe UI', 10))
        style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'))
        self.tree.tag_configure('odd', background='#ffffff')
        self.tree.tag_configure('even', background='#f6f6f6')

        # context menu
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label='Open', command=self.ctx_open)
        self.menu.add_command(label='Reveal in Explorer', command=self.ctx_reveal)
        self.menu.add_command(label='Copy Path', command=self.ctx_copy_path)
        self.tree.bind('<Button-3>', self.on_right_click)

    def apply_filter(self):
        # simple filter: reload current root with filter applied
        f = self.filter_var.get().lower().strip()
        self._current_filter = f
        if hasattr(self, 'root_path') and self.root_path:
            # reload path; this will use current filter during insert
            self.load_path(self.root_path)

    def on_right_click(self, event):
        iid = self.tree.identify_row(event.y)
        if iid:
            try:
                self.tree.selection_set(iid)
            except Exception:
                pass
            try:
                self.menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.menu.grab_release()

    def ctx_open(self):
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
                    subprocess.Popen(['xdg-open', full])
            except Exception:
                pass

    def ctx_reveal(self):
        item = self.tree.focus()
        if not item:
            return
        full = os.path.join(self.root_path, item)
        try:
            folder = full if os.path.isdir(full) else os.path.dirname(full)
            if sys.platform.startswith('win'):
                os.startfile(folder)
            else:
                subprocess.Popen(['xdg-open', folder])
        except Exception:
            pass

    def ctx_copy_path(self):
        item = self.tree.focus()
        if not item:
            return
        full = os.path.join(self.root_path, item)
        try:
            self.clipboard_clear()
            self.clipboard_append(full)
        except Exception:
            pass

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
            for idx, (name, full, is_dir, size, mtime) in enumerate(items):
                nid = name
                tag = 'even' if idx % 2 == 0 else 'odd'
                if is_dir:
                    try:
                        self.tree.insert('', 'end', nid, text=name, values=('Directory', '', ''), tags=(tag,))
                        self.tree.insert(nid, 'end', nid + '__dummy', text='')
                    except Exception:
                        pass
                else:
                    try:
                        self.tree.insert('', 'end', nid, text=name, values=('File', file_ops.format_size(size), file_ops.format_mtime(mtime)), tags=(tag,))
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
            base_count = len(self.tree.get_children(node_id))
            for idx, (name, full, is_dir, size, mtime) in enumerate(items, start=base_count):
                child_rel = os.path.join(node_id, name) if node_id else name
                tag = 'even' if idx % 2 == 0 else 'odd'
                if is_dir:
                    try:
                        if not self.tree.exists(child_rel):
                            self.tree.insert(node_id, 'end', child_rel, text=name, values=('Directory', '', ''), tags=(tag,))
                            self.tree.insert(child_rel, 'end', child_rel + '__dummy', text='')
                    except Exception:
                        pass
                else:
                    try:
                        if not self.tree.exists(child_rel):
                            self.tree.insert(node_id, 'end', child_rel, text=name, values=('File', file_ops.format_size(size), file_ops.format_mtime(mtime)), tags=(tag,))
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
