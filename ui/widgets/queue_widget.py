"""
Queue widget with drag-and-drop and album grouping
"""

from typing import List, Dict, Optional
from pathlib import Path
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QScrollArea, QFrame, QPushButton)
from PySide6.QtCore import Qt, Signal, QMimeData, QPoint, QSize, QByteArray
from PySide6.QtGui import QFont, QDrag, QPixmap, QPainter, QColor, QImage
from ui.themes.colors import TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, ACCENT_HOVER
from core.audio_scanner import AudioTrack
from core.queue_manager import QueueManager


class QueueTrackWidget(QFrame):
    """Widget representing a single track in the queue with drag support."""
    
    track_clicked = Signal(int)  # Emits queue index
    remove_requested = Signal(int)  # Emits queue index
    drag_started = Signal(int)  # Emits queue index
    
    def __init__(self, track: AudioTrack, index: int, is_current: bool = False, read_only: bool = False, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.track = track
        self.index = index
        self.is_current = is_current
        self.read_only = read_only
        self._drag_start_pos = QPoint()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Initialize track item UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 8, 8)
        layout.setSpacing(12)
        
        # Track info container
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        # Title
        title = QLabel(self.track.title)
        title.setFont(QFont("Segoe UI", 10, QFont.Bold if self.is_current else QFont.Normal))
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        title.setWordWrap(False)
        
        # Artist
        artist = QLabel(self.track.artist)
        artist.setFont(QFont("Segoe UI", 9))
        artist.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        artist.setWordWrap(False)
        
        info_layout.addWidget(title)
        info_layout.addWidget(artist)
        
        layout.addLayout(info_layout, 1)
        
        # Remove button (only for editable tracks)
        if not self.read_only:
            remove_btn = QPushButton("×")
            remove_btn.setFixedSize(24, 24)
            remove_btn.setFont(QFont("Segoe UI", 14))
            remove_btn.setCursor(Qt.PointingHandCursor)
            remove_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba(0, 0, 0, 0.1);
                    color: {TEXT_SECONDARY};
                    border: none;
                    border-radius: 12px;
                }}
                QPushButton:hover {{
                    background-color: #e57373;
                    color: white;
                }}
            """)
            remove_btn.clicked.connect(lambda: self.remove_requested.emit(self.index))
            layout.addWidget(remove_btn)
        
        # Styling
        bg_color = "rgba(100, 150, 255, 0.15)" if self.is_current else "rgba(0, 0, 0, 0.03)"
        hover_color = "rgba(100, 150, 255, 0.25)" if self.is_current else ACCENT_HOVER
        
        self.setStyleSheet(f"""
            QueueTrackWidget {{
                background-color: {bg_color};
                border-radius: 6px;
                border-left: 3px solid {"#6495ed" if self.is_current else "transparent"};
            }}
            QueueTrackWidget:hover {{
                background-color: {hover_color};
            }}
        """)
        if not self.read_only:
            self.setCursor(Qt.PointingHandCursor)
        
    def mousePressEvent(self, event) -> None:
        """Handle mouse press for dragging."""
        if event.button() == Qt.LeftButton and not self.read_only:
            self._drag_start_pos = event.pos()
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event) -> None:
        """Handle mouse move for drag initiation."""
        if self.read_only or not (event.buttons() & Qt.LeftButton):
            return
            
        if (event.pos() - self._drag_start_pos).manhattanLength() < 10:
            return
            
        # Start drag operation
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(str(self.index))  # Store the queue index
        drag.setMimeData(mime_data)
        
        # Create drag pixmap
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setOpacity(0.7)
        self.render(painter, QPoint())
        painter.end()
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())
        
        self.drag_started.emit(self.index)
        drag.exec(Qt.MoveAction)
        
    def mouseDoubleClickEvent(self, event) -> None:
        """Handle double-click to play track."""
        if event.button() == Qt.LeftButton:
            self.track_clicked.emit(self.index)
        super().mouseDoubleClickEvent(event)


class AlbumGroupWidget(QFrame):
    """Widget representing an album group with cover and tracks."""
    
    def __init__(self, album_name: str, artist_name: str, album_art: Optional[QPixmap] = None, 
                 parent: QWidget = None) -> None:
        super().__init__(parent)
        self.album_name = album_name
        self.artist_name = artist_name
        self.album_art = album_art
        self.track_widgets: List[QueueTrackWidget] = []
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Initialize album group UI."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 12)
        self.main_layout.setSpacing(8)
        
        # Album header with cover
        header = self._create_header()
        self.main_layout.addWidget(header)
        
        # Track container
        self.track_container = QVBoxLayout()
        self.track_container.setSpacing(4)
        self.main_layout.addLayout(self.track_container)
        
        self.setStyleSheet("AlbumGroupWidget { background: transparent; }")
        
    def _create_header(self) -> QWidget:
        """Create album header with cover art."""
        header = QFrame()
        header.setAttribute(Qt.WA_StyledBackground, True)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)
        
        # Album cover (placeholder for now)
        cover_label = QLabel()
        cover_label.setFixedSize(48, 48)
        
        if self.album_art:
            cover_label.setPixmap(self.album_art.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            # Placeholder album cover
            cover_label.setStyleSheet(f"""
                QLabel {{
                    background-color: rgba(0, 0, 0, 0.15);
                    border-radius: 4px;
                    border: 2px solid rgba(0, 0, 0, 0.1);
                }}
            """)
            cover_label.setAlignment(Qt.AlignCenter)
            cover_label.setText("♪")
            cover_label.setFont(QFont("Segoe UI", 16))
            
        # Album info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        album_label = QLabel(self.album_name)
        album_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        album_label.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        album_label.setWordWrap(False)
        
        artist_label = QLabel(self.artist_name)
        artist_label.setFont(QFont("Segoe UI", 9))
        artist_label.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        artist_label.setWordWrap(False)
        
        info_layout.addWidget(album_label)
        info_layout.addWidget(artist_label)
        
        layout.addWidget(cover_label)
        layout.addLayout(info_layout, 1)
        
        header.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 0.05);
                border-radius: 6px;
            }
        """)
        
        return header
        
    def add_track_widget(self, widget: QueueTrackWidget) -> None:
        """Add a track widget to this album group."""
        self.track_widgets.append(widget)
        self.track_container.addWidget(widget)
        
    def clear_tracks(self) -> None:
        """Remove all track widgets."""
        for widget in self.track_widgets:
            widget.deleteLater()
        self.track_widgets.clear()


class QueueWidget(QWidget):
    """Queue display widget with album grouping and drag-and-drop."""
    
    track_double_clicked = Signal(int)  # Emits queue index to play
    
    def __init__(self, queue_manager: QueueManager, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.queue_manager = queue_manager
        self.up_next_album_groups: Dict[str, AlbumGroupWidget] = {}
        self.just_played_album_groups: Dict[str, AlbumGroupWidget] = {}
        self._drag_source_index: Optional[int] = None
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAcceptDrops(True)
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self) -> None:
        """Initialize queue widget UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header with Up Next title and Clear button
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(16, 12, 12, 8)
        header_layout.setSpacing(8)
        
        up_next_label = QLabel("Up Next")
        up_next_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        up_next_label.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        header_layout.addWidget(up_next_label)
        
        header_layout.addStretch()
        
        # Clear Queue button
        self.clear_btn = QPushButton("Clear Queue")
        self.clear_btn.setFont(QFont("Segoe UI", 9))
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(0, 0, 0, 0.05);
                color: {TEXT_SECONDARY};
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: rgba(229, 115, 115, 0.2);
                color: #e57373;
            }}
            QPushButton:pressed {{
                background-color: rgba(229, 115, 115, 0.3);
            }}
        """)
        self.clear_btn.clicked.connect(self._on_clear_queue)
        header_layout.addWidget(self.clear_btn)
        
        main_layout.addLayout(header_layout)
        
        # Up Next scroll area
        self.up_next_scroll = QScrollArea()
        self.up_next_scroll.setWidgetResizable(True)
        self.up_next_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.up_next_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.up_next_scroll.setFrameShape(QFrame.NoFrame)
        self.up_next_scroll.setAcceptDrops(True)
        
        self.up_next_content = QWidget()
        self.up_next_layout = QVBoxLayout(self.up_next_content)
        self.up_next_layout.setContentsMargins(12, 0, 12, 12)
        self.up_next_layout.setSpacing(16)
        self.up_next_layout.addStretch()
        
        self.up_next_scroll.setWidget(self.up_next_content)
        main_layout.addWidget(self.up_next_scroll, 1)
        
        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("background-color: rgba(0, 0, 0, 0.1); max-height: 2px;")
        main_layout.addWidget(divider)
        
        # Just Played Section (Bottom)
        just_played_label = QLabel("Just Played")
        just_played_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        just_played_label.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent; padding: 8px 16px 8px 16px;")
        main_layout.addWidget(just_played_label)
        
        # Just Played scroll area
        self.just_played_scroll = QScrollArea()
        self.just_played_scroll.setWidgetResizable(True)
        self.just_played_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.just_played_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.just_played_scroll.setFrameShape(QFrame.NoFrame)
        
        self.just_played_content = QWidget()
        self.just_played_layout = QVBoxLayout(self.just_played_content)
        self.just_played_layout.setContentsMargins(12, 0, 12, 12)
        self.just_played_layout.setSpacing(16)
        self.just_played_layout.addStretch()
        
        self.just_played_scroll.setWidget(self.just_played_content)
        main_layout.addWidget(self.just_played_scroll, 1)
        
        # Styling
        self.setStyleSheet("QueueWidget { background: transparent; }")
        scroll_style = """
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
        """
        self.up_next_scroll.setStyleSheet(scroll_style)
        self.just_played_scroll.setStyleSheet(scroll_style)
        
    def _connect_signals(self) -> None:
        """Connect queue manager signals."""
        self.queue_manager.queue_changed.connect(self._refresh_display)
        self.queue_manager.current_track_changed.connect(self._on_current_track_changed)
        
    def _refresh_display(self) -> None:
        """Refresh the queue display with album grouping in two sections."""
        # Clear existing content
        while self.up_next_layout.count() > 1:  # Keep the stretch
            item = self.up_next_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        while self.just_played_layout.count() > 1:  # Keep the stretch
            item = self.just_played_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        self.up_next_album_groups.clear()
        self.just_played_album_groups.clear()
        
        queue = self.queue_manager.get_queue()
        current_index = self.queue_manager.get_current_index()
        
        if not queue:
            self._show_empty_state()
            return
        
        # Split queue into sections
        just_played_tracks = []
        up_next_tracks = []
        
        for idx, track in enumerate(queue):
            if idx <= current_index:
                just_played_tracks.append((track, idx))
            else:
                up_next_tracks.append((track, idx))
        
        # Render Up Next section
        if up_next_tracks:
            self._render_section(up_next_tracks, self.up_next_layout, self.up_next_album_groups, False, current_index)
        else:
            empty_label = QLabel("No upcoming tracks")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setFont(QFont("Segoe UI", 10))
            empty_label.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent; padding: 40px;")
            self.up_next_layout.insertWidget(0, empty_label)
        
        # Render Just Played section (in reverse order - most recent first)
        if just_played_tracks:
            just_played_tracks.reverse()
            self._render_section(just_played_tracks, self.just_played_layout, self.just_played_album_groups, True, current_index)
        else:
            empty_label = QLabel("No played tracks yet")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setFont(QFont("Segoe UI", 10))
            empty_label.setStyleSheet(f"color: {TEXT_MUTED}; background: transparent; padding: 40px;")
            self.just_played_layout.insertWidget(0, empty_label)
    
    def _render_section(self, tracks: List[tuple[AudioTrack, int]], layout: QVBoxLayout, 
                       album_groups_dict: Dict[str, AlbumGroupWidget], read_only: bool, current_index: int) -> None:
        """Render a section (Up Next or Just Played) with album grouping."""
        # Group adjacent tracks by album
        album_groups: List[tuple[str, str, List[tuple[AudioTrack, int]]]] = []
        
        current_group_key = None
        current_group_name = None
        current_group_artist = None
        current_group_tracks = []
        
        for track, idx in tracks:
            album_key = f"{track.album}|{track.artist}"
            
            # Start new group if album changes or first track
            if album_key != current_group_key:
                # Save previous group if it exists
                if current_group_tracks:
                    album_groups.append((current_group_name, current_group_artist, current_group_tracks))
                
                # Start new group
                current_group_key = album_key
                current_group_name = track.album
                current_group_artist = track.artist
                current_group_tracks = [(track, idx)]
            else:
                # Add to current group
                current_group_tracks.append((track, idx))
        
        # Don't forget the last group
        if current_group_tracks:
            album_groups.append((current_group_name, current_group_artist, current_group_tracks))
            
        # Create album group widgets
        for album_name, artist_name, album_tracks in album_groups:
            # Get album art from first track in album
            album_art_pixmap = None
            if album_tracks[0][0].album_art_data:
                album_art_pixmap = self._load_album_art(album_tracks[0][0].album_art_data)
            
            album_group = AlbumGroupWidget(album_name, artist_name, album_art_pixmap)
            
            # Add tracks to group
            for track, idx in album_tracks:
                is_current = (idx == current_index)
                track_widget = QueueTrackWidget(track, idx, is_current, read_only)
                if not read_only:
                    track_widget.track_clicked.connect(self.track_double_clicked.emit)
                    track_widget.remove_requested.connect(self._on_remove_track)
                    track_widget.drag_started.connect(self._on_drag_started)
                else:
                    track_widget.track_clicked.connect(self.track_double_clicked.emit)
                album_group.add_track_widget(track_widget)
                
            album_key = f"{album_name}|{artist_name}"
            album_groups_dict[album_key] = album_group
            layout.insertWidget(layout.count() - 1, album_group)
            
    def _show_empty_state(self) -> None:
        """Show empty queue message."""
        empty_label = QLabel("Queue is empty\n\nDouble-click or drag tracks\nfrom your library to add them")
        empty_label.setAlignment(Qt.AlignCenter)
        empty_label.setFont(QFont("Segoe UI", 11))
        empty_label.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent; padding: 60px;")
        empty_label.setWordWrap(True)
        self.up_next_layout.insertWidget(0, empty_label)
        
    def _on_remove_track(self, index: int) -> None:
        """Handle track removal request."""
        self.queue_manager.remove_track(index)
        
    def _on_drag_started(self, index: int) -> None:
        """Track which item started being dragged."""
        self._drag_source_index = index
        
    def _on_current_track_changed(self, track: Optional[AudioTrack]) -> None:
        """Handle current track change."""
        self._refresh_display()
    
    def _on_clear_queue(self) -> None:
        """Handle clear queue button click."""
        self.queue_manager.clear_queue()
        
    def _load_album_art(self, image_data: bytes) -> Optional[QPixmap]:
        """Convert image bytes to QPixmap."""
        try:
            image = QImage()
            if image.loadFromData(QByteArray(image_data)):
                return QPixmap.fromImage(image)
        except Exception as e:
            print(f"Error loading album art: {e}")
        return None
        
    def dragEnterEvent(self, event) -> None:
        """Handle drag enter for reordering and adding from library."""
        if (event.mimeData().hasText() or 
            event.mimeData().hasFormat("application/x-audiotrack") or
            event.mimeData().hasFormat("application/x-audiotrack-list")):
            event.acceptProposedAction()
            
    def dragMoveEvent(self, event) -> None:
        """Handle drag move."""
        if (event.mimeData().hasText() or 
            event.mimeData().hasFormat("application/x-audiotrack") or
            event.mimeData().hasFormat("application/x-audiotrack-list")):
            event.acceptProposedAction()
            
    def dropEvent(self, event) -> None:
        """Handle drop for reordering tracks or adding from library."""
        mime_data = event.mimeData()
        
        # Check if drop is in Up Next section
        drop_pos = event.position().toPoint()
        up_next_rect = self.up_next_scroll.geometry()
        in_up_next = up_next_rect.contains(drop_pos)
        
        # Handle adding single track from library (only to Up Next)
        if mime_data.hasFormat("application/x-audiotrack"):
            import pickle
            try:
                track_data = bytes(mime_data.data("application/x-audiotrack"))
                track = pickle.loads(track_data)
                self.queue_manager.add_track(track)
                # If first track, set as current
                if self.queue_manager.size() == 1:
                    self.queue_manager.set_current_index(0)
                event.acceptProposedAction()
                print(f"Added track to queue: {track.title}")
                return
            except Exception as e:
                print(f"Error adding track: {e}")
                
        # Handle adding album/multiple tracks from library (only to Up Next)
        if mime_data.hasFormat("application/x-audiotrack-list"):
            import pickle
            try:
                tracks_data = bytes(mime_data.data("application/x-audiotrack-list"))
                tracks = pickle.loads(tracks_data)
                was_empty = self.queue_manager.is_empty()
                self.queue_manager.add_tracks(tracks)
                # If was empty, set first track as current
                if was_empty:
                    self.queue_manager.set_current_index(0)
                event.acceptProposedAction()
                print(f"Added {len(tracks)} tracks to queue")
                return
            except Exception as e:
                print(f"Error adding tracks: {e}")
        
        # Handle reordering within queue (only in Up Next section)
        if mime_data.hasText() and self._drag_source_index is not None and in_up_next:
            current_index = self.queue_manager.get_current_index()
            
            # Only allow reordering if source is from Up Next (after current)
            if self._drag_source_index > current_index:
                # Find drop position in Up Next section
                up_next_content_pos = self.up_next_content.mapFrom(self, drop_pos)
                target_index = None
                
                for album_group in self.up_next_album_groups.values():
                    for track_widget in album_group.track_widgets:
                        widget_pos = track_widget.mapTo(self.up_next_content, QPoint(0, 0))
                        widget_rect = track_widget.geometry()
                        widget_rect.moveTo(widget_pos)
                        
                        if widget_rect.contains(up_next_content_pos):
                            target_index = track_widget.index
                            break
                    if target_index is not None:
                        break
                        
                if target_index is not None and target_index != self._drag_source_index:
                    # Only move if both are in Up Next
                    if target_index > current_index:
                        self.queue_manager.move_track(self._drag_source_index, target_index)
                    
            self._drag_source_index = None
            event.acceptProposedAction()
