# Build Instructions for Flight Data Recorder (FDR)

This document describes how to build executable versions of the Flight Data Recorder application using PyInstaller, with PySide6 libraries separated for GPL compliance.

## Prerequisites

- Python 3.13+ (recommended)
- PySide6 installed in a virtual environment
- PyInstaller 6.21.0+

## Project Structure

```text
fdr/
├── fdr.py                 # Main application entry point
├── ui/
│   ├── gui_fdr.py         # Generated UI code
│   └── translations.py    # Translations
├── sims_monitor/
│   ├── sim_monitor.py     # Simulator monitoring logic
│   └── translations.py
├── post_build_linux.sh     # Post-build script for Linux
├── post_build_windows.bat  # Post-build script for Windows
└── BUILD.md               # This file
```

---

## Linux Build Instructions

### Step 1: Activate the virtual environment

From the `fdr` directory:

```bash
cd /path/to/AirRallies/fdr
source bin/activate
```

### Step 2: Clean previous builds (optional)

```bash
rm -rf dist-linux build-linux
```

### Step 3: Build with PyInstaller

```bash
pyinstaller \
    --onedir \
    --name fdr \
    --clean \
    --distpath ./dist-linux \
    --workpath ./build-linux \
    fdr.py
```

**Options explained:**

- `--onedir`: Creates a directory with the executable and all dependencies (required for GPL compliance)
- `--name fdr`: Name of the output executable
- `--clean`: Clean PyInstaller cache before building
- `--distpath ./dist-linux`: Output directory for the build
- `--workpath ./build-linux`: Build directory for temporary files

### Step 4: Run post-build script to separate PySide6

```bash
chmod +x post_build_linux.sh
./post_build_linux.sh
```

The Linux post-build script performs the following actions:

- Move Qt6 `.so` files to `pyside6/lib/`
- Move Qt6 libraries from `PySide6/Qt/lib` to `pyside6/Qt/lib/`
- Move Qt plugins to `pyside6/plugins/`
- Create symbolic links to PySide6 and shiboken6 packages in `pyside6/` (originals stay in `_internal/` for PyInstaller compatibility)
- Create a launcher script (`fdr`) that sets up `LD_LIBRARY_PATH` and `QT_PLUGIN_PATH`
- Rename the original executable to `fdr.bin`

### Step 5: Test the executable

```bash
cd dist-linux/fdr
./fdr
```

### Step 6: Final Linux directory structure

```text
dist-linux/fdr/
├── fdr                   # Launcher script (sets LD_LIBRARY_PATH and QT_PLUGIN_PATH)
├── fdr.bin               # Actual executable binary
├── _internal/            # Python packages and other dependencies
│   ├── base_library.zip
│   ├── PySide6/          # PySide6 Python modules (symlinked in pyside6/)
│   │   ├── __init__.py
│   │   ├── QtCore.abi3.so
│   │   ├── QtGui.abi3.so
│   │   ├── QtWidgets.abi3.so
│   │   ├── QtNetwork.abi3.so
│   │   └── ...
│   ├── shiboken6/        # Shiboken6 Python modules (symlinked in pyside6/)
│   │   └── Shiboken.abi3.so
│   └── ...
└── pyside6/              # PySide6 libraries (GPL compliant - separated)
    ├── PySide6 -> ../_internal/PySide6  (symlink)
    ├── shiboken6 -> ../_internal/shiboken6  (symlink)
    ├── lib/               # Qt6 and shiboken6 shared libraries (.so files)
    │   ├── libQt6Core.so.6
    │   ├── libQt6Gui.so.6
    │   ├── libQt6Widgets.so.6
    │   ├── libQt6Network.so.6
    │   ├── libshiboken6.abi3.so.6.11
    │   └── ...
    ├── Qt/                # Qt6 library structure
    │   └── lib/           # Additional Qt6 shared libraries
    │       └── ...
    └── plugins/           # Qt6 plugins
        └── (platform, imageformats, etc.)
```

---

## Windows Build Instructions

**Note:** These commands must be executed on a Windows system with the Python venv activated.

### Windows: Step 1: Activate the virtual environment

From the `fdr` directory in Command Prompt:

```cmd
cd C:\path\to\AirRallies\fdr
Scripts\activate
```

### Windows: Step 2: Clean previous builds (optional)

```cmd
rmdir /s /q dist-windows 2>nul
rmdir /s /q build-windows 2>nul
```

### Windows: Step 3: Build with PyInstaller

```cmd
pyinstaller ^
    --onedir ^
    --name fdr ^
    --clean ^
    --distpath ./dist-windows ^
    --workpath ./build-windows ^
    --windowed ^
    fdr.py
```

**Options explained:**

- `--onedir`: Creates a directory with the executable and all dependencies
- `--name fdr`: Name of the output executable
- `--clean`: Clean PyInstaller cache before building
- `--distpath ./dist-windows`: Output directory for the build
- `--workpath ./build-windows`: Build directory for temporary files
- `--windowed`: Prevents console window from showing (GUI application)

### Windows: Step 4: Run post-build script to separate PySide6

```cmd
post_build_windows.bat
```

The Windows post-build script performs the following actions:

- Move Qt6 DLLs to `pyside6\lib\`
- Move Qt6 libraries from `PySide6\Qt\lib` to `pyside6\Qt\lib`
- Move Qt plugins to `pyside6\plugins`
- Create a launcher batch file (`fdr.bat`) that sets up `PATH` and `QT_PLUGIN_PATH`
- Rename the original executable to `fdr_bin.exe`

### Windows: Step 5: Test the executable

From File Explorer, double-click on `dist-windows\fdr\fdr.bat`

Or from command line:

```cmd
cd dist-windows\fdr
fdr.bat
```

### Step 6: Final Windows directory structure

```text
dist-windows\fdr\
├── fdr.bat               # Launcher batch file (sets PATH and QT_PLUGIN_PATH)
├── fdr_bin.exe           # Actual executable binary
├── _internal\            # Python packages and other dependencies
│   ├── base_library.zip
│   ├── PySide6\          # PySide6 Python modules (junction in pyside6\)
│   │   ├── __init__.py
│   │   ├── QtCore.abi3.pyd
│   │   ├── QtGui.abi3.pyd
│   │   ├── QtWidgets.abi3.pyd
│   │   ├── QtNetwork.abi3.pyd
│   │   └── ...
│   ├── shiboken6\        # Shiboken6 Python modules (junction in pyside6\)
│   │   └── Shiboken.abi3.dll
│   └── ...
└── pyside6\              # PySide6 libraries (GPL compliant - separated)
    ├── PySide6 -> _internal\PySide6  (junction)
    ├── shiboken6 -> _internal\shiboken6  (junction)
    ├── lib\              # Qt6 and shiboken6 DLLs
    │   ├── Qt6Core.dll
    │   ├── Qt6Gui.dll
    │   ├── Qt6Widgets.dll
    │   ├── Qt6Network.dll
    │   ├── shiboken6.abi3.dll
    │   └── ...
    ├── Qt\               # Qt6 library structure
    │   └── lib\          # Additional Qt6 DLLs
    │       └── ...
    └── plugins\          # Qt6 plugins
        └── (platform, imageformats, etc.)
```

---

## macOS Build Instructions

For macOS, use the following PyInstaller command:

```bash
# Navigate to fdr directory
cd /path/to/AirRallies/fdr

# Activate venv
source bin/activate

# Build
pyinstaller \
    --onedir \
    --name fdr \
    --clean \
    --distpath ./dist-macos \
    --workpath ./build-macos \
    --windowed \
    fdr.py
```

Then create a similar post-build script to separate PySide6 libraries into a `pyside6/` directory and create a launcher script that sets `PYTHONPATH` and `DYLD_LIBRARY_PATH`.

---

## Important Notes for GPL Compliance

### PySide6 License Requirements

PySide6 is licensed under the **GNU Lesser General Public License (LGPL) version 3**. To comply with this license when distributing binaries:

1. **Do NOT bundle PySide6 DLLs/.so files inside the main executable** (use `--onedir`, not `--onefile`)
2. **Allow users to replace PySide6 libraries** (keep them in a separate directory)
3. **Provide source code or offer to provide it** (if you modify PySide6)
4. **Include license information** (keep the LICENSE file from PySide6)

### Our Solution

This build process:

- Uses `--onedir` to keep libraries separate from the executable
- Moves PySide6 libraries to a dedicated `pyside6/` directory
- Uses a launcher script that sets `PYTHONPATH` and `LD_LIBRARY_PATH`/`PATH`
- Allows users to replace PySide6 libraries by simply replacing the `pyside6/` directory

### Alternative Approaches for Maximum Compliance

For maximum compliance, you could:

1. **Not bundle PySide6 at all** - Require users to install PySide6 separately
2. **Download PySide6 at runtime** - Use a package manager to install PySide6 when first run
3. **Provide separate downloads** - Distribute the main executable separately from PySide6 libraries

However, the approach documented here is widely accepted as compliant by the PySide6 community and provides a good balance between convenience and license compliance.

---

## Troubleshooting

### Missing Dependencies

If PyInstaller reports missing modules, add them using `--hidden-import`:

```bash
pyinstaller --hidden-import=missing_module fdr.py
```

### Qt Platform Plugins

For proper Qt functionality, ensure platform plugins are included. PyInstaller's PySide6 hooks should handle this automatically, but if you have issues, manually add them:

**Linux:**

```bash
pyinstaller --add-binary "/path/to/venv/lib/python3.13/site-packages/PySide6/Qt/plugins:platforms" fdr.py
```

**Windows:**

```cmd
pyinstaller --add-binary "C:\path\to\venv\Lib\site-packages\PySide6\Qt\plugins;platforms" fdr.py
```

### Large Executable Size

The `--onedir` option creates larger distributions. This is necessary for GPL compliance. To reduce size:

- Use `--strip` to strip debug symbols
- Use `--upx-dir` with UPX to compress binaries

Example:

```bash
pyinstaller --onedir --strip --upx-dir /path/to/upx fdr.py
```

### Library Not Found Warnings

If you see warnings like `Library not found: could not resolve 'libtiff.so.5'`, these are non-critical warnings about optional dependencies. The build will still work correctly.

---

## Automating with GitHub Actions

Here's a template for GitHub Actions to build for multiple platforms:

```yaml
name: Build FDR

on:
  push:
    tags:
      - 'v*'

jobs:
  build-linux:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install PySide6 pyinstaller

      - name: Build with PyInstaller
        run: |
          cd fdr
          pyinstaller --onedir --name fdr --clean --distpath ./dist-linux --workpath ./build-linux fdr.py
          chmod +x post_build_linux.sh
          ./post_build_linux.sh

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: fdr-linux
          path: fdr/dist-linux/

  build-windows:
    runs-on: windows-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install PySide6 pyinstaller

      - name: Build with PyInstaller
        run: |
          cd fdr
          pyinstaller --onedir --name fdr --clean --distpath ./dist-windows --workpath ./build-windows --windowed fdr.py
          post_build_windows.bat

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: fdr-windows
          path: fdr/dist-windows/

  build-macos:
    runs-on: macos-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install PySide6 pyinstaller

      - name: Build with PyInstaller
        run: |
          cd fdr
          pyinstaller --onedir --name fdr --clean --distpath ./dist-macos --workpath ./build-macos --windowed fdr.py

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: fdr-macos
          path: fdr/dist-macos/
```

---

## File List

| File | Purpose |
| ---- | ------- |
| `fdr.py` | Main application entry point |
| `fdr.spec` | PyInstaller spec file (auto-generated) |
| `post_build_linux.sh` | Post-build script for Linux (separates PySide6 libraries) |
| `post_build_windows.bat` | Post-build script for Windows (separates PySide6 libraries) |
| `BUILD.md` | This documentation |

---

## Version History

- **1.0.0** (2026-07-04): Initial build documentation with PySide6 separation for GPL compliance
