# Desktop Music Player

A cross-platform desktop audio player with real-time visualization, built with Python and Qt.

## Features

- **Cross-Platform**: Windows & Linux support
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
- **Real-Time Audio Visualizer**: Frequency spectrum visualization powered by librosa
  - 64-bar frequency spectrum display
  - Smooth animations with peak indicators
  - Modern gradient styling (peachy theme)
  - Synced with playback position
  - Automatic pause/resume with playback state
- **Mini Mode**: Dockable, always-on-top widgets (coming soon)
- **MVVM Architecture**: Clean separation between audio engine and UI

## Tech Stack

- **UI Framework**: PySide6 (Qt for Python)
- **Audio Engine**: miniaudio (cross-platform playback)
- **Metadata**: mutagen (audio file tag reading)
- **Audio Analysis**: librosa for frequency analysis and FFT
- **DSP/Visualization**: numpy for real-time PCM data processing
- **Concurrency**: Worker threads for audio decoding, playback, and analysis

## Project Structure

```
desktop-music-player/
├── core/              # Audio engine and backend logic
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

### Running Locally

```bash
python main.py
```

## Dependencies

- **PySide6**: Qt framework for Python
- **miniaudio**: Cross-platform audio playback
- **mutagen**: Audio metadata extraction and album art
- **numpy**: Fast array operations for DSP
- **librosa**: Audio analysis and feature extraction
- **soundfile**: Audio file I/O for librosa

Install all dependencies via:
```bash
pip install -r requirements.txt
```

## Audio Visualizer

The audio visualizer provides real-time frequency spectrum visualization:

- **Technology**: Uses librosa for audio analysis with FFT (Fast Fourier Transform)
- **Features**:
  - 64-band frequency spectrum with smooth animations
  - Peak indicators with gravity-based decay
  - Position-synchronized visualization (analyzes audio at current playback position)
  - Automatic pause/resume with playback state
  - Modern gradient styling matching the app theme
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
