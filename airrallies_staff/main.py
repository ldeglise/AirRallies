#!/usr/bin/env python3
"""Main entry point for Air Rallies Staff application."""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from ui.gui_airrallies_staff import Ui_MainWindow


def main():
    """Launch the Air Rallies Staff GUI."""
    app = QApplication(sys.argv)
    window = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(window)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
