"""
Detect fundamental frequency (pitch) from audio

Implements various pitch detection algorithms.
"""

import numpy as np
import librosa
from src.utils.logger import Logger
from src.utils.error_handler import PitchDetectionError

logger = Logger.get_logger(__name__)


class PitchDetector:
    """Detects pitch/fundamental frequency from audio"""
    
    def __init__(self, sr: int = 22050, hop_length: int = 512):
        """
        Initialize the pitch detector
        
        Args:
            sr: Sample rate in Hz
            hop_length: Number of samples between frames
        """
        self.sr = sr
        self.hop_length = hop_length
    
    def detect_pitch(self, audio_file: str):
        """
        Detect pitch over time using piptrack algorithm
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Dictionary with 'frequencies' and 'times' arrays
            
        Raises:
            PitchDetectionError: If detection fails
        """
        try:
            logger.info(f"Detecting pitch in: {audio_file}")
            
            y, sr = librosa.load(audio_file, sr=self.sr)
            
            # Use piptrack for pitch detection
            f0 = librosa.yin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C8'), 
                            hop_length=self.hop_length)
            
            # Convert sample indices to time
            times = librosa.frames_to_time(np.arange(len(f0)), sr=sr, hop_length=self.hop_length)
            
            result = {
                'frequencies': f0,
                'times': times,
                'sr': sr,
                'hop_length': self.hop_length,
            }
            
            logger.info(f"Pitch detection complete: {len(f0)} frames")
            return result
        
        except Exception as e:
            error_msg = f"Failed to detect pitch: {str(e)}"
            logger.error(error_msg)
            raise PitchDetectionError(error_msg)
    
    def get_pitch_confidence(self, audio_file: str):
        """
        Get confidence score for detected pitches
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Array of confidence scores (0-1)
            
        Raises:
            PitchDetectionError: If computation fails
        """
        try:
            logger.debug(f"Computing pitch confidence for: {audio_file}")
            
            y, sr = librosa.load(audio_file, sr=self.sr)
            
            # Compute onset strength as confidence proxy
            onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=self.hop_length)
            
            # Normalize to [0, 1]
            confidence = onset_env / (np.max(onset_env) + 1e-8)
            
            logger.debug(f"Confidence shape: {confidence.shape}")
            return confidence
        
        except Exception as e:
            error_msg = f"Failed to compute pitch confidence: {str(e)}"
            logger.error(error_msg)
            raise PitchDetectionError(error_msg)
    
    def smooth_pitch(self, pitch_data: np.ndarray, median_filter_size: int = 5) -> np.ndarray:
        """
        Smooth pitch contour using median filtering
        
        Args:
            pitch_data: Array of pitch frequencies
            median_filter_size: Size of median filter window
            
        Returns:
            Smoothed pitch array
        """
        try:
            from scipy import signal
            smoothed = signal.medfilt(pitch_data, kernel_size=median_filter_size)
            return smoothed
        
        except Exception as e:
            logger.warning(f"Failed to smooth pitch: {str(e)}")
            return pitch_data
    
    def extract_voicing(self, pitch_data: np.ndarray, confidence: np.ndarray, 
                       threshold: float = 0.1) -> np.ndarray:
        """
        Extract voiced regions (where there is clear pitch)
        
        Args:
            pitch_data: Array of pitch frequencies
            confidence: Array of confidence scores
            threshold: Confidence threshold for voicing
            
        Returns:
            Boolean array indicating voiced frames
        """
        try:
            voiced = (confidence > threshold) & (pitch_data > 0)
            logger.debug(f"Voiced frames: {np.sum(voiced)}/{len(voiced)}")
            return voiced
        
        except Exception as e:
            logger.error(f"Failed to extract voicing: {str(e)}")
            return pitch_data > 0
