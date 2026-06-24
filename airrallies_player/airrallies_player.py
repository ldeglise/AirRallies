#!/usr/bin/env python3
"""Main entry point for Air Rallies Player application."""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from ui.gui_airrallies_player import Ui_MainWindow


def main():
    """Launch the Air Rallies Player GUI."""
    app = QApplication(sys.argv)
    window = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(window)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
