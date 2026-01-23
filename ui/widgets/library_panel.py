"""
Library panel widget with folder selection
"""

from typing import Optional
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon
from ui.themes.colors import TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, ACCENT_HOVER
from ui.widgets import PlaceholderContent
from core.settings import Settings
from utils import load_icon


class LibraryPanel(QWidget):
    """Library panel with folder selection and path display."""
    
    folder_changed = Signal(str)
    
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.settings = Settings()
        self._setup_ui()
        self._load_saved_folder()
        
    def _setup_ui(self) -> None:
        """Initialize panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header section with title and folder path
        header = self._create_header()
        layout.addWidget(header)
        
        # Folder selection button
        folder_section = self._create_folder_section()
        layout.addWidget(folder_section)
        
        # Content area (placeholder for now)
        self.content_widget = PlaceholderContent(
            "Your music library will appear here.\n\n"
            "• Playlists\n• Albums\n• Artists\n• Folders"
        )
        layout.addWidget(self.content_widget, 1)
        
        self.setStyleSheet("LibraryPanel { background-color: #fec5bb; }")
        
    def _create_header(self) -> QWidget:
        """Create header with title and folder path."""
        header = QWidget()
        header.setAttribute(Qt.WA_StyledBackground, True)
        header.setStyleSheet("background: transparent;")
        
        layout = QVBoxLayout(header)
        layout.setContentsMargins(24, 20, 24, 12)
        layout.setSpacing(8)
        
        # Title and path container
        title_row = QHBoxLayout()
        title_row.setSpacing(0)
        
        # Title
        title = QLabel("My Library")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        title_row.addWidget(title)
        
        title_row.addStretch()
        
        layout.addLayout(title_row)
        
        # Folder path display
        self.path_label = QLabel("No folder selected")
        self.path_label.setFont(QFont("Segoe UI", 9))
        self.path_label.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        self.path_label.setWordWrap(True)
        self.path_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        layout.addWidget(self.path_label)
        
        return header
        
    def _create_folder_section(self) -> QWidget:
        """Create folder selection button section."""
        section = QWidget()
        section.setAttribute(Qt.WA_StyledBackground, True)
        section.setStyleSheet("background: transparent;")
        
        layout = QHBoxLayout(section)
        layout.setContentsMargins(24, 8, 24, 20)
        
        # Folder icon button
        self.folder_btn = QPushButton()
        self.folder_btn.setFixedSize(48, 48)
        self.folder_btn.setCursor(Qt.PointingHandCursor)
        self.folder_btn.setToolTip("Select music folder")
        
        # Try to load folder icon
        folder_icon = load_icon("folder", category="media")
        if not folder_icon.isNull():
            self.folder_btn.setIcon(folder_icon)
            self.folder_btn.setIconSize(self.folder_btn.size() * 0.6)
        else:
            self.folder_btn.setText("📁")
            self.folder_btn.setFont(QFont("Segoe UI", 20))
        
        self.folder_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.3);
                border: 2px solid rgba(0, 0, 0, 0.1);
                border-radius: 24px;
            }}
            QPushButton:hover {{
                background-color: {ACCENT_HOVER};
                border-color: rgba(0, 0, 0, 0.15);
            }}
            QPushButton:pressed {{
                background-color: rgba(255, 255, 255, 0.5);
            }}
        """)
        
        self.folder_btn.clicked.connect(self._select_folder)
        
        layout.addWidget(self.folder_btn)
        layout.addStretch()
        
        return section
        
    def _select_folder(self) -> None:
        """Open folder selection dialog."""
        current_folder = self.settings.get_music_folder()
        start_dir = current_folder if current_folder else str(Path.home())
        
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Music Folder",
            start_dir,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if folder_path:
            self._set_folder(folder_path)
            
    def _set_folder(self, path: str) -> None:
        """Set the music folder and update UI."""
        self.settings.set_music_folder(path)
        self._update_path_display(path)
        self.folder_changed.emit(path)
        
    def _load_saved_folder(self) -> None:
        """Load previously saved folder path."""
        saved_path = self.settings.get_music_folder()
        if saved_path:
            self._update_path_display(saved_path)
            
    def _update_path_display(self, path: str) -> None:
        """Update the path label with shortened path."""
        path_obj = Path(path)
        
        # Shorten path if too long
        try:
            # Try to make path relative to home for display
            home = Path.home()
            if path_obj.is_relative_to(home):
                display_path = "~/" + str(path_obj.relative_to(home))
            else:
                display_path = str(path_obj)
        except (ValueError, AttributeError):
            display_path = str(path_obj)
        
        # Truncate if still too long
        if len(display_path) > 40:
            display_path = "..." + display_path[-37:]
            
        self.path_label.setText(display_path)
        self.path_label.setToolTip(path)
        
    def get_music_folder(self) -> Optional[str]:
        """Get the currently selected music folder."""
        return self.settings.get_music_folder()
