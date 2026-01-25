# Desktop Music Player

A cross-platform desktop audio player with real-time visualization, built with Python and Qt.

## Features

- **Cross-Platform**: Windows & Linux support
- **OS Media Key Integration**: Control playback with your keyboard media keys
  - Play/Pause, Next, Previous, Stop support
  - Works with any keyboard shortcuts configured in your OS
  - **Windows**: Uses Qt shortcuts for media keys (all Windows versions)
  - **Linux**: MPRIS D-Bus integration for desktop environments (GNOME, KDE, etc.)
- **Modern UI**: Frameless, transparent window with custom title bar
- **Audio Playback**: Full playback engine with play/pause/skip controls
  - Real-time progress bar and position tracking
  - Album art display with track information
  - Auto-advance to next track
  - Playback history (15 tracks back)
- **Queue Management**: Add tracks by double-clicking or dragging from library
  - Album-grouped display with cover art
  - Drag-and-drop reordering within queue
  - Manual track removal
  - Visual highlighting of currently playing track
- **Library Scanner**: Automatic metadata extraction
  - Supports MP3, FLAC, WAV, OGG, M4A, AAC
  - Album art extraction from tags
  - Group by Album, Artist, Year, or Folder
- **Real-Time Audio Visualizer**: Waveform visualization powered by librosa
  - Smooth, animated waveform display
  - Shows ~0.5 seconds of audio at current playback position
  - Glow effects and gradient styling (peachy theme)
  - 200-sample resolution for fluid motion
  - Automatic pause/resume with playback state
- **Mini Mode**: Dockable, always-on-top widgets (coming soon)
- **MVVM Architecture**: Clean separation between audio engine and UI

## Tech Stack

- **UI Framework**: PySide6 (Qt for Python)
- **Audio Engine**: miniaudio (cross-platform playback)
- **Metadata**: mutagen (audio file tag reading)
- **Audio Analysis**: librosa for frequency analysis and FFT
- **DSP/Visualization**: numpy for real-time PCM data processing
- **Media Keys (Windows)**: Qt QShortcut for media key support
- **Media Keys (Linux)**: dbus-python for MPRIS2 integration
- **Concurrency**: Worker threads for audio decoding, playback, and analysis

## Project Structure

```
desktop-music-player/
├── core/              # Audio engine and backend logic
│   ├── audio_engine.py           # Playback engine
│   ├── media_controller.py       # OS media key integration (base)
│   ├── media_controller_windows.py  # Windows media keys
│   ├── media_controller_linux.py    # Linux MPRIS
│   └── ...
├── ui/                # GUI components
│   ├── widgets/       # Custom Qt widgets
│   │   ├── audio_visualizer_widget.py  # Real-time visualizer
│   │   ├── now_playing_widget.py       # Track info display
│   │   ├── library_panel.py            # Music library
│   │   └── ...
│   └── themes/        # QSS stylesheets
├── utils/             # File I/O and utilities
├── assets/            # Icons, themes, and resources
│   ├── icons/
│   └── themes/
├── main.py            # Application entry point
└── requirements.txt   # Python dependencies
```

## Setup & Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- **Windows**: Windows 7 or later (media keys work on all versions)
- **Linux**: D-Bus installed (standard on most distros)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd desktop-music-player
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   Platform-specific dependencies will be installed automatically:
   - Windows: Qt shortcuts (built-in, no extra packages)
   - Linux: `dbus-python` for MPRIS integration

### Running Locally

```bash
python main.py
```

## Dependencies

Core dependencies:
- **PySide6**: Qt framework for Python
- **miniaudio**: Cross-platform audio playback
- **mutagen**: Audio metadata extraction and album art
- **numpy**: Fast array operations for DSP
- **librosa**: Audio analysis and feature extraction
- **soundfile**: Audio file I/O for librosa

Platform-specific (auto-installed):
- **winsdk** (Windows): System Media Transport Controls (currently optional)
- **dbus-python** (Linux): MPRIS D-Bus integration

Install all dependencies via:
```bash
pip install -r requirements.txt
```

## Media Key Support

### Windows
Media keys work out of the box using Qt's built-in shortcut system:
- Play/Pause ▶⏸
- Next ⏭
- Previous ⏮
- Stop ⏹

Compatible with all keyboards and Windows versions. Your configured media key shortcuts will work automatically.

### Linux
Uses MPRIS2 D-Bus interface for desktop integration:
- Works with GNOME, KDE, and other desktop environments
- Shows track metadata in system media controls
- Integrates with lock screen and notification area media controls
- Keyboard media keys trigger the player automatically

## Audio Visualizer

The audio visualizer provides real-time waveform visualization:

- **Technology**: Uses librosa for audio analysis with real-time waveform extraction
- **Features**:
  - Smooth waveform display showing audio amplitude over time
  - Displays ~0.5 seconds of audio centered at current playback position
  - Glow effects for modern, sleek appearance
  - Horizontal gradient styling matching the app theme (red → pink)
  - 200-sample resolution for fluid, smooth animations
  - Automatic pause/resume with playback state
- **Performance**: Runs in a separate worker thread to prevent UI blocking
- **Location**: Displayed in the right panel under the seek slider

## Development Guidelines

- **Architecture**: Follow MVVM pattern (Model-View-ViewModel)
- **Concurrency**: Audio decoding, analysis, and FFT run in worker threads
- **Type Hints**: All functions must use type annotations
- **Style**: PEP8 compliant, self-documenting code
- **UI Styling**: CSS-based styling using QSS files

## License

[To be determined]

## Contributing

[To be determined]
