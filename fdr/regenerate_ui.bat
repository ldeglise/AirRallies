@echo off
REM Script Windows batch to regenerate GUI files from .ui files
REM Requires PySide6 to be installed (pyside6-uic command)

setlocal

cd /d "%~dp0"

echo Regenerating GUI files from .ui files...

REM Regenerate gui_fdr.py from gui_fdr.ui
pyside6-uic ui\gui_fdr.ui -o ui\gui_fdr.py

if errorlevel 1 (
    echo Error: Failed to regenerate GUI files
    echo Make sure PySide6 is installed and pyside6-uic is in your PATH
    pause
    exit /b 1
)

REM Fix QDoubleSpinBox properties (pyside6-uic has issues with decimal values)
python "%~dp0fix_spinbox.py"

if errorlevel 1 (
    echo Error: Failed to fix QDoubleSpinBox properties
    pause
    exit /b 1
)

echo GUI files regenerated successfully!
pause