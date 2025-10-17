import os
import sys
import threading
import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class FileListerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("File Lister")
        self.geometry("900x600")

        self.create_widgets()

    def create_widgets(self):
        top = ttk.Frame(self)
        top.pack(fill=tk.X, padx=8, pady=6)

        self.path_var = tk.StringVar()

        path_entry = ttk.Entry(top, textvariable=self.path_var)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        browse_btn = ttk.Button(top, text="Browse...", command=self.browse)
        browse_btn.pack(side=tk.LEFT)

        refresh_btn = ttk.Button(top, text="Refresh", command=self.refresh)
        refresh_btn.pack(side=tk.LEFT, padx=(6, 0))

        self.status_var = tk.StringVar()
        status = ttk.Label(self, textvariable=self.status_var)
        status.pack(fill=tk.X, padx=8, pady=(0,6))

        # Treeview
        columns = ("type", "size", "modified")
        self.tree = ttk.Treeview(self, columns=columns, show="tree headings")
        self.tree.heading("#0", text="Name", anchor=tk.W)
        self.tree.heading("type", text="Type")
        self.tree.heading("size", text="Size")
        self.tree.heading("modified", text="Modified")

        self.tree.column("type", width=100, anchor=tk.W)
        self.tree.column("size", width=120, anchor=tk.E)
        self.tree.column("modified", width=180, anchor=tk.W)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        # double-click to open file
        self.tree.bind('<Double-1>', self.on_double)
        # expand event for lazy-loading
        self.tree.bind('<<TreeviewOpen>>', self.on_open)

    def browse(self):
        path = filedialog.askdirectory()
        if path:
            self.path_var.set(path)
            self.load_path(path)

    def refresh(self):
        path = self.path_var.get()
        if not path:
            messagebox.showinfo("Info", "Please select a directory first")
            return
        self.load_path(path)

    def set_status(self, text):
        self.status_var.set(text)
        self.update_idletasks()

    def load_path(self, path):
        # store root path for building full paths
        self.root_path = path

        # clear tree
        children = self.tree.get_children()
        if children:
            try:
                self.tree.delete(*children)
            except Exception:
                for i in children:
                    try:
                        self.tree.delete(i)
                    except Exception:
                        pass

        # List top-level entries in background to avoid blocking UI
        self.set_status("Listing top-level entries...")
        t = threading.Thread(target=self._list_top_level, args=(path,))
        t.daemon = True
        t.start()

    def _list_top_level(self, path):
        try:
            entries = []
            try:
                for name in sorted(os.listdir(path), key=lambda s: s.lower()):
                    full = os.path.join(path, name)
                    entries.append((name, full))
            except Exception as e:
                self.set_status(f"Error listing folder: {e}")
                return

            # prepare lightweight metadata then insert on main thread
            def insert_top():
                for name, full in entries:
                    rel = name
                    if os.path.isdir(full):
                        # directory: add node and a dummy child so it's expandable
                        try:
                            self.tree.insert('', 'end', rel, text=name, values=('Directory', '', ''))
                            # dummy child
                            dummy_id = rel + '__dummy'
                            self.tree.insert(rel, 'end', dummy_id, text='')
                        except Exception:
                            pass
                    else:
                        try:
                            size = os.path.getsize(full)
                            mtime = os.path.getmtime(full)
                            mstr = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                            size_str = f"{size:,} bytes"
                        except Exception:
                            mstr = ''
                            size_str = ''
                        try:
                            self.tree.insert('', 'end', rel, text=name, values=('File', size_str, mstr))
                        except Exception:
                            pass
                self.set_status(f"Listed {len(entries)} top-level items")

            self.after(0, insert_top)
        except Exception as e:
            self.set_status(f"Error: {e}")

    def on_open(self, event):
        # lazy-load children when a node is expanded
        item = self.tree.focus()
        if not item:
            return
        # if the first child is a dummy marker, populate
        children = self.tree.get_children(item)
        if children and any(c.endswith('__dummy') for c in children):
            # remove dummy(s)
            for c in children:
                if c.endswith('__dummy'):
                    try:
                        self.tree.delete(c)
                    except Exception:
                        pass
            # build full path for this item
            rel = item
            full = os.path.join(self.root_path, rel)
            # populate this node in a background thread
            t = threading.Thread(target=self._populate_node, args=(item, full))
            t.daemon = True
            t.start()

    def _populate_node(self, node_id, full_path):
        try:
            entries = []
            try:
                names = sorted(os.listdir(full_path), key=lambda s: s.lower())
            except Exception:
                names = []
            for name in names:
                child_full = os.path.join(full_path, name)
                entries.append((name, child_full))

            def insert_children():
                for name, child_full in entries:
                    # child node id is relative path from root
                    # compute rel by joining node_id and name
                    if node_id:
                        child_rel = os.path.join(node_id, name)
                    else:
                        child_rel = name

                    if os.path.isdir(child_full):
                        try:
                            if not self.tree.exists(child_rel):
                                self.tree.insert(node_id, 'end', child_rel, text=name, values=('Directory', '', ''))
                                # add dummy child
                                self.tree.insert(child_rel, 'end', child_rel + '__dummy', text='')
                        except Exception:
                            pass
                    else:
                        try:
                            size = os.path.getsize(child_full)
                            mtime = os.path.getmtime(child_full)
                            mstr = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                            size_str = f"{size:,} bytes"
                        except Exception:
                            mstr = ''
                            size_str = ''
                        try:
                            if not self.tree.exists(child_rel):
                                self.tree.insert(node_id, 'end', child_rel, text=name, values=('File', size_str, mstr))
                        except Exception:
                            pass

            self.after(0, insert_children)
        except Exception as e:
            # update status with error
            self.set_status(f"Error populating node: {e}")

    def _id_exists(self, iid):
        try:
            # rely on Treeview's exists which is accurate for any iid
            return bool(self.tree.exists(iid))
        except Exception:
            return False

    def _insert_node(self, nid, text, typ, size, modified):
        # run in main thread
        def cb():
            # if parent is nested path, determine its parent id
            parent = ''
            if os.sep in nid:
                parent = os.path.dirname(nid)
            # if parent is '.', treat as root
            if parent == '.':
                parent = ''
            # ensure parent chain exists (create parents synchronously so child inserts won't fail)
            def ensure_parent(p):
                if not p or self.tree.exists(p):
                    return
                # determine parent's parent
                pp = os.path.dirname(p) if os.sep in p else ''
                if pp == '.':
                    pp = ''
                ensure_parent(pp)
                # insert this parent if still missing
                if not self.tree.exists(p):
                    try:
                        self.tree.insert(pp, 'end', p, text=os.path.basename(p), values=('Directory', '', ''))
                    except Exception:
                        # if insert fails, ignore and continue; child insert may still fail and be reported
                        pass

            ensure_parent(parent)
            # avoid duplicates
            if self.tree.exists(nid):
                return
            try:
                self.tree.insert(parent, 'end', nid, text=text, values=(typ, size, modified))
            except Exception:
                # insertion failed (parent may not exist); attempt to create parent then retry once
                ensure_parent(parent)
                try:
                    if not self.tree.exists(nid):
                        self.tree.insert(parent, 'end', nid, text=text, values=(typ, size, modified))
                except Exception:
                    pass
        try:
            self.after(0, cb)
        except Exception:
            pass

    def on_double(self, event):
        item = self.tree.focus()
        if not item:
            return
        typ = self.tree.set(item, 'type')
        # build full path
        root_path = self.path_var.get()
        rel = item
        full = os.path.join(root_path, rel)
        if typ == 'File':
            try:
                if sys.platform.startswith('win'):
                    os.startfile(full)
                else:
                    # attempt generic opener
                    import subprocess
                    subprocess.Popen(['xdg-open', full])
            except Exception as e:
                messagebox.showerror('Open file', f'Could not open file: {e}')


def main():
    app = FileListerApp()
    app.mainloop()


if __name__ == '__main__':
    main()
