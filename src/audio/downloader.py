"""
Download audio from YouTube links

Uses yt-dlp to fetch and extract audio tracks.
"""

import os
from pathlib import Path
import yt_dlp
from src.utils.logger import Logger
from src.utils.error_handler import AudioDownloadError

logger = Logger.get_logger(__name__)


class YouTubeDownloader:
    """Downloads audio from YouTube URLs"""
    
    def __init__(self, output_dir: str = "downloads"):
        """
        Initialize the downloader
        
        Args:
            output_dir: Directory to save downloaded files
        """
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    def download(self, url: str, output_path: str = None) -> str:
        """
        Download audio from YouTube URL
        
        Args:
            url: YouTube URL
            output_path: Path to save the audio file (optional)
            
        Returns:
            Path to downloaded audio file
            
        Raises:
            AudioDownloadError: If download fails
        """
        try:
            logger.info(f"Downloading audio from: {url}")
            
            if output_path is None:
                output_path = os.path.join(self.output_dir, "%(title)s.%(ext)s")
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                    'preferredquality': '192',
                }],
                'outtmpl': output_path.replace('.wav', ''),
                'quiet': False,
                'no_warnings': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                audio_path = filename.replace('.webm', '.wav').replace('.m4a', '.wav')
                
                if not os.path.exists(audio_path):
                    # Try common audio extensions
                    base_path = os.path.splitext(filename)[0]
                    for ext in ['.wav', '.mp3', '.m4a', '.webm']:
                        candidate = base_path + ext
                        if os.path.exists(candidate):
                            audio_path = candidate
                            break
                
                logger.info(f"Download complete: {audio_path}")
                return audio_path
        
        except Exception as e:
            error_msg = f"Failed to download audio from {url}: {str(e)}"
            logger.error(error_msg)
            raise AudioDownloadError(error_msg)
    
    def get_video_info(self, url: str) -> dict:
        """
        Get video information without downloading
        
        Args:
            url: YouTube URL
            
        Returns:
            Dictionary with video metadata
            
        Raises:
            AudioDownloadError: If fetching info fails
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'url': url,
                }
        
        except Exception as e:
            error_msg = f"Failed to get video info from {url}: {str(e)}"
            logger.error(error_msg)
            raise AudioDownloadError(error_msg)
