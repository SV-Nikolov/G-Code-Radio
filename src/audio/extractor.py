"""
Extract and convert audio files to standard formats

Handles various audio formats and conversion operations.
"""

import os
from pathlib import Path
import librosa
import numpy as np
from pydub import AudioSegment
from src.utils.logger import Logger
from src.utils.error_handler import AudioProcessingError

logger = Logger.get_logger(__name__)


class AudioExtractor:
    """Extracts and converts audio files"""
    
    SUPPORTED_FORMATS = ['mp3', 'wav', 'ogg', 'm4a', 'flac', 'aac']
    
    def __init__(self, sr: int = 22050):
        """
        Initialize the extractor
        
        Args:
            sr: Sample rate in Hz (default: 22050)
        """
        self.sr = sr
    
    def convert_to_wav(self, input_file: str, output_file: str = None) -> str:
        """
        Convert audio file to WAV format
        
        Args:
            input_file: Path to input audio file
            output_file: Path to output WAV file (optional)
            
        Returns:
            Path to converted WAV file
            
        Raises:
            AudioProcessingError: If conversion fails
        """
        try:
            if output_file is None:
                base_name = os.path.splitext(input_file)[0]
                output_file = base_name + "_converted.wav"
            
            logger.info(f"Converting {input_file} to WAV format")
            
            # Use pydub for conversion
            try:
                audio = AudioSegment.from_file(input_file)
                audio.export(output_file, format="wav")
                logger.info(f"Conversion complete: {output_file}")
                return output_file
            except Exception as pydub_error:
                # Fallback to librosa
                logger.debug(f"Pydub conversion failed, trying librosa: {pydub_error}")
                y, sr = librosa.load(input_file, sr=self.sr)
                import soundfile as sf
                sf.write(output_file, y, sr)
                logger.info(f"Conversion complete (librosa): {output_file}")
                return output_file
        
        except Exception as e:
            error_msg = f"Failed to convert audio: {str(e)}"
            logger.error(error_msg)
            raise AudioProcessingError(error_msg)
    
    def get_duration(self, audio_file: str) -> float:
        """
        Get audio duration in seconds
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Duration in seconds
            
        Raises:
            AudioProcessingError: If file cannot be read
        """
        try:
            logger.debug(f"Getting duration for: {audio_file}")
            y, sr = librosa.load(audio_file, sr=self.sr)
            duration = librosa.get_duration(y=y, sr=sr)
            logger.debug(f"Duration: {duration:.2f}s")
            return duration
        
        except Exception as e:
            error_msg = f"Failed to get audio duration: {str(e)}"
            logger.error(error_msg)
            raise AudioProcessingError(error_msg)
    
    def load_audio(self, audio_file: str, sr: int = None):
        """
        Load audio file as numpy array
        
        Args:
            audio_file: Path to audio file
            sr: Sample rate (uses self.sr if None)
            
        Returns:
            Tuple of (audio_data, sample_rate)
            
        Raises:
            AudioProcessingError: If file cannot be read
        """
        try:
            if sr is None:
                sr = self.sr
            
            logger.debug(f"Loading audio: {audio_file} at {sr}Hz")
            y, sr_loaded = librosa.load(audio_file, sr=sr)
            return y, sr_loaded
        
        except Exception as e:
            error_msg = f"Failed to load audio file: {str(e)}"
            logger.error(error_msg)
            raise AudioProcessingError(error_msg)
    
    def normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Normalize audio to [-1, 1] range
        
        Args:
            audio_data: Audio array
            
        Returns:
            Normalized audio array
        """
        try:
            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                normalized = audio_data / max_val
            else:
                normalized = audio_data
            logger.debug("Audio normalization complete")
            return normalized
        
        except Exception as e:
            error_msg = f"Failed to normalize audio: {str(e)}"
            logger.error(error_msg)
            raise AudioProcessingError(error_msg)
