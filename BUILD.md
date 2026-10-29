# 🛠 Building HadesEditor

How to generate the executable for both **Mac** and **Windows**.

---

### 1. Requirements
*   Python 3.13+
*   Dependencies:
    ```bash
    pip install pyqt5 construct luabins lz4 pyinstaller
    ```

### 2. Generating for Mac (.app)
Run this command from your terminal:
```bash
pyinstaller --onefile --windowed --name "HadesSaveEditor" --add-data "resources:resources" main.py
```
After the build, you will find `dist/HadesSaveEditor.app` (the complete app bundle) and `dist/HadesSaveEditor` (the single executable binary).

### 3. Generating for Windows (.exe)
Since **PyInstaller** builds for the system it's currently running on, you **must** run this command from a Windows PC or Virtual Machine:

```bash
pyinstaller --onefile --windowed --name "HadesSaveEditor" --add-data "resources;resources" main.py
```
This will result in `dist/HadesSaveEditor.exe`.

> [!NOTE]
> Since we use **PyQt5**, cross-compilation (e.g. building for Windows from a Mac) is not directly supported without complex setups (Wine/Docker). It is always safer to build the binary on the actual target OS.

---

### 📜 Folder Structure
-   `main.py`: The UI implementation (PyQt5).
-   `models/`: Save file logic (binary data parsing and compression).
-   `schemas/`: Binary layout definitions for Version 14/16.
-   `lua.json`: Reference file for internal lua keys.
-   `LICENSE`: Original fork and credit information.
-   `README.md`: General project description and features.
-   `BUILD.md`: Building instructions for Mac/Windows.
