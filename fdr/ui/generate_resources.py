#!/usr/bin/env python3
"""
Script to generate icon resources for local development.

This script generates all icon formats from the source SVG and compiles the Qt resources.
It allows you to test your icons locally without going through the GitHub workflow.

Usage:
    python generate_resources.py

Requirements:
    - ImageMagick (convert command) for generating icons from SVG
    - pyside6-rcc, pyrcc6, or rcc for compiling Qt resources
"""

import os
import sys
import subprocess
from pathlib import Path


def check_command(cmd):
    """Check if a command is available."""
    try:
        subprocess.run(
            [cmd, "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            shell=False
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return False


def run_command(cmd, cwd=None):
    """Run a command and return True if successful."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running: {cmd}")
        if e.stderr:
            print(f"  {e.stderr.strip()}")
        return False


def generate_icons():
    """Generate all icon formats from the source SVG."""
    icons_dir = Path(__file__).parent / "icons"
    svg_file = icons_dir / "icon.svg"

    if not svg_file.exists():
        print(f"Error: Source SVG file not found: {svg_file}")
        return False

    print("\nGenerating icon files from SVG...")

    # Icon sizes to generate
    sizes = [16, 32, 64, 128, 256, 512]

    # Generate PNG files at different sizes
    for size in sizes:
        output_file = icons_dir / f"icon_{size}x{size}.png"
        cmd = f"convert -background none -density 300 \"{svg_file}\" -resize {size}x{size} \"{output_file}\""
        if not run_command(cmd):
            return False
        print(f"  Created: icon_{size}x{size}.png")

    # Copy 512x512 as default icon.png
    cmd = f"cp \"{icons_dir / 'icon_512x512.png'}\" \"{icons_dir / 'icon.png'}\""
    if not run_command(cmd, cwd=icons_dir):
        return False
    print("  Created: icon.png (512x512)")

    # Generate ICO for Windows (multi-size icon)
    print("\nGenerating Windows ICO file...")
    ico_sizes = [16, 32, 64, 128, 256]
    ico_files = " ".join([f"\"{icons_dir / f'icon_{s}x{s}.png'}\"" for s in ico_sizes])
    cmd = f"convert {ico_files} -colors 256 \"{icons_dir / 'icon.ico'}\""
    if not run_command(cmd, cwd=icons_dir):
        # Try without -colors option for compatibility
        cmd = f"convert {ico_files} \"{icons_dir / 'icon.ico'}\""
        if not run_command(cmd, cwd=icons_dir):
            print("  Warning: Could not generate ICO file")
            print("  ImageMagick may not support ICO format on this system")
        else:
            print("  Created: icon.ico")
    else:
        print("  Created: icon.ico")

    # Generate ICNS for macOS
    print("\nGenerating macOS ICNS file...")
    icns_sizes = [512, 256, 128, 64, 32, 16]
    icns_files = " ".join([f"\"{icons_dir / f'icon_{s}x{s}.png'}\"" for s in icns_sizes])
    cmd = f"convert {icns_files} \"{icons_dir / 'icon.icns'}\""
    if not run_command(cmd, cwd=icons_dir):
        print("  Warning: Could not generate ICNS file")
        print("  ImageMagick may not support ICNS format on this system")
    else:
        print("  Created: icon.icns")

    return True


def compile_resources():
    """Compile the Qt resources file."""
    ui_dir = Path(__file__).parent
    qrc_file = ui_dir / "resources.qrc"
    output_file = ui_dir / "resources_rc.py"

    if not qrc_file.exists():
        print(f"Error: Resources file not found: {qrc_file}")
        return False

    print("\nCompiling Qt resources...")

    # Try pyside6-rcc first (preferred for PySide6)
    if check_command("pyside6-rcc"):
        cmd = f"pyside6-rcc -o \"{output_file}\" \"{qrc_file}\""
        if run_command(cmd, cwd=ui_dir):
            print(f"  Created: resources_rc.py (using pyside6-rcc)")
            return True

    # Try pyrcc6 (PyQt6)
    if check_command("pyrcc6"):
        cmd = f"pyrcc6 -o \"{output_file}\" \"{qrc_file}\""
        if run_command(cmd, cwd=ui_dir):
            print(f"  Created: resources_rc.py (using pyrcc6)")
            return True

    # Try rcc (Qt tool)
    if check_command("rcc"):
        cmd = f"rcc -o \"{output_file}\" \"{qrc_file}\""
        if run_command(cmd, cwd=ui_dir):
            print(f"  Created: resources_rc.py (using rcc)")
            return True

    print("  Error: No Qt resource compiler found!")
    print("  Tried: pyside6-rcc, pyrcc6, rcc")
    print("  Install PySide6: pip install pyside6")
    return False


def main():
    """Main entry point."""
    print("=" * 70)
    print("Flight Data Recorder - Icon Resources Generator")
    print("=" * 70)

    script_dir = Path(__file__).parent

    # Check dependencies
    print("\n[1/3] Checking dependencies...")

    has_imagemagick = check_command("convert")
    has_rcc = (
        check_command("pyside6-rcc")
        or check_command("pyrcc6")
        or check_command("rcc")
    )

    if not has_imagemagick:
        print("  ERROR: ImageMagick (convert) is required but not found!")
        print()
        print("  Please install ImageMagick:")
        print("    Linux (Debian/Ubuntu): sudo apt-get install imagemagick")
        print("    macOS (Homebrew):      brew install imagemagick")
        print("    Windows:               Download from https://imagemagick.org")
        return 1

    print("  ImageMagick: OK")

    if not has_rcc:
        print("  WARNING: No Qt resource compiler found")
        print("  Resources will be generated but Qt integration may be limited")
    else:
        print("  Qt resource compiler: OK")

    # Generate icons
    print("\n[2/3] Generating icon files...")
    if not generate_icons():
        print("\n  ERROR: Failed to generate icon files")
        return 1

    # Compile resources
    print("\n[3/3] Compiling Qt resources...")
    resources_ok = compile_resources()

    # Summary
    print("\n" + "=" * 70)
    if not resources_ok:
        print("WARNING: Icon files generated, but Qt resources compilation failed")
        print("  Icon files are ready but resources_rc.py was not created")
        print("  Qt icons in the UI may not work until you install a resource compiler")
        return 0
    
    print("SUCCESS: All resources generated successfully!")
    print("=" * 70)
    print(f"\nGenerated files in {script_dir}:")
    print("  Icons:")
    print("    - icon.svg (source)")
    for size in [16, 32, 64, 128, 256, 512]:
        print(f"    - icon_{size}x{size}.png")
    print("    - icon.png (512x512, default)")
    print("    - icon.ico (Windows)")
    print("    - icon.icns (macOS)")
    print("  Qt Resources:")
    print("    - resources.qrc (source)")
    print("    - resources_rc.py (compiled - in .gitignore)")
    print("\nThese generated files are in .gitignore and will NOT be committed.")
    print("They will be automatically regenerated during the build process.")
    print("\nTo test locally, run:")
    print(f"  cd {script_dir.parent}")
    print("  python fdr.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
