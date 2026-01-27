# Desktop Music Player

A cross-platform desktop audio player with real-time visualization, built with Python and Qt.

## Features

- **Cross-Platform**: Windows & Linux support
- **OS Media Key Integration**: Control playback with keyboard media keys
- **Modern UI**: Frameless window with custom title bar and mini-mode
- **Audio Playback**: Full playback engine with controls and playback history
- **Queue Management**: Add, reorder, and remove tracks with drag-and-drop
- **Library Scanner**: Auto-discover audio files with metadata extraction (MP3, FLAC, WAV, OGG, M4A, AAC)
- **Real-Time Audio Visualizer**: Waveform display with smooth animations
- **MVVM Architecture**: Clean separation between audio engine and UI

## Tech Stack

- **UI**: PySide6 (Qt for Python)
- **Audio**: miniaudio (playback), mutagen (metadata), librosa (analysis)
- **DSP**: numpy for real-time audio processing
- **Media Keys**: Qt shortcuts (Windows) + MPRIS2 (Linux)
- **Threading**: Worker threads for audio decoding and analysis

## Installation

### Prerequisites
- Python 3.8+
- Windows 7+ or Linux with D-Bus

### Setup
```bash
git clone <repository-url>
cd desktop-music-player

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run
```bash
python main.py
```

## Project Structure

```
desktop-music-player/
├── core/                      # Audio engine & backend logic
├── ui/                        # GUI components & themes
│   ├── widgets/               # Custom Qt widgets
│   ├── themes/                # Styling (colors, fonts)
│   └── main_window.py         # Main application window
├── utils/                     # Utilities (icon manager)
├── assets/                    # Icons and resources
├── main.py                    # Entry point
└── requirements.txt           # Dependencies
```

## Media Key Support

**Windows**: Works out-of-the-box with all keyboards using Qt shortcuts.

**Linux**: Uses MPRIS2 D-Bus interface for GNOME, KDE, and other desktop environments. Shows track metadata in system media controls.

## Development

- **Architecture**: MVVM pattern with signal/slot connections
- **Concurrency**: Audio processing runs in worker threads
- **Code Style**: PEP8, type hints required
- **UI Styling**: QSS (Qt stylesheets) with custom colors and fonts
