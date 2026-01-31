# Desktop Music Player

A desktop audio player for Windows & Linux with real-time visualization, built with Python and Qt.

Built for the [Github Copilot CLI Challenge](https://dev.to/challenges/github-2026-01-21) hosted by dev.to. See my entry blog + **demo** here: [Desktop Music Player Using QT for Python - Built with Github Copilot CLI](https://dev.to/charlottetowell/desktop-music-player-using-qt-for-python-built-with-github-copilot-cli-45mk)

**In this README:**
* [Features 🎶](#features-)
* [Tech Stack 💻](#tech-stack-)
* [Running Locally](#running-locally)
* [Desktop Installation](#desktop-installation)
* [Project Structure](#project-structure)

## Features 🎶

- **Cross-Platform**: Windows & Linux support
- **OS Media Key Integration**: Control playback with keyboard media keys
- **Mini player**: A pop-out mini player window with audio waveform visualisation
- **Audio Playback**: Full playback engine with controls and playback history
- **Queue Management**: Add, reorder, and remove tracks with drag-and-drop
- **Library Scanner**: Auto-discover audio files with metadata extraction (MP3, FLAC, WAV, OGG, M4A, AAC)
- **Real-Time Audio Visualizer**: Waveform display with smooth animations

## Tech Stack 💻

- **UI**: PySide6 (Qt for Python)
- **Audio**: miniaudio (playback), mutagen (metadata), librosa (analysis)
- **DSP**: numpy for real-time audio processing
- **Media Keys**: Qt shortcuts (Windows) + MPRIS2 (Linux)
- **Threading**: Worker threads for audio decoding and analysis

## Running Locally

#### Step 1: Clone the Repository
```bash
git clone https://github.com/charlottetowell/desktop-music-player
cd desktop-music-player
```

#### Step 2: Set Up Virtual Environment
**Windows:**
```bash
python -m venv venv
source venv/Scripts/activate
```

**Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install System Dependencies (Linux only)
```bash
sudo apt-get update
sudo apt-get install libdbus-1-dev libglib2.0-dev
```

#### Step 4: Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Step 5: Run the Application
```bash
python main.py
```

## Desktop Installation

Install additional build requirements:
```bash
pip install -r build_requirements.txt
```

After following the same steps for how to run locally, run the build script as below:

**Windows:**
```bash
scripts\build_windows.bat
```

**Linux:**
```bash
chmod +x scripts/build_linux.sh
./scripts/build_linux.sh
```

> Note: expect the script to take 3-5 mins to execute.

#### Step 4: Locate the Executable

After building, the standalone application will be located at:
- **Windows**: `dist\DesktopMusicPlayer\DesktopMusicPlayer.exe`
- **Linux**: `dist/DesktopMusicPlayer/DesktopMusicPlayer`

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