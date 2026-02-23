import random
from typing import List, Dict, Any, Optional
from .scales import get_scale_notes, get_triad_notes

# Rhythmic Patterns (Start time, Duration) for 1 bar (4 beats)
RHYTHMS = [
    # Simple Quarter Notes
    [(0.0, 1.0), (1.0, 1.0), (2.0, 1.0), (3.0, 1.0)],
    # 8th Note Run
    [(0.0, 0.5), (0.5, 0.5), (1.0, 0.5), (1.5, 0.5), (2.0, 1.0), (3.0, 1.0)],
    # Syncopated
    [(0.0, 0.75), (0.75, 0.25), (1.0, 1.0), (2.5, 0.5), (3.0, 1.0)],
    # Sparse / Trap-like
    [(0.0, 0.5), (0.5, 0.5), (2.0, 0.5), (2.5, 0.5), (3.5, 0.5)],
    # Drill-like (Triplets/Fast)
    [(0.0, 0.5), (0.5, 0.5), (1.0, 0.33), (1.33, 0.33), (1.66, 0.33), (2.0, 1.0), (3.0, 1.0)],
    # Drill Bell (Sparse)
    [(0.0, 1.5), (1.5, 1.5), (3.0, 1.0)],
    # Drill Repetitive (Ghost Notes)
    [(0.0, 0.5), (0.75, 0.25), (1.0, 0.5), (1.75, 0.25), (2.0, 0.5), (2.75, 0.25), (3.0, 0.5)],
    # Rolling Hi-Hat Counter
    [(0.0, 0.25), (0.25, 0.25), (0.5, 0.25), (0.75, 0.25), (1.5, 0.5), (2.5, 1.0)],
    # Off-beat Stabs
    [(0.5, 0.5), (1.5, 0.5), (2.5, 0.5), (3.5, 0.5)],
    # Pop Anthem (Syncopated)
    [(0.0, 1.5), (1.5, 0.5), (2.0, 1.0), (3.0, 1.0)],
    # Emotional Ballad
    [(0.0, 2.0), (2.0, 0.5), (2.5, 0.5), (3.0, 1.0)],
    # Rapid Fire
    [(0.0, 0.25), (0.25, 0.25), (0.5, 0.25), (0.75, 0.25), (1.0, 0.5), (1.5, 0.5), (2.0, 0.5), (2.5, 0.5), (3.0, 1.0)]
]

def get_closest_scale_tone(target_pitch: int, scale_notes: List[int]) -> int:
    """Finds the closest note in the scale to the target pitch."""
    if not scale_notes:
        return target_pitch
    return min(scale_notes, key=lambda x: abs(x - target_pitch))

class Motif:
    def __init__(self, rhythm: List[tuple], intervals: List[int], start_degree: int = 0):
        self.rhythm = rhythm
        self.intervals = intervals # Intervals relative to start_degree
        self.start_degree = start_degree

def generate_motif(mood: str) -> Motif:
    """Generates a rhythmic and melodic motif based on mood."""
    
    # Select Rhythm
    if "walker" in mood.lower():
        # Walker: Simple, repetitive, emotional. Often starts on off-beat or long notes.
        possible_rhythms = [
            [(0.0, 1.5), (1.5, 0.5), (2.0, 1.0), (3.0, 1.0)], # Dotted Q + 8th + Q + Q
            [(0.0, 1.0), (1.0, 1.0), (2.0, 1.0), (3.0, 1.0)], # 4 Quarters
            [(0.0, 0.5), (0.5, 0.5), (1.0, 1.0), (2.0, 1.0), (3.0, 1.0)], # 2 8ths + 3 Quarters
        ]
        rhythm = random.choice(possible_rhythms)
        # Intervals: Stepwise motion mostly. 
        # Example: 0, 1, 2, 0 (C D E C)
        intervals = [0, 1, 2, 0] if len(rhythm) >= 4 else [0, 1, 0]
        # Adjust intervals to match rhythm length
        # Start with simple steps
        intervals = [random.choice([-1, 0, 1, 2]) for _ in range(len(rhythm))]
        
        # Walker themes often ascend then resolve
        if len(intervals) >= 3:
            intervals[0] = 0
            intervals[1] = 1
            intervals[2] = 2
    
    elif "drill" in mood.lower():
        rhythm = random.choice([r for r in RHYTHMS if len(r) > 5])
        # Drill: Fast repetitive notes, small intervals
        intervals = [random.choice([0, 0, 1, -1]) for _ in range(len(rhythm))]
        
    elif "pop" in mood.lower() or "tropical" in mood.lower():
        rhythm = random.choice([RHYTHMS[9], RHYTHMS[10], RHYTHMS[2]])
        # Pop: Catchy, skips allowed
        intervals = [random.choice([0, 2, 4, -2]) for _ in range(len(rhythm))]

    elif "reggaeton" in mood.lower():
        # Tresillo / Latin feel
        rhythm = [(0.0, 0.75), (0.75, 0.25), (1.0, 1.0), (2.0, 0.5), (2.5, 0.5), (3.0, 1.0)]
        # Simple, repetitive melody
        intervals = [0, 0, 2, 0, -1, 0]
        # Adjust length
        intervals = (intervals * 2)[:len(rhythm)]
        
    elif "synthwave" in mood.lower():
        # 8th note driving or sustained
        rhythm = [(0.0, 0.5), (0.5, 0.5), (1.0, 0.5), (1.5, 0.5), (2.0, 1.0), (3.0, 1.0)]
        # Arpeggiated feel
        intervals = [0, 2, 4, 7, 4, 2]
        intervals = (intervals * 2)[:len(rhythm)]

    elif "rnb" in mood.lower():
        # Slow, expressive, maybe triplets
        rhythm = [(0.0, 1.5), (1.5, 0.5), (2.0, 0.33), (2.33, 0.33), (2.66, 0.33), (3.0, 1.0)]
        # Pentatonic / Bluesy runs
        intervals = [0, -1, 0, 2, 4, 7]
        intervals = (intervals * 2)[:len(rhythm)]
        
    else:
        rhythm = random.choice(RHYTHMS)
        intervals = [random.choice([-2, -1, 0, 1, 2]) for _ in range(len(rhythm))]
        
    return Motif(rhythm, intervals)

def generate_melody(key: str, scale: str, progression: List[Dict[str, Any]], complexity: float = 0.5, mood: str = "dark_trap") -> List[Dict[str, Any]]:
    """
    Generates a melody track based on the chord progression using Motif-based Call & Answer logic.
    """
    melody_events = []
    
    # 1. Setup Range based on Mood
    low_oct = 4
    high_oct = 5
    if "drill" in mood.lower():
        low_oct = 5
        high_oct = 6
    elif "walker" in mood.lower():
        low_oct = 5
        high_oct = 6 # High lead for Walker style
    elif "lo_fi" in mood.lower() or "neo_soul" in mood.lower():
        low_oct = 4
        high_oct = 5
    
    # Get available notes
    all_scale_notes = []
    for oct_idx in range(low_oct, high_oct + 1):
        all_scale_notes.extend(get_scale_notes(key, scale, octave=oct_idx))
    
    all_scale_notes = sorted(list(set(all_scale_notes)))
    if not all_scale_notes:
        return []

    # 2. Generate Main Motif (Theme A)
    motif_a = generate_motif(mood)
    
    # 3. Generate Secondary Motif (Theme B) - Variation or different
    motif_b = generate_motif(mood)
    
    # Structure: A A B A (Classic Pop/Walker)
    # Walker structure often: A1 (Call), A2 (Answer), A1 (Call), B (Resolution/Bridge)
    phrase_structure = ["A", "A_var", "A", "B"]
    
    # State tracking
    # Start around the middle of the range
    current_anchor_index = len(all_scale_notes) // 2
    
    for i, chord in enumerate(progression):
        chord_notes = chord["notes"]
        chord_duration = chord.get("duration", 4.0)
        
        # Determine current phrase type
        phrase_type = phrase_structure[i % len(phrase_structure)]
        
        current_motif = motif_a if "A" in phrase_type else motif_b
        
        # Determine anchor note for this bar based on Chord
        # Try to find a chord tone that is close to our current range
        chord_tones_in_range = [n for n in all_scale_notes if (n % 12) in [c % 12 for c in chord_notes]]
        
        if chord_tones_in_range:
            # Pick a chord tone as the anchor for the motif start
            # Prefer the root or 5th of the chord
            root_pitch = chord_notes[0] % 12
            fifth_pitch = (chord_notes[0] + 7) % 12
            
            preferred_tones = [n for n in chord_tones_in_range if (n % 12) == root_pitch or (n % 12) == fifth_pitch]
            if not preferred_tones:
                preferred_tones = chord_tones_in_range
                
            # Pick one closest to current anchor to avoid huge jumps
            # But for Walker, we might WANT high leads.
            if "walker" in mood.lower():
                # Force high range
                anchor_note = max(preferred_tones, key=lambda x: x) # Pick highest available chord tone
            else:
                anchor_note = min(preferred_tones, key=lambda x: abs(all_scale_notes.index(x) - current_anchor_index))
                
            try:
                start_index = all_scale_notes.index(anchor_note)
            except ValueError:
                start_index = len(all_scale_notes) // 2
        else:
            start_index = current_anchor_index

        # Apply Motif
        rhythm = current_motif.rhythm
        intervals = current_motif.intervals
        
        # Variation logic for A_var
        if phrase_type == "A_var":
            # Invert intervals or shift start
            intervals = [-1 * inv for inv in intervals]
        
        bar_start_time = i * 4.0 # Assuming 4/4 bars of length 4.0
        
        for k, (rel_start, duration) in enumerate(rhythm):
            if k >= len(intervals): break
            
            # Calculate target index
            # motif.intervals are relative steps in the scale
            step = intervals[k]
            target_idx = start_index + step
            
            # Bound check
            target_idx = max(0, min(len(all_scale_notes) - 1, target_idx))
            
            note_val = all_scale_notes[target_idx]
            
            # Humanization
            velocity = 90 + random.randint(-10, 10)
            if k == 0: velocity += 10 # Accent first note
            
            # Walker specific: High velocity for leads
            if "walker" in mood.lower():
                velocity = min(127, velocity + 15)
                
            timing_offset = random.uniform(-0.02, 0.02)
            
            melody_events.append({
                "note": note_val,
                "time": bar_start_time + rel_start + timing_offset,
                "duration": duration * 0.95, # Legato-ish
                "velocity": velocity
            })
            
        # Update anchor for next bar to follow the melody contour (Gap Fill)
        # If we ended high, maybe start lower next time, or stay there.
        # For now, let's reset to a chord tone of the next chord (handled at start of loop)
            
    return melody_events
