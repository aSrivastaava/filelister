# File Lister (Windows)

Simple cross-platform (Tkinter) GUI that lists all files and directories in a selected folder.

Features:

- Browse for a folder
- Recursive listing (tree) with columns: Type, Size, Modified
- Double-click files to open them (Windows: uses startfile)

Requirements

- Python 3.8+
- Tkinter (usually included with Python on Windows)

Project layout

```
e:/Projects/SearchInFile/
├─ src/
│  └─ filelister/
│     ├─ __init__.py
│     └─ main.py
├─ run.py
├─ README.md
└─ requirements.txt
```

Quick start (PowerShell):

```powershell
python .\run.py
```

Notes and next steps:

- For very large directories this app loads entries in the background but still inserts into the Treeview on the main thread; consider adding paging or lazy loading.
  -- To build an EXE, use PyInstaller: `pip install pyinstaller; pyinstaller --onefile run.py`.
