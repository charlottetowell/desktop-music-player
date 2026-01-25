"""
Application settings manager with persistent storage
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any


class Settings:
    """Manage application settings with JSON persistence."""
    
    _instance = None
    _settings_file = Path.home() / ".peachy-player" / "settings.json"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self._data = {}
        self._ensure_settings_dir()
        self._load()
    
    def _ensure_settings_dir(self) -> None:
        """Create settings directory if it doesn't exist."""
        self._settings_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _load(self) -> None:
        """Load settings from file."""
        if self._settings_file.exists():
            try:
                with open(self._settings_file, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load settings: {e}")
                self._data = {}
        else:
            self._data = {}
    
    def _save(self) -> None:
        """Save settings to file."""
        try:
            with open(self._settings_file, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error: Could not save settings: {e}")
    
    def get(self, key: str, default=None):
        """Get a setting value."""
        return self._data.get(key, default)
    
    def set(self, key: str, value) -> None:
        """Set a setting value and save."""
        self._data[key] = value
        self._save()
    
    def get_music_folder(self) -> Optional[str]:
        """Get the configured music folder path."""
        return self.get("music_folder")
    
    def set_music_folder(self, path: str) -> None:
        """Set the music folder path."""
        self.set("music_folder", path)
    
    def clear_music_folder(self) -> None:
        """Clear the music folder setting."""
        if "music_folder" in self._data:
            del self._data["music_folder"]
            self._save()
    
    def get_queue(self) -> List[Dict[str, Any]]:
        """Get the saved queue."""
        return self.get("queue", [])
    
    def set_queue(self, queue_data: List[Dict[str, Any]]) -> None:
        """Save the queue data."""
        self.set("queue", queue_data)
    
    def get_current_queue_index(self) -> int:
        """Get the saved current queue index."""
        return self.get("current_queue_index", -1)
    
    def set_current_queue_index(self, index: int) -> None:
        """Save the current queue index."""
        self.set("current_queue_index", index)
