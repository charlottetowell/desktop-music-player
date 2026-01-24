"""
Audio file scanner with metadata extraction
"""

from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from mutagen import File as MutagenFile
from mutagen.id3 import ID3NoHeaderError
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
from mutagen.oggvorbis import OggVorbis
from mutagen.mp4 import MP4


@dataclass
class AudioTrack:
    """Audio track with metadata."""
    file_path: Path
    title: str = "Unknown Title"
    artist: str = "Unknown Artist"
    album: str = "Unknown Album"
    year: str = "Unknown"
    track_number: Optional[int] = None
    duration: float = 0.0
    file_size: int = 0
    format: str = "unknown"
    
    def __post_init__(self):
        if isinstance(self.file_path, str):
            self.file_path = Path(self.file_path)


class AudioScanner:
    """Scans directories for audio files and extracts metadata."""
    
    SUPPORTED_FORMATS: Set[str] = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac'}
    
    def __init__(self) -> None:
        self.tracks: List[AudioTrack] = []
        
    def scan_directory(self, directory: str) -> List[AudioTrack]:
        """
        Scan directory recursively for audio files.
        
        Args:
            directory: Path to directory to scan
            
        Returns:
            List of AudioTrack objects with metadata
        """
        dir_path = Path(directory)
        if not dir_path.exists() or not dir_path.is_dir():
            return []
            
        self.tracks.clear()
        
        for file_path in dir_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_FORMATS:
                track = self._extract_metadata(file_path)
                if track:
                    self.tracks.append(track)
                    
        return self.tracks
        
    def _extract_metadata(self, file_path: Path) -> Optional[AudioTrack]:
        """
        Extract metadata from audio file.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            AudioTrack object or None if extraction failed
        """
        try:
            audio = MutagenFile(str(file_path), easy=True)
            if audio is None:
                return self._create_fallback_track(file_path)
                
            track = AudioTrack(
                file_path=file_path,
                format=file_path.suffix[1:].lower(),
                file_size=file_path.stat().st_size,
                duration=getattr(audio.info, 'length', 0.0)
            )
            
            # Extract common tags
            if hasattr(audio, 'tags') and audio.tags:
                track.title = self._get_tag(audio, 'title', file_path.stem)
                track.artist = self._get_tag(audio, 'artist', 'Unknown Artist')
                track.album = self._get_tag(audio, 'album', 'Unknown Album')
                track.year = self._get_tag(audio, 'date', 'Unknown')
                
                # Extract track number
                track_num = self._get_tag(audio, 'tracknumber', None)
                if track_num:
                    try:
                        # Handle "1/12" format
                        track.track_number = int(str(track_num).split('/')[0])
                    except (ValueError, AttributeError):
                        pass
            else:
                track.title = file_path.stem
                
            return track
            
        except Exception as e:
            print(f"Error extracting metadata from {file_path}: {e}")
            return self._create_fallback_track(file_path)
            
    def _get_tag(self, audio, tag_name: str, default: str) -> str:
        """Safely get tag value from audio file."""
        try:
            value = audio.get(tag_name, [default])
            if isinstance(value, list) and value:
                return str(value[0])
            return str(value) if value else default
        except:
            return default
            
    def _create_fallback_track(self, file_path: Path) -> AudioTrack:
        """Create track with minimal info when metadata extraction fails."""
        return AudioTrack(
            file_path=file_path,
            title=file_path.stem,
            format=file_path.suffix[1:].lower(),
            file_size=file_path.stat().st_size
        )
        
    def group_by_album(self) -> Dict[str, List[AudioTrack]]:
        """Group tracks by album."""
        groups: Dict[str, List[AudioTrack]] = {}
        for track in self.tracks:
            album_key = f"{track.album} - {track.artist}"
            if album_key not in groups:
                groups[album_key] = []
            groups[album_key].append(track)
            
        # Sort tracks within each album by track number
        for tracks in groups.values():
            tracks.sort(key=lambda t: t.track_number if t.track_number else 999)
            
        return dict(sorted(groups.items()))
        
    def group_by_artist(self) -> Dict[str, List[AudioTrack]]:
        """Group tracks by artist."""
        groups: Dict[str, List[AudioTrack]] = {}
        for track in self.tracks:
            if track.artist not in groups:
                groups[track.artist] = []
            groups[track.artist].append(track)
            
        # Sort tracks within each artist by album then track number
        for tracks in groups.values():
            tracks.sort(key=lambda t: (t.album, t.track_number if t.track_number else 999))
            
        return dict(sorted(groups.items()))
        
    def group_by_year(self) -> Dict[str, List[AudioTrack]]:
        """Group tracks by year."""
        groups: Dict[str, List[AudioTrack]] = {}
        for track in self.tracks:
            year = str(track.year).split('-')[0][:4] if track.year != "Unknown" else "Unknown"
            if year not in groups:
                groups[year] = []
            groups[year].append(track)
            
        # Sort tracks within each year by artist then album
        for tracks in groups.values():
            tracks.sort(key=lambda t: (t.artist, t.album, t.track_number if t.track_number else 999))
            
        return dict(sorted(groups.items(), reverse=True))
        
    def group_by_folder(self) -> Dict[str, List[AudioTrack]]:
        """Group tracks by parent folder."""
        groups: Dict[str, List[AudioTrack]] = {}
        for track in self.tracks:
            folder = track.file_path.parent.name
            if folder not in groups:
                groups[folder] = []
            groups[folder].append(track)
            
        # Sort tracks within each folder by filename
        for tracks in groups.values():
            tracks.sort(key=lambda t: t.file_path.name)
            
        return dict(sorted(groups.items()))
