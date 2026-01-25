"""
Audio playback engine using miniaudio for cross-platform support
"""

from typing import Optional, List
from pathlib import Path
import threading
import time
from PySide6.QtCore import QObject, Signal, QTimer
import miniaudio
from core.audio_scanner import AudioTrack


class PlaybackHistory:
    """Manages playback history for back-skipping."""
    
    def __init__(self, max_size: int = 15) -> None:
        self.max_size = max_size
        self._history: List[AudioTrack] = []
        
    def add(self, track: AudioTrack) -> None:
        """Add a track to history."""
        self._history.append(track)
        # Keep only last max_size tracks
        if len(self._history) > self.max_size:
            self._history.pop(0)
            
    def get_previous(self) -> Optional[AudioTrack]:
        """Get the previous track from history."""
        if len(self._history) >= 2:
            # Remove current track
            self._history.pop()
            # Get and return previous
            return self._history[-1] if self._history else None
        return None
        
    def clear(self) -> None:
        """Clear history."""
        self._history.clear()
        
    def size(self) -> int:
        """Get history size."""
        return len(self._history)


class AudioEngine(QObject):
    """Cross-platform audio playback engine."""
    
    # Signals
    playback_started = Signal(AudioTrack)
    playback_paused = Signal()
    playback_resumed = Signal()
    playback_stopped = Signal()
    playback_finished = Signal()  # Track finished playing
    position_changed = Signal(float)  # Current position in seconds
    duration_changed = Signal(float)  # Total duration in seconds
    error_occurred = Signal(str)
    
    def __init__(self) -> None:
        super().__init__()
        self.current_track: Optional[AudioTrack] = None
        self.history = PlaybackHistory()
        
        self._device: Optional[miniaudio.PlaybackDevice] = None
        self._decoder: Optional[miniaudio.Decoder] = None
        self._stream: Optional[miniaudio.stream_file] = None
        self._is_playing = False
        self._is_paused = False
        self._position = 0.0
        self._duration = 0.0
        self._playback_thread: Optional[threading.Thread] = None
        self._stop_playback = False
        
        # Timer for position updates
        self._position_timer = QTimer()
        self._position_timer.timeout.connect(self._update_position)
        self._position_timer.setInterval(100)  # Update every 100ms
        
    def play(self, track: AudioTrack) -> bool:
        """
        Start playing a track.
        
        Args:
            track: AudioTrack to play
            
        Returns:
            True if playback started successfully
        """
        try:
            # Stop current playback if any
            self.stop()
            
            self.current_track = track
            file_path = str(track.file_path)
            
            # Decode the audio file to get duration
            try:
                decoder = miniaudio.decode_file(file_path)
                self._duration = len(decoder.samples) / decoder.sample_rate / decoder.nchannels
                self.duration_changed.emit(self._duration)
            except Exception as e:
                print(f"Could not decode file for duration: {e}")
                self._duration = 0.0
            
            # Start playback in separate thread
            self._stop_playback = False
            self._is_playing = True
            self._is_paused = False
            self._position = 0.0
            
            self._playback_thread = threading.Thread(target=self._playback_worker, args=(file_path,))
            self._playback_thread.daemon = True
            self._playback_thread.start()
            
            # Start position timer
            self._position_timer.start()
            
            # Add to history
            self.history.add(track)
            
            self.playback_started.emit(track)
            return True
            
        except Exception as e:
            error_msg = f"Failed to play track: {e}"
            print(error_msg)
            self.error_occurred.emit(error_msg)
            return False
            
    def _playback_worker(self, file_path: str) -> None:
        """Worker thread for audio playback."""
        try:
            # Stream the file
            stream = miniaudio.stream_file(file_path)
            
            with miniaudio.PlaybackDevice() as device:
                self._device = device
                
                # Start streaming
                device.start(stream)
                
                # Wait for playback to finish or stop signal
                start_time = time.time()
                while self._is_playing and not self._stop_playback:
                    if not self._is_paused:
                        # Update position estimate
                        self._position = time.time() - start_time
                        
                    time.sleep(0.05)  # Check every 50ms
                    
                    # Check if playback finished
                    if self._position >= self._duration and self._duration > 0:
                        break
                        
        except Exception as e:
            print(f"Playback error: {e}")
            self.error_occurred.emit(str(e))
        finally:
            self._device = None
            self._is_playing = False
            
            if not self._stop_playback and self._position >= self._duration - 0.5:
                # Track finished naturally
                self.playback_finished.emit()
            else:
                # Track was stopped
                self.playback_stopped.emit()
                
    def pause(self) -> None:
        """Pause playback."""
        if self._is_playing and not self._is_paused:
            self._is_paused = True
            self._position_timer.stop()
            self.playback_paused.emit()
            
    def resume(self) -> None:
        """Resume playback."""
        if self._is_playing and self._is_paused:
            self._is_paused = False
            self._position_timer.start()
            self.playback_resumed.emit()
            
    def stop(self) -> None:
        """Stop playback."""
        if self._is_playing:
            self._stop_playback = True
            self._is_playing = False
            self._is_paused = False
            self._position_timer.stop()
            
            # Wait for thread to finish
            if self._playback_thread and self._playback_thread.is_alive():
                self._playback_thread.join(timeout=1.0)
                
            self.playback_stopped.emit()
            
    def toggle_play_pause(self) -> None:
        """Toggle between play and pause."""
        if self._is_paused:
            self.resume()
        elif self._is_playing:
            self.pause()
            
    def seek(self, position: float) -> None:
        """
        Seek to position in seconds.
        Note: Basic seeking support - may need restart for some formats.
        """
        if 0 <= position <= self._duration:
            self._position = position
            self.position_changed.emit(position)
            
    def get_position(self) -> float:
        """Get current playback position in seconds."""
        return self._position
        
    def get_duration(self) -> float:
        """Get track duration in seconds."""
        return self._duration
        
    def is_playing(self) -> bool:
        """Check if audio is currently playing."""
        return self._is_playing and not self._is_paused
        
    def is_paused(self) -> bool:
        """Check if audio is paused."""
        return self._is_paused
        
    def get_previous_track(self) -> Optional[AudioTrack]:
        """Get previous track from history."""
        return self.history.get_previous()
        
    def _update_position(self) -> None:
        """Timer callback to emit position updates."""
        if self._is_playing and not self._is_paused:
            self.position_changed.emit(self._position)
