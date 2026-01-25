"""
Home screen widget - main 3-column interface
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.widgets import Panel, SectionHeader, PlaceholderContent
from ui.widgets.library_panel import LibraryPanel
from ui.widgets.queue_widget import QueueWidget
from ui.widgets.now_playing_widget import NowPlayingWidget
from ui.widgets.playback_controls_widget import PlaybackControlsWidget
from core.queue_manager import QueueManager
from core.audio_engine import AudioEngine
from core.settings import Settings


class HomeScreen(QWidget):
    """Main 3-column layout: Library | Queue | Now Playing."""
    
    def __init__(self) -> None:
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.queue_manager = QueueManager()
        self.audio_engine = AudioEngine()
        self.settings = Settings()
        self._setup_ui()
        self._connect_audio_signals()
        self._restore_queue()
        
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
        
        # Now playing widget
        self.now_playing_widget = NowPlayingWidget()
        self.now_playing_widget.seek_requested.connect(self._on_seek_requested)
        panel.add_widget(self.now_playing_widget)
        
        panel.add_stretch()
        
        # Playback controls at bottom
        self.playback_controls = PlaybackControlsWidget()
        self.playback_controls.play_pause_clicked.connect(self._on_play_pause)
        self.playback_controls.next_clicked.connect(self._on_next)
        self.playback_controls.previous_clicked.connect(self._on_previous)
        panel.add_widget(self.playback_controls)
        
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
        self._play_current_track()
        
    def _connect_audio_signals(self) -> None:
        """Connect audio engine signals."""
        self.audio_engine.playback_started.connect(self._on_playback_started)
        self.audio_engine.playback_paused.connect(self._on_playback_paused)
        self.audio_engine.playback_resumed.connect(self._on_playback_resumed)
        self.audio_engine.playback_finished.connect(self._on_playback_finished)
        self.audio_engine.position_changed.connect(self._on_position_changed)
        self.audio_engine.duration_changed.connect(self._on_duration_changed)
        
        # Connect queue manager signals
        self.queue_manager.current_track_changed.connect(self._on_current_track_changed)
        self.queue_manager.queue_changed.connect(self.save_queue)
        
    def _play_current_track(self) -> None:
        """Play the current track from queue."""
        track = self.queue_manager.get_current_track()
        if track:
            self.audio_engine.play(track)
            
    def _on_playback_started(self, track) -> None:
        """Handle playback start."""
        self.now_playing_widget.set_track(track)
        self.playback_controls.set_playing(True)
        self.playback_controls.set_enabled(True)
        
    def _on_playback_paused(self) -> None:
        """Handle playback pause."""
        self.playback_controls.set_playing(False)
        self.now_playing_widget.pause_visualizer()
        
    def _on_playback_resumed(self) -> None:
        """Handle playback resume."""
        self.playback_controls.set_playing(True)
        self.now_playing_widget.resume_visualizer()
        
    def _on_playback_finished(self) -> None:
        """Handle track finish - auto advance."""
        print("Track finished, advancing to next...")
        if self.queue_manager.has_next():
            self.queue_manager.next_track()
            self._play_current_track()
        else:
            print("End of queue reached")
            self.playback_controls.set_playing(False)
            self.now_playing_widget.stop_visualizer()
            
    def _on_position_changed(self, position: float) -> None:
        """Handle playback position update."""
        self.now_playing_widget.update_position(position)
        
    def _on_duration_changed(self, duration: float) -> None:
        """Handle duration change."""
        self.now_playing_widget.set_duration(duration)
        
    def _on_current_track_changed(self, track) -> None:
        """Handle current track change from queue manager."""
        if track and not self.audio_engine.is_playing():
            # Track changed but not playing - update display only
            self.now_playing_widget.set_track(track)
            
    def _on_play_pause(self) -> None:
        """Handle play/pause button."""
        if self.audio_engine.is_playing() or self.audio_engine.is_paused():
            # Toggle current playback
            self.audio_engine.toggle_play_pause()
        else:
            # Start playing current track
            self._play_current_track()
            
    def _on_next(self) -> None:
        """Handle next button."""
        if self.queue_manager.has_next():
            self.queue_manager.next_track()
            self._play_current_track()
            
    def _on_previous(self) -> None:
        """Handle previous button."""
        # Try history first
        prev_track = self.audio_engine.get_previous_track()
        if prev_track:
            # Find track in queue and play it
            queue = self.queue_manager.get_queue()
            for idx, track in enumerate(queue):
                if track.file_path == prev_track.file_path:
                    self.queue_manager.set_current_index(idx)
                    self._play_current_track()
                    return
                    
        # Fallback to queue previous
        if self.queue_manager.has_previous():
            self.queue_manager.previous_track()
            self._play_current_track()
            
    def _on_seek_requested(self, position: float) -> None:
        """Handle seek request from progress bar."""
        self.audio_engine.seek(position)
    
    def _restore_queue(self) -> None:
        """Restore queue from settings on startup."""
        try:
            saved_queue = self.settings.get_queue()
            saved_index = self.settings.get_current_queue_index()
            if saved_queue:
                print(f"Restoring queue with {len(saved_queue)} tracks, index {saved_index}")
                self.queue_manager.restore(saved_queue, saved_index)
        except Exception as e:
            print(f"Could not restore queue: {e}")
    
    def save_queue(self) -> None:
        """Save queue to settings."""
        try:
            serialized_queue = self.queue_manager.serialize()
            current_index = self.queue_manager.get_current_index()
            self.settings.set_queue(serialized_queue)
            self.settings.set_current_queue_index(current_index)
            print(f"Queue saved with {len(serialized_queue)} tracks, index {current_index}")
        except Exception as e:
            print(f"Could not save queue: {e}")
