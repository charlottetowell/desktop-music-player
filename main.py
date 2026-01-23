"""
Desktop Music Player - Main Entry Point
Cross-platform audio player with real-time visualization
"""

import sys
from PySide6.QtWidgets import QApplication


def main() -> int:
    """Initialize and run the application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Desktop Music Player")
    app.setOrganizationName("DesktopMusicPlayer")
    
    # TODO: Initialize main window
    # from ui.main_window import MainWindow
    # window = MainWindow()
    # window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
