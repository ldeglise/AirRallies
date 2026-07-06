<#
.SYNOPSIS
    Regenerates GUI files from .ui files for the Flight Data Recorder application.
.DESCRIPTION
    This script uses PySide6-uic to convert .ui files to .py files,
    then fixes known issues with QDoubleSpinBox properties.

.NOTES
    Requires PySide6 to be installed (pyside6-uic command must be in PATH)
#>

param()

$scriptDir = $PSScriptRoot

Write-Host "Regenerating GUI files from .ui files..."

# Change to script directory
Set-Location -Path $scriptDir

# Regenerate gui_fdr.py from gui_fdr.ui
try {
    & pyside6-uic ui\gui_fdr.ui -o ui\gui_fdr.py
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to run pyside6-uic"
    }
    Write-Host "Successfully regenerated gui_fdr.py from gui_fdr.ui"
}
catch {
    Write-Error "Error regenerating GUI files: $_"
    Write-Error "Make sure PySide6 is installed and pyside6-uic is in your PATH"
    exit 1
}

# Fix QDoubleSpinBox properties
try {
    & python ($scriptDir + "\fix_spinbox.py")
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to fix QDoubleSpinBox properties"
    }
}
catch {
    Write-Error "Error fixing QDoubleSpinBox properties: $_"
    exit 1
}

Write-Host "GUI files regenerated successfully!"
