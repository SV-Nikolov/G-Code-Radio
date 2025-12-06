# G-Code Radio - Project Structure

This file documents the complete project structure and development progress.

## Project Overview

G-Code Radio converts YouTube audio into G-code for the Moment S1 (2014) 3D printer, allowing it to "play" music through stepper motor movement sounds.

---

## Directory Structure

```
G-Code-Radio/
├── src/
│   ├── __init__.py                          # Package initialization
│   ├── main.py                              # Application entry point
│   │
│   ├── audio/                               # Audio processing module
│   │   ├── __init__.py
│   │   ├── downloader.py                    # YouTube audio download
│   │   ├── extractor.py                     # Audio extraction/conversion
│   │   └── analyzer.py                      # Audio feature analysis
│   │
│   ├── signal_processing/                   # Signal analysis module
│   │   ├── __init__.py
│   │   ├── pitch_detection.py               # Fundamental frequency detection
│   │   ├── note_detection.py                # Pitch to discrete notes
│   │   ├── tempo_analysis.py                # Tempo/beat detection
│   │   └── complexity_reducer.py            # Note sequence simplification
│   │
│   ├── mapping/                             # Note to movement mapping
│   │   ├── __init__.py
│   │   ├── note_mapper.py                   # MIDI to movement conversion
│   │   ├── parameter_controller.py          # Speed/Pitch/Complexity control
│   │   └── bounds_validator.py              # Movement bounds checking
│   │
│   ├── gcode/                               # G-code generation module
│   │   ├── __init__.py
│   │   ├── gcode_generator.py               # G-code file generation
│   │   ├── gcode_optimizer.py               # G-code optimization
│   │   └── gcode_validator.py               # Safety validation
│   │
│   ├── printer/                             # Printer configuration
│   │   ├── __init__.py
│   │   └── moment_s1_config.py              # Moment S1 specifications
│   │
│   ├── ui/                                  # User interface module
│   │   ├── __init__.py
│   │   ├── cli.py                           # Command-line interface
│   │   └── parameter_interface.py           # Parameter input handling
│   │
│   └── utils/                               # Utility module
│       ├── __init__.py
│       ├── logger.py                        # Logging system
│       ├── config_manager.py                # Configuration management
│       └── error_handler.py                 # Exception handling
│
├── tests/                                   # Test suite
│   ├── __init__.py
│   ├── test_audio.py                        # Audio module tests
│   ├── test_signal_processing.py            # Signal processing tests
│   ├── test_mapping.py                      # Mapping module tests
│   ├── test_gcode.py                        # G-code module tests
│   └── test_integration.py                  # Integration tests
│
├── output/                                  # Generated G-code files
│
├── requirements.txt                         # Python dependencies
├── PROJECT_OUTLINE.md                       # Project architecture document
├── .gitignore                               # Git ignore file
├── LICENSE                                  # License file
└── README.md                                # Project documentation
```

---

## Development Status

### Phase 1: Core Audio Processing
- [x] Project structure created
- [ ] Audio downloader implementation
- [ ] Audio analyzer implementation
- [ ] Pitch detection implementation
- [ ] Note detection implementation

### Phase 2: Mapping and Transformation
- [ ] Note mapper implementation
- [ ] Parameter controller implementation
- [ ] Bounds validator implementation

### Phase 3: G-Code Generation
- [ ] G-code generator implementation
- [ ] G-code optimizer implementation
- [ ] G-code validator implementation

### Phase 4: User Interface
- [ ] CLI interface implementation
- [ ] Parameter input handling

### Phase 5: Testing
- [ ] Unit tests
- [ ] Integration tests

### Phase 6: Documentation
- [ ] User guide
- [ ] API documentation
- [ ] Examples

---

## Module Descriptions

### Audio Module (`src/audio/`)
Handles downloading audio from YouTube and extracting audio features.

**Key Classes:**
- `YouTubeDownloader` - Downloads audio from YouTube URLs
- `AudioExtractor` - Converts audio to standard formats
- `AudioAnalyzer` - Extracts chromagrams, onsets, and features

### Signal Processing Module (`src/signal_processing/`)
Analyzes audio signals to detect pitches and convert them to musical notes.

**Key Classes:**
- `PitchDetector` - Detects fundamental frequencies
- `NoteDetector` - Converts frequencies to MIDI notes
- `TempoAnalyzer` - Analyzes tempo and beat positions
- `ComplexityReducer` - Simplifies note sequences

### Mapping Module (`src/mapping/`)
Converts musical notes to 3D printer movements while respecting constraints.

**Key Classes:**
- `NoteMapper` - Maps MIDI notes to movement instructions
- `ParameterController` - Applies Speed, Pitch, and Complexity adjustments
- `BoundsValidator` - Ensures movements stay within printer bounds

### G-Code Module (`src/gcode/`)
Generates and validates G-code for the 3D printer.

**Key Classes:**
- `GCodeGenerator` - Generates G-code from movements
- `GCodeOptimizer` - Optimizes G-code for efficiency
- `GCodeValidator` - Validates safety constraints

### Printer Configuration Module (`src/printer/`)
Defines printer specifications and constraints.

**Key Classes:**
- `MomentS1Config` - Moment S1 (2014) specifications and bounds

### UI Module (`src/ui/`)
Provides user interface for input and output.

**Key Classes:**
- `CLIInterface` - Command-line user interface
- `ParameterInterface` - Handles Speed, Pitch, Complexity parameters

### Utilities Module (`src/utils/`)
Provides helper functions and utilities.

**Key Classes:**
- `Logger` - Application logging
- `ConfigManager` - Configuration file management
- Custom exceptions in `error_handler.py`

---

## Technology Stack

- **Python 3.9+** - Core language
- **yt-dlp** - YouTube audio download
- **librosa** - Audio analysis
- **numpy/scipy** - Signal processing
- **pydub** - Audio file handling
- **pytest** - Testing framework

---

## Next Steps

1. Implement audio downloader (yt-dlp integration)
2. Implement audio analyzer (librosa integration)
3. Implement pitch detection algorithm
4. Implement note detection
5. Implement note to movement mapping
6. Implement G-code generation
7. Build CLI interface
8. Add comprehensive tests

