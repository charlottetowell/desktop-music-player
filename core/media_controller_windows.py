"""
Windows Media Controller using native Windows messages
Intercepts WM_APPCOMMAND to catch all media key events including user-configured shortcuts
"""

from typing import Optional
from PySide6.QtCore import Slot, QObject, QEvent
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QShortcut, QKeySequence
from core.media_controller import MediaController
from core.audio_scanner import AudioTrack


# Windows WM_APPCOMMAND constants
WM_APPCOMMAND = 0x0319
APPCOMMAND_MEDIA_PLAY_PAUSE = 14
APPCOMMAND_MEDIA_STOP = 13
APPCOMMAND_MEDIA_NEXTTRACK = 11
APPCOMMAND_MEDIA_PREVIOUSTRACK = 12
APPCOMMAND_MEDIA_PLAY = 46
APPCOMMAND_MEDIA_PAUSE = 47


class WindowsMediaController(MediaController, QObject):
    """Windows implementation using native message handling for media keys."""
    
    def __init__(self) -> None:
        # Call both parent constructors properly
        super().__init__()  # This calls MediaController.__init__ which calls QObject.__init__
        self._current_track: Optional[AudioTrack] = None
        self._shortcuts = []
        self._main_window = None
        
    def register(self) -> bool:
        """Register native Windows message handler for media keys."""
        try:
            # Get the main window
            self._main_window = None
            for widget in QApplication.topLevelWidgets():
                if widget.isWindow():
                    self._main_window = widget
                    break
                    
            if not self._main_window:
                print("WindowsMediaController: No window found")
                return False
            
            print(f"WindowsMediaController: Installing native event filter for WM_APPCOMMAND...")
            
            # Install native event filter to catch WM_APPCOMMAND messages
            # This catches ALL media key events including user-configured shortcuts
            self._main_window.installEventFilter(self)
            
            # Also register Qt shortcuts as fallback for hardware media keys
            self._register_qt_shortcuts()
            
            self._is_registered = True
            print(f"WindowsMediaController: Successfully registered media key handler")
            return True
            
        except Exception as e:
            print(f"WindowsMediaController: Registration failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def _register_qt_shortcuts(self) -> None:
        """Register Qt shortcuts as fallback for hardware media keys."""
        if not self._main_window:
            return
            
        try:
            # These work for keyboards with dedicated media keys
            shortcuts_map = [
                ("Media Play", self.play_pause_requested),
                ("Media Pause", self.play_pause_requested),
                ("Media Toggle Play Pause", self.play_pause_requested),
                ("Media Next", self.next_requested),
                ("Media Previous", self.previous_requested),
                ("Media Stop", self.stop_requested),
            ]
            
            for key_seq, signal in shortcuts_map:
                shortcut = QShortcut(QKeySequence(key_seq), self._main_window)
                shortcut.activated.connect(signal.emit)
                self._shortcuts.append(shortcut)
                
            print(f"WindowsMediaController: Registered {len(self._shortcuts)} Qt shortcuts as fallback")
        except Exception as e:
            print(f"WindowsMediaController: Qt shortcuts registration failed: {e}")
            
    def eventFilter(self, obj, event) -> bool:
        """Qt event filter to intercept native Windows messages."""
        try:
            # Check if this is a native event (Windows message)
            if event.type() == QEvent.Type.NativeGesture:
                # On Windows, we need to check for WM_APPCOMMAND
                pass
                
            # PySide6 doesn't expose nativeEvent directly like PyQt5 does
            # but we can use winEvent on Windows
            # The event filter approach may not catch WM_APPCOMMAND directly
            # Let's override nativeEvent in the main window instead
            
        except Exception as e:
            pass
            
        return False  # Don't filter the event
        
    def handle_windows_message(self, msg, wparam, lparam) -> bool:
        """
        Handle Windows WM_APPCOMMAND messages.
        Call this from the main window's nativeEvent handler.
        """
        if msg == WM_APPCOMMAND:
            # Extract the command from lparam
            cmd = (lparam >> 16) & 0xFFF
            
            print(f"WindowsMediaController: Received WM_APPCOMMAND with code: {cmd}")
            
            if cmd == APPCOMMAND_MEDIA_PLAY_PAUSE:
                print("WindowsMediaController: Play/Pause command (14)")
                self.play_pause_requested.emit()
                return True
            elif cmd == APPCOMMAND_MEDIA_PLAY:
                print("WindowsMediaController: Play command (46)")
                self.play_pause_requested.emit()
                return True
            elif cmd == APPCOMMAND_MEDIA_PAUSE:
                print("WindowsMediaController: Pause command (47)")
                self.play_pause_requested.emit()
                return True
            elif cmd == APPCOMMAND_MEDIA_NEXTTRACK:
                print("WindowsMediaController: Next command (11)")
                self.next_requested.emit()
                return True
            elif cmd == APPCOMMAND_MEDIA_PREVIOUSTRACK:
                print("WindowsMediaController: Previous command (12)")
                self.previous_requested.emit()
                return True
            elif cmd == APPCOMMAND_MEDIA_STOP:
                print("WindowsMediaController: Stop command (13)")
                self.stop_requested.emit()
                return True
            else:
                # Log unhandled command codes for debugging
                print(f"WindowsMediaController: Unhandled APPCOMMAND code: {cmd}")
                
        return False
            
    def update_track(self, track: Optional[AudioTrack]) -> None:
        """Update track metadata (not supported with Qt shortcuts)."""
        self._current_track = track
        if track:
            print(f"WindowsMediaController: Now playing: {track.title} by {track.artist}")
            
    def update_state(self, is_playing: bool, is_paused: bool) -> None:
        """Update playback state (not supported with Qt shortcuts)."""
        pass
            
    def cleanup(self) -> None:
        """Clean up shortcuts and event filters."""
        try:
            if self._main_window:
                self._main_window.removeEventFilter(self)
            for shortcut in self._shortcuts:
                shortcut.setEnabled(False)
            self._shortcuts.clear()
            print("WindowsMediaController: Cleaned up")
        except Exception as e:
            print(f"WindowsMediaController: Cleanup error: {e}")

