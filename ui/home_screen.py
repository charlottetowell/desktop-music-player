"""
Home screen widget - main 3-column interface
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.widgets import Panel, SectionHeader, PlaceholderContent
from ui.widgets.library_panel import LibraryPanel
from ui.widgets.queue_widget import QueueWidget
from core.queue_manager import QueueManager


class HomeScreen(QWidget):
    """Main 3-column layout: Library | Queue | Now Playing."""
    
    def __init__(self) -> None:
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.queue_manager = QueueManager()
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Initialize main 3-column layout."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left Column - My Library (25%) - #fec5bb
        self.library_panel = LibraryPanel()
        self.library_panel.folder_changed.connect(self._on_folder_changed)
        self.library_panel.track_selected.connect(self._on_track_selected)
        self.library_panel.track_double_clicked.connect(self._on_track_double_clicked)
        self.library_panel.album_add_requested.connect(self._on_album_add_requested)
        main_layout.addWidget(self.library_panel, 25)
        
        # Middle Column - Queue (50%) - #f8edeb
        self.queue_panel = self._create_queue_panel()
        main_layout.addWidget(self.queue_panel, 50)
        
        # Right Column - Currently Playing (25%) - #fec5bb
        self.playing_panel = self._create_playing_panel()
        main_layout.addWidget(self.playing_panel, 25)
        
    def _on_folder_changed(self, folder_path: str) -> None:
        """Handle music folder selection."""
        print(f"Music folder selected: {folder_path}")
        
    def _on_track_selected(self, track) -> None:
        """Handle track selection from library."""
        print(f"Track selected: {track.title} by {track.artist}")
        
    def _on_track_double_clicked(self, track) -> None:
        """Handle track double-click from library - add to queue and play."""
        print(f"Track double-clicked: {track.title} - adding to queue")
        self.queue_manager.add_track(track)
        # If this is the first track, set it as current
        if self.queue_manager.size() == 1:
            self.queue_manager.set_current_index(0)
            
    def _on_album_add_requested(self, tracks: list) -> None:
        """Handle album addition from library."""
        if tracks:
            print(f"Adding album with {len(tracks)} tracks to queue")
            self.queue_manager.add_tracks(tracks)
            # If this is the first content, set first track as current
            if self.queue_manager.size() == len(tracks):
                self.queue_manager.set_current_index(0)
        
    def _create_queue_panel(self) -> Panel:
        """Create middle panel for queue with app logo."""
        panel = Panel(background_color="#f8edeb")
        
        # App logo/name at top
        logo_widget = self._create_logo_header()
        panel.content_layout.setContentsMargins(0, 0, 0, 0)
        panel.main_layout.insertWidget(0, logo_widget)
        
        # Queue header
        self.queue_header = SectionHeader("Queue", "0 tracks")
        panel.content_layout.setContentsMargins(24, 12, 24, 0)
        panel.content_layout.addWidget(self.queue_header)
        
        # Queue widget
        self.queue_widget = QueueWidget(self.queue_manager)
        self.queue_widget.track_double_clicked.connect(self._on_queue_track_double_clicked)
        panel.content_layout.addWidget(self.queue_widget, 1)
        
        # Update header when queue changes
        self.queue_manager.queue_changed.connect(self._update_queue_header)
        
        return panel
        
    def _create_playing_panel(self) -> Panel:
        """Create right panel for currently playing track."""
        panel = Panel(title="Currently Playing", background_color="#fec5bb")
        
        # Placeholder content
        placeholder = PlaceholderContent(
            "Track information and controls will appear here.\n\n"
            "• Album artwork\n• Track details\n• Playback controls\n• Volume control"
        )
        panel.add_widget(placeholder)
        panel.add_stretch()
        
        return panel
        
    def _create_logo_header(self) -> QWidget:
        """Create Peachy Player logo header."""
        header = QWidget()
        header.setAttribute(Qt.WA_StyledBackground, True)
        header.setFixedHeight(80)
        
        layout = QVBoxLayout(header)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setAlignment(Qt.AlignCenter)
        
        # App name
        logo = QLabel("Peachy Player")
        logo.setAlignment(Qt.AlignCenter)
        logo.setFont(QFont("Segoe UI", 24, QFont.Bold))
        logo.setStyleSheet("""
            QLabel {
                color: #2b2b2b;
                background: transparent;
                letter-spacing: 1px;
            }
        """)
        
        layout.addWidget(logo)
        
        header.setStyleSheet("QWidget { background: transparent; }")
        
        return header
        
    def _update_queue_header(self) -> None:
        """Update queue header with track count."""
        count = self.queue_manager.size()
        self.queue_header.update_subtitle(f"{count} track{'s' if count != 1 else ''}")
        
    def _on_queue_track_double_clicked(self, index: int) -> None:
        """Handle double-click on queue track - play from that position."""
        print(f"Playing from queue index: {index}")
        self.queue_manager.set_current_index(index)
        # TODO: Start playback of selected track
