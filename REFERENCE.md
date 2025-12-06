# G-Code Radio - Quick Reference

## 🚀 Launch Applications

### GUI (Recommended for Most Users)
```
G-Code-Radio-GUI.exe
```
- File browser and URL input
- Interactive parameter sliders
- Real-time visualization
- Statistics and analysis

### CLI (For Scripting)
```
G-Code-Radio.exe [input] [options]
```

---

## 🎚️ Parameter Quick Reference

| Parameter | Range | Default | Effect |
|-----------|-------|---------|--------|
| **Speed** | 0.5x - 3.0x | 1.0x | Playback speed (lower = slower) |
| **Pitch** | -12 to +12 semitones | 0 | Note height adjustment |
| **Complexity** | 0% - 100% | 50% | Movement detail level |

---

## 📊 GUI Tabs Explained

### 1. G-code Preview
- View raw printer commands
- Check file size and line count
- Verify syntax

### 2. Movement Visualization
- **XY Path**: 2D top-down view (green = start, red = end)
- **3D Path**: Full 3D movement trajectory
- **Axis Positions**: How X, Y, Z change over time
- **Feedrate**: Printer speed for each movement

### 3. Statistics
- Axis ranges and averages
- Feedrate analysis (min/max/mean)
- Total travel distance
- **Print time estimate** ⏱️

---

## 📝 CLI Examples

### YouTube to G-code
```bash
G-Code-Radio.exe "https://www.youtube.com/watch?v=..."
```
Output: `output/music.gcode`

### Local Audio File
```bash
G-Code-Radio.exe "song.mp3"
```

### Custom Output Path
```bash
G-Code-Radio.exe "song.mp3" --output "output\mysong.gcode"
```

### With Parameter Adjustment
```bash
G-Code-Radio.exe "song.mp3" --speed 1.5 --pitch 2 --complexity 75
```

### All Options
```bash
G-Code-Radio.exe --help
```

---

## 🎯 Tips for Best Results

### Choose Good Audio
- Clear vocals or single instruments work best
- Avoid heavily compressed audio
- Test with familiar songs first

### Optimize Parameters
- **For faster playback**: Increase speed (2.0x - 3.0x)
- **For slower playback**: Decrease speed (0.5x - 1.0x)
- **For detail**: Increase complexity (75% - 100%)
- **For simplicity**: Decrease complexity (0% - 50%)
- **Adjust pitch** if song is in unusual range

### Check Results
1. After conversion, click "Visualize"
2. Check "Movement Visualization" for bounds
3. Check "Statistics" for time estimate
4. Verify printer can handle feedrates in "Feedrate" tab

---

## 🔧 File Locations

- **Executables**: `dist/`
  - `G-Code-Radio.exe` - CLI version
  - `G-Code-Radio-GUI.exe` - GUI version
- **Output**: `output/` (default)
- **Source**: `src/` (all Python modules)
- **Tests**: `test_*.py` files

---

## ⚡ Supported Audio Formats

- MP3
- WAV
- OGG
- M4A
- FLAC
- AAC

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| File not found | Check full path, use Browse button in GUI |
| No notes detected | Try increasing complexity, check audio quality |
| Out of bounds | Reduce complexity or adjust pitch |
| Slow conversion | Normal for YouTube (downloading), try local file |
| Empty visualization | Need to convert file first |

---

## 📱 Features Summary

### GUI Version Includes
✓ File browser  
✓ Parameter sliders  
✓ Real-time progress  
✓ 3 visualization tabs  
✓ Statistics analysis  
✓ Print time estimation  

### CLI Version Includes
✓ Command-line interface  
✓ Batch processing support  
✓ Script automation  
✓ Advanced logging  
✓ Piping support  

---

## 🎵 How It Works

```
Audio Input
  ↓
[Pitch Detection] - Find frequencies
  ↓
[Note Detection] - Convert to MIDI notes
  ↓
[Parameter Control] - Apply speed/pitch/complexity
  ↓
[Movement Mapping] - Map notes to X/Y/Z positions
  ↓
[G-code Generation] - Create printer commands
  ↓
[Validation] - Safety checks (no extrusion)
  ↓
G-code Output
```

High notes → Higher positions, faster moves  
Low notes → Lower positions, slower moves  
Tempo → Speed of movement between notes  

---

## 📊 Visualization Interpretation

### High Feedrate (in Feedrate tab)
= High notes, fast tempo sections

### Low Feedrate
= Low notes, slow tempo sections

### XY Path Density
= Complexity setting (more movements = busier pattern)

### 3D Height Variations
= Pitch variations in audio

---

## 🚀 Getting Started

1. **Download**: `G-Code-Radio-GUI.exe`
2. **Run**: Double-click to launch
3. **Load Audio**: Browse or paste YouTube URL
4. **Adjust**: Use sliders to tune parameters
5. **Convert**: Click "Convert to G-code"
6. **Preview**: Click "Visualize" to see results
7. **Export**: G-code ready in `output/` folder

---

*Version: 1.0 | Build: 2 executables | Tests: 13/13 passing*
