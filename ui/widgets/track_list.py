"""
Track list widget with grouping controls
"""

from typing import List, Dict, Optional
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QScrollArea, QLabel, QFrame)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont
from ui.themes.colors import TEXT_PRIMARY, TEXT_SECONDARY, ACCENT_HOVER
from core.audio_scanner import AudioTrack


class GroupButton(QPushButton):
    """Custom button for group selection."""
    
    def __init__(self, text: str, parent: QWidget = None) -> None:
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(True)
        self.setFont(QFont("Segoe UI", 9, QFont.Medium))
        self.setFixedHeight(32)
        self._update_style()
        self.toggled.connect(self._update_style)
        
    def _update_style(self) -> None:
        """Update button style based on checked state."""
        if self.isChecked():
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba(0, 0, 0, 0.15);
                    color: {TEXT_PRIMARY};
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: rgba(0, 0, 0, 0.2);
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba(255, 255, 255, 0.3);
                    color: {TEXT_SECONDARY};
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                }}
                QPushButton:hover {{
                    background-color: {ACCENT_HOVER};
                    color: {TEXT_PRIMARY};
                }}
            """)


class TrackItemWidget(QFrame):
    """Widget representing a single track in the list."""
    
    track_clicked = Signal(AudioTrack)
    
    def __init__(self, track: AudioTrack, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.track = track
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Initialize track item UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(2)
        
        # Title
        title = QLabel(self.track.title)
        title.setFont(QFont("Segoe UI", 10))
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        title.setWordWrap(False)
        title.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        # Artist - Album info
        info = QLabel(f"{self.track.artist}")
        info.setFont(QFont("Segoe UI", 9))
        info.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        info.setWordWrap(False)
        
        layout.addWidget(title)
        layout.addWidget(info)
        
        self.setStyleSheet(f"""
            TrackItemWidget {{
                background-color: rgba(255, 255, 255, 0.15);
                border-radius: 4px;
            }}
            TrackItemWidget:hover {{
                background-color: {ACCENT_HOVER};
            }}
        """)
        self.setCursor(Qt.PointingHandCursor)
        
    def mousePressEvent(self, event) -> None:
        """Handle track click."""
        if event.button() == Qt.LeftButton:
            self.track_clicked.emit(self.track)
        super().mousePressEvent(event)


class GroupHeaderWidget(QFrame):
    """Header widget for track groups."""
    
    def __init__(self, group_name: str, track_count: int, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._setup_ui(group_name, track_count)
        
    def _setup_ui(self, group_name: str, track_count: int) -> None:
        """Initialize group header UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 8)
        
        # Group name
        name_label = QLabel(group_name)
        name_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        name_label.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        
        # Track count
        count_label = QLabel(f"{track_count} track{'s' if track_count != 1 else ''}")
        count_label.setFont(QFont("Segoe UI", 9))
        count_label.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        
        layout.addWidget(name_label)
        layout.addStretch()
        layout.addWidget(count_label)
        
        self.setStyleSheet("GroupHeaderWidget { background: transparent; }")


class TrackListWidget(QWidget):
    """
    Track list with grouping controls.
    Displays tracks grouped by Album, Artist, Year, or Folder.
    """
    
    track_selected = Signal(AudioTrack)
    
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.current_group_mode = "album"
        self.tracks: List[AudioTrack] = []
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Initialize track list UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Group buttons
        button_container = self._create_group_buttons()
        layout.addWidget(button_container)
        
        # Scrollable track list
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Content widget for tracks
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(12, 12, 12, 12)
        self.content_layout.setSpacing(4)
        self.content_layout.addStretch()
        
        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area, 1)
        
        # Styling
        self.setStyleSheet("TrackListWidget { background: transparent; }")
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: rgba(0, 0, 0, 0.05);
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0, 0, 0, 0.2);
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(0, 0, 0, 0.3);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
    def _create_group_buttons(self) -> QWidget:
        """Create group selection buttons."""
        container = QWidget()
        container.setAttribute(Qt.WA_StyledBackground, True)
        container.setStyleSheet("background: transparent;")
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(12, 12, 12, 8)
        layout.setSpacing(6)
        
        # Create buttons
        self.album_btn = GroupButton("Album")
        self.artist_btn = GroupButton("Artist")
        self.year_btn = GroupButton("Year")
        self.folder_btn = GroupButton("Folder")
        
        # Set default
        self.album_btn.setChecked(True)
        
        # Connect signals
        self.album_btn.clicked.connect(lambda: self._change_group_mode("album"))
        self.artist_btn.clicked.connect(lambda: self._change_group_mode("artist"))
        self.year_btn.clicked.connect(lambda: self._change_group_mode("year"))
        self.folder_btn.clicked.connect(lambda: self._change_group_mode("folder"))
        
        layout.addWidget(self.album_btn)
        layout.addWidget(self.artist_btn)
        layout.addWidget(self.year_btn)
        layout.addWidget(self.folder_btn)
        layout.addStretch()
        
        return container
        
    def _change_group_mode(self, mode: str) -> None:
        """Change the grouping mode."""
        if mode == self.current_group_mode:
            return
            
        self.current_group_mode = mode
        
        # Update button states
        self.album_btn.setChecked(mode == "album")
        self.artist_btn.setChecked(mode == "artist")
        self.year_btn.setChecked(mode == "year")
        self.folder_btn.setChecked(mode == "folder")
        
        # Refresh display
        self._refresh_display()
        
    def set_tracks(self, tracks: List[AudioTrack]) -> None:
        """Set tracks and refresh display."""
        self.tracks = tracks
        self._refresh_display()
        
    def _refresh_display(self) -> None:
        """Refresh the track list display based on current group mode."""
        # Clear existing content
        while self.content_layout.count() > 1:  # Keep the stretch
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        if not self.tracks:
            self._show_empty_state()
            return
            
        # Group tracks
        from core.audio_scanner import AudioScanner
        scanner = AudioScanner()
        scanner.tracks = self.tracks
        
        if self.current_group_mode == "album":
            groups = scanner.group_by_album()
        elif self.current_group_mode == "artist":
            groups = scanner.group_by_artist()
        elif self.current_group_mode == "year":
            groups = scanner.group_by_year()
        else:  # folder
            groups = scanner.group_by_folder()
            
        # Display grouped tracks
        for group_name, group_tracks in groups.items():
            # Add group header
            header = GroupHeaderWidget(group_name, len(group_tracks))
            self.content_layout.insertWidget(self.content_layout.count() - 1, header)
            
            # Add tracks in group
            for track in group_tracks:
                track_widget = TrackItemWidget(track)
                track_widget.track_clicked.connect(self.track_selected.emit)
                self.content_layout.insertWidget(self.content_layout.count() - 1, track_widget)
                
    def _show_empty_state(self) -> None:
        """Show empty state message."""
        empty_label = QLabel("No tracks found\n\nSelect a music folder to get started")
        empty_label.setAlignment(Qt.AlignCenter)
        empty_label.setFont(QFont("Segoe UI", 10))
        empty_label.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent; padding: 40px;")
        empty_label.setWordWrap(True)
        self.content_layout.insertWidget(0, empty_label)
