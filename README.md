# Desktop Music Player

A cross-platform desktop audio player with real-time visualization, built with Python and Qt.

## Features

- **Cross-Platform**: Windows & Linux support
- **Modern UI**: Frameless, transparent window with custom title bar
- **Mini Mode**: Dockable, always-on-top widgets
- **Real-Time Visualization**: FFT-based audio visualization using numpy
- **MVVM Architecture**: Clean separation between audio engine and UI

## Tech Stack

- **UI Framework**: PySide6 (Qt for Python)
- **Audio Engine**: miniaudio or pygame.mixer
- **DSP/Visualization**: numpy for real-time PCM data processing
- **Concurrency**: Worker threads for audio decoding and FFT analysis

## Project Structure

```
desktop-music-player/
├── core/              # Audio engine and backend logic
├── ui/                # GUI components
│   ├── widgets/       # Custom Qt widgets
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
- **numpy**: Fast array operations for DSP
- **miniaudio** or **pygame**: Audio playback backend

Install all dependencies via:
```bash
pip install -r requirements.txt
```

## Development Guidelines

- **Architecture**: Follow MVVM pattern (Model-View-ViewModel)
- **Concurrency**: Audio decoding and FFT run in worker threads
- **Type Hints**: All functions must use type annotations
- **Style**: PEP8 compliant, self-documenting code
- **UI Styling**: CSS-based styling using QSS files

## License

[To be determined]

## Contributing

[To be determined]
