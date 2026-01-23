"""
Home screen widget - main 3-column interface
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.themes.colors import BG_SIDEBAR, BG_MAIN, TEXT_PRIMARY
from ui.widgets import Panel, SectionHeader, PlaceholderContent


class HomeScreen(QWidget):
    """Main 3-column layout: Library | Queue | Now Playing."""
    
    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Initialize main 3-column layout."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left Column - My Library (25%)
        self.library_panel = self._create_library_panel()
        main_layout.addWidget(self.library_panel, 25)
        
        # Middle Column - Queue (50%)
        self.queue_panel = self._create_queue_panel()
        main_layout.addWidget(self.queue_panel, 50)
        
        # Right Column - Currently Playing (25%)
        self.playing_panel = self._create_playing_panel()
        main_layout.addWidget(self.playing_panel, 25)
        
    def _create_library_panel(self) -> Panel:
        """Create left panel for library."""
        panel = Panel(title="My Library", background_color=BG_SIDEBAR)
        
        # Add placeholder content
        placeholder = PlaceholderContent(
            "Your music library will appear here.\n\n"
            "• Playlists\n• Albums\n• Artists\n• Folders"
        )
        panel.add_widget(placeholder)
        panel.add_stretch()
        
        return panel
        
    def _create_queue_panel(self) -> Panel:
        """Create middle panel for queue with app logo."""
        panel = Panel(background_color=BG_MAIN)
        
        # App logo/name at top
        logo_widget = self._create_logo_header()
        panel.content_layout.setContentsMargins(0, 0, 0, 24)
        panel.main_layout.insertWidget(0, logo_widget)
        
        # Queue header
        queue_header = SectionHeader("Queue", "0 tracks")
        panel.add_widget(queue_header)
        
        # Placeholder content
        placeholder = PlaceholderContent(
            "Your playback queue will appear here.\n\n"
            "Add tracks from your library to start playing."
        )
        panel.add_widget(placeholder)
        panel.add_stretch()
        
        return panel
        
    def _create_playing_panel(self) -> Panel:
        """Create right panel for currently playing track."""
        panel = Panel(title="Currently Playing", background_color=BG_SIDEBAR)
        
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
        header.setFixedHeight(80)
        
        layout = QVBoxLayout(header)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setAlignment(Qt.AlignCenter)
        
        # App name
        logo = QLabel("Peachy Player")
        logo.setAlignment(Qt.AlignCenter)
        logo.setFont(QFont("Segoe UI", 24, QFont.Bold))
        logo.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_PRIMARY};
                background: transparent;
                letter-spacing: 1px;
            }}
        """)
        
        layout.addWidget(logo)
        
        header.setStyleSheet("QWidget { background: transparent; }")
        
        return header
