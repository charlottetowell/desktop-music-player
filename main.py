"""
Desktop Music Player - Main Entry Point
Cross-platform audio player with real-time visualization
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from ui.loading_screen import LoadingScreen
from ui.main_window import MainWindow


def main() -> int:
    """Initialize and run the application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Desktop Music Player")
    app.setOrganizationName("DesktopMusicPlayer")
    
    # Create main window (hidden initially)
    main_window = MainWindow()
    main_window.center_on_screen()
    
    # Create and show loading screen
    loading = LoadingScreen()
    loading.center_on_screen()
    loading.show()
    
    def on_loading_complete() -> None:
        """Transition from loading to main window."""
        loading.close()
        main_window.show()
    
    loading.loading_complete.connect(on_loading_complete)
    
    # Start loading after event loop begins
    QTimer.singleShot(100, loading.start_loading)
    
    return app.exec()


if __name__ == "__main__":
    print("Starting Desktop Music Player...")
    sys.exit(main())
