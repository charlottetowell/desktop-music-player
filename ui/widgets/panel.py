"""
Reusable panel widget component
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from ui.themes.colors import TEXT_PRIMARY, TEXT_SECONDARY
from ui.themes.fonts import FontManager


class Panel(QWidget):
    """Reusable panel widget with optional header."""
    
    def __init__(self, title: str = "", background_color: str = "#ffffff", show_mini_player: bool = False, parent: QWidget = None) -> None:
        super().__init__(parent)
        self._title = title
        self._background_color = background_color
        self._show_mini_player = show_mini_player
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Initialize panel UI."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Optional header with mini player button
        if self._title:
            header_container = QWidget()
            header_layout = QHBoxLayout(header_container)
            header_layout.setContentsMargins(24, 20, 24, 20)
            header_layout.setSpacing(0)
            
            self.header = QLabel(self._title)
            self.header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.header.setFont(FontManager.get_title_font(14))
            self.header.setStyleSheet(f"""
                QLabel {{
                    color: {TEXT_PRIMARY};
                    background-color: transparent;
                }}
            """)
            header_layout.addWidget(self.header)
            header_layout.addStretch()
            
            # Mini player button in header
            self.mini_player_btn = None
            if hasattr(self, '_show_mini_player') and self._show_mini_player:
                from PySide6.QtWidgets import QPushButton
                from PySide6.QtCore import Signal
                from ui.themes.colors import ACCENT_LAVENDER
                from utils.icon_manager import IconManager
                
                self.mini_player_btn = QPushButton()
                self.mini_player_btn.setIcon(IconManager.get_icon("miniplayer"))
                self.mini_player_btn.setCursor(Qt.PointingHandCursor)
                self.mini_player_btn.setFixedSize(36, 36)
                self.mini_player_btn.setIconSize(self.mini_player_btn.size() * 0.7)
                self.mini_player_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {TEXT_PRIMARY};
                        border: none;
                        border-radius: 6px;
                        padding: 0px;
                    }}
                    QPushButton:hover {{
                        background-color: rgba(255, 255, 255, 0.1);
                        color: {ACCENT_LAVENDER};
                    }}
                    QPushButton:pressed {{
                        background-color: rgba(255, 255, 255, 0.2);
                    }}
                """)
                self.mini_player_btn.setToolTip("Open Mini Player")
                header_layout.addWidget(self.mini_player_btn)
            
            header_container.setStyleSheet("QWidget { background: transparent; }")
            self.main_layout.addWidget(header_container)
        
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
