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
        self._seek_position: Optional[float] = None  # Target seek position
        self._pause_position = 0.0  # Position when paused
        
        # Timer for position updates
        self._position_timer = QTimer()
        self._position_timer.timeout.connect(self._update_position)
        self._position_timer.setInterval(100)  # Update every 100ms
        
    def play(self, track: AudioTrack, start_position: float = 0.0) -> bool:
        """
        Start playing a track.
        
        Args:
            track: AudioTrack to play
            start_position: Position in seconds to start from (for seeking)
            
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
            self._position = start_position
            self._seek_position = start_position if start_position > 0 else None
            
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
            # Use file streaming for all cases - simple and works
            stream = miniaudio.stream_file(file_path)
            
            # If seeking, we need to skip samples
            if self._seek_position and self._seek_position > 0:
                # Decode to get format info first
                decoded = miniaudio.decode_file(file_path)
                sample_rate = decoded.sample_rate
                nchannels = decoded.nchannels
                
                # Calculate how many samples to skip
                seek_frame = int(self._seek_position * sample_rate)
                samples_to_skip = seek_frame * nchannels
                
                # Consume the stream to skip to position
                consumed = 0
                for chunk in stream:
                    chunk_len = len(chunk)
                    if consumed + chunk_len > samples_to_skip:
                        # This chunk contains our start position
                        break
                    consumed += chunk_len
                
            with miniaudio.PlaybackDevice() as device:
                self._device = device
                device.start(stream)
                self._wait_for_playback()
                        
        except Exception as e:
            print(f"Playback error: {e}")
            import traceback
            traceback.print_exc()
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
    
    def _wait_for_playback(self) -> None:
        """Wait for playback to finish with pause support."""
        start_time = time.time()
        pause_accumulated = 0.0
        last_pause_time = None
        
        while self._is_playing and not self._stop_playback:
            if self._is_paused:
                if last_pause_time is None:
                    last_pause_time = time.time()
                time.sleep(0.05)
            else:
                if last_pause_time is not None:
                    pause_accumulated += time.time() - last_pause_time
                    last_pause_time = None
                
                # Update position estimate
                elapsed = time.time() - start_time - pause_accumulated
                self._position = (self._seek_position or 0.0) + elapsed
                
                time.sleep(0.05)  # Check every 50ms
            
            # Check if playback finished
            if self._position >= self._duration and self._duration > 0:
                break
                
    def pause(self) -> None:
        """Pause playback."""
        if self._is_playing and not self._is_paused:
            self._is_paused = True
            self._pause_position = self._position
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
        Seek to position in seconds by restarting playback from that position.
        """
        if self.current_track and 0 <= position <= self._duration:
            was_paused = self._is_paused
            self.play(self.current_track, start_position=position)
            if was_paused:
                # If we were paused, pause again after seeking
                time.sleep(0.1)  # Brief delay to let playback start
                self.pause()
            
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
