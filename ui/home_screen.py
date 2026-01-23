"""
Home screen widget - placeholder for main interface
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class HomeScreen(QWidget):
    """Simple home screen placeholder."""
    
    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setSpacing(30)
        
        # Welcome message
        welcome = QLabel("Welcome to Desktop Music Player")
        welcome.setAlignment(Qt.AlignCenter)
        welcome_font = QFont("Segoe UI", 28, QFont.Bold)
        welcome.setFont(welcome_font)
        welcome.setStyleSheet("color: #ffffff;")
        
        # Subtitle
        subtitle = QLabel("Your audio library at your fingertips")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont("Segoe UI", 13)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("color: #b3b3b3;")
        
        # Placeholder button
        start_button = QPushButton("Get Started")
        start_button.setFixedSize(180, 50)
        start_button.setCursor(Qt.PointingHandCursor)
        start_button.setFont(QFont("Segoe UI", 12, QFont.Medium))
        start_button.setStyleSheet("""
            QPushButton {
                background-color: #1db954;
                color: #ffffff;
                border: none;
                border-radius: 25px;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: #1ed760;
            }
            QPushButton:pressed {
                background-color: #1aa34a;
            }
        """)
        
        # Status label
        status = QLabel("This is a placeholder home screen.\nUI components will be implemented here.")
        status.setAlignment(Qt.AlignCenter)
        status_font = QFont("Segoe UI", 10)
        status.setFont(status_font)
        status.setStyleSheet("color: #808080;")
        
        layout.addStretch(2)
        layout.addWidget(welcome)
        layout.addWidget(subtitle)
        layout.addSpacing(40)
        
        # Center the button
        button_layout = QVBoxLayout()
        button_layout.addWidget(start_button, alignment=Qt.AlignCenter)
        layout.addLayout(button_layout)
        
        layout.addSpacing(20)
        layout.addWidget(status)
        layout.addStretch(3)
