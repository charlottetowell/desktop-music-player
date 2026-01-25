"""
Queue manager for playback queue operations
"""

from typing import List, Optional, Dict, Any
from PySide6.QtCore import QObject, Signal
from core.audio_scanner import AudioTrack, AudioScanner
from pathlib import Path


class QueueManager(QObject):
    """Manages the playback queue with add, remove, and reorder operations."""
    
    queue_changed = Signal()  # Emitted when queue structure changes
    current_track_changed = Signal(object)  # Emits AudioTrack or None
    track_added = Signal(AudioTrack)  # Emitted when a track is added
    track_removed = Signal(int)  # Emits index of removed track
    
    def __init__(self) -> None:
        super().__init__()
        self._queue: List[AudioTrack] = []
        self._current_index: int = -1
        
    def add_track(self, track: AudioTrack) -> None:
        """Add a single track to the end of the queue."""
        self._queue.append(track)
        self.track_added.emit(track)
        self.queue_changed.emit()
        
    def add_tracks(self, tracks: List[AudioTrack]) -> None:
        """Add multiple tracks to the end of the queue."""
        if not tracks:
            return
        self._queue.extend(tracks)
        for track in tracks:
            self.track_added.emit(track)
        self.queue_changed.emit()
        
    def insert_track(self, index: int, track: AudioTrack) -> None:
        """Insert a track at a specific position."""
        if 0 <= index <= len(self._queue):
            self._queue.insert(index, track)
            # Adjust current index if needed
            if index <= self._current_index:
                self._current_index += 1
            self.track_added.emit(track)
            self.queue_changed.emit()
            
    def remove_track(self, index: int) -> Optional[AudioTrack]:
        """Remove track at specified index."""
        if 0 <= index < len(self._queue):
            track = self._queue.pop(index)
            # Adjust current index if needed
            if index < self._current_index:
                self._current_index -= 1
            elif index == self._current_index:
                self._current_index = -1
                self.current_track_changed.emit(None)
            self.track_removed.emit(index)
            self.queue_changed.emit()
            return track
        return None
        
    def move_track(self, from_index: int, to_index: int) -> bool:
        """Move a track from one position to another."""
        if (0 <= from_index < len(self._queue) and 
            0 <= to_index < len(self._queue) and 
            from_index != to_index):
            
            track = self._queue.pop(from_index)
            self._queue.insert(to_index, track)
            
            # Adjust current index if needed
            if self._current_index == from_index:
                self._current_index = to_index
            elif from_index < self._current_index <= to_index:
                self._current_index -= 1
            elif to_index <= self._current_index < from_index:
                self._current_index += 1
                
            self.queue_changed.emit()
            return True
        return False
        
    def clear_queue(self) -> None:
        """Clear all tracks from the queue."""
        self._queue.clear()
        self._current_index = -1
        self.current_track_changed.emit(None)
        self.queue_changed.emit()
        
    def get_queue(self) -> List[AudioTrack]:
        """Get a copy of the current queue."""
        return self._queue.copy()
        
    def get_track(self, index: int) -> Optional[AudioTrack]:
        """Get track at specified index."""
        if 0 <= index < len(self._queue):
            return self._queue[index]
        return None
        
    def get_current_track(self) -> Optional[AudioTrack]:
        """Get the currently playing track."""
        if 0 <= self._current_index < len(self._queue):
            return self._queue[self._current_index]
        return None
        
    def get_current_index(self) -> int:
        """Get the index of the currently playing track."""
        return self._current_index
        
    def set_current_index(self, index: int) -> None:
        """Set the currently playing track by index."""
        if -1 <= index < len(self._queue):
            self._current_index = index
            track = self.get_current_track()
            self.current_track_changed.emit(track)
        
    def next_track(self) -> Optional[AudioTrack]:
        """Move to the next track in the queue."""
        if self._current_index < len(self._queue) - 1:
            self._current_index += 1
            track = self.get_current_track()
            self.current_track_changed.emit(track)
            return track
        return None
        
    def previous_track(self) -> Optional[AudioTrack]:
        """Move to the previous track in the queue."""
        if self._current_index > 0:
            self._current_index -= 1
            track = self.get_current_track()
            self.current_track_changed.emit(track)
            return track
        return None
        
    def has_next(self) -> bool:
        """Check if there is a next track."""
        return self._current_index < len(self._queue) - 1
        
    def has_previous(self) -> bool:
        """Check if there is a previous track."""
        return self._current_index > 0
        
    def remove_current_track(self) -> Optional[AudioTrack]:
        """Remove the currently playing track and move to next."""
        if 0 <= self._current_index < len(self._queue):
            current_idx = self._current_index
            track = self._queue.pop(current_idx)
            
            # Don't increment current_index, as removal shifts items down
            # If we were at the last track, move back
            if self._current_index >= len(self._queue):
                self._current_index = len(self._queue) - 1
                
            # Emit signals
            self.track_removed.emit(current_idx)
            next_track = self.get_current_track()
            self.current_track_changed.emit(next_track)
            self.queue_changed.emit()
            return track
        return None
        
    def size(self) -> int:
        """Get the number of tracks in the queue."""
        return len(self._queue)
        
    def is_empty(self) -> bool:
        """Check if the queue is empty."""
        return len(self._queue) == 0
    
    def serialize(self) -> List[Dict[str, Any]]:
        """Serialize queue to a list of dictionaries for persistence."""
        serialized = []
        for track in self._queue:
            serialized.append({
                'file_path': str(track.file_path),
                'title': track.title,
                'artist': track.artist,
                'album': track.album,
                'year': track.year,
                'track_number': track.track_number,
                'duration': track.duration,
                'file_size': track.file_size,
                'format': track.format,
            })
        return serialized
    
    def restore(self, serialized_queue: List[Dict[str, Any]], current_index: int) -> None:
        """Restore queue from serialized data."""
        self._queue.clear()
        scanner = AudioScanner()  # For extracting album art
        
        for track_data in serialized_queue:
            try:
                file_path = Path(track_data['file_path'])
                
                # Only add if file still exists
                if not file_path.exists():
                    continue
                    
                track = AudioTrack(
                    file_path=file_path,
                    title=track_data.get('title', 'Unknown Title'),
                    artist=track_data.get('artist', 'Unknown Artist'),
                    album=track_data.get('album', 'Unknown Album'),
                    year=track_data.get('year', 'Unknown'),
                    track_number=track_data.get('track_number'),
                    duration=track_data.get('duration', 0.0),
                    file_size=track_data.get('file_size', 0),
                    format=track_data.get('format', 'unknown'),
                )
                
                # Re-extract album art from the file
                track.album_art_data = scanner._extract_album_art(file_path)
                
                self._queue.append(track)
            except Exception as e:
                print(f"Could not restore track: {e}")
        
        # Set current index if valid
        if 0 <= current_index < len(self._queue):
            self._current_index = current_index
        else:
            self._current_index = -1
        
        self.queue_changed.emit()
        if self._current_index >= 0:
            self.current_track_changed.emit(self.get_current_track())
