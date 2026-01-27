"""
Mini Player Window - Compact player with visualizer and controls
"""

from typing import Optional
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QImage
from ui.themes.colors import TEXT_PRIMARY, TEXT_SECONDARY, ACCENT_HOVER, BG_MID_PURPLE, ACCENT_LAVENDER
from ui.themes import FontManager
from core.audio_scanner import AudioTrack
from ui.widgets.audio_visualizer_widget import AudioVisualizerWidget
from utils.icon_manager import IconManager


class MiniPlayerWindow(QWidget):
    """Compact mini player window with visualizer and controls."""
    
    play_pause_clicked = Signal()
    next_clicked = Signal()
    previous_clicked = Signal()
    
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.current_track: Optional[AudioTrack] = None
        self.is_playing = False
        self._setup_window()
        self._setup_ui()
        
    def _setup_window(self) -> None:
        """Configure window properties."""
        self.setWindowTitle("Mini Player")
        self.setMinimumSize(400, 250)
        self.resize(600, 300)
        
        # Window flags for independent window
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowCloseButtonHint |
            Qt.WindowMinimizeButtonHint |
            Qt.WindowMaximizeButtonHint
        )
        
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"""
            MiniPlayerWindow {{
                background-color: {BG_MID_PURPLE};
            }}
        """)
        
    def _setup_ui(self) -> None:
        """Initialize UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Audio Visualizer (top section - takes remaining space)
        self.visualizer = AudioVisualizerWidget()
        self.visualizer.setMinimumHeight(100)
        main_layout.addWidget(self.visualizer, 1)
        
        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("background-color: rgba(0, 0, 0, 0.1); max-height: 1px;")
        main_layout.addWidget(divider)
        
        # Info and Controls Strip (bottom section - fixed height)
        control_strip = QFrame()
        control_strip.setFixedHeight(100)
        control_strip.setAttribute(Qt.WA_StyledBackground, True)
        control_strip.setStyleSheet("background-color: rgba(0, 0, 0, 0.03);")
        
        strip_layout = QHBoxLayout(control_strip)
        strip_layout.setContentsMargins(16, 12, 16, 12)
        strip_layout.setSpacing(16)
        
        # Album Art (small)
        self.album_art_label = QLabel()
        self.album_art_label.setFixedSize(75, 75)
        self.album_art_label.setAlignment(Qt.AlignCenter)
        self.album_art_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 6px;
                border: 2px solid rgba(0, 0, 0, 0.1);
            }
        """)
        strip_layout.addWidget(self.album_art_label)
        
        # Track Info (flexible width)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        info_layout.setAlignment(Qt.AlignVCenter)
        
        self.title_label = QLabel("No track playing")
        self.title_label.setFont(FontManager.get_body_font(12))
        self.title_label.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent; font-weight: bold;")
        self.title_label.setWordWrap(False)
        
        self.artist_label = QLabel("")
        self.artist_label.setFont(FontManager.get_small_font(10))
        self.artist_label.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        self.artist_label.setWordWrap(False)
        
        self.album_label = QLabel("")
        self.album_label.setFont(FontManager.get_small_font(9))
        self.album_label.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        self.album_label.setWordWrap(False)
        
        info_layout.addWidget(self.title_label)
        info_layout.addWidget(self.artist_label)
        info_layout.addWidget(self.album_label)
        
        strip_layout.addLayout(info_layout, 1)
        
        # Playback Controls (fixed width)
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)
        controls_layout.setAlignment(Qt.AlignVCenter)
        
        button_style = f"""
            QPushButton {{
                background-color: rgba(0, 0, 0, 0.1);
                color: {TEXT_PRIMARY};
                border: none;
                border-radius: 20px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {ACCENT_HOVER};
            }}
            QPushButton:pressed {{
                background-color: rgba(0, 0, 0, 0.2);
            }}
        """
        
        large_button_style = f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_PRIMARY};
                border: none;
                border-radius: 24px;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background-color: rgba(183, 148, 246, 0.2);
            }}
            QPushButton:pressed {{
                background-color: rgba(183, 148, 246, 0.3);
            }}
        """
        
        # Previous button
        self.prev_btn = QPushButton()
        self.prev_btn.setIcon(IconManager.get_icon("track-prev"))
        self.prev_btn.setFixedSize(40, 40)
        self.prev_btn.setIconSize(self.prev_btn.size() * 0.6)
        self.prev_btn.setCursor(Qt.PointingHandCursor)
        self.prev_btn.setStyleSheet(button_style)
        self.prev_btn.setToolTip("Previous track")
        self.prev_btn.clicked.connect(self.previous_clicked.emit)
        
        # Play/Pause button
        self.play_pause_btn = QPushButton()
        self.play_pause_btn.setIcon(IconManager.get_icon("play"))
        self.play_pause_btn.setFixedSize(48, 48)
        self.play_pause_btn.setIconSize(self.play_pause_btn.size() * 0.65)
        self.play_pause_btn.setCursor(Qt.PointingHandCursor)
        self.play_pause_btn.setStyleSheet(large_button_style)
        self.play_pause_btn.setToolTip("Play")
        self.play_pause_btn.clicked.connect(self.play_pause_clicked.emit)
        
        # Next button
        self.next_btn = QPushButton()
        self.next_btn.setIcon(IconManager.get_icon("track-next"))
        self.next_btn.setFixedSize(40, 40)
        self.next_btn.setIconSize(self.next_btn.size() * 0.6)
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.setStyleSheet(button_style)
        self.next_btn.setToolTip("Next track")
        self.next_btn.clicked.connect(self.next_clicked.emit)
        
        controls_layout.addWidget(self.prev_btn)
        controls_layout.addWidget(self.play_pause_btn)
        controls_layout.addWidget(self.next_btn)
        
        strip_layout.addLayout(controls_layout)
        
        main_layout.addWidget(control_strip)
        
    def update_track(self, track: Optional[AudioTrack]) -> None:
        """Update displayed track information."""
        self.current_track = track
        
        if track:
            self.title_label.setText(track.title)
            self.artist_label.setText(track.artist)
            album_text = track.album
            if track.year and track.year != "Unknown":
                album_text += f" ({track.year})"
            self.album_label.setText(album_text)
            
            # Update album art
            if track.album_art_data:
                pixmap = self._load_album_art(track.album_art_data)
                if pixmap:
                    scaled_pixmap = pixmap.scaled(
                        75, 75,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    self.album_art_label.setPixmap(scaled_pixmap)
                else:
                    self._set_placeholder_art()
            else:
                self._set_placeholder_art()
        else:
            self.title_label.setText("No track playing")
            self.artist_label.setText("")
            self.album_label.setText("")
            self._set_placeholder_art()
            
    def _load_album_art(self, image_data: bytes) -> Optional[QPixmap]:
        """Convert image bytes to QPixmap."""
        try:
            image = QImage()
            if image.loadFromData(image_data):
                return QPixmap.fromImage(image)
        except Exception as e:
            print(f"Error loading album art: {e}")
        return None
        
    def _set_placeholder_art(self) -> None:
        """Set placeholder album art."""
        self.album_art_label.clear()
        self.album_art_label.setText("♪")
        self.album_art_label.setFont(FontManager.get_display_font(28))
        self.album_art_label.setAlignment(Qt.AlignCenter)
        
    def set_playing(self, playing: bool) -> None:
        """Update play/pause button state."""
        self.is_playing = playing
        if playing:
            self.play_pause_btn.setIcon(IconManager.get_icon("pause"))
            self.play_pause_btn.setToolTip("Pause")
            self.visualizer.resume()
        else:
            self.play_pause_btn.setIcon(IconManager.get_icon("play"))
            self.play_pause_btn.setToolTip("Play")
            self.visualizer.pause()
            
    def update_position(self, position: float) -> None:
        """Update visualizer position."""
        self.visualizer.update_position(position)
        
    def set_duration(self, duration: float) -> None:
        """Update visualizer duration."""
        self.visualizer.set_duration(duration)
        
    def set_track(self, track: AudioTrack) -> None:
        """Load audio track into visualizer."""
        self.visualizer.set_track(track)
        self.visualizer.start()
        
    def stop_visualization(self) -> None:
        """Stop visualizer animation."""
        self.visualizer.stop()
        
    def pause_visualization(self) -> None:
        """Pause visualizer animation."""
        self.visualizer.pause()
        
    def resume_visualization(self) -> None:
        """Resume visualizer animation."""
        self.visualizer.resume()
