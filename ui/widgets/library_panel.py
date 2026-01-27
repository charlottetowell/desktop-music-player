"""
Library panel widget with folder selection
"""

from typing import Optional
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QIcon
from ui.themes.colors import (TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, 
                               ACCENT_HOVER, BG_SIDEBAR, ACCENT_LAVENDER, 
                               BORDER_LIGHT)
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
        
        # LIBRARY header with folder icon/path inline
        header = self._create_header()
        layout.addWidget(header)
        
        # Status label (hidden by default)
        self.status_label = QLabel("")
        self.status_label.setFont(FontManager.get_small_font(9))
        self.status_label.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent; padding: 0 16px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.hide()
        layout.addWidget(self.status_label)
        
        # Track list widget (contains "By" toggles, search, and scrollable results)
        self.track_list = TrackListWidget()
        self.track_list.track_selected.connect(self.track_selected.emit)
        self.track_list.track_double_clicked.connect(self.track_double_clicked.emit)
        self.track_list.album_add_requested.connect(self.album_add_requested.emit)
        layout.addWidget(self.track_list, 1)
        
        self.setStyleSheet(f"LibraryPanel {{ background-color: {BG_SIDEBAR}; }}")
        
    def _create_header(self) -> QWidget:
        """Create LIBRARY header with inline folder icon and path."""
        header = QWidget()
        header.setAttribute(Qt.WA_StyledBackground, True)
        header.setStyleSheet("background: transparent;")
        
        layout = QVBoxLayout(header)
        layout.setContentsMargins(16, 24, 16, 12)
        layout.setSpacing(4)
        
        # Top row: LIBRARY title and folder icon
        top_row = QHBoxLayout()
        top_row.setSpacing(0)
        
        # LIBRARY title
        title = QLabel("LIBRARY")
        title.setFont(FontManager.get_title_font(18))
        title.setStyleSheet(f"""
            color: {TEXT_PRIMARY}; 
            background: transparent;
            font-weight: 700;
            letter-spacing: 2px;
        """)
        top_row.addWidget(title)
        top_row.addStretch()
        
        # Folder icon button (no background, just white icon)
        self.folder_btn = QPushButton()
        self.folder_btn.setFixedSize(40, 40)
        self.folder_btn.setCursor(Qt.PointingHandCursor)
        self.folder_btn.setToolTip("Select music folder")
        
        # Try to load folder icon
        folder_icon = load_icon("folder")
        if not folder_icon.isNull():
            self.folder_btn.setIcon(folder_icon)
            self.folder_btn.setIconSize(self.folder_btn.size() * 0.65)
        else:
            self.folder_btn.setText("📁")
            self.folder_btn.setFont(FontManager.get_display_font(20))
        
        self.folder_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {TEXT_PRIMARY};
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: rgba(183, 148, 246, 0.15);
                border-radius: 8px;
            }}
            QPushButton:pressed {{
                background-color: rgba(183, 148, 246, 0.25);
            }}
        """)
        
        self.folder_btn.clicked.connect(self._select_folder)
        top_row.addWidget(self.folder_btn)
        
        layout.addLayout(top_row)
        
        # Folder path display (right aligned, below folder icon)
        self.path_label = QLabel("No folder selected")
        self.path_label.setFont(FontManager.get_small_font(8))
        self.path_label.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        self.path_label.setWordWrap(True)
        self.path_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        layout.addWidget(self.path_label)
        
        return header
        
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
