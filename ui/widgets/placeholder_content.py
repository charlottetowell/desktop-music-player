"""
Placeholder content widget for development
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.themes.colors import TEXT_MUTED


class PlaceholderContent(QWidget):
    """Placeholder widget for content areas under development."""
    
    def __init__(self, text: str = "Content coming soon...", parent: QWidget = None) -> None:
        super().__init__(parent)
        self._text = text
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Initialize placeholder UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 40, 20, 40)
        
        label = QLabel(self._text)
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Segoe UI", 11))
        label.setWordWrap(True)
        label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_MUTED};
                background: transparent;
            }}
        """)
        
        layout.addStretch()
        layout.addWidget(label)
        layout.addStretch()
        
        self.setStyleSheet("PlaceholderContent { background: transparent; }")
