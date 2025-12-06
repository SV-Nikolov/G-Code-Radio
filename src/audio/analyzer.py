"""
Analyze audio to extract pitch, tempo, and other features

Uses librosa for audio feature extraction.
"""

import numpy as np
import librosa
from src.utils.logger import Logger
from src.utils.error_handler import AudioProcessingError

logger = Logger.get_logger(__name__)


class AudioAnalyzer:
    """Analyzes audio files for musical features"""
    
    def __init__(self, sr: int = 22050, hop_length: int = 512):
        """
        Initialize the analyzer
        
        Args:
            sr: Sample rate in Hz (default: 22050)
            hop_length: Number of samples between frames (default: 512)
        """
        self.sr = sr
        self.hop_length = hop_length
    
    def extract_features(self, audio_file: str) -> dict:
        """
        Extract all audio features
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Dictionary of extracted features
            
        Raises:
            AudioProcessingError: If extraction fails
        """
        try:
            logger.info(f"Extracting features from: {audio_file}")
            
            y, sr = librosa.load(audio_file, sr=self.sr)
            
            features = {
                'duration': librosa.get_duration(y=y, sr=sr),
                'rms': librosa.feature.rms(y=y, hop_length=self.hop_length)[0],
                'zero_crossing_rate': librosa.feature.zero_crossing_rate(y, hop_length=self.hop_length)[0],
                'spectral_centroid': librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=self.hop_length)[0],
                'chromagram': self.get_chromagram(audio_file),
                'onsets': self.get_onset_frames(audio_file),
            }
            
            logger.info("Feature extraction complete")
            return features
        
        except Exception as e:
            error_msg = f"Failed to extract features: {str(e)}"
            logger.error(error_msg)
            raise AudioProcessingError(error_msg)
    
    def get_chromagram(self, audio_file: str):
        """
        Extract chromagram (pitch content by note class)
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Chromagram representation (12 notes x time frames)
            
        Raises:
            AudioProcessingError: If extraction fails
        """
        try:
            logger.debug(f"Computing chromagram for: {audio_file}")
            
            y, sr = librosa.load(audio_file, sr=self.sr)
            
            # Compute chromagram
            chroma = librosa.feature.chroma_cqt(
                y=y,
                sr=sr,
                hop_length=self.hop_length,
                n_octaves=7,
                norm=2
            )
            
            logger.debug(f"Chromagram shape: {chroma.shape}")
            return chroma
        
        except Exception as e:
            error_msg = f"Failed to compute chromagram: {str(e)}"
            logger.error(error_msg)
            raise AudioProcessingError(error_msg)
    
    def get_onset_frames(self, audio_file: str):
        """
        Detect onset frames (note starts/transients)
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Array of onset frame indices
            
        Raises:
            AudioProcessingError: If detection fails
        """
        try:
            logger.debug(f"Detecting onsets in: {audio_file}")
            
            y, sr = librosa.load(audio_file, sr=self.sr)
            
            # Compute onset strength
            onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=self.hop_length)
            
            # Detect peaks in onset strength
            onset_frames = librosa.util.peak_pick(
                onset_env,
                pre_max=3,
                post_max=3,
                pre_avg=3,
                post_avg=3,
                delta=0.1,
                wait=10
            )
            
            logger.debug(f"Detected {len(onset_frames)} onset frames")
            return onset_frames
        
        except Exception as e:
            error_msg = f"Failed to detect onsets: {str(e)}"
            logger.error(error_msg)
            raise AudioProcessingError(error_msg)
    
    def get_spectrogram(self, audio_file: str, log_scale: bool = True):
        """
        Compute spectrogram
        
        Args:
            audio_file: Path to audio file
            log_scale: Whether to use log scale
            
        Returns:
            Spectrogram array
            
        Raises:
            AudioProcessingError: If computation fails
        """
        try:
            logger.debug(f"Computing spectrogram for: {audio_file}")
            
            y, sr = librosa.load(audio_file, sr=self.sr)
            
            # Compute STFT
            D = librosa.stft(y, hop_length=self.hop_length)
            
            if log_scale:
                # Convert to log scale
                S = librosa.power_to_db(np.abs(D) ** 2, ref=np.max)
            else:
                S = np.abs(D)
            
            logger.debug(f"Spectrogram shape: {S.shape}")
            return S
        
        except Exception as e:
            error_msg = f"Failed to compute spectrogram: {str(e)}"
            logger.error(error_msg)
            raise AudioProcessingError(error_msg)
