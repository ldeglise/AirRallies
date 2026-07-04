#!/bin/bash
# Post-build script for Linux to separate PySide6 for GPL compliance
# This script reorganizes the PyInstaller output to separate PySide6 libraries
# Strategy: Keep Python packages in _internal/ but move .so files to pyside6/lib/

set -e

DIST_DIR="/home/laurent/AirRallies/fdr/dist-linux/fdr"
PYSIDE_DIR="${DIST_DIR}/pyside6"

# Create pyside6 directory structure
mkdir -p "${PYSIDE_DIR}/lib"
mkdir -p "${PYSIDE_DIR}/Qt/lib"
mkdir -p "${PYSIDE_DIR}/plugins"

echo "Separating PySide6 libraries..."

# Move Qt6 .so files from _internal root to pyside6/lib/
for lib in $(find "${DIST_DIR}/_internal" -maxdepth 1 -name "libQt6*.so*"); do
    if [ -f "$lib" ]; then
        echo "  Moving $(basename $lib) to pyside6/lib/..."
        mv "$lib" "${PYSIDE_DIR}/lib/"
    fi
done

# Move shiboken6 .so files
for lib in $(find "${DIST_DIR}/_internal" -maxdepth 1 -name "libshiboken*.so*"); do
    if [ -f "$lib" ]; then
        echo "  Moving $(basename $lib) to pyside6/lib/..."
        mv "$lib" "${PYSIDE_DIR}/lib/"
    fi
done

# Move Qt6 libraries from PySide6/Qt/lib to pyside6/Qt/lib
if [ -d "${DIST_DIR}/_internal/PySide6/Qt/lib" ]; then
    echo "  Moving Qt libraries from PySide6/Qt/lib to pyside6/Qt/lib..."
    cp -r "${DIST_DIR}/_internal/PySide6/Qt/lib"/* "${PYSIDE_DIR}/Qt/lib/" 2>/dev/null || true
fi

# Move Qt plugins
if [ -d "${DIST_DIR}/_internal/PySide6/Qt/plugins" ]; then
    echo "  Moving Qt plugins to pyside6/plugins..."
    cp -r "${DIST_DIR}/_internal/PySide6/Qt/plugins"/* "${PYSIDE_DIR}/plugins/" 2>/dev/null || true
fi

# Create symlinks for PySide6 and shiboken6 in pyside6 for clarity
# (The actual Python packages stay in _internal/ for PyInstaller to find them)
if [ -d "${DIST_DIR}/_internal/PySide6" ]; then
    echo "  Creating symlink to PySide6 in pyside6..."
    ln -sf "${DIST_DIR}/_internal/PySide6" "${PYSIDE_DIR}/PySide6"
fi

if [ -d "${DIST_DIR}/_internal/shiboken6" ]; then
    echo "  Creating symlink to shiboken6 in pyside6..."
    ln -sf "${DIST_DIR}/_internal/shiboken6" "${PYSIDE_DIR}/shiboken6"
fi

# Backup original executable
if [ -f "${DIST_DIR}/fdr" ] && [ ! -d "${DIST_DIR}/fdr" ]; then
    echo "  Backing up original executable..."
    mv "${DIST_DIR}/fdr" "${DIST_DIR}/fdr.bin"
fi

# Create launcher script
cat > "${DIST_DIR}/fdr" << 'EOF'
#!/bin/bash
# Flight Data Recorder Launcher
# Configures environment for PySide6 GPL compliance

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYSIDE_DIR="${SCRIPT_DIR}/pyside6"

# Add pyside6 libraries to LD_LIBRARY_PATH
export LD_LIBRARY_PATH="${PYSIDE_DIR}/lib:${PYSIDE_DIR}/Qt/lib:${LD_LIBRARY_PATH}"

# Add pyside6 to Qt plugin path
export QT_PLUGIN_PATH="${PYSIDE_DIR}/plugins:${QT_PLUGIN_PATH}"

# Execute the actual binary
exec "${SCRIPT_DIR}/fdr.bin" "$@"
EOF

chmod +x "${DIST_DIR}/fdr"

echo ""
echo "Post-build processing complete!"
echo "================================"
echo "Structure:"
echo "  ${DIST_DIR}/"
echo "    ├── fdr          (launcher script)"
echo "    ├── fdr.bin      (actual executable)"
echo "    ├── _internal/   (other dependencies)"
echo "    └── pyside6/     (PySide6 libraries - GPL compliant)"
echo ""
echo "To run: ${DIST_DIR}/fdr"
