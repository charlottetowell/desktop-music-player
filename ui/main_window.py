"""
Main application window with frameless design
"""

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QFont
from ui.themes.colors import BG_PANEL, TEXT_PRIMARY, BORDER_LIGHT


class CustomTitleBar(QWidget):
    """Custom title bar for frameless window."""
    
    def __init__(self, parent: QMainWindow) -> None:
        super().__init__(parent)
        self.parent_window = parent
        self._drag_pos = QPoint()
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Initialize title bar components."""
        self.setFixedHeight(40)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 10, 0)
        layout.setSpacing(0)
        
        # App title
        title = QLabel("Peachy Player")
        title.setFont(QFont("Segoe UI", 11, QFont.Medium))
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        
        # Window controls
        self.minimize_btn = QPushButton("−")
        self.maximize_btn = QPushButton("□")
        self.close_btn = QPushButton("×")
        
        for btn in [self.minimize_btn, self.maximize_btn, self.close_btn]:
            btn.setFixedSize(40, 40)
            btn.setFont(QFont("Segoe UI", 16))
            btn.setCursor(Qt.PointingHandCursor)
            
        self.minimize_btn.clicked.connect(self.parent_window.showMinimized)
        self.maximize_btn.clicked.connect(self._toggle_maximize)
        self.close_btn.clicked.connect(self.parent_window.close)
        
        # Styling
        button_style = f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_PRIMARY};
                border: none;
            }}
            QPushButton:hover {{
                background-color: rgba(0, 0, 0, 0.05);
            }}
        """
        close_style = button_style + """
            QPushButton:hover {
                background-color: #e57373;
                color: #ffffff;
            }
        """
        
        self.minimize_btn.setStyleSheet(button_style)
        self.maximize_btn.setStyleSheet(button_style)
        self.close_btn.setStyleSheet(close_style)
        
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.maximize_btn)
        layout.addWidget(self.close_btn)
        
        self.setStyleSheet(f"""
            CustomTitleBar {{
                background-color: {BG_PANEL};
                border-bottom: 1px solid {BORDER_LIGHT};
            }}
        """)
        
    def _toggle_maximize(self) -> None:
        """Toggle window maximize state."""
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
        else:
            self.parent_window.showMaximized()
            
    def mousePressEvent(self, event) -> None:
        """Handle mouse press for window dragging."""
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.parent_window.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event) -> None:
        """Handle mouse move for window dragging."""
        if event.buttons() == Qt.LeftButton and not self.parent_window.isMaximized():
            self.parent_window.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()


class MainWindow(QMainWindow):
    """Main application window with custom title bar."""
    
    def __init__(self) -> None:
        super().__init__()
        self._setup_window()
        self._setup_ui()
        
    def _setup_window(self) -> None:
        """Configure window properties."""
        self.setWindowTitle("Peachy Player")
        self.setMinimumSize(900, 600)
        self.resize(1200, 800)
        
        # Frameless window
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        
    def _setup_ui(self) -> None:
        """Initialize UI components."""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Custom title bar
        self.title_bar = CustomTitleBar(self)
        main_layout.addWidget(self.title_bar)
        
        # Content area with stacked widget for future screens
        self.content_stack = QStackedWidget()
        
        # Import and add home screen
        from ui.home_screen import HomeScreen
        self.home_screen = HomeScreen()
        self.content_stack.addWidget(self.home_screen)
        
        main_layout.addWidget(self.content_stack)
        
        # Main window styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {BG_PANEL};
            }}
            QWidget {{
                background-color: {BG_PANEL};
            }}
        """)
        
    def center_on_screen(self) -> None:
        """Center the main window on the primary display."""
        screen = self.screen().geometry()
        self.move(
            screen.center().x() - self.width() // 2,
            screen.center().y() - self.height() // 2
        )
