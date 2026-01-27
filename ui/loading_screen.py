"""
Loading screen widget with progress indicator
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt, QTimer, Signal
from ui.themes.colors import ACCENT_LAVENDER, TEXT_PRIMARY, TEXT_SECONDARY, BG_PANEL
from ui.themes import FontManager


class LoadingScreen(QWidget):
    """Frameless loading screen with progress animation."""
    
    loading_complete = Signal()
    
    def __init__(self) -> None:
        super().__init__()
        self._progress = 0
        self._setup_ui()
        self._setup_timer()
        
    def _setup_ui(self) -> None:
        """Initialize UI components."""
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 60, 40, 60)
        layout.setSpacing(30)
        
        # App title
        title = QLabel("Peachy Player")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(FontManager.get_display_font(24))
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        
        # Loading text
        self.loading_label = QLabel("Initializing...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setFont(FontManager.get_body_font(11))
        self.loading_label.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: rgba(0, 0, 0, 0.08);
                border-radius: 2px;
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {ACCENT_LAVENDER};
                border-radius: 2px;
            }}
        """)
        
        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(self.loading_label)
        layout.addWidget(self.progress_bar)
        layout.addStretch()
        
        # Background styling
        self.setStyleSheet(f"""
            LoadingScreen {{
                background-color: {BG_PANEL};
                border-radius: 12px;
            }}
        """)
        
    def _setup_timer(self) -> None:
        """Setup progress simulation timer."""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_progress)
        
    def start_loading(self) -> None:
        """Begin loading animation."""
        self._progress = 0
        self.progress_bar.setValue(0)
        self.timer.start(30)  # Update every 30ms
        
    def _update_progress(self) -> None:
        """Update progress bar animation."""
        self._progress += 2
        
        if self._progress <= 30:
            self.loading_label.setText("Loading audio engine...")
        elif self._progress <= 60:
            self.loading_label.setText("Initializing components...")
        elif self._progress <= 90:
            self.loading_label.setText("Preparing interface...")
        else:
            self.loading_label.setText("Ready!")
        
        self.progress_bar.setValue(self._progress)
        
        if self._progress >= 100:
            self.timer.stop()
            QTimer.singleShot(300, self.loading_complete.emit)
            
    def center_on_screen(self) -> None:
        """Center the loading screen on the primary display."""
        screen = self.screen().geometry()
        self.move(
            screen.center().x() - self.width() // 2,
            screen.center().y() - self.height() // 2
        )
