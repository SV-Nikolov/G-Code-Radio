# G-Code Radio - Quick Start Guide

## 📦 Executable Build Complete!

The executable has been successfully built and is ready to use.

**Location:** `dist/G-Code-Radio.exe` (7.3 MB)

---

## 🚀 Quick Start

### Option 1: Convert YouTube Video to G-Code

```bash
G-Code-Radio.exe "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

The application will:
1. Download the audio from YouTube
2. Analyze the pitch and detect notes
3. Generate printer-friendly G-code
4. Save to `output/music.gcode`

### Option 2: Convert Local Audio File

```bash
G-Code-Radio.exe "song.mp3"
```

Supported formats: MP3, WAV, OGG, M4A, FLAC, AAC

### Option 3: Custom Output Location

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
