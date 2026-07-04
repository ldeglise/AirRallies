#!/bin/bash
# Script to regenerate GUI files from .ui files

# Regenerate gui_fdr.py from gui_fdr.ui
pyside6-uic ui/gui_fdr.ui -o ui/gui_fdr.py

# Fix QDoubleSpinBox properties (pyside6-uic has issues with decimal values)
python3 << 'EOF'
with open('ui/gui_fdr.py', 'r') as f:
    content = f.read()

# Fix QDoubleSpinBox properties for spinBoxPollInterval
content = content.replace(
    '''self.spinBoxPollInterval.setDecimals(1)
        self.spinBoxPollInterval.setMinimum(0)
        self.spinBoxPollInterval.setMaximum(0)
        self.spinBoxPollInterval.setSingleStep(0)
        self.spinBoxPollInterval.setValue(0)''',
    '''self.spinBoxPollInterval.setDecimals(1)
        self.spinBoxPollInterval.setMinimum(0.1)
        self.spinBoxPollInterval.setMaximum(10.0)
        self.spinBoxPollInterval.setSingleStep(0.1)
        self.spinBoxPollInterval.setValue(1.0)'''
)

with open('ui/gui_fdr.py', 'w') as f:
    f.write(content)

print("GUI files regenerated successfully!")
EOF

echo "GUI regeneration complete."
