# File Lister (Windows)

Simple cross-platform (Tkinter) GUI that lists all files and directories in a selected folder.

Features:

- Browse for a folder
- Recursive listing (tree) with columns: Type, Size, Modified
- Double-click files to open them (Windows: uses startfile)

Requirements

- Python 3.8+
- Tkinter (usually included with Python on Windows)

Quick start (PowerShell):

```powershell
python .\run.py
```

## Project Structure Overview

```
file_lister_app/
├── src/                        # **Source Code Root:** Contains all Python application logic.
│   ├── core/                   # **Backend Logic:** Modules for data access and heavy computation, independent of the GUI.
│   │   ├── __init__.py         # Initializes 'core' as a Python sub-package.
│   │   ├── file_ops.py         # **Core File Operations:** Functions for listing directories, retrieving file stats (size, date), and size formatting.
│   │   └── search_ops.py       # **Search Logic:** Functions dedicated to opening files and searching their content for a specific term (the future feature).
│   ├── views/                  # **Frontend Views:** Modules containing the UI and event handlers for each feature, inheriting from tk.Frame.
│   │   ├── __init__.py         # Initializes 'views' as a Python sub-package.
│   │   ├── listing_view.py     # **Listing View:** The Tkinter Frame class containing the directory entry, 'Browse' button, 'Refresh' button, and the Treeview for file display.
│   │   └── search_view.py      # **Search View:** The Tkinter Frame class containing the search term input, 'Search' button, and the results display list for file content searching.
│   ├── main_layout.py          # **Main Layout/Container:** The primary Tkinter window (inherits from tk.Tk). Sets up the overall app structure, navigation bar, and handles switching between the different 'views'.
│   └── main.py                 # **Application Entry Point:** The file executed to start the application. Simply imports and runs the MainLayout class.
├── assets/                     # **Static Resources:** Contains non-code assets used by the application.
│   └── icons/                  # Holds application icons and small images used in the GUI.
│       └── app_icon.ico        # (Example) The application's main icon file.
├── tests/                      # **Testing Suite:** Directory for all unit and integration tests.
│   ├── __init__.py             # Initializes 'tests' as a Python sub-package.
│   ├── test_file_ops.py        # Unit tests ensuring file_ops functions (like listing and formatting) work correctly.
│   └── test_search_ops.py      # Unit tests for the search_ops functions (testing text matching and file reading).
├── requirements.txt            # **Dependencies:** Lists all required external Python packages (e.g., `pip install -r requirements.txt`).
├── README.md                   # **Project Documentation:** Provides a general overview, installation instructions, and usage guide for the application.
└── .gitignore                  # **Git Exclusion List:** Specifies files and folders that Git should ignore (e.g., virtual environments, compiled files, OS files).
```

Notes and next steps:

- For very large directories this app loads entries in the background but still inserts into the Treeview on the main thread; consider adding paging or lazy loading.
  -- To build an EXE, use PyInstaller: `pip install pyinstaller; pyinstaller --onefile run.py`.

## Automated releases

This repository includes a GitHub Actions workflow at `.github/workflows/build-release.yml` which runs on every push to `main`. It will:

- Compute the next version tag automatically from existing `vMAJOR.MINOR` tags (for example, if the latest tag is `v1.0` it will create `v1.1`). If no tags exist it starts from `v1.0`.
- Build a single-file EXE using PyInstaller on Windows.
- Create a GitHub Release with the new tag and upload the built EXE as a release asset.

Notes:

- The workflow uses the repository's `GITHUB_TOKEN` to create releases and upload assets. No extra secrets are required for the basic flow.
- If you want custom versioning, or to trigger releases manually, consider changing the workflow to listen to tag creation events instead of push-to-main.
