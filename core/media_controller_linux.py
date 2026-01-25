"""
Linux Media Controller using MPRIS D-Bus interface
Integrates with Linux desktop media keys and controls
"""

from typing import Optional, Dict, Any
from PySide6.QtCore import Slot, QTimer
from core.media_controller import MediaController
from core.audio_scanner import AudioTrack

try:
    import dbus
    import dbus.service
    from dbus.mainloop.glib import DBusGMainLoop
    DBUS_AVAILABLE = True
except ImportError:
    DBUS_AVAILABLE = False
    print("Warning: dbus-python not available. Linux media key support disabled.")


class LinuxMediaController(MediaController):
    """Linux implementation using MPRIS D-Bus interface."""
    
    MPRIS_INTERFACE = "org.mpris.MediaPlayer2"
    MPRIS_PLAYER_INTERFACE = "org.mpris.MediaPlayer2.Player"
    MPRIS_PATH = "/org/mpris/MediaPlayer2"
    
    def __init__(self) -> None:
        super().__init__()
        self._bus: Optional[Any] = None
        self._mpris_service: Optional[Any] = None
        self._current_track: Optional[AudioTrack] = None
        self._playback_status = "Stopped"
        self._position_us = 0  # Position in microseconds
        
    def register(self) -> bool:
        """Register with D-Bus MPRIS."""
        if not DBUS_AVAILABLE:
            print("LinuxMediaController: dbus-python not available")
            return False
            
        try:
            # Initialize DBus main loop
            DBusGMainLoop(set_as_default=True)
            
            # Get session bus
            self._bus = dbus.SessionBus()
            
            # Request bus name
            bus_name = dbus.service.BusName(
                f"{self.MPRIS_INTERFACE}.DesktopMusicPlayer",
                bus=self._bus
            )
            
            # Create MPRIS service
            self._mpris_service = MPRISService(bus_name, self)
            
            self._is_registered = True
            print("LinuxMediaController: Successfully registered with MPRIS")
            return True
            
        except Exception as e:
            print(f"LinuxMediaController: Registration failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def update_track(self, track: Optional[AudioTrack]) -> None:
        """Update track metadata for MPRIS."""
        self._current_track = track
        if self._mpris_service:
            self._mpris_service.update_metadata()
            
    def update_state(self, is_playing: bool, is_paused: bool) -> None:
        """Update playback state for MPRIS."""
        if is_playing and not is_paused:
            self._playback_status = "Playing"
        elif is_paused:
            self._playback_status = "Paused"
        else:
            self._playback_status = "Stopped"
            
        if self._mpris_service:
            self._mpris_service.update_playback_status()
            
    def get_metadata(self) -> Dict[str, Any]:
        """Get current track metadata in MPRIS format."""
        if not self._current_track:
            return {}
            
        track = self._current_track
        metadata = {
            "mpris:trackid": dbus.ObjectPath(f"/org/mpris/MediaPlayer2/Track/{id(track)}"),
            "xesam:title": track.title or "Unknown Track",
            "xesam:artist": [track.artist or "Unknown Artist"],
            "xesam:album": track.album or "Unknown Album",
        }
        
        if track.file_path:
            metadata["xesam:url"] = str(track.file_path.as_uri())
            
        return metadata
        
    def cleanup(self) -> None:
        """Clean up D-Bus resources."""
        if self._mpris_service:
            self._mpris_service.remove_from_connection()
            self._mpris_service = None
        self._bus = None
        print("LinuxMediaController: Cleaned up")


if DBUS_AVAILABLE:
    class MPRISService(dbus.service.Object):
        """D-Bus service implementing MPRIS2 interface."""
        
        def __init__(self, bus_name: Any, controller: LinuxMediaController) -> None:
            super().__init__(bus_name, LinuxMediaController.MPRIS_PATH)
            self.controller = controller
            
        # org.mpris.MediaPlayer2 interface
        @dbus.service.method(LinuxMediaController.MPRIS_INTERFACE)
        def Raise(self) -> None:
            """Bring the application to the front."""
            pass
            
        @dbus.service.method(LinuxMediaController.MPRIS_INTERFACE)
        def Quit(self) -> None:
            """Quit the application."""
            pass
            
        # org.mpris.MediaPlayer2.Player interface
        @dbus.service.method(LinuxMediaController.MPRIS_PLAYER_INTERFACE)
        def Play(self) -> None:
            """Handle Play command."""
            print("LinuxMediaController: Play command received")
            self.controller.play_pause_requested.emit()
            
        @dbus.service.method(LinuxMediaController.MPRIS_PLAYER_INTERFACE)
        def Pause(self) -> None:
            """Handle Pause command."""
            print("LinuxMediaController: Pause command received")
            self.controller.play_pause_requested.emit()
            
        @dbus.service.method(LinuxMediaController.MPRIS_PLAYER_INTERFACE)
        def PlayPause(self) -> None:
            """Handle PlayPause command."""
            print("LinuxMediaController: PlayPause command received")
            self.controller.play_pause_requested.emit()
            
        @dbus.service.method(LinuxMediaController.MPRIS_PLAYER_INTERFACE)
        def Next(self) -> None:
            """Handle Next command."""
            print("LinuxMediaController: Next command received")
            self.controller.next_requested.emit()
            
        @dbus.service.method(LinuxMediaController.MPRIS_PLAYER_INTERFACE)
        def Previous(self) -> None:
            """Handle Previous command."""
            print("LinuxMediaController: Previous command received")
            self.controller.previous_requested.emit()
            
        @dbus.service.method(LinuxMediaController.MPRIS_PLAYER_INTERFACE)
        def Stop(self) -> None:
            """Handle Stop command."""
            print("LinuxMediaController: Stop command received")
            self.controller.stop_requested.emit()
            
        # Properties
        @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='ss', out_signature='v')
        def Get(self, interface: str, prop: str) -> Any:
            """Get property value."""
            if interface == LinuxMediaController.MPRIS_PLAYER_INTERFACE:
                if prop == "PlaybackStatus":
                    return self.controller._playback_status
                elif prop == "Metadata":
                    return dbus.Dictionary(self.controller.get_metadata(), signature='sv')
                elif prop == "CanPlay":
                    return True
                elif prop == "CanPause":
                    return True
                elif prop == "CanGoNext":
                    return True
                elif prop == "CanGoPrevious":
                    return True
            elif interface == LinuxMediaController.MPRIS_INTERFACE:
                if prop == "Identity":
                    return "Desktop Music Player"
                elif prop == "CanQuit":
                    return True
                elif prop == "CanRaise":
                    return True
            return None
            
        @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='s', out_signature='a{sv}')
        def GetAll(self, interface: str) -> Dict[str, Any]:
            """Get all properties for interface."""
            if interface == LinuxMediaController.MPRIS_PLAYER_INTERFACE:
                return {
                    "PlaybackStatus": self.controller._playback_status,
                    "Metadata": dbus.Dictionary(self.controller.get_metadata(), signature='sv'),
                    "CanPlay": True,
                    "CanPause": True,
                    "CanGoNext": True,
                    "CanGoPrevious": True,
                }
            elif interface == LinuxMediaController.MPRIS_INTERFACE:
                return {
                    "Identity": "Desktop Music Player",
                    "CanQuit": True,
                    "CanRaise": True,
                }
            return {}
            
        def update_metadata(self) -> None:
            """Emit metadata changed signal."""
            self.PropertiesChanged(
                LinuxMediaController.MPRIS_PLAYER_INTERFACE,
                {"Metadata": dbus.Dictionary(self.controller.get_metadata(), signature='sv')},
                []
            )
            
        def update_playback_status(self) -> None:
            """Emit playback status changed signal."""
            self.PropertiesChanged(
                LinuxMediaController.MPRIS_PLAYER_INTERFACE,
                {"PlaybackStatus": self.controller._playback_status},
                []
            )
            
        @dbus.service.signal(dbus.PROPERTIES_IFACE, signature='sa{sv}as')
        def PropertiesChanged(self, interface: str, changed: Dict[str, Any], invalidated: list) -> None:
            """Signal for property changes."""
            pass
