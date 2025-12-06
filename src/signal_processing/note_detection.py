"""
Convert continuous pitch data to discrete musical notes

Maps frequencies to MIDI note numbers and note names.
"""

import numpy as np
from src.utils.logger import Logger
from src.utils.error_handler import NoteDetectionError

logger = Logger.get_logger(__name__)


class NoteDetector:
    """Converts detected pitches to discrete musical notes"""
    
    # MIDI note numbers for reference
    NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    A4_MIDI = 69
    A4_FREQ = 440.0
    
    def __init__(self):
        """Initialize the note detector"""
        pass
    
    def pitch_to_midi(self, frequency: float) -> int:
        """
        Convert frequency (Hz) to MIDI note number
        
        Args:
            frequency: Frequency in Hz
            
        Returns:
            MIDI note number (0-127)
        """
        try:
            if frequency <= 0:
                return 0
            
            # MIDI note formula: 69 + 12 * log2(f/440)
            midi_float = self.A4_MIDI + 12 * np.log2(frequency / self.A4_FREQ)
            midi_note = int(np.round(midi_float))
            
            # Clamp to valid range
            midi_note = max(0, min(127, midi_note))
            
            return midi_note
        
        except Exception as e:
            logger.error(f"Failed to convert frequency to MIDI: {str(e)}")
            raise NoteDetectionError(f"Pitch to MIDI conversion failed: {str(e)}")
    
    def midi_to_frequency(self, midi_number: int) -> float:
        """
        Convert MIDI note number to frequency (Hz)
        
        Args:
            midi_number: MIDI note number (0-127)
            
        Returns:
            Frequency in Hz
        """
        try:
            # Inverse formula: f = 440 * 2^((m-69)/12)
            frequency = self.A4_FREQ * (2.0 ** ((midi_number - self.A4_MIDI) / 12.0))
            return frequency
        
        except Exception as e:
            logger.error(f"Failed to convert MIDI to frequency: {str(e)}")
            raise NoteDetectionError(f"MIDI to frequency conversion failed: {str(e)}")
    
    def midi_to_note_name(self, midi_number: int) -> str:
        """
        Convert MIDI note number to note name
        
        Args:
            midi_number: MIDI note number (0-127)
            
        Returns:
            Note name (e.g., "C4", "A#3")
        """
        try:
            if not (0 <= midi_number <= 127):
                raise ValueError(f"MIDI number out of range: {midi_number}")
            
            octave = (midi_number // 12) - 1
            note_index = midi_number % 12
            note_name = self.NOTE_NAMES[note_index]
            
            return f"{note_name}{octave}"
        
        except Exception as e:
            logger.error(f"Failed to convert MIDI to note name: {str(e)}")
            raise NoteDetectionError(f"MIDI to note name conversion failed: {str(e)}")
    
    def frequency_to_note_name(self, frequency: float) -> str:
        """
        Convert frequency directly to note name
        
        Args:
            frequency: Frequency in Hz
            
        Returns:
            Note name (e.g., "C4", "A#3")
        """
        midi = self.pitch_to_midi(frequency)
        return self.midi_to_note_name(midi)
    
    def detect_notes(self, pitch_data: dict, onsets: np.ndarray, 
                    voiced: np.ndarray = None) -> list:
        """
        Detect discrete notes from pitch data
        
        Args:
            pitch_data: Dictionary with 'frequencies' and 'times'
            onsets: Onset frame indices
            voiced: Optional boolean array indicating voiced frames
            
        Returns:
            List of detected notes with MIDI numbers and durations
            
        Raises:
            NoteDetectionError: If detection fails
        """
        try:
            logger.info("Detecting notes from pitch data")
            
            frequencies = pitch_data['frequencies']
            times = pitch_data['times']
            sr = pitch_data['sr']
            hop_length = pitch_data['hop_length']
            
            # Default voiced mask
            if voiced is None:
                voiced = frequencies > 0
            
            notes = []
            
            if len(onsets) == 0:
                logger.warning("No onsets detected")
                return notes
            
            # Process each onset
            for i, onset_idx in enumerate(onsets):
                # Find next onset or end
                if i + 1 < len(onsets):
                    next_onset_idx = onsets[i + 1]
                else:
                    next_onset_idx = len(frequencies)
                
                # Extract pitch contour for this note
                note_section = frequencies[onset_idx:next_onset_idx]
                voiced_section = voiced[onset_idx:next_onset_idx]
                
                if np.sum(voiced_section) == 0:
                    continue  # No voiced segment
                
                # Get median frequency of voiced frames
                voiced_freqs = note_section[voiced_section]
                if len(voiced_freqs) == 0:
                    continue
                
                median_freq = np.median(voiced_freqs)
                midi_note = self.pitch_to_midi(median_freq)
                
                # Calculate duration
                start_time = times[onset_idx]
                end_time = times[min(next_onset_idx - 1, len(times) - 1)]
                duration = end_time - start_time
                
                note = {
                    'midi': midi_note,
                    'frequency': median_freq,
                    'note_name': self.midi_to_note_name(midi_note),
                    'start_time': start_time,
                    'duration': duration,
                    'onset_frame': onset_idx,
                }
                
                notes.append(note)
            
            logger.info(f"Detected {len(notes)} notes")
            return notes
        
        except Exception as e:
            error_msg = f"Failed to detect notes: {str(e)}"
            logger.error(error_msg)
            raise NoteDetectionError(error_msg)
