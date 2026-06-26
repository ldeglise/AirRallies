#!/usr/bin/env python3
"""Main entry point for Flight Data Recorder application."""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from ui.gui_fdr import Ui_MainWindow


def main():
    """Launch the Flight Data Recorder GUI."""
    app = QApplication(sys.argv)
    window = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(window)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()