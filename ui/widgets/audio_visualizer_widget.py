"""
Audio visualizer widget using librosa for real-time waveform visualization
"""

from typing import Optional
import numpy as np
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, Signal, QThread, QPointF
from PySide6.QtGui import QPainter, QLinearGradient, QColor, QPen, QPainterPath
import librosa
from core.audio_scanner import AudioTrack


class AudioAnalysisWorker(QThread):
    """Worker thread for audio analysis to prevent UI blocking."""
    
    analysis_ready = Signal(np.ndarray, float)  # waveform data, sample_rate
    
    def __init__(self) -> None:
        super().__init__()
        self.track: Optional[AudioTrack] = None
        self.should_stop = False
        
    def set_track(self, track: AudioTrack) -> None:
        """Set the track to analyze."""
        self.track = track
        
    def run(self) -> None:
        """Analyze audio file and emit waveform data."""
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
    Modern audio visualizer displaying waveform.
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
        
        # Waveform visualization state
        self.n_samples = 200  # Number of samples to display in waveform
        self.waveform_points = np.zeros(self.n_samples)
        self.smoothing = 0.6  # Smoothing factor for waveform
        
        # Style settings
        self.line_width = 3.0
        self.glow_enabled = True
        self.amplitude_boost = 2.5  # Boost amplitude for more dramatic effect
        self.compression_factor = 0.7  # Compress dynamic range to make quiet parts visible
        
        # Worker thread for audio analysis
        self.worker: Optional[AudioAnalysisWorker] = None
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_visualization)
        self.update_timer.setInterval(33)  # ~30 FPS
        
        # Gradient colors (purple theme)
        self.gradient_colors = [
            QColor("#b794f6"),  # Lavender
            QColor("#9d7ed9"),  # Purple
            QColor("#7b5db8"),  # Deep purple
            QColor("#5a3d99"),  # Darker purple
        ]
        
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            AudioVisualizerWidget {
                background-color: transparent;
                border-radius: 0px;
            }
        """)
        
    def set_track(self, track: AudioTrack) -> None:
        """Set the track to visualize."""
        # Stop previous analysis
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            
        # Reset visualization
        self.waveform_points = np.zeros(self.n_samples)
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
        # Smoothly animate waveform to zero
        self.waveform_points *= 0.5
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
        """Update waveform visualization based on current playback position."""
        if self.audio_data is None or len(self.audio_data) == 0:
            self.update()
            return
            
        try:
            # Calculate the current frame position
            frame_pos = int(self.current_position * self.sample_rate)
            
            # Define window size for waveform display (show ~0.5 seconds of audio)
            window_size = int(self.sample_rate * 0.5)
            
            # Get audio window centered at current position
            start = max(0, frame_pos - window_size // 2)
            end = min(len(self.audio_data), start + window_size)
            
            if end - start < window_size:
                # Pad if necessary
                audio_window = np.zeros(window_size)
                audio_window[:end-start] = self.audio_data[start:end]
            else:
                audio_window = self.audio_data[start:end]
                
            # Downsample to n_samples points for display
            if len(audio_window) > self.n_samples:
                # Use stride to downsample evenly
                indices = np.linspace(0, len(audio_window) - 1, self.n_samples, dtype=int)
                new_points = audio_window[indices]
            else:
                # Interpolate if we have fewer samples
                new_points = np.interp(
                    np.linspace(0, len(audio_window) - 1, self.n_samples),
                    np.arange(len(audio_window)),
                    audio_window
                )
            
            # Apply amplitude boost and compression for more dramatic effect
            # Compression: apply power function to reduce dynamic range
            sign = np.sign(new_points)
            magnitude = np.abs(new_points)
            compressed = np.power(magnitude, self.compression_factor)
            new_points = sign * compressed * self.amplitude_boost
            
            # Clip to prevent overflow
            new_points = np.clip(new_points, -1.0, 1.0)
            
            # Apply smoothing for animation
            self.waveform_points = (self.smoothing * self.waveform_points + 
                                   (1 - self.smoothing) * new_points)
                        
        except Exception as e:
            print(f"Visualization update error: {e}")
            
        self.update()
        
    def paintEvent(self, event) -> None:
        """Paint the waveform visualizer."""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        center_y = height / 2
        
        # Create gradient for waveform
        gradient = QLinearGradient(0, 0, width, 0)
        gradient.setColorAt(0.0, self.gradient_colors[0])
        gradient.setColorAt(0.33, self.gradient_colors[1])
        gradient.setColorAt(0.66, self.gradient_colors[2])
        gradient.setColorAt(1.0, self.gradient_colors[3])
        
        # Draw waveform with multiple glow layers for more dramatic effect
        if self.glow_enabled:
            # Outer glow (widest, most transparent)
            outer_glow = QPen(QColor(self.gradient_colors[2]))
            outer_glow.setWidth(int(self.line_width + 8))
            outer_glow.setCapStyle(Qt.RoundCap)
            outer_glow.setJoinStyle(Qt.RoundJoin)
            glow_color = QColor(self.gradient_colors[2])
            glow_color.setAlpha(40)
            outer_glow.setColor(glow_color)
            painter.setPen(outer_glow)
            self._draw_waveform_path(painter, width, height, center_y)
            
            # Inner glow (medium thickness)
            inner_glow = QPen(QColor(self.gradient_colors[1]))
            inner_glow.setWidth(int(self.line_width + 4))
            inner_glow.setCapStyle(Qt.RoundCap)
            inner_glow.setJoinStyle(Qt.RoundJoin)
            glow_color2 = QColor(self.gradient_colors[1])
            glow_color2.setAlpha(80)
            inner_glow.setColor(glow_color2)
            painter.setPen(inner_glow)
            self._draw_waveform_path(painter, width, height, center_y)
        
        # Draw main waveform
        main_pen = QPen(gradient, self.line_width)
        main_pen.setCapStyle(Qt.RoundCap)
        main_pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(main_pen)
        
        self._draw_waveform_path(painter, width, height, center_y)
        
        # Draw center line (subtle)
        center_line_pen = QPen(QColor(0, 0, 0, 30), 1)
        painter.setPen(center_line_pen)
        painter.drawLine(0, int(center_y), width, int(center_y))
        
        painter.end()
        
    def _draw_waveform_path(self, painter: QPainter, width: int, height: int, center_y: float) -> None:
        """Draw the waveform path."""
        if len(self.waveform_points) < 2:
            return
            
        path = QPainterPath()
        
        # Calculate x position for each sample
        x_step = width / (self.n_samples - 1)
        
        # Start path
        first_y = center_y + (self.waveform_points[0] * height * 0.45)
        path.moveTo(0, first_y)
        
        # Draw waveform with more dramatic scaling
        for i in range(1, self.n_samples):
            x = i * x_step
            # Scale to 48% of height for more dramatic effect (was 45%)
            y = center_y + (self.waveform_points[i] * height * 0.48)
            path.lineTo(x, y)
        
        painter.drawPath(path)
        
    def cleanup(self) -> None:
        """Cleanup resources."""
        self.stop()
        if self.worker and self.worker.isRunning():
            self.worker.stop()
