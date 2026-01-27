"""
Reusable panel widget component
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from ui.themes.colors import TEXT_PRIMARY, TEXT_SECONDARY
from ui.themes.fonts import FontManager


class Panel(QWidget):
    """Reusable panel widget with optional header."""
    
    def __init__(self, title: str = "", background_color: str = "#ffffff", parent: QWidget = None) -> None:
        super().__init__(parent)
        self._title = title
        self._background_color = background_color
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Initialize panel UI."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Optional header
        if self._title:
            self.header = QLabel(self._title)
            self.header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.header.setFont(FontManager.get_title_font(14))
            self.header.setStyleSheet(f"""
                QLabel {{
                    color: {TEXT_PRIMARY};
                    padding: 20px 24px;
                    background-color: transparent;
                }}
            """)
            self.main_layout.addWidget(self.header)
        
        # Content area
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(24, 12, 24, 24)
        self.content_layout.setSpacing(12)
        self.main_layout.addLayout(self.content_layout)
        
        self.setStyleSheet(f"""
            Panel {{
                background-color: {self._background_color};
            }}
        """)
        
    def add_widget(self, widget: QWidget) -> None:
        """Add widget to panel content area."""
        self.content_layout.addWidget(widget)
        
    def add_layout(self, layout) -> None:
        """Add layout to panel content area."""
        self.content_layout.addLayout(layout)
        
    def add_stretch(self, stretch: int = 1) -> None:
        """Add stretch to panel content area."""
        self.content_layout.addStretch(stretch)
