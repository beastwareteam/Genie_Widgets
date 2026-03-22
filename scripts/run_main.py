#!/usr/bin/env python3
"""Main WidgetSystem application entry point."""

import sys

from PySide6.QtWidgets import QApplication

from widgetsystem.core.main import MainWindow


def main() -> int:
    """Run the main application.
    
    Returns:
        Exit code
    """
    app = QApplication(sys.argv)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
