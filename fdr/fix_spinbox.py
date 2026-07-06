#!/usr/bin/env python3
"""
Script to fix QDoubleSpinBox properties after pyside6-uic conversion.
PySide6-uic has issues with decimal values for QDoubleSpinBox, setting them to 0.
This script corrects the spinBoxPollInterval properties.
"""

import os
import sys

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
gui_py_path = os.path.join(script_dir, 'ui', 'gui_fdr.py')

print(f"Fixing QDoubleSpinBox properties in {gui_py_path}")

try:
    with open(gui_py_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix QDoubleSpinBox properties for spinBoxPollInterval
    # pyside6-uic sometimes converts decimal values to 0
    old_spinbox = '''self.spinBoxPollInterval.setDecimals(1)
        self.spinBoxPollInterval.setMinimum(0)
        self.spinBoxPollInterval.setMaximum(0)
        self.spinBoxPollInterval.setSingleStep(0)
        self.spinBoxPollInterval.setValue(0)'''
    
    new_spinbox = '''self.spinBoxPollInterval.setDecimals(1)
        self.spinBoxPollInterval.setMinimum(0.1)
        self.spinBoxPollInterval.setMaximum(10.0)
        self.spinBoxPollInterval.setSingleStep(0.1)
        self.spinBoxPollInterval.setValue(1.0)'''
    
    if old_spinbox in content:
        content = content.replace(old_spinbox, new_spinbox)
        print("Fixed spinBoxPollInterval properties")
    else:
        print("spinBoxPollInterval properties already correct or pattern not found")
    
    with open(gui_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("GUI files fixed successfully!")
    sys.exit(0)
    
except FileNotFoundError as e:
    print(f"Error: File not found - {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)