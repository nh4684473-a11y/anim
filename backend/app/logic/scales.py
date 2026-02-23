
import random
from typing import List, Dict

# Constants
NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
NOTE_TO_INT = {note: i for i, note in enumerate(NOTES)}

SCALES = {
    "minor": [0, 2, 3, 5, 7, 8, 10],            # Natural Minor (Aeolian)
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],   # Harmonic Minor (Dark/Trap)
    "phrygian": [0, 1, 3, 5, 7, 8, 10],         # Phrygian (Dark/Aggressive)
    "dorian": [0, 2, 3, 5, 7, 9, 10],           # Dorian (Jazzy/Soulful)
    "lydian": [0, 2, 4, 6, 7, 9, 11],           # Lydian (Dreamy/Bright)
    "minor_pentatonic": [0, 3, 5, 7, 10],       # Simple/Safe
    "major": [0, 2, 4, 5, 7, 9, 11]             # Major
}

def get_note_index(note_name: str) -> int:
    """Converts a note name (e.g., 'C#') to its integer index (0-11)."""
    flat_map = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"}
    norm_note = flat_map.get(note_name, note_name)
    return NOTE_TO_INT.get(norm_note, 0)

def get_scale_intervals(scale_type: str) -> List[int]:
    return SCALES.get(scale_type.lower(), SCALES["minor"])

def get_triad_notes(root_note_name: str, scale_type: str, degree: int, octave: int = 4) -> List[int]:
    """
    Generates a triad (3 notes) for a specific scale degree.
    degree: 1-based (1 = i, 2 = ii, etc.)
    """
    root_val = get_note_index(root_note_name)
    intervals = get_scale_intervals(scale_type)
    
    # Create a long list of relative intervals spanning 2 octaves
    # e.g., [0, 2, 3... 12, 14, 15...]
    extended_intervals = intervals + [i + 12 for i in intervals] + [i + 24 for i in intervals]
    
    # Adjust for 0-based index
    deg_idx = degree - 1
    
    # Get the intervals for the chord (Root, 3rd, 5th)
    # This picks the specific notes from the scale
    i1 = extended_intervals[deg_idx]
    i2 = extended_intervals[deg_idx + 2]
    i3 = extended_intervals[deg_idx + 4]
    
    # Calculate absolute MIDI notes
    base_midi = (octave + 1) * 12 + root_val # C4 = 60. If octave=4, (4+1)*12 = 60.
    
    return [base_midi + i1, base_midi + i2, base_midi + i3]

def get_scale_notes(root_note_name: str, scale_type: str, octave: int = 4) -> List[int]:
    """
    Returns all notes in the scale for a given octave.
    """
    root_val = get_note_index(root_note_name)
    intervals = get_scale_intervals(scale_type)
    
    base_midi = (octave + 1) * 12 + root_val
    
    return [base_midi + i for i in intervals]
