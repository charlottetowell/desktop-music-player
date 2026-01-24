"""
Reusable section header component
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.themes.colors import TEXT_PRIMARY, TEXT_SECONDARY


class SectionHeader(QWidget):
    """Section header with title and optional subtitle."""
    
    def __init__(self, title: str, subtitle: str = "", parent: QWidget = None) -> None:
        super().__init__(parent)
        self._title = title
        self._subtitle = subtitle
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.subtitle_label = None
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Initialize header UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Title
        title_label = QLabel(self._title)
        title_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        title_label.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        
        layout.addWidget(title_label)
        
        # Optional subtitle
        if self._subtitle:
            self.subtitle_label = QLabel(self._subtitle)
            self.subtitle_label.setFont(QFont("Segoe UI", 10))
            self.subtitle_label.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
            layout.addWidget(self.subtitle_label)
        
        layout.addStretch()
        
        self.setStyleSheet("SectionHeader { background: transparent; }")
        
    def update_subtitle(self, subtitle: str) -> None:
        """Update the subtitle text."""
        self._subtitle = subtitle
        if self.subtitle_label:
            self.subtitle_label.setText(subtitle)
