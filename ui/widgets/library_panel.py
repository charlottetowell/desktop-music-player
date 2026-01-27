"""
Library panel widget with folder selection
"""

from typing import Optional
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QIcon
from ui.themes.colors import TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, ACCENT_HOVER
from ui.themes.fonts import FontManager
from ui.widgets import PlaceholderContent
from ui.widgets.track_list import TrackListWidget
from core.settings import Settings
from core.audio_scanner import AudioScanner, AudioTrack
from utils import load_icon


class ScannerThread(QThread):
    """Background thread for scanning audio files."""
    
    scan_complete = Signal(list)  # Emits list of AudioTrack
    
    def __init__(self, folder_path: str, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.folder_path = folder_path
        
    def run(self) -> None:
        """Scan directory for audio files."""
        scanner = AudioScanner()
        tracks = scanner.scan_directory(self.folder_path)
        self.scan_complete.emit(tracks)


class LibraryPanel(QWidget):
    """Library panel with folder selection and path display."""
    
    folder_changed = Signal(str)
    track_selected = Signal(AudioTrack)
    track_double_clicked = Signal(AudioTrack)
    album_add_requested = Signal(list)  # Emits list of AudioTrack
    
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.settings = Settings()
        self.scanner_thread: Optional[ScannerThread] = None
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
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setFont(FontManager.get_small_font(9))
        self.status_label.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent; padding: 0 24px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.hide()
        layout.addWidget(self.status_label)
        
        # Track list widget
        self.track_list = TrackListWidget()
        self.track_list.track_selected.connect(self.track_selected.emit)
        self.track_list.track_double_clicked.connect(self.track_double_clicked.emit)
        self.track_list.album_add_requested.connect(self.album_add_requested.emit)
        layout.addWidget(self.track_list, 1)
        
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
        title.setFont(FontManager.get_title_font(14))
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        title_row.addWidget(title)
        
        title_row.addStretch()
        
        layout.addLayout(title_row)
        
        # Folder path display
        self.path_label = QLabel("No folder selected")
        self.path_label.setFont(FontManager.get_small_font(9))
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
            self.folder_btn.setFont(FontManager.get_display_font(20))
        
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
        self._scan_folder(path)
        
    def _load_saved_folder(self) -> None:
        """Load previously saved folder path."""
        saved_path = self.settings.get_music_folder()
        if saved_path:
            self._update_path_display(saved_path)
            self._scan_folder(saved_path)
            
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
        
    def _scan_folder(self, path: str) -> None:
        """Scan folder for audio files in background thread."""
        if self.scanner_thread and self.scanner_thread.isRunning():
            self.scanner_thread.quit()
            self.scanner_thread.wait()
            
        self.status_label.setText("Scanning for audio files...")
        self.status_label.show()
        
        self.scanner_thread = ScannerThread(path)
        self.scanner_thread.scan_complete.connect(self._on_scan_complete)
        self.scanner_thread.start()
        
    def _on_scan_complete(self, tracks: list) -> None:
        """Handle scan completion."""
        self.status_label.hide()
        self.track_list.set_tracks(tracks)
        
        if tracks:
            print(f"Found {len(tracks)} audio files")
        else:
            print("No audio files found in selected folder")
        
    def get_music_folder(self) -> Optional[str]:
        """Get the currently selected music folder."""
        return self.settings.get_music_folder()
