"""
Audio visualizer widget using librosa for real-time frequency analysis
"""

from typing import Optional
import numpy as np
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtGui import QPainter, QLinearGradient, QColor, QPen
import librosa
from core.audio_scanner import AudioTrack


class AudioAnalysisWorker(QThread):
    """Worker thread for audio analysis to prevent UI blocking."""
    
    analysis_ready = Signal(np.ndarray, float)  # spectrum data, sample_rate
    
    def __init__(self) -> None:
        super().__init__()
        self.track: Optional[AudioTrack] = None
        self.should_stop = False
        
    def set_track(self, track: AudioTrack) -> None:
        """Set the track to analyze."""
        self.track = track
        
    def run(self) -> None:
        """Analyze audio file and emit spectrum data."""
        if not self.track:
            return
            
        try:
            # Load audio file with librosa
            y, sr = librosa.load(str(self.track.file_path), sr=22050, duration=None, mono=True)
            
            # Emit the full audio data
            self.analysis_ready.emit(y, sr)
            
        except Exception as e:
            print(f"Audio analysis error: {e}")
            
    def stop(self) -> None:
        """Stop the worker."""
        self.should_stop = True
        self.quit()
        self.wait()


class AudioVisualizerWidget(QWidget):
    """
    Modern audio visualizer displaying frequency spectrum.
    Uses librosa for audio analysis.
    """
    
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(120)
        self.setMaximumHeight(180)
        
        # Audio data
        self.audio_data: Optional[np.ndarray] = None
        self.sample_rate: float = 22050
        self.current_position: float = 0.0
        self.duration: float = 0.0
        
        # Visualization state
        self.n_bars = 64  # Number of frequency bars
        self.bar_heights = np.zeros(self.n_bars)
        self.bar_velocities = np.zeros(self.n_bars)
        self.bar_peaks = np.zeros(self.n_bars)
        self.peak_decay = np.zeros(self.n_bars)
        
        # Style settings
        self.bar_spacing = 2
        self.smoothing = 0.7  # Smoothing factor for bar heights
        self.gravity = 0.95  # Gravity for falling bars
        self.peak_hold = 20  # Frames to hold peak
        
        # Worker thread for audio analysis
        self.worker: Optional[AudioAnalysisWorker] = None
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_visualization)
        self.update_timer.setInterval(33)  # ~30 FPS
        
        # Gradient colors (modern peachy gradient)
        self.gradient_colors = [
            QColor("#ff6b6b"),  # Red
            QColor("#ff8787"),  # Light red
            QColor("#ffa07a"),  # Orange
            QColor("#ffc0cb"),  # Pink
        ]
        
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            AudioVisualizerWidget {
                background-color: rgba(0, 0, 0, 0.03);
                border-radius: 8px;
            }
        """)
        
    def set_track(self, track: AudioTrack) -> None:
        """Set the track to visualize."""
        # Stop previous analysis
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            
        # Reset visualization
        self.bar_heights = np.zeros(self.n_bars)
        self.bar_peaks = np.zeros(self.n_bars)
        self.audio_data = None
        
        # Start new analysis
        self.worker = AudioAnalysisWorker()
        self.worker.set_track(track)
        self.worker.analysis_ready.connect(self._on_analysis_ready)
        self.worker.start()
        
    def set_duration(self, duration: float) -> None:
        """Set track duration."""
        self.duration = duration
        
    def update_position(self, position: float) -> None:
        """Update playback position."""
        self.current_position = position
        
    def start(self) -> None:
        """Start visualization updates."""
        self.update_timer.start()
        
    def stop(self) -> None:
        """Stop visualization updates."""
        self.update_timer.stop()
        # Smoothly animate bars to zero
        for i in range(self.n_bars):
            self.bar_heights[i] *= 0.8
        self.update()
        
    def pause(self) -> None:
        """Pause visualization (keep current state but stop updates)."""
        self.update_timer.stop()
        
    def resume(self) -> None:
        """Resume visualization."""
        self.update_timer.start()
        
    def _on_analysis_ready(self, audio_data: np.ndarray, sample_rate: float) -> None:
        """Handle analyzed audio data."""
        self.audio_data = audio_data
        self.sample_rate = sample_rate
        
    def _update_visualization(self) -> None:
        """Update visualization based on current playback position."""
        if self.audio_data is None or len(self.audio_data) == 0:
            self.update()
            return
            
        try:
            # Calculate the current frame position
            frame_pos = int(self.current_position * self.sample_rate)
            
            # Extract a window of audio around current position
            window_size = 2048
            hop_length = 512
            
            # Get audio window
            start = max(0, frame_pos - window_size // 2)
            end = min(len(self.audio_data), start + window_size)
            
            if end - start < window_size:
                # Pad if necessary
                audio_window = np.zeros(window_size)
                audio_window[:end-start] = self.audio_data[start:end]
            else:
                audio_window = self.audio_data[start:end]
                
            # Apply window function
            audio_window = audio_window * np.hamming(len(audio_window))
            
            # Compute FFT
            fft = np.fft.rfft(audio_window)
            magnitude = np.abs(fft)
            
            # Convert to dB scale
            magnitude = librosa.amplitude_to_db(magnitude, ref=np.max)
            
            # Normalize to 0-1 range
            magnitude = (magnitude + 80) / 80  # Assuming -80dB to 0dB range
            magnitude = np.clip(magnitude, 0, 1)
            
            # Bin the frequencies into bars
            n_fft_bins = len(magnitude)
            bins_per_bar = max(1, n_fft_bins // self.n_bars)
            
            new_heights = np.zeros(self.n_bars)
            for i in range(self.n_bars):
                start_bin = i * bins_per_bar
                end_bin = min((i + 1) * bins_per_bar, n_fft_bins)
                if end_bin > start_bin:
                    # Use max value in bin range for more dynamic visualization
                    new_heights[i] = np.max(magnitude[start_bin:end_bin])
                    
            # Apply smoothing
            self.bar_heights = (self.smoothing * self.bar_heights + 
                              (1 - self.smoothing) * new_heights)
            
            # Update peaks
            for i in range(self.n_bars):
                if self.bar_heights[i] > self.bar_peaks[i]:
                    self.bar_peaks[i] = self.bar_heights[i]
                    self.peak_decay[i] = self.peak_hold
                else:
                    if self.peak_decay[i] > 0:
                        self.peak_decay[i] -= 1
                    else:
                        self.bar_peaks[i] *= self.gravity
                        
        except Exception as e:
            print(f"Visualization update error: {e}")
            
        self.update()
        
    def paintEvent(self, event) -> None:
        """Paint the visualizer."""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        # Calculate bar dimensions
        bar_width = (width - (self.n_bars - 1) * self.bar_spacing) / self.n_bars
        
        # Create gradient
        gradient = QLinearGradient(0, height, 0, 0)
        gradient.setColorAt(0.0, self.gradient_colors[0])
        gradient.setColorAt(0.4, self.gradient_colors[1])
        gradient.setColorAt(0.7, self.gradient_colors[2])
        gradient.setColorAt(1.0, self.gradient_colors[3])
        
        # Draw bars
        for i in range(self.n_bars):
            x = i * (bar_width + self.bar_spacing)
            bar_height = self.bar_heights[i] * height * 0.9
            y = height - bar_height
            
            # Draw main bar with gradient
            painter.fillRect(
                int(x), int(y),
                int(bar_width), int(bar_height),
                gradient
            )
            
            # Draw peak indicator
            peak_y = height - (self.bar_peaks[i] * height * 0.9)
            if self.bar_peaks[i] > 0.05:  # Only draw visible peaks
                painter.setPen(QPen(self.gradient_colors[3], 2))
                painter.drawLine(
                    int(x), int(peak_y),
                    int(x + bar_width), int(peak_y)
                )
                
        painter.end()
        
    def cleanup(self) -> None:
        """Cleanup resources."""
        self.stop()
        if self.worker and self.worker.isRunning():
            self.worker.stop()
