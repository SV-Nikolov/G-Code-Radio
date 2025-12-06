"""
Analyze and extract tempo information from audio

Detects BPM and beat positions.
"""

import numpy as np
import librosa
from src.utils.logger import Logger
from src.utils.error_handler import AudioProcessingError

logger = Logger.get_logger(__name__)


class TempoAnalyzer:
    """Analyzes tempo and beat information"""
    
    def __init__(self, sr: int = 22050, hop_length: int = 512):
        """
        Initialize the tempo analyzer
        
        Args:
            sr: Sample rate in Hz
            hop_length: Number of samples between frames
        """
        self.sr = sr
        self.hop_length = hop_length
    
    def estimate_tempo(self, audio_file: str) -> float:
        """
        Estimate tempo (BPM) from audio
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Estimated tempo in BPM
            
        Raises:
            AudioProcessingError: If estimation fails
        """
        try:
            logger.info(f"Estimating tempo for: {audio_file}")
            
            y, sr = librosa.load(audio_file, sr=self.sr)
            
            # Estimate tempo
            onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=self.hop_length)
            tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr, hop_length=self.hop_length)
            
            logger.info(f"Estimated tempo: {tempo:.1f} BPM")
            return tempo
        
        except Exception as e:
            error_msg = f"Failed to estimate tempo: {str(e)}"
            logger.error(error_msg)
            raise AudioProcessingError(error_msg)
    
    def detect_beats(self, audio_file: str):
        """
        Detect beat positions in audio
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Dictionary with 'frames' and 'times' arrays
            
        Raises:
            AudioProcessingError: If detection fails
        """
        try:
            logger.info(f"Detecting beats in: {audio_file}")
            
            y, sr = librosa.load(audio_file, sr=self.sr)
            
            # Detect beats
            onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=self.hop_length)
            _, beat_frames = librosa.beat.beat_track(
                onset_envelope=onset_env,
                sr=sr,
                hop_length=self.hop_length
            )
            
            # Convert frames to time
            beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=self.hop_length)
            
            result = {
                'frames': beat_frames,
                'times': beat_times,
            }
            
            logger.info(f"Detected {len(beat_frames)} beats")
            return result
        
        except Exception as e:
            error_msg = f"Failed to detect beats: {str(e)}"
            logger.error(error_msg)
            raise AudioProcessingError(error_msg)
    
    def estimate_meter(self, audio_file: str) -> dict:
        """
        Estimate time signature (meter) from audio
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Dictionary with meter information
            
        Raises:
            AudioProcessingError: If estimation fails
        """
        try:
            logger.debug(f"Estimating meter for: {audio_file}")
            
            y, sr = librosa.load(audio_file, sr=self.sr)
            
            # Get beat information
            onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=self.hop_length)
            tempo, beats = librosa.beat.beat_track(
                onset_envelope=onset_env,
                sr=sr,
                hop_length=self.hop_length
            )
            
            # Simple meter estimation based on beat intervals
            if len(beats) > 1:
                intervals = np.diff(beats)
                mean_interval = np.mean(intervals)
                
                # Common time signatures
                if 0.8 < mean_interval < 1.2:
                    meter = "4/4"
                elif 0.5 < mean_interval < 0.8:
                    meter = "3/4"
                else:
                    meter = "4/4"  # default
            else:
                meter = "4/4"
            
            result = {
                'meter': meter,
                'tempo': tempo,
                'beat_count': len(beats),
            }
            
            logger.debug(f"Estimated meter: {meter}")
            return result
        
        except Exception as e:
            error_msg = f"Failed to estimate meter: {str(e)}"
            logger.error(error_msg)
            raise AudioProcessingError(error_msg)
