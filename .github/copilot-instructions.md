Context: Cross-platform (Win/Linux) Desktop Audio Player.
Stack: Python (PySide6/Qt), miniaudio or pygame.mixer, numpy (DSP).

## Core Architecture
Patterns: Follow MVVM (Model-View-ViewModel). Decouple the Audio Engine (backend) from the Visualizer/GUI (frontend).

Concurrency: Run audio decoding and FFT analysis in a dedicated worker thread to prevent UI blocking.

UI: Implement a Frameless, transparent main window with custom title bars. Support "Mini-Mode" (dockable, AlwaysOnTop widgets).

## Code Guidelines

Modularity: Separate /core (audio logic), /ui (widgets/themes), and /utils (file I/O).

Visualization: Use numpy for real-time PCM data processing (FFT).

Documentation: Maintain a live README.md reflecting the feature set and dependency tree.

Style: Minimal PEP8 comments; prioritize self-documenting code. Use Type Hinting for all functions.

Consistency: Adhere to existing Qt Signal/Slot patterns and CSS-based styling (QSS).