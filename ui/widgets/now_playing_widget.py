"""
Now Playing widget - displays current track information
"""

from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QFrame
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap, QImage
from ui.themes.colors import TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED
from core.audio_scanner import AudioTrack
from ui.widgets.audio_visualizer_widget import AudioVisualizerWidget


class NowPlayingWidget(QWidget):
    """Widget displaying currently playing track with album art and progress."""
    
    seek_requested = Signal(float)  # Emits position in seconds
    
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.current_track: Optional[AudioTrack] = None
        self.duration = 0.0
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignTop)
        
        # Album art
        self.album_art_label = QLabel()
        self.album_art_label.setFixedSize(200, 200)
        self.album_art_label.setAlignment(Qt.AlignCenter)
        self.album_art_label.setStyleSheet(f"""
            QLabel {{
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                border: 2px solid rgba(0, 0, 0, 0.1);
            }}
        """)
        
        # Center album art
        art_container = QHBoxLayout()
        art_container.addStretch()
        art_container.addWidget(self.album_art_label)
        art_container.addStretch()
        layout.addLayout(art_container)
        
        # Track info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)
        info_layout.setAlignment(Qt.AlignCenter)
        
        # Track title
        self.title_label = QLabel("No track playing")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.title_label.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        self.title_label.setWordWrap(True)
        
        # Artist
        self.artist_label = QLabel("")
        self.artist_label.setAlignment(Qt.AlignCenter)
        self.artist_label.setFont(QFont("Segoe UI", 12))
        self.artist_label.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        self.artist_label.setWordWrap(True)
        
        # Album & Year
        self.album_label = QLabel("")
        self.album_label.setAlignment(Qt.AlignCenter)
        self.album_label.setFont(QFont("Segoe UI", 10))
        self.album_label.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        self.album_label.setWordWrap(True)
        
        info_layout.addWidget(self.title_label)
        info_layout.addWidget(self.artist_label)
        info_layout.addWidget(self.album_label)
        
        layout.addLayout(info_layout)
        layout.addSpacing(12)
        
        # Progress bar section
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(8)
        
        # Time labels
        time_layout = QHBoxLayout()
        self.current_time_label = QLabel("0:00")
        self.current_time_label.setFont(QFont("Segoe UI", 9))
        self.current_time_label.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        
        self.total_time_label = QLabel("0:00")
        self.total_time_label.setFont(QFont("Segoe UI", 9))
        self.total_time_label.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        
        time_layout.addWidget(self.current_time_label)
        time_layout.addStretch()
        time_layout.addWidget(self.total_time_label)
        
        # Progress slider
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setMinimum(0)
        self.progress_slider.setMaximum(1000)  # Use 1000 for smooth progress
        self.progress_slider.setValue(0)
        self.progress_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: rgba(0, 0, 0, 0.1);
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #6495ed;
                width: 14px;
                height: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
            QSlider::sub-page:horizontal {
                background: #6495ed;
                border-radius: 3px;
            }
        """)
        self.progress_slider.sliderPressed.connect(self._on_slider_pressed)
        self.progress_slider.sliderReleased.connect(self._on_slider_released)
        
        progress_layout.addWidget(self.progress_slider)
        progress_layout.addLayout(time_layout)
        
        layout.addLayout(progress_layout)
        
        # Audio visualizer
        layout.addSpacing(16)
        self.visualizer = AudioVisualizerWidget()
        layout.addWidget(self.visualizer)
        
        layout.addStretch()
        
        self.setStyleSheet("NowPlayingWidget { background: transparent; }")
        
        # Show default state
        self._show_empty_state()
        
    def set_track(self, track: AudioTrack) -> None:
        """Set the currently playing track."""
        self.current_track = track
        
        # Update track info
        self.title_label.setText(track.title)
        self.artist_label.setText(track.artist)
        
        album_text = track.album
        if track.year and track.year != "Unknown":
            album_text += f" • {track.year}"
        self.album_label.setText(album_text)
        
        # Update album art
        if track.album_art_data:
            self._load_album_art(track.album_art_data)
        else:
            self._show_default_art()
            
        # Set track for visualizer
        self.visualizer.set_track(track)
        self.visualizer.start()
            
    def set_duration(self, duration: float) -> None:
        """Set track duration."""
        self.duration = duration
        self.total_time_label.setText(self._format_time(duration))
        self.visualizer.set_duration(duration)
        
    def update_position(self, position: float) -> None:
        """Update playback position."""
        self.current_time_label.setText(self._format_time(position))
        
        # Update slider if not being dragged
        if not self.progress_slider.isSliderDown():
            if self.duration > 0:
                progress = int((position / self.duration) * 1000)
                self.progress_slider.setValue(progress)
                
        # Update visualizer
        self.visualizer.update_position(position)
                
    def _load_album_art(self, image_data: bytes) -> None:
        """Load album art from bytes."""
        try:
            from PySide6.QtCore import QByteArray
            image = QImage()
            if image.loadFromData(QByteArray(image_data)):
                pixmap = QPixmap.fromImage(image)
                scaled = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.album_art_label.setPixmap(scaled)
        except Exception as e:
            print(f"Error loading album art: {e}")
            self._show_default_art()
            
    def _show_default_art(self) -> None:
        """Show default album art placeholder."""
        self.album_art_label.clear()
        self.album_art_label.setText("♪")
        self.album_art_label.setFont(QFont("Segoe UI", 64))
        self.album_art_label.setStyleSheet(f"""
            QLabel {{
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                border: 2px solid rgba(0, 0, 0, 0.1);
                color: {TEXT_MUTED};
            }}
        """)
        
    def _show_empty_state(self) -> None:
        """Show empty state when no track is playing."""
        self._show_default_art()
        self.title_label.setText("No track playing")
        self.artist_label.setText("")
        self.album_label.setText("")
        self.current_time_label.setText("0:00")
        self.total_time_label.setText("0:00")
        self.progress_slider.setValue(0)
        
    def _format_time(self, seconds: float) -> str:
        """Format seconds as MM:SS."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"
        
    def _on_slider_pressed(self) -> None:
        """Handle slider press (start seeking)."""
        pass
        
    def _on_slider_released(self) -> None:
        """Handle slider release (seek to position)."""
        if self.duration > 0:
            position = (self.progress_slider.value() / 1000) * self.duration
            self.seek_requested.emit(position)
            
    def pause_visualizer(self) -> None:
        """Pause the visualizer."""
        self.visualizer.pause()
        
    def resume_visualizer(self) -> None:
        """Resume the visualizer."""
        self.visualizer.resume()
        
    def stop_visualizer(self) -> None:
        """Stop the visualizer."""
        self.visualizer.stop()
