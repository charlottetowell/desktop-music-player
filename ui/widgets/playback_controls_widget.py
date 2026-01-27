"""
Playback controls widget - play/pause, next, previous buttons
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, Signal
from ui.themes.colors import TEXT_PRIMARY, ACCENT_HOVER
from ui.themes.fonts import FontManager


class PlaybackControlsWidget(QWidget):
    """Widget with playback control buttons."""
    
    play_pause_clicked = Signal()
    next_clicked = Signal()
    previous_clicked = Signal()
    
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.is_playing = False
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Initialize control buttons."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 12, 24, 24)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignCenter)
        
        # Button style
        button_style = f"""
            QPushButton {{
                background-color: rgba(0, 0, 0, 0.1);
                color: {TEXT_PRIMARY};
                border: none;
                border-radius: 24px;
                font-size: 18px;
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
                background-color: #6495ed;
                color: white;
                border: none;
                border-radius: 28px;
                font-size: 20px;
            }}
            QPushButton:hover {{
                background-color: #5080d0;
            }}
            QPushButton:pressed {{
                background-color: #4070c0;
            }}
        """
        
        # Previous button
        self.prev_btn = QPushButton("⏮")
        self.prev_btn.setFixedSize(48, 48)
        self.prev_btn.setFont(FontManager.get_title_font(16))
        self.prev_btn.setCursor(Qt.PointingHandCursor)
        self.prev_btn.setStyleSheet(button_style)
        self.prev_btn.setToolTip("Previous track")
        self.prev_btn.clicked.connect(self.previous_clicked.emit)
        
        # Play/Pause button (larger)
        self.play_pause_btn = QPushButton("▶")
        self.play_pause_btn.setFixedSize(56, 56)
        self.play_pause_btn.setFont(FontManager.get_title_font(18))
        self.play_pause_btn.setCursor(Qt.PointingHandCursor)
        self.play_pause_btn.setStyleSheet(large_button_style)
        self.play_pause_btn.setToolTip("Play")
        self.play_pause_btn.clicked.connect(self.play_pause_clicked.emit)
        
        # Next button
        self.next_btn = QPushButton("⏭")
        self.next_btn.setFixedSize(48, 48)
        self.next_btn.setFont(FontManager.get_title_font(16))
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.setStyleSheet(button_style)
        self.next_btn.setToolTip("Next track")
        self.next_btn.clicked.connect(self.next_clicked.emit)
        
        layout.addWidget(self.prev_btn)
        layout.addWidget(self.play_pause_btn)
        layout.addWidget(self.next_btn)
        
        self.setStyleSheet("PlaybackControlsWidget { background: transparent; }")
        
    def set_playing(self, playing: bool) -> None:
        """Update play/pause button state."""
        self.is_playing = playing
        if playing:
            self.play_pause_btn.setText("⏸")
            self.play_pause_btn.setToolTip("Pause")
        else:
            self.play_pause_btn.setText("▶")
            self.play_pause_btn.setToolTip("Play")
            
    def set_enabled(self, enabled: bool) -> None:
        """Enable/disable all controls."""
        self.prev_btn.setEnabled(enabled)
        self.play_pause_btn.setEnabled(enabled)
        self.next_btn.setEnabled(enabled)
