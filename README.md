# 3D Printer Music Player

Turn your **Moment S1 (2014)** 3D printer into a musical instrument by playing tunes with the pitch of the stepper motors.  
Given a **YouTube link**, this tool:

1. Downloads the audio
2. Converts it into a simplified sequence of musical notes
3. Translates those notes into safe 3D-printer movement (G-code)
4. Lets your printer “perform” the song using only motion – **no heat, no extrusion**

---

## Features

- 🎵 **YouTube to G-code**  
  Paste a YouTube URL and generate a G-code file that plays the tune.

- 🎚️ **Three musical controls**
  - **Speed** – how fast the song plays on the printer  
  - **Pitch** – shifts the overall note range higher or lower  
  - **Complexity** – simplifies or preserves detail in the melody

- 🖨️ **Printer-safe by design**
  - Targets **Moment S1 (2014)** dimensions
  - No extrusion commands
  - No heat commands (hotend or bed)
  - Movements stay **within printer bounds** and avoid crashing into the bed

---

## How It Works

1. **Input**: You provide a YouTube link to a song.
2. **Audio Extraction**: The program downloads and extracts the audio track.
3. **Note Detection**: The audio is processed into a series of pitches and durations
   (simplified based on the chosen **complexity** setting).
4. **Parameter Mapping**:
   - **Speed** controls timing between movements.
   - **Pitch** maps musical notes to travel distances / axis frequencies.
   - **Complexity** controls how many notes are kept vs. merged/simplified.
5. **G-code Generation**:
   - Converts notes into axis moves (e.g., X/Y/Z) at specific feedrates.
   - Enforces printer bounds so no axis exceeds the Moment S1 build volume.
   - Generates **movement-only** G-code (no extrusion / no heating).
6. **Playback**:
   - You load the G-code on your printer like a normal print job.
   - The printer “plays” the tune via its stepper motor sounds.

---

## Requirements

> Adjust this section to match your actual implementation.

- A computer with:
  - Python 3.9+ (or your chosen language/runtime)
- A Moment S1 (2014) 3D printer connected via USB or using SD card / USB stick
- Internet access (for YouTube audio retrieval)
- Suggested Python dependencies (example):
  - `yt-dlp` or similar (download audio from YouTube)
  - `librosa` or another audio analysis library
  - `numpy` / `scipy` for signal processing

---

## Installation

```bash
# Clone this repository
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>

# (Optional) create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
