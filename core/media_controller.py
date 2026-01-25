"""
OS-native media key controller for Windows and Linux
Provides integration with system media controls (SMTC on Windows, MPRIS on Linux)
"""

import sys
from abc import ABCMeta, abstractmethod
from typing import Optional
from PySide6.QtCore import QObject, Signal, Slot
from core.audio_scanner import AudioTrack


def get_platform() -> str:
    """Detect current platform."""
    if sys.platform == "win32":
        return "windows"
    elif sys.platform.startswith("linux"):
        return "linux"
    elif sys.platform == "darwin":
        return "macos"
    return "unknown"


# Combine Qt metaclass with ABC metaclass
class MediaControllerMeta(type(QObject), ABCMeta):
    """Metaclass that combines QObject's metaclass with ABCMeta."""
    pass


class MediaController(QObject, metaclass=MediaControllerMeta):
    """Abstract base class for platform-specific media controllers."""
    
    # Signals emitted when OS media keys are pressed
    play_pause_requested = Signal()
    next_requested = Signal()
    previous_requested = Signal()
    stop_requested = Signal()
    
    def __init__(self) -> None:
        super().__init__()
        self._is_registered = False
        
    @abstractmethod
    def register(self) -> bool:
        """
        Register with OS media control system.
        Returns True if successful.
        """
        pass
        
    @abstractmethod
    def update_track(self, track: Optional[AudioTrack]) -> None:
        """Update current track metadata in OS media display."""
        pass
        
    @abstractmethod
    def update_state(self, is_playing: bool, is_paused: bool) -> None:
        """Update playback state in OS media display."""
        pass
        
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources and unregister from OS."""
        pass
        
    def is_registered(self) -> bool:
        """Check if controller is registered with OS."""
        return self._is_registered


class DummyMediaController(MediaController):
    """Fallback controller that does nothing (for unsupported platforms)."""
    
    def register(self) -> bool:
        print("MediaController: Platform not supported, using dummy controller")
        self._is_registered = True
        return True
        
    def update_track(self, track: Optional[AudioTrack]) -> None:
        pass
        
    def update_state(self, is_playing: bool, is_paused: bool) -> None:
        pass
        
    def cleanup(self) -> None:
        pass


def create_media_controller() -> MediaController:
    """Factory function to create platform-specific media controller."""
    platform = get_platform()
    
    if platform == "windows":
        try:
            from core.media_controller_windows import WindowsMediaController
            return WindowsMediaController()
        except ImportError as e:
            print(f"Failed to import Windows media controller: {e}")
            return DummyMediaController()
    elif platform == "linux":
        try:
            from core.media_controller_linux import LinuxMediaController
            return LinuxMediaController()
        except ImportError as e:
            print(f"Failed to import Linux media controller: {e}")
            return DummyMediaController()
    else:
        return DummyMediaController()
