# G-Code Radio - Application Outline

## Overview
G-Code Radio transforms YouTube audio into G-code for the Moment S1 (2014) 3D printer, allowing it to "play" music through stepper motor movement sounds.

---

## Architecture

### Core Modules

#### 1. **Audio Management** (`src/audio/`)
- `downloader.py` - Download audio from YouTube links using yt-dlp
- `extractor.py` - Extract audio features and convert to WAV/MP3
- `analyzer.py` - Analyze audio to detect pitches and durations

#### 2. **Signal Processing** (`src/signal_processing/`)
- `pitch_detection.py` - Detect fundamental frequencies (pitch) from audio
- `note_detection.py` - Convert continuous pitches to discrete musical notes
- `tempo_analysis.py` - Analyze and extract tempo information
- `complexity_reducer.py` - Simplify note sequences based on complexity parameter

#### 3. **Note-to-Movement Mapping** (`src/mapping/`)
- `note_mapper.py` - Convert MIDI notes to stepper motor movement patterns
- `parameter_controller.py` - Apply Speed, Pitch, and Complexity adjustments
- `bounds_validator.py` - Ensure all movements stay within printer bounds

#### 4. **G-Code Generation** (`src/gcode/`)
- `gcode_generator.py` - Convert movement sequences to G-code commands
- `gcode_optimizer.py` - Optimize G-code for efficient movement
- `gcode_validator.py` - Validate G-code safety (no extrusion, no heating)

#### 5. **Printer Configuration** (`src/printer/`)
- `moment_s1_config.py` - Define Moment S1 specifications and bounds
  - Build volume dimensions
  - Maximum feedrates
  - Safe movement zones
  - Stepper motor frequencies and characteristics

#### 6. **User Interface** (`src/ui/`)
- `cli.py` - Command-line interface for input/output
- `gui.py` *(optional)* - GUI for easier user interaction
- `parameter_interface.py` - Handle Speed, Pitch, Complexity controls

#### 7. **Utilities** (`src/utils/`)
- `logger.py` - Logging system for debugging
- `config_manager.py` - Configuration file handling
- `error_handler.py` - Error management and user feedback

---

## Data Flow

```
YouTube URL
    ↓
[Audio Downloader] → Audio File (WAV/MP3)
    ↓
[Audio Analyzer] → Pitch/Duration Data
    ↓
[Note Detector] → Discrete Notes Sequence
    ↓
[Complexity Reducer] → Simplified Note Sequence (based on parameter)
    ↓
[Parameter Controller] → Apply Speed & Pitch Adjustments
    ↓
[Note Mapper] → Movement Instructions (X/Y/Z with feedrates)
    ↓
[Bounds Validator] → Validated Movement Sequence
    ↓
[G-Code Generator] → G-Code Commands
    ↓
[G-Code Validator] → Verified G-Code (no extrusion/heating)
    ↓
Output G-Code File (.gcode)
```

---

## User Control Parameters

### 1. **Speed** (Range: 0.5x - 3.0x)
- Controls playback speed of the song
- Affects timing between movements
- Lower = slower song, higher = faster song

### 2. **Pitch** (Range: -12 to +12 semitones)
- Transposes the entire melody up or down
- Maps to different motor frequencies or movement amplitudes
- Enables playing the same song in different keys

### 3. **Complexity** (Range: 0 - 100 or Low/Medium/High)
- 0 (Low): Heavily simplified, only major melodic points
- 50 (Medium): Balanced detail and simplification
- 100 (High): Preserve maximum detail from original

---

## Printer Specifications (Moment S1 2014)

### Build Volume
- X: 0 - 200mm
- Y: 0 - 200mm
- Z: 0 - 200mm

### Safety Constraints
- No extrusion commands (M104, M109, E-axis moves)
- No heating commands (M104 hotend, M140 bed)
- Movement-only G-code
- Stay within bounds with safety margin

### Stepper Motor Characteristics
- Typical stepping frequency range: 100Hz - 10,000Hz
- Used to create audible tones via motor movement
- Multiple axes can run simultaneously for harmonic effects

---

## Technology Stack

### Backend
- **Python 3.9+** - Core language
- **yt-dlp** - YouTube audio download
- **librosa** - Audio analysis and feature extraction
- **numpy/scipy** - Signal processing
- **pydub** - Audio file handling

### Frontend (Optional)
- **tkinter** - Simple GUI alternative
- **Flask/FastAPI** - Web interface (future)

### Testing
- **pytest** - Unit testing
- **unittest** - Standard library tests

---

## File Structure

```
G-Code-Radio/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Entry point
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── downloader.py
│   │   ├── extractor.py
│   │   └── analyzer.py
│   ├── signal_processing/
│   │   ├── __init__.py
│   │   ├── pitch_detection.py
│   │   ├── note_detection.py
│   │   ├── tempo_analysis.py
│   │   └── complexity_reducer.py
│   ├── mapping/
│   │   ├── __init__.py
│   │   ├── note_mapper.py
│   │   ├── parameter_controller.py
│   │   └── bounds_validator.py
│   ├── gcode/
│   │   ├── __init__.py
│   │   ├── gcode_generator.py
│   │   ├── gcode_optimizer.py
│   │   └── gcode_validator.py
│   ├── printer/
│   │   ├── __init__.py
│   │   └── moment_s1_config.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── cli.py
│   │   └── parameter_interface.py
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       ├── config_manager.py
│       └── error_handler.py
├── tests/
│   ├── __init__.py
│   ├── test_audio.py
│   ├── test_signal_processing.py
│   ├── test_mapping.py
│   ├── test_gcode.py
│   └── test_integration.py
├── output/                        # Generated G-code files
├── requirements.txt
├── .gitignore
├── LICENSE
├── README.md
└── PROJECT_OUTLINE.md
```

---

## Development Phases

### Phase 1: Core Audio Processing
- [ ] Audio downloader (YouTube)
- [ ] Audio analyzer (pitch detection)
- [ ] Note detector (convert pitch to notes)

### Phase 2: Mapping and Transformation
- [ ] Note-to-movement mapper
- [ ] Parameter controllers (Speed, Pitch, Complexity)
- [ ] Bounds validator

### Phase 3: G-Code Generation
- [ ] G-code generator
- [ ] G-code validator (safety checks)
- [ ] G-code optimizer

### Phase 4: User Interface
- [ ] CLI interface
- [ ] Parameter input handling
- [ ] Output file management

### Phase 5: Testing & Refinement
- [ ] Unit tests for each module
- [ ] Integration tests
- [ ] Real printer testing (if available)

### Phase 6: Documentation & Polish
- [ ] User documentation
- [ ] API documentation
- [ ] Example configurations

---

## Key Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Accurate pitch detection | Use librosa with appropriate windowing and frequency resolution |
| Note simplification | Implement complexity levels with note merging/dropping algorithms |
| Printer bounds enforcement | Pre-validate all coordinates, add safety margins |
| Audio file handling | Support multiple formats via ffmpeg/pydub |
| Stepper motor frequency mapping | Calibrate feedrates to desired musical pitches |

---

## Next Steps

1. Create base module structure with `__init__.py` files
2. Implement `requirements.txt` with dependencies
3. Start with audio downloader module
4. Build pitch detection pipeline
5. Implement note detection
6. Create G-code generation
7. Add parameter controls
8. Build CLI interface

