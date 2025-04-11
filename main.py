#!/usr/bin/env python3
import sys
import os

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from coterie.ui.main_window import MainWindow
from coterie.database.engine import init_db
from PyQt6.QtWidgets import QApplication

def main():
    """Main entry point for the Coterie application."""
    app = QApplication(sys.argv)
    init_db()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 