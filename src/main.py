"""
Main entry point for G-Code Radio application
"""

import argparse
import sys
import time
from pathlib import Path

from src.utils.logger import Logger
from src.utils.error_handler import handle_error, GCodeRadioException

# Initialize logging
Logger.setup_logging(level="INFO")
logger = Logger.get_logger(__name__)


def main():
    """Main application entry point"""
    try:
        parser = argparse.ArgumentParser(
            description="Convert YouTube audio to 3D printer G-code music",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  %(prog)s "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --speed 1.5 --pitch 2 --complexity 75
  %(prog)s "song.mp3" --output "output/song.gcode"
            """
        )
        
        parser.add_argument("input", help="YouTube URL or audio file path")
        
        parser.add_argument(
            "--speed",
            type=float,
            default=1.0,
            help="Playback speed multiplier (0.5-3.0, default: 1.0)"
        )
        
        parser.add_argument(
            "--pitch",
            type=int,
            default=0,
            help="Pitch shift in semitones (-12 to +12, default: 0)"
        )
        
        parser.add_argument(
            "--complexity",
            type=int,
            default=50,
            help="Note complexity level (0-100, default: 50)"
        )
        
        parser.add_argument(
            "--output",
            type=str,
            default="output/music.gcode",
            help="Output G-code file path (default: output/music.gcode)"
        )
        
        parser.add_argument(
            "--log-level",
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
            default="INFO",
            help="Logging level (default: INFO)"
        )
        
        args = parser.parse_args()
        
        # Set logging level
        Logger.setup_logging(level=args.log_level)
        
        print("\n" + "=" * 60)
        print(" G-Code Radio v0.1.0 - 3D Printer Music Player")
        print("=" * 60 + "\n")
        
        logger.info(f"Input: {args.input}")
        logger.info(f"Speed: {args.speed}x")
        logger.info(f"Pitch: {args.pitch:+d} semitones")
        logger.info(f"Complexity: {args.complexity}%")
        logger.info(f"Output: {args.output}\n")
        
        # Validate parameters
        from src.mapping.parameter_controller import ParameterController
        pc = ParameterController()
        pc.validate_parameters(args.speed, args.pitch, args.complexity)
        
        # Detect if input is a URL or file
        if args.input.startswith(('http://', 'https://')):
            logger.info("Detected YouTube URL")
            process_youtube_url(args)
        else:
            logger.info("Detected audio file")
            process_audio_file(args)
        
        print("\n" + "=" * 60)
        print(" Conversion complete!")
        print(f" Output: {args.output}")
        print("=" * 60 + "\n")
    
    except GCodeRadioException as e:
        logger.error(handle_error(e))
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)


def process_youtube_url(args):
    """Process YouTube URL and convert to G-code"""
    logger.info("=" * 60)
    logger.info("PHASE 1: Downloading audio from YouTube")
    logger.info("=" * 60)
    
    from src.audio.downloader import YouTubeDownloader
    from src.audio.extractor import AudioExtractor
    
    # Download audio
    downloader = YouTubeDownloader()
    audio_file = downloader.download(args.input, "downloads/audio")
    
    # Convert to WAV if needed
    if not audio_file.endswith('.wav'):
        logger.info("Converting to WAV format...")
        extractor = AudioExtractor()
        audio_file = extractor.convert_to_wav(audio_file)
    
    # Process the audio file
    process_audio_file_internal(audio_file, args)


def process_audio_file(args):
    """Process local audio file and convert to G-code"""
    audio_file = args.input
    
    if not Path(audio_file).exists():
        raise GCodeRadioException(f"Audio file not found: {audio_file}")
    
    # Convert to WAV if needed
    from src.audio.extractor import AudioExtractor
    if not audio_file.endswith('.wav'):
        logger.info("Converting to WAV format...")
        extractor = AudioExtractor()
        audio_file = extractor.convert_to_wav(audio_file)
    
    process_audio_file_internal(audio_file, args)


def process_audio_file_internal(audio_file: str, args):
    """Internal method to process audio file through the full pipeline"""
    
    logger.info("=" * 60)
    logger.info("PHASE 2: Analyzing audio")
    logger.info("=" * 60)
    
    from src.audio.analyzer import AudioAnalyzer
    from src.signal_processing.pitch_detection import PitchDetector
    from src.signal_processing.note_detection import NoteDetector
    from src.mapping.note_mapper import NoteMapper
    from src.mapping.parameter_controller import ParameterController
    from src.mapping.bounds_validator import BoundsValidator
    from src.gcode.gcode_generator import GCodeGenerator
    from src.gcode.gcode_validator import GCodeValidator
    from src.printer.moment_s1_config import MomentS1Config
    
    # Step 1: Extract audio features
    analyzer = AudioAnalyzer()
    features = analyzer.extract_features(audio_file)
    onsets = analyzer.get_onset_frames(audio_file)
    
    # Step 2: Detect pitch
    logger.info("Detecting pitch...")
    pitch_detector = PitchDetector()
    pitch_data = pitch_detector.detect_pitch(audio_file)
    confidence = pitch_detector.get_pitch_confidence(audio_file)
    
    # Step 3: Detect notes
    logger.info("Detecting notes...")
    note_detector = NoteDetector()
    voiced = pitch_detector.extract_voicing(pitch_data['frequencies'], confidence, threshold=0.1)
    notes = note_detector.detect_notes(pitch_data, onsets, voiced)
    
    if not notes:
        logger.warning("No notes detected in audio")
        return
    
    logger.info(f"Detected {len(notes)} notes")
    
    # Step 4: Apply parameters
    logger.info("=" * 60)
    logger.info("PHASE 3: Applying parameters")
    logger.info("=" * 60)
    
    param_controller = ParameterController()
    notes = param_controller.apply_all_parameters(
        notes, 
        args.speed, 
        args.pitch, 
        args.complexity
    )
    
    logger.info(f"After parameter adjustment: {len(notes)} notes")
    
    # Step 5: Convert notes to movements
    logger.info("=" * 60)
    logger.info("PHASE 4: Generating movements")
    logger.info("=" * 60)
    
    printer_config = MomentS1Config()
    note_mapper = NoteMapper(printer_config)
    
    movements = []
    for note in notes:
        try:
            movement = note_mapper.note_to_movement(note['midi'], note['duration'])
            movements.append(movement)
        except Exception as e:
            logger.warning(f"Failed to convert note: {str(e)}")
    
    logger.info(f"Generated {len(movements)} movements")
    
    # Step 6: Validate bounds
    logger.info("Validating bounds...")
    bounds_validator = BoundsValidator(printer_config)
    movements = bounds_validator.validate_all_movements(movements)
    
    # Step 7: Generate G-code
    logger.info("=" * 60)
    logger.info("PHASE 5: Generating G-code")
    logger.info("=" * 60)
    
    gcode_generator = GCodeGenerator(printer_config)
    gcode_path = gcode_generator.write_gcode_file(
        movements,
        args.output,
        title=Path(audio_file).stem
    )
    
    # Step 8: Validate G-code
    logger.info("=" * 60)
    logger.info("PHASE 6: Validating G-code")
    logger.info("=" * 60)
    
    with open(gcode_path, 'r') as f:
        gcode_content = f.read()
    
    gcode_validator = GCodeValidator(printer_config)
    is_valid, report = gcode_validator.validate_all(gcode_content)
    
    logger.info(f"Validation: {report['checks_passed']}/{report['checks_total']} checks passed")
    logger.info(f"  - No extrusion: {report['no_extrusion']}")
    logger.info(f"  - No heating: {report['no_heating']}")
    logger.info(f"  - In bounds: {report['in_bounds']}")
    
    if is_valid:
        logger.info("✓ G-code validation passed!")
    else:
        logger.warning("⚠ G-code validation failed!")


if __name__ == "__main__":
    main()
