import random
import math
from typing import List, Dict, Any

def euclidean_pattern(steps: int, pulses: int) -> List[int]:
    """
    Generates a Euclidean rhythm pattern using Bresenham's line algorithm.
    Returns a list of 1s (hits) and 0s (rests).
    """
    pattern = []
    bucket = steps  # Initialize bucket to steps to ensure a hit on the first beat
    for _ in range(steps):
        bucket += pulses
        if bucket >= steps:
            bucket -= steps
            pattern.append(1)
        else:
            pattern.append(0)
    return pattern

def apply_arpeggio(notes: List[int], pattern_type: str = "up", length: float = 4.0, steps: int = 16, octaves: int = 1, rate: float = 0.25) -> List[Dict[str, Any]]:
    """
    Converts a block chord (list of notes) into an arpeggio pattern.
    
    Args:
        notes: List of MIDI note numbers
        pattern_type: "up", "down", "up_down", "random", "converge", "diverge", "thumb_up", "pinky_up"
        length: Total duration in beats (e.g., 4.0 for a whole bar)
        steps: Number of steps to generate (overrides length if used for loop count, but we use length/rate for total steps)
        octaves: Number of octaves to span (1 = original only, 2 = original + octave up)
        rate: Duration of each step in beats (e.g., 0.25 for 16th notes)
    """
    events = []
    if not notes:
        return events
        
    num_original_notes = len(notes)
    
    # Expand notes across octaves
    expanded_notes = []
    for oct_idx in range(octaves):
        for note in notes:
            expanded_notes.append(note + (oct_idx * 12))
            
    # Sort expanded notes for consistent patterns
    expanded_notes.sort()
    num_notes = len(expanded_notes)
    
    # Calculate total steps based on length and rate
    total_steps = int(length / rate)
    
    current_step = 0
    
    while current_step < total_steps:
        note_idx = 0
        velocity = 90 + random.randint(-10, 10)
        
        # Calculate index based on pattern type
        if pattern_type == "up":
            note_idx = current_step % num_notes
            
        elif pattern_type == "down":
            note_idx = (num_notes - 1) - (current_step % num_notes)
            
        elif pattern_type == "up_down":
            cycle_len = (num_notes * 2) - 2
            if cycle_len < 1: cycle_len = 1 # Safety for single note
            cycle = current_step % cycle_len
            if cycle < num_notes:
                note_idx = cycle
            else:
                note_idx = (num_notes - 1) - (cycle - (num_notes - 1))
                
        elif pattern_type == "random":
            note_idx = random.randint(0, num_notes - 1)
            
        elif pattern_type == "converge":
            # 0, N-1, 1, N-2, 2, N-3...
            cycle = current_step % num_notes
            if cycle % 2 == 0:
                note_idx = cycle // 2
            else:
                note_idx = (num_notes - 1) - (cycle // 2)
                
        elif pattern_type == "diverge":
            # Middle out: Mid, Mid+1, Mid-1...
            mid = num_notes // 2
            cycle = current_step % num_notes
            if cycle == 0:
                note_idx = mid
            elif cycle % 2 != 0:
                note_idx = mid + (cycle // 2) + 1
            else:
                note_idx = mid - (cycle // 2)
            # Bounds check
            note_idx = max(0, min(note_idx, num_notes - 1))
            
        elif pattern_type == "thumb_up":
            # Lowest note, then random high notes
            cycle = current_step % 4
            if cycle == 0:
                note_idx = 0 # Root
                velocity += 15 # Accent
            else:
                note_idx = random.randint(1, num_notes - 1)
                
        elif pattern_type == "pinky_up":
             # Highest note, then random low notes
            cycle = current_step % 4
            if cycle == 0:
                note_idx = num_notes - 1 # Top
                velocity += 15 # Accent
            else:
                note_idx = random.randint(0, num_notes - 2)
        
        # Safety check
        if note_idx >= num_notes: note_idx = 0
        
        note = expanded_notes[note_idx]
        
        # Add event
        events.append({
            "note": note,
            "time": current_step * rate,
            "duration": rate * 0.9, # Legato-ish
            "velocity": velocity
        })
        
        current_step += 1
        
    return events

def apply_rhythm(notes: List[int], rhythm_type: str = "basic", length: float = 4.0, strum_speed: float = 0.0) -> List[Dict[str, Any]]:
    """
    Applies a rhythmic pattern to the full chord.
    
    Args:
        notes: List of MIDI notes
        rhythm_type: Name of the rhythm pattern
        length: Duration in beats
        strum_speed: Delay in seconds between notes in a chord (0.02 is standard strum)
    """
    events = []
    
    # Define rhythm patterns (start_time, duration, velocity_scale)
    # 1.0 = Quarter Note, 0.5 = Eighth Note, 0.25 = Sixteenth Note
    patterns = {
        "basic": [(0.0, 4.0, 1.0)], # Whole note
        
        # --- Essential Genres ---
        "charleston": [(0.0, 1.5, 1.0), (1.5, 2.5, 0.8)], # Dotted quarter, then rest/tied
        "reggaeton": [(0.0, 0.75, 1.0), (0.75, 0.25, 0.6), (1.0, 1.0, 0.8), (2.0, 0.75, 1.0), (2.75, 0.25, 0.6), (3.0, 1.0, 0.8)],
        "syncopated": [(0.0, 0.75, 1.0), (0.75, 0.75, 0.9), (1.5, 0.5, 0.8), (2.5, 0.5, 1.0), (3.5, 0.5, 0.7)],
        "waltz": [(0.0, 1.0, 1.0), (1.0, 1.0, 0.6), (2.0, 1.0, 0.6), (3.0, 1.0, 0.8)], # Extended to 4/4
        
        # --- Modern / Urban ---
        "drill_stabs": [(0.0, 0.25, 1.0), (0.75, 0.25, 0.9), (1.5, 0.25, 1.0), (2.5, 0.25, 0.9), (3.25, 0.25, 1.0), (3.75, 0.25, 0.8)], # Sharp staccato stabs
        "drill_sustained": [(0.0, 4.0, 0.9)], # Long dark pad
        "drill_counter": [(0.5, 0.25, 0.8), (1.25, 0.25, 0.9), (2.0, 0.25, 0.8), (3.5, 0.5, 0.9)], # Off-beat accents
        "trap_bounce": [(0.0, 1.5, 1.0), (1.5, 1.5, 0.9), (3.0, 1.0, 0.8)], # Classic Tresillo-ish
        "neo_soul": [(0.0, 1.25, 1.0), (1.25, 0.25, 0.7), (1.5, 1.0, 0.9), (2.75, 1.25, 0.8)], # Laid back, slightly behind
        "rnb_strum": [(0.0, 2.0, 1.0), (2.0, 1.0, 0.9), (3.0, 1.0, 0.8)], # Smooth changes
        "lofi_chop": [(0.0, 1.0, 0.9), (1.5, 1.0, 0.8), (2.5, 0.5, 0.7), (3.0, 1.0, 0.8)], # MPC style chops
        
        # --- Electronic ---
        "house_stab": [(0.0, 0.5, 1.0), (0.5, 0.5, 0.0), (1.0, 0.5, 1.0), (1.5, 0.5, 0.0), (2.0, 0.5, 1.0), (2.5, 0.5, 0.0), (3.0, 0.5, 1.0), (3.5, 0.5, 0.0)], # Offbeat stabs
        "house_piano": [(0.0, 0.75, 1.0), (0.75, 0.75, 0.9), (1.5, 0.5, 1.0), (2.0, 1.0, 0.9), (3.0, 1.0, 1.0)], # Classic M1 piano rhythm
        "techno_drive": [(0.0, 0.25, 1.0), (0.5, 0.25, 0.9), (1.0, 0.25, 1.0), (1.5, 0.25, 0.9), (2.0, 0.25, 1.0), (2.5, 0.25, 0.9), (3.0, 0.25, 1.0), (3.5, 0.25, 0.9)], # Driving 16ths
        "techno_rumble": [(0.0, 0.25, 1.0), (0.75, 0.25, 0.7), (1.5, 0.25, 0.9), (2.25, 0.25, 0.7), (3.0, 0.25, 0.9), (3.75, 0.25, 0.7)], # Spacey
        "future_bass_wub": [(0.0, 0.75, 1.0), (0.75, 0.75, 0.9), (1.5, 0.5, 0.8), (2.0, 0.75, 1.0), (2.75, 0.75, 0.9), (3.5, 0.5, 0.8)], # Super Saw Rhythm
        "future_bass_saw": [(0.0, 1.5, 1.0), (1.5, 0.5, 0.9), (2.0, 1.0, 1.0), (3.0, 0.5, 0.8), (3.5, 0.5, 0.9)], # Big chords
        "future_bass_16th": [(0.0, 0.25, 1.0), (0.25, 0.25, 0.8), (0.5, 0.25, 1.0), (0.75, 0.25, 0.8), (1.0, 0.5, 1.0), (1.5, 0.5, 0.0), (2.0, 0.25, 1.0), (2.25, 0.25, 0.8), (2.5, 0.25, 1.0), (2.75, 0.25, 0.8), (3.0, 0.5, 1.0), (3.5, 0.5, 0.0)], # Fast flutter
        "synthwave_pulse": [(0.0, 0.5, 1.0), (0.5, 0.5, 0.8), (1.0, 0.5, 1.0), (1.5, 0.5, 0.8), (2.0, 0.5, 1.0), (2.5, 0.5, 0.8), (3.0, 0.5, 1.0), (3.5, 0.5, 0.8)], # Steady 8ths
        "synthwave_arps": [(0.0, 0.25, 1.0), (0.5, 0.25, 0.9), (1.0, 0.25, 1.0), (1.5, 0.25, 0.9), (2.0, 0.25, 1.0), (2.5, 0.25, 0.9), (3.0, 0.25, 1.0), (3.5, 0.25, 0.9)], # Short arp base
        
        # --- Acoustic / Pop ---
        "pop_strum": [(0.0, 1.0, 1.0), (1.0, 1.0, 0.9), (2.0, 1.0, 1.0), (3.0, 1.0, 0.9)], # Basic quarter notes
        "pop_arpeggio": [(0.0, 0.5, 1.0), (0.5, 0.5, 0.9), (1.0, 0.5, 1.0), (1.5, 0.5, 0.9), (2.0, 0.5, 1.0), (2.5, 0.5, 0.9), (3.0, 0.5, 1.0), (3.5, 0.5, 0.9)], # Simple broken chords
        "jazz_swing": [(0.0, 1.0, 1.0), (1.0, 0.66, 0.8), (1.66, 0.33, 0.6), (2.0, 1.0, 1.0), (3.0, 0.66, 0.8), (3.66, 0.33, 0.6)], # Swing feel
        "gospel_sway": [(0.0, 1.5, 1.0), (1.5, 1.5, 0.9), (3.0, 0.5, 0.8), (3.5, 0.5, 0.9)], # 6/8 feel sway
        "cinematic_swell": [(0.0, 4.0, 0.6)], # Very soft, long pad
        
        # --- New Complex Patterns ---
        "afrobeat": [(0.0, 0.75, 1.0), (0.75, 0.25, 0.7), (1.0, 0.5, 0.9), (1.5, 0.75, 0.8), (2.25, 0.75, 1.0), (3.0, 0.5, 0.9), (3.5, 0.5, 0.7)],
        "reggaeton_bounce": [(0.0, 0.75, 1.0), (0.75, 0.25, 0.6), (1.0, 0.5, 0.9), (1.5, 0.5, 0.8), (2.0, 0.75, 1.0), (2.75, 0.25, 0.6), (3.0, 0.5, 0.9), (3.5, 0.5, 0.8)],
        "dnb_pad": [(0.0, 2.5, 0.9), (2.5, 1.5, 0.8)], # Atmospheric pad
        "dnb_stab": [(0.0, 0.5, 1.0), (1.5, 0.5, 0.9), (2.5, 0.5, 1.0), (3.5, 0.5, 0.9)], # Liquid piano stabs
        "dubstep_wub": [(0.0, 1.0, 1.0), (1.0, 0.5, 0.8), (1.5, 0.5, 0.9), (2.0, 2.0, 1.0)], # Half-time feel
        "euro_trance": [(0.0, 0.75, 1.0), (0.75, 0.75, 0.0), (1.5, 0.75, 1.0), (2.25, 0.75, 0.0), (3.0, 0.75, 1.0), (3.75, 0.25, 0.0)], # Gate effect
        "trance_gate": [(0.0, 0.25, 1.0), (0.25, 0.25, 0.0), (0.5, 0.25, 1.0), (0.75, 0.25, 0.0), (1.0, 0.25, 1.0), (1.25, 0.25, 0.0), (1.5, 0.25, 1.0), (1.75, 0.25, 0.0), (2.0, 0.25, 1.0), (2.25, 0.25, 0.0), (2.5, 0.25, 1.0), (2.75, 0.25, 0.0), (3.0, 0.25, 1.0), (3.25, 0.25, 0.0), (3.5, 0.25, 1.0), (3.75, 0.25, 0.0)], # Fast gate
        
        # --- Specific Artists ---
        "walker_piano": [(0.0, 0.5, 1.3), (0.5, 0.5, 0.8), (1.0, 0.5, 1.3), (1.5, 0.5, 0.8), (2.0, 0.5, 1.3), (2.5, 0.5, 0.8), (3.0, 0.5, 1.3), (3.5, 0.5, 0.8)], # Heavy pulse
        "walker_arp": [(0.0, 0.5, 1.2), (0.5, 0.25, 0.9), (0.75, 0.25, 0.9), (1.0, 0.5, 1.1), (1.5, 0.25, 0.9), (1.75, 0.25, 0.9), (2.0, 0.5, 1.2), (2.5, 0.25, 0.9), (2.75, 0.25, 0.9), (3.0, 0.5, 1.1), (3.5, 0.25, 0.9), (3.75, 0.25, 0.9)], # Dotted feel
    }
    
    selected_pattern = patterns.get(rhythm_type, patterns["basic"])
    
    # Walker Arpeggiator Logic (Override standard block chords)
    if rhythm_type == "walker_arp":
        # Create a custom arpeggio pattern instead of block chords
        # Pattern: Root (strong), 5th+Octave (weak), 5th (weak), Root...
        events = []
        if not notes: return []
        
        root = notes[0]
        # Find a suitable fifth (avoid close clusters if possible)
        fifth = root + 7
        if len(notes) > 2:
            fifth = notes[2]
        elif len(notes) > 1:
            fifth = notes[1]
            
        octave = root + 12
        
        # Simple broken chord pattern: 
        # Beat 1: Root
        # Beat 1.5: 5th
        # Beat 2: Octave
        # Beat 2.5: 5th
        
        arp_sequence = [root, fifth, octave, fifth]
        step_size = 0.5
        
        current_time = 0.0
        step_idx = 0
        
        while current_time < length:
            n = arp_sequence[step_idx % len(arp_sequence)]
            
            # Stronger velocity for downbeats
            is_strong = (current_time % 2.0 == 0)
            vel = 100 if is_strong else 85
            
            events.append({
                "note": n,
                "time": current_time + random.uniform(-0.01, 0.01),
                "duration": step_size * 0.95,
                "velocity": vel + random.randint(-5, 5)
            })
            
            current_time += step_size
            step_idx += 1
            
        return events

    # Check if we should use Euclidean rhythms for "random" or unknown types
    if rhythm_type == "euclidean_random":
        pulses = random.randint(3, 9)
        steps = 16
        euc_pattern = euclidean_pattern(steps, pulses)
        selected_pattern = []
        step_len = 0.25
        for i, hit in enumerate(euc_pattern):
            if hit:
                selected_pattern.append((i * step_len, step_len, 1.0 if i % 4 == 0 else 0.8))
    
    for start, dur, vel_scale in selected_pattern:
        # If the pattern exceeds the chord length, stop
        if start >= length:
            break
            
        real_dur = min(dur, length - start)
        
        # Determine Strum Offset
        current_strum_speed = strum_speed
        if current_strum_speed == 0.0:
            if "neo_soul" in rhythm_type or "lofi" in rhythm_type:
                 current_strum_speed = random.uniform(0.01, 0.03) # 10-30ms strum
            elif "pop_strum" in rhythm_type:
                 current_strum_speed = 0.02
        
        for i, note in enumerate(notes):
            # Apply slight swing/humanization to time
            humanize = random.uniform(-0.02, 0.02)
            
            # Apply strum (lowest note first)
            current_strum = i * current_strum_speed
            
            # Velocity Humanization
            # Accent first beat of bar
            beat_accent = 0
            if start % 4.0 == 0: beat_accent = 10
            elif start % 1.0 == 0: beat_accent = 5
            
            # Higher notes slightly softer naturally? Or louder? Let's keep random.
            pitch_variance = 0 # (note % 12) / 2 # Slight variance by pitch class?
            
            final_velocity = int(80 * vel_scale) + beat_accent + random.randint(-5, 5)
            final_velocity = max(1, min(127, final_velocity))
            
            events.append({
                "note": note,
                "time": start + humanize + current_strum,
                "duration": real_dur * 0.95,
                "velocity": final_velocity
            })
            
    return events
