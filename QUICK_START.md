# G-Code Radio - Quick Start Guide

## 📦 Complete Installation

Two executable versions are available:
- **G-Code-Radio.exe** - Command-line interface (CLI)
- **G-Code-Radio-GUI.exe** - Graphical user interface (GUI)

---

## 🚀 Getting Started (GUI - Recommended for Most Users)

### Launch the GUI

Simply run:
```
G-Code-Radio-GUI.exe
```

A graphical window will open with:
- File browser for selecting audio files
- YouTube URL input field
- Interactive parameter sliders
- Real-time log output
- G-code preview and visualization tools

### Using the GUI

1. **Select Input:**
   - Click "Browse File" to select a local audio file, OR
   - Paste a YouTube URL directly

2. **Adjust Parameters:**
   - **Speed**: Drag the slider (0.5x - 3.0x)
   - **Pitch**: Drag the slider (-12 to +12 semitones)
   - **Complexity**: Drag the slider (0% - 100%)

3. **Convert:**
   - Click "Convert to G-code"
   - Watch the progress bar and log output
   - Click "Visualize" to see the generated movements

4. **View Results:**
   - **G-code Preview**: See the raw G-code commands
   - **Movement Visualization**: 3D plot of printer movements
   - **Statistics**: Analysis of movements and feedrates

---

## 🖥️ Command-Line Interface (CLI)

For advanced users or scripting:

### Convert YouTube Video to G-Code

```bash
G-Code-Radio.exe "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

The application will:
1. Download the audio from YouTube
2. Analyze the pitch and detect notes
3. Generate printer-friendly G-code
4. Save to `output/music.gcode`

### Convert Local Audio File

```bash
G-Code-Radio.exe "song.mp3"
```

Supported formats: MP3, WAV, OGG, M4A, FLAC, AAC

### Custom Output Location

```bash
G-Code-Radio.exe "song.mp3" --output "C:\my_songs\output.gcode"
```

---

## 🎚️ Control Parameters

### Speed (Playback Speed)
```bash
--speed 1.5
```
- Range: 0.5x to 3.0x
- Default: 1.0x (normal speed)
- 0.5x = half speed (slower)
- 2.0x = double speed (faster)

### Pitch (Transpose)
```bash
--pitch 5
```
- Range: -12 to +12 semitones
- Default: 0 (original pitch)
- 5 = 5 semitones higher
- -3 = 3 semitones lower

### Complexity (Note Detail)
```bash
--complexity 75
```
- Range: 0 to 100
- Default: 50
- 0 = very simplified (only main notes)
- 100 = full detail (all notes)
- 50 = balanced detail and simplification

---

## 📋 Full Example Commands

```bash
# Basic usage
G-Code-Radio.exe "song.mp3"

# Fast version, higher pitch
G-Code-Radio.exe "song.mp3" --speed 2.0 --pitch 7

# Slow, simplified version
G-Code-Radio.exe "song.mp3" --speed 0.7 --complexity 30

# Custom output location
G-Code-Radio.exe "song.mp3" --output "output\my_song.gcode"

# All parameters combined
G-Code-Radio.exe "https://youtu.be/..." --speed 1.5 --pitch 2 --complexity 75 --output "output\song.gcode"

# Get help
G-Code-Radio.exe --help
```

---

## 📂 Output Structure

After running the application, you'll get:

```
output/
├── music.gcode          # Generated G-code file
├── audio.wav            # Converted audio (if from video)
└── logs/                # Processing logs
```

---

## 📊 What Happens During Processing

### Phase 1: Audio Input
- Downloads from YouTube OR loads local audio file
- Converts to WAV format if needed

### Phase 2: Audio Analysis
- Extracts audio features (chromagram, onsets)
- Detects tempo and beat positions

### Phase 3: Pitch Detection
- Analyzes frequency content
- Detects fundamental frequencies (pitches)
- Computes confidence scores

### Phase 4: Note Detection
- Converts continuous pitch to discrete musical notes
- Detects note onsets and durations
- Generates MIDI note sequence

### Phase 5: Parameter Application
- Applies complexity reduction (simplifies or preserves notes)
- Applies pitch shift transposition
- Applies speed scaling to durations

### Phase 6: Movement Generation
- Converts notes to 3D printer movements
- Maps frequencies to stepper motor feedrates
- Calculates movement distances

### Phase 7: Bounds Validation
- Ensures all movements stay within printer bounds
- Applies safety margins
- Clamps coordinates if needed

### Phase 8: G-Code Generation
- Generates G1 move commands
- Adds safety headers (no extrusion, no heating)
- Creates home/reset commands

### Phase 9: Validation
- Verifies no extrusion commands
- Checks for no heating commands
- Confirms all coordinates are in bounds

---

## ⚙️ Printer Specifications (Moment S1 2014)

The application is configured for the Moment S1 (2014):

- **Build Volume:** 200 × 200 × 200 mm
- **Movement Range:** XY: 6000 mm/min, Z: 3000 mm/min
- **Stepper Frequency:** 100 - 10,000 Hz
- **Safety:** Movement only (no extrusion, no heating)
- **Home Position:** 100, 100, 100 mm

---

## 🔍 Output G-Code Format

The generated G-code is optimized for music playback:

```gcode
; G-Code Radio - 3D Printer Music Player
; Generated on 2025-12-06 10:30:45
; Title: song_name

M82                    ; Set extruder absolute
G90                    ; Absolute positioning
G28                    ; Home all axes
G92 X100 Y100 Z100     ; Set home position

; Movement sequence
G1 X110.00 F1000       ; Move X axis at 1000 mm/min
G1 Y105.00 F1000       ; Move Y axis
G1 Z102.00 F500        ; Move Z axis

G28                    ; Return home
M18                    ; Disable steppers
```

---

## ❓ Troubleshooting

### "Could not find YouTube video"
- Check your internet connection
- Verify the YouTube URL is correct and public
- Ensure the video has audio

### "Failed to detect notes"
- Try increasing complexity (--complexity 100)
- Ensure audio file is clear and not silent
- Try adjusting parameters

### "G-Code validation failed"
- This is a safety check - shouldn't happen with valid inputs
- Check the error message for details
- Try simpler audio or different parameters

### "Audio format not supported"
- Ensure audio is in a supported format: MP3, WAV, OGG, M4A, FLAC, AAC
- Try converting to MP3 or WAV first

---

## 📊 Visualization & Analysis (GUI Only)

After successfully converting audio to G-code, use the visualization tools:

### G-code Preview Tab
- **View raw G-code**: See all printer commands
- **File statistics**: Line count, file size, movement count
- **Syntax validation**: Ensures G-code is valid

### Movement Visualization Tab
Contains 4 plots:

1. **XY Path (2D)**: Shows the X-Y movement pattern
   - Green dot: Start position
   - Red X: End position
   - Blue line: Movement path

2. **3D Path**: Three-dimensional view of all movements
   - Helpful for understanding Z-axis motion
   - Shows spatial relationships

3. **Axis Positions**: How X, Y, Z change over time
   - Useful for identifying movement patterns
   - Helps understand tempo representation

4. **Feedrate Analysis**: Printer speed over time
   - Shows how notes map to feedrates
   - Blue line: Feedrate per movement
   - Dashed line: Average feedrate

### Statistics Tab
Comprehensive analysis including:
- **Movement data**: Total movements, command count
- **Axis ranges**: Min/max/range for X, Y, Z
- **Feedrate statistics**: Min/max/mean/median speeds
- **Total travel distance**: Cumulative movement length
- **Estimated print time**: How long the song will take to "play"

### Example: High Note vs Low Note
- **High notes**: Higher X/Y positions, faster feedrates
- **Low notes**: Lower X/Y positions, slower feedrates
- **Complexity effect**: More movements at higher complexity

---

## 🎨 Tips for Best Results

### Audio Selection
- Clear vocals or single instruments work best
- Avoid heavily compressed or noise-filled audio
- Test with familiar songs first

### Parameter Tuning
- **Speed**: Increase for faster playback, decrease for slower
- **Pitch**: Shift if song is in unusual range
- **Complexity**: Increase for more note detail, decrease for simpler patterns

### Printer Considerations
- Ensure printer has enough time for movements (this is just movement, not actual extrusion)
- Check that output G-code doesn't exceed printer bounds
- Verify feedrates are safe for your printer

---

## 📂 File Locations

- **Input files**: Any local audio file or YouTube URL
- **Output files**: `output/music.gcode` (default) or custom path
- **Logs**: Console or GUI log window (real-time)
- **Executables**: `dist/G-Code-Radio.exe` (CLI) and `dist/G-Code-Radio-GUI.exe` (GUI)

---

## 🔧 Advanced Features (CLI Only)

### Logging Levels
```bash
G-Code-Radio.exe "song.mp3" --log-level DEBUG
```
Options: DEBUG, INFO, WARNING, ERROR

### Batch Processing
Run multiple conversions:
```bash
for %%f in (*.mp3) do G-Code-Radio.exe "%%f" --output "output\%%~nf.gcode"
```

---

## 📝 Example Workflows

### Workflow 1: Convert YouTube Song (GUI)
1. Open G-Code-Radio-GUI.exe
2. Paste YouTube URL
3. Keep default parameters
4. Click "Convert to G-code"
5. Click "Visualize" to preview
6. Export G-code file

### Workflow 2: Optimize for Specific Printer
1. Open G-Code-Radio-GUI.exe
2. Load a local MP3 file
3. Adjust Speed/Pitch until timing feels right
4. Lower Complexity for faster execution
5. Visualize to ensure no bounds violations
6. Export ready-to-print G-code

### Workflow 3: Batch Convert from Python Script
```python
import subprocess
import os

songs = ['song1.mp3', 'song2.mp3', 'song3.mp3']
for song in songs:
    output = f"output/{os.path.splitext(song)[0]}.gcode"
    subprocess.run([
        'G-Code-Radio.exe',
        song,
        '--output', output,
        '--complexity', '75',
        '--speed', '1.2'
    ])
```

---


## 📝 Requirements

The executable is fully self-contained and includes all dependencies:
- ✅ Python runtime
- ✅ Audio libraries (librosa, pydub)
- ✅ YouTube downloader (yt-dlp)
- ✅ Signal processing (numpy, scipy)
- ✅ No installation required!

---

## 📊 Example Workflow

1. **Find a song on YouTube:**
   ```
   https://www.youtube.com/watch?v=dQw4w9WgXcQ
   ```

2. **Convert to G-code:**
   ```bash
   G-Code-Radio.exe "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --complexity 60
   ```

3. **Wait for processing** (typically 30-60 seconds depending on song length)

4. **Load onto printer:**
   - Copy `output/music.gcode` to your printer's SD card
   - Load the file in your printer's menu
   - Press play!

5. **Hear the music!** 🎵
   - The printer will play the song through stepper motor movements
   - No extrusion, no heating - just pure motion!

---

## 🎉 You're Ready!

Run `G-Code-Radio.exe` and start creating printer music! 🖨️🎵
