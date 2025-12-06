"""
Simplify note sequences based on complexity parameter

Reduces or preserves note detail in the melody.
"""

import numpy as np
from src.utils.logger import Logger
from src.utils.error_handler import AudioProcessingError

logger = Logger.get_logger(__name__)


class ComplexityReducer:
    """Reduces note sequence complexity"""
    
    def __init__(self):
        """Initialize the complexity reducer"""
        pass
    
    def reduce_complexity(self, notes: list, complexity_level: int) -> list:
        """
        Reduce note sequence complexity
        
        Args:
            notes: List of note dictionaries
            complexity_level: 0-100 (0=minimal, 100=maximum detail)
            
        Returns:
            Simplified note sequence
            
        Raises:
            AudioProcessingError: If reduction fails
        """
        try:
            if not notes:
                return notes
            
            # Clamp complexity to valid range
            complexity_level = max(0, min(100, complexity_level))
            
            logger.info(f"Reducing complexity: {complexity_level}%")
            
            if complexity_level == 100:
                # Keep all notes
                return notes
            elif complexity_level == 0:
                # Keep only first note
                return [notes[0]] if notes else []
            
            # Calculate reduction ratio
            keep_ratio = complexity_level / 100.0
            target_count = max(1, int(len(notes) * keep_ratio))
            
            # Use different strategies based on complexity
            if complexity_level < 30:
                # Heavy reduction - keep only important notes
                reduced = self._keep_important_notes(notes, target_count)
            elif complexity_level < 70:
                # Medium reduction - merge similar notes
                reduced = self._merge_similar_notes(notes, target_count)
            else:
                # Light reduction - remove very short notes
                reduced = self._remove_short_notes(notes, target_count)
            
            logger.info(f"Reduced from {len(notes)} to {len(reduced)} notes")
            return reduced
        
        except Exception as e:
            error_msg = f"Failed to reduce complexity: {str(e)}"
            logger.error(error_msg)
            raise AudioProcessingError(error_msg)
    
    def merge_similar_notes(self, notes: list, tolerance_cents: int = 50) -> list:
        """
        Merge consecutive notes with similar pitch
        
        Args:
            notes: List of note dictionaries
            tolerance_cents: MIDI tolerance in cents (100 cents = 1 semitone)
            
        Returns:
            Merged note sequence
        """
        try:
            if len(notes) <= 1:
                return notes
            
            merged = []
            current_group = [notes[0]]
            
            for i in range(1, len(notes)):
                note = notes[i]
                prev_note = current_group[-1]
                
                # Calculate pitch difference in cents
                midi_diff = abs(note['midi'] - prev_note['midi'])
                cents_diff = midi_diff * 100
                
                if cents_diff <= tolerance_cents:
                    # Similar pitch - add to group
                    current_group.append(note)
                else:
                    # Different pitch - save group and start new one
                    merged.append(self._merge_group(current_group))
                    current_group = [note]
            
            # Add final group
            if current_group:
                merged.append(self._merge_group(current_group))
            
            logger.debug(f"Merged similar notes: {len(notes)} → {len(merged)}")
            return merged
        
        except Exception as e:
            logger.error(f"Failed to merge similar notes: {str(e)}")
            return notes
    
    def _merge_group(self, note_group: list) -> dict:
        """
        Merge a group of notes into one
        
        Args:
            note_group: List of consecutive similar notes
            
        Returns:
            Merged note dictionary
        """
        # Take median MIDI note
        midi_values = [n['midi'] for n in note_group]
        merged_midi = int(np.median(midi_values))
        
        # Sum durations
        total_duration = sum(n['duration'] for n in note_group)
        
        # Use first note's start time
        start_time = note_group[0]['start_time']
        
        merged = note_group[0].copy()
        merged['midi'] = merged_midi
        merged['duration'] = total_duration
        merged['start_time'] = start_time
        merged['merged_count'] = len(note_group)
        
        return merged
    
    def _remove_short_notes(self, notes: list, target_count: int) -> list:
        """
        Remove shortest notes to reach target count
        
        Args:
            notes: List of note dictionaries
            target_count: Target number of notes
            
        Returns:
            Filtered note sequence
        """
        if len(notes) <= target_count:
            return notes
        
        # Sort by duration (ascending)
        sorted_notes = sorted(notes, key=lambda n: n['duration'])
        
        # Keep longest notes
        kept_indices = set(notes.index(n) for n in sorted_notes[-(target_count):])
        result = [n for i, n in enumerate(notes) if i in kept_indices]
        
        # Sort by original order
        return sorted(result, key=lambda n: n['start_time'])
    
    def _keep_important_notes(self, notes: list, target_count: int) -> list:
        """
        Keep only important notes (high energy/long duration)
        
        Args:
            notes: List of note dictionaries
            target_count: Target number of notes
            
        Returns:
            Filtered note sequence
        """
        if len(notes) <= target_count:
            return notes
        
        # Score notes by duration and onset
        scores = []
        for i, note in enumerate(notes):
            # Score based on duration
            duration_score = note['duration']
            
            # Score based on position (favor early notes)
            position_score = 1.0 / (1.0 + i * 0.1)
            
            # Combined score
            score = duration_score * 0.7 + position_score * 0.3
            scores.append(score)
        
        # Keep top scoring notes
        kept_indices = sorted(range(len(notes)), key=lambda i: scores[i], reverse=True)[:target_count]
        kept_indices = sorted(kept_indices)  # Sort by original order
        
        return [notes[i] for i in kept_indices]
