#!/bin/bash
# Post-build script for Linux to separate PySide6 for GPL compliance
# Adapted for GitHub Actions

set -e  # Arrête le script en cas d'erreur

DIST_DIR="dist-linux/fdr"
PYSIDE_DIR="$DIST_DIR/pyside6"

# Create pyside6 directory structure
mkdir -p "$PYSIDE_DIR/lib"
mkdir -p "$PYSIDE_DIR/Qt/lib"
mkdir -p "$PYSIDE_DIR/plugins"

echo "Separating PySide6 libraries..."

# First, copy PySide6 and shiboken6 directories to pyside6
if [ -d "$DIST_DIR/_internal/PySide6" ]; then
    echo "Copying PySide6 to pyside6..."
    cp -r "$DIST_DIR/_internal/PySide6" "$PYSIDE_DIR/" || echo "  Warning: Failed to copy PySide6"
fi

if [ -d "$DIST_DIR/_internal/shiboken6" ]; then
    echo "Copying shiboken6 to pyside6..."
    cp -r "$DIST_DIR/_internal/shiboken6" "$PYSIDE_DIR/" || echo "  Warning: Failed to copy shiboken6"
fi

# Copy Qt6 and shiboken6 libraries to pyside6/lib (use cp, not mv!)
if [ -d "$DIST_DIR/_internal" ]; then
    find "$DIST_DIR/_internal" -type f \( -name "*Qt6*.so*" -o -name "*shiboken*.so*" \) | while read -r file; do
        echo "  Copying $(basename "$file") to pyside6/lib..."
        cp "$file" "$PYSIDE_DIR/lib/" || echo "  Warning: Failed to copy $file"
    done
fi

# Copy any remaining .so files from PySide6 directory
if [ -d "$DIST_DIR/_internal/PySide6" ]; then
    find "$DIST_DIR/_internal/PySide6" -type f -name "*.so*" | while read -r file; do
        echo "  Copying $(basename "$file") to pyside6/lib..."
        cp "$file" "$PYSIDE_DIR/lib/" || echo "  Warning: Failed to copy $file"
    done
fi

# Copy any remaining .so files from shiboken6 directory
if [ -d "$DIST_DIR/_internal/shiboken6" ]; then
    find "$DIST_DIR/_internal/shiboken6" -type f -name "*.so*" | while read -r file; do
        echo "  Copying $(basename "$file") to pyside6/lib..."
        cp "$file" "$PYSIDE_DIR/lib/" || echo "  Warning: Failed to copy $file"
    done
fi

# Copy Qt libraries
if [ -d "$DIST_DIR/_internal/PySide6/Qt/lib" ]; then
    echo "Copying Qt libraries to pyside6/Qt/lib..."
    cp -r "$DIST_DIR/_internal/PySide6/Qt/lib/." "$PYSIDE_DIR/Qt/lib/" || echo "  Warning: Failed to copy Qt libraries"
fi

# Copy Qt plugins
if [ -d "$DIST_DIR/_internal/PySide6/Qt/plugins" ]; then
    echo "Copying Qt plugins to pyside6/plugins..."
    cp -r "$DIST_DIR/_internal/PySide6/Qt/plugins/." "$PYSIDE_DIR/plugins/" || echo "  Warning: Failed to copy Qt plugins"
fi

# Backup original executable
if [ -f "$DIST_DIR/fdr" ]; then
    echo "Backing up original executable..."
    mv "$DIST_DIR/fdr" "$DIST_DIR/fdr_bin" || echo "  Warning: Failed to backup executable"
fi

# Create launcher script
cat > "$DIST_DIR/fdr" << 'EOF'
#!/bin/bash
SCRIPT_DIR=$(dirname "$0")
PYSIDE_DIR="$SCRIPT_DIR/pyside6"

# Add PySide6 libraries to LD_LIBRARY_PATH
export LD_LIBRARY_PATH="$PYSIDE_DIR/lib:$PYSIDE_DIR/Qt/lib:$LD_LIBRARY_PATH"

# Add PySide6 to Python path
export PYTHONPATH="$PYSIDE_DIR/PySide6:$PYSIDE_DIR/shiboken6:$PYTHONPATH"

# Add PySide6 to Qt plugin path
export QT_PLUGIN_PATH="$PYSIDE_DIR/plugins:$QT_PLUGIN_PATH"

# Execute the actual binary
exec "$SCRIPT_DIR/fdr_bin" "$@"
EOF

# Make the launcher script executable
chmod +x "$DIST_DIR/fdr"

echo ""
echo "Post-build processing complete!"
echo "================================"