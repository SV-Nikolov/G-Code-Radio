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
    
    def __init__(self, output_dir: str = "downloads", cookie_file: str = None):
        """
        Initialize the downloader
        
        Args:
            output_dir: Directory to save downloaded files
            cookie_file: Path to cookies.txt file for YouTube authentication
        """
        self.output_dir = output_dir
        self.cookie_file = cookie_file
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
                # Prefer m4a audio if available, then any bestaudio
                'format': 'bestaudio[ext=m4a]/bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                    'preferredquality': '192',
                }],
                'outtmpl': output_path.replace('.wav', ''),
                'quiet': False,
                'no_warnings': False,
                'nocheckcertificate': True,
                'ignoreerrors': False,
                'no_color': True,
                'extractor_args': {
                    'youtube': {
                        'skip': ['dash', 'hls'],
                    }
                },
                # Add user agent to appear as regular browser
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-us,en;q=0.5',
                    'Sec-Fetch-Mode': 'navigate',
                },
            }
            
            # If cookie file provided, use it directly
            if self.cookie_file:
                if os.path.exists(self.cookie_file):
                    logger.info(f"Using cookie file: {self.cookie_file}")
                    ydl_opts['cookiefile'] = self.cookie_file
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
                else:
                    logger.warning(f"Cookie file not found: {self.cookie_file}. Falling back to browser cookies.")
            
            # Otherwise try browser cookies
            browser_order = [
                ('chrome', None),
                ('chrome', 'Default'),
                ('chrome', 'Profile 1'),
                ('chrome', 'Profile 2'),
                ('chrome', 'Profile 3'),
                ('edge', None),
                ('firefox', None),
            ]
            last_error = None
            
            for browser, profile in browser_order:
                try:
                    opts = ydl_opts.copy()
                    opts['cookiesfrombrowser'] = (browser,) if profile is None else (browser, profile)
                    profile_msg = profile if profile else 'default'
                    logger.info(f"Trying YouTube download with {browser} ({profile_msg}) cookies...")
                    with yt_dlp.YoutubeDL(opts) as ydl:
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
                except Exception as err:
                    last_error = err
                    logger.warning(f"{browser} cookie attempt failed: {err}")
                    continue

            if last_error:
                raise last_error
        
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
