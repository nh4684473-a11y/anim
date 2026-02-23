
import random
from typing import List, Dict, Any
from .scales import get_triad_notes, get_note_index, get_scale_intervals
from .patterns import apply_arpeggio, apply_rhythm
from .melody import generate_melody

def smooth_voice_leading(current_notes: List[int], prev_notes: List[int]) -> List[int]:
    """
    Adjusts the inversion of current_notes to be closest to prev_notes (voice leading).
    Minimizes total movement distance.
    """
    if not prev_notes or not current_notes:
        return current_notes
        
    # Keep bass fixed? Usually for pop/EDM we might want to keep the root in bass
    # But for smooth pads, we might want to invert everything.
    # Let's assume we keep the bass note as the root of the chord for now, 
    # but invert the upper structure.
    
    bass = current_notes[0]
    upper = current_notes[1:]
    
    if not upper:
        return current_notes

    prev_upper = prev_notes[1:] if len(prev_notes) > 1 else prev_notes
    if not prev_upper:
        return current_notes
        
    prev_avg = sum(prev_upper) / len(prev_upper)
    
    # Generate inversions of the upper structure
    # An inversion is just rotating the notes and adjusting octaves
    # But here we just want to find the set of octaves for these pitch classes 
    # that minimizes distance to prev_avg.
    
    best_upper = []
    min_dist = float('inf')
    
    # Try different octave shifts for the whole chord first
    # Then fine tune individual notes?
    # No, let's just place each note in the octave closest to prev_avg
    
    candidate_upper = []
    for note in upper:
        # Normalize to 0-11
        pc = note % 12
        
        # Find octave of prev_avg
        target_octave = int(prev_avg // 12)
        
        # Candidates: target_octave - 1, target, target + 1
        c1 = (target_octave - 1) * 12 + pc
        c2 = target_octave * 12 + pc
        c3 = (target_octave + 1) * 12 + pc
        
        # Pick closest to prev_avg
        best_note = min([c1, c2, c3], key=lambda n: abs(n - prev_avg))
        candidate_upper.append(best_note)
        
    candidate_upper.sort()
    
    # Check if this configuration is valid (not too spread, not overlapping bass too much)
    # If bass is fixed, we ensure upper > bass
    if candidate_upper[0] <= bass:
        candidate_upper = [n + 12 for n in candidate_upper]
        
    return [bass] + candidate_upper

def get_smart_extension(degree: int, mood_key: str) -> str:
    """
    Decides the best extension based on chord function and genre.
    """
    # 1. Jazz/Neo-Soul/Lo-Fi: Complex extensions
    if any(g in mood_key for g in ["jazz", "neo_soul", "lo_fi", "rnb"]):
        if degree == 5: return random.choice(["9", "13", "7b9", "7#9", "alt"]) # Dominant variations
        if degree == 2: return random.choice(["9", "11", "m9"]) # Supertonic
        if degree == 1: return random.choice(["maj9", "6/9", "maj7"]) # Tonic
        return random.choice(["7", "9", "11"])
        
    # 2. Future Bass / Kawaii: Lush 7ths/9ths
    if "future_bass" in mood_key:
        return random.choice(["maj9", "add9", "7"])
        
    # 3. Pop / House: Selective 7ths
    if "pop" in mood_key or "house" in mood_key:
        if degree == 5: return "7" # V7
        if degree == 2: return "m7" # ii7
        if degree == 6: return "m7" # vi7
        if degree == 1: return random.choice(["triad", "add9", "sus2"])
        return "triad"
        
    # 4. Drill / Trap / Dark: Tension
    if "drill" in mood_key or "trap" in mood_key:
        if degree == 5: return "m7" # Minor v for Phrygian feel
        return "triad"

    # 5. Walker / Epic: Emotional
    if "walker" in mood_key or "epic" in mood_key:
        if degree == 1: return random.choice(["add9", "sus2", "triad"])
        if degree == 6: return random.choice(["m7", "add9"]) # vi is minor
        if degree == 4: return "add9"
        return "triad"
        
    return "triad"

# --- Helper Functions ---
def get_extended_chord_notes(key: str, scale: str, degree: int, octave: int = 4, extension: str = "triad") -> List[int]:
    """
    Generates notes for a chord including extensions (7th, 9th, 11th, alterations).
    """
    root_val = get_note_index(key)
    intervals = get_scale_intervals(scale)
    
    # Create a long list of relative intervals spanning 3 octaves
    extended_intervals = intervals + [i + 12 for i in intervals] + [i + 24 for i in intervals] + [i + 36 for i in intervals]
    
    deg_idx = degree - 1
    indices = [deg_idx] # Root
    
    ext_clean = extension.lower()
    
    # 3rd or Suspension
    if "sus4" in ext_clean:
        indices.append(deg_idx + 3) # 4th
    elif "sus2" in ext_clean:
        indices.append(deg_idx + 1) # 2nd
    else:
        indices.append(deg_idx + 2) # 3rd
        
    # 5th (omit if specific voicings require, but usually present)
    indices.append(deg_idx + 4) # 5th
    
    # Extensions
    if "6" in ext_clean and "9" in ext_clean: # 6/9
        indices.append(deg_idx + 5) # 6th
        indices.append(deg_idx + 8) # 9th
    elif "6" in ext_clean:
        indices.append(deg_idx + 5) # 6th
    elif "add9" in ext_clean:
        indices.append(deg_idx + 8) # 9th (no 7th)
        
    elif "alt" in ext_clean:
        # Altered Dominant (7#9b13 is a common voicing)
        indices.append(deg_idx + 6) # 7th
        indices.append(deg_idx + 8) # 9th slot (will be sharpened)
        indices.append(deg_idx + 12) # 13th slot (will be flattened)
        # We handle alterations in post-processing
        
    elif "7" in ext_clean or "9" in ext_clean or "11" in ext_clean or "13" in ext_clean or "maj" in ext_clean:
        indices.append(deg_idx + 6) # 7th
        
        if "9" in ext_clean or "11" in ext_clean or "13" in ext_clean:
             indices.append(deg_idx + 8) # 9th
             
        if "11" in ext_clean or "13" in ext_clean:
             indices.append(deg_idx + 10) # 11th
             
        if "13" in ext_clean:
             indices.append(deg_idx + 12) # 13th
        
    # Calculate absolute MIDI notes
    base_midi = (octave + 1) * 12 + root_val
    notes = [base_midi + extended_intervals[i] for i in indices]
    
    # Alterations (Post-processing)
    # Handle b9 / #9 / alt / b13 if present
    
    # Helper to find index of degree
    def find_index(target_deg_offset):
        try:
            return indices.index(deg_idx + target_deg_offset)
        except ValueError:
            return None

    if "alt" in ext_clean:
        # #9
        idx9 = find_index(8)
        if idx9 is not None: notes[idx9] += 1
        # b13
        idx13 = find_index(12)
        if idx13 is not None: notes[idx13] -= 1
        # b5 or #5? Let's just do #9 b13 for now, very common jazz sound.
        
    if "b9" in ext_clean:
        idx = find_index(8)
        if idx is not None: notes[idx] -= 1
    elif "#9" in ext_clean:
        idx = find_index(8)
        if idx is not None: notes[idx] += 1
        
    return notes

def get_secondary_dominant(target_degree: int, key: str, scale: str, octave: int = 4) -> List[int]:
    """
    Returns the V7 of the target degree (Secondary Dominant).
    """
    # 1. Find the root of the target chord
    root_val = get_note_index(key)
    intervals = get_scale_intervals(scale)
    target_interval = intervals[target_degree - 1]
    target_root_midi = (octave + 1) * 12 + root_val + target_interval
    
    # 2. The dominant is a perfect 5th above the target (or perfect 4th below)
    # V of target = Target + 7 semitones
    dom_root_midi = target_root_midi + 7
    
    # 3. Build a Major 7 (Dominant 7) chord on this root: Root, Maj3, P5, min7
    # 0, 4, 7, 10 relative to dom_root
    dom_intervals = [0, 4, 7, 10]
    
    return [dom_root_midi + i for i in dom_intervals]

def get_passing_chord(from_degree: int, to_degree: int, key: str, scale: str, octave: int = 4) -> List[int]:
    """
    Returns a passing chord (usually diminished) between two degrees.
    """
    root_val = get_note_index(key)
    intervals = get_scale_intervals(scale)
    
    from_interval = intervals[from_degree - 1]
    to_interval = intervals[to_degree - 1]
    
    # Calculate midi of 'from' chord root
    from_root_midi = (octave + 1) * 12 + root_val + from_interval
    
    # If moving up a whole step (2 semitones), insert a chromatic passing chord
    # e.g., I -> ii (C -> D), insert C#dim7
    if (to_interval - from_interval) == 2 or (to_interval - from_interval) == -10: # Wrap around handling roughly
        # Diminished 7th on the half step: Root + 1
        pass_root_midi = from_root_midi + 1
        # Dim7 intervals: 0, 3, 6, 9
        dim_intervals = [0, 3, 6, 9]
        return [pass_root_midi + i for i in dim_intervals]
        
    return []

# --- Progression Templates ---
# Expanded with Industry Standard Progressions
PROGRESSIONS = {
    "dark_trap": [
        [1, 6, 1, 7],      # i - VI - i - VII (Classic)
        [1, 6, 3, 7],      # i - VI - III - VII (Metro Boomin style)
        [1, 4, 5, 1],      # i - iv - v - i
        [1, 2, 1, 7],      # i - ii - i - VII (Phrygian Tension)
        [1, 3, 6, 7],      # i - III - VI - VII (Epic/Cinematic)
        [1, 7, 6, 5],      # i - VII - VI - v (Andalusian Descent)
        [1, 6, 4, 5],      # i - VI - iv - v
        [1, 5, 1, 4]       # i - v - i - iv (Spooky/Hollow)
    ],
    "boom_bap": [
        [2, 5, 1, 6],      # ii - V - i - VI (Jazz Turnaround)
        [1, 4, 5, 1],      # i - iv - v - i
        [1, 3, 6, 2],      # i - III - VI - ii (Soulful)
        [4, 3, 2, 1],      # iv - III - ii - i (Descending Soul)
        [1, 6, 2, 5],      # i - VI - ii - V (The "Changes" progression)
        [2, 5, 1, 1],      # ii - V - i - i
        [1, 7, 6, 7]       # i - VII - VI - VII (90s East Coast)
    ],
    "emotional": [
        [6, 7, 1, 1],      # VI - VII - i - i (Anime/Emo)
        [1, 5, 6, 4],      # i - v - VI - iv (Pop-Punk/Emo Rap)
        [4, 1, 5, 6],      # IV - I - V - vi (Radio Hit)
        [6, 4, 1, 5],      # vi - IV - I - V (Sad but hopeful)
        [1, 6, 3, 7],      # i - VI - III - VII (Deep emotion)
        [4, 5, 3, 6],      # IV - V - iii - vi (J-Pop/Sentimental)
        [1, 4, 6, 5]       # i - iv - VI - v
    ],
    "uk_drill": [
        [1, 6, 3, 7],      # i - VI - III - VII (The Anthem)
        [1, 7, 6, 5],      # i - VII - VI - v (The Slide)
        [1, 2, 1, 2],      # i - ii - i - ii (Phrygian rubbing)
        [1, 6, 4, 5],      # i - VI - iv - v (Emotional Drill)
        [1, 3, 6, 5],      # i - III - VI - v
        [1, 6, 1, 7],      # i - VI - i - VII
        [1, 5, 6, 7],      # i - v - VI - VII
        [1, 4, 1, 5],      # i - iv - i - v
        [1, 2, 3, 1],      # i - ii - III - i (Dark & creepy)
        [1, 7, 1, 2],      # i - VII - i - ii (Tension)
        [6, 5, 1, 1],      # VI - v - i - i (Drop resolution)
        [1, 3, 2, 1],      # i - III - ii - i (Chromatic-ish)
        [1, 6, 5, 1],      # i - VI - v - i
        [1, 2, 7, 1]       # i - ii - VII - i
    ],
    "lo_fi": [
        [2, 5, 1, 6],      # ii7 - V7 - Imaj7 - vi7 (The Lofi Standard)
        [4, 5, 3, 6],      # IV - V - iii - vi (Royal Road)
        [1, 4, 1, 5],      # I - IV - I - V
        [6, 4, 1, 5],      # vi - IV - I - V
        [3, 6, 2, 5],      # iii - vi - ii - V
        [1, 2, 3, 4],      # I - ii - iii - IV (Climbing)
        [4, 3, 2, 1],      # IV - iii - ii - I
        [2, 5, 1, 4],      # ii - V - I - IV
        [1, 6, 2, 5],      # I - vi - ii - V (Classic Jazz)
        [4, 5, 1, 1],      # IV - V - I - I (Simple resolution)
        [2, 5, 3, 6],      # ii - V - iii - vi (Extended turnaround)
        [6, 2, 5, 1],      # vi - ii - V - I
        [1, 4, 5, 6],      # I - IV - V - vi
        [3, 4, 5, 1]       # iii - IV - V - I
    ],
    "rnb": [
        [4, 3, 2, 1],      # IV - iii - ii - I (Neo Soul Descent)
        [2, 5, 1, 6],      # ii9 - V13 - Imaj9 - vi7
        [6, 2, 5, 1],      # vi - ii - V - I
        [4, 5, 6, 1],      # IV - V - vi - I
        [1, 6, 2, 5],      # I - vi - ii - V
        [3, 6, 2, 5],      # iii - vi - ii - V
        [1, 4, 5, 4],      # I - IV - V - IV (Smooth)
        [6, 4, 1, 5],      # vi - IV - I - V
        [2, 3, 4, 5],      # ii - iii - IV - V (Climb)
        [1, 2, 3, 4],      # I - ii - iii - IV
        [6, 5, 4, 3],      # vi - V - IV - iii (Walk down)
        [2, 6, 4, 5],      # ii - vi - IV - V
        [1, 7, 6, 5]       # I - VII - vi - V
    ],
    "future_bass": [
        [4, 5, 3, 6],      # IV - V - iii - vi (Royal Road / Kawaii)
        [4, 5, 6, 1],      # IV - V - vi - I (Rising)
        [6, 4, 1, 5],      # vi - IV - I - V (Emotional)
        [1, 5, 6, 4],      # I - V - vi - IV (Anthem)
        [4, 1, 5, 6],      # IV - I - V - vi
        [2, 5, 1, 6],      # ii - V - I - vi
        [1, 6, 4, 5],      # I - vi - IV - V
        [6, 5, 4, 1],      # vi - V - IV - I
        [4, 1, 6, 5],      # IV - I - vi - V
        [1, 3, 6, 4],      # I - iii - vi - IV
        [6, 3, 4, 1],      # vi - iii - IV - I
        [4, 6, 1, 5],      # IV - vi - I - V
        [2, 6, 5, 1]       # ii - vi - V - I
    ],
    "jazz": [
        [2, 5, 1, 6],      # ii - V - I - vi (Standard Turnaround)
        [3, 6, 2, 5],      # iii - vi - ii - V (Circle of Fifths)
        [1, 6, 2, 5],      # I - vi - ii - V (Rhythm Changes)
        [2, 5, 3, 6],      # ii - V - iii - vi
        [1, 4, 1, 5],      # I - IV - I - V
        [2, 5, 1, 1],      # ii - V - I - I
        [6, 2, 5, 1],      # vi - ii - V - I
        [1, 2, 3, 4],      # I - ii - iii - IV (Coltrane-ish start)
        [1, 3, 6, 2],      # I - iii - vi - ii
        [4, 7, 3, 6],      # IV - VII - iii - vi (Back cycling)
        [2, 5, 6, 2],      # ii - V - vi - ii
        [1, 4, 3, 6]       # I - IV - iii - vi
    ],
    "cinematic": [
        [1, 6, 4, 5],      # I - vi - IV - V (Heroic)
        [1, 5, 6, 3],      # I - V - vi - iii (Pachelbel-ish)
        [6, 4, 1, 5],      # vi - IV - I - V (Hans Zimmer-ish)
        [1, 3, 4, 5],      # I - iii - IV - V (Rising)
        [1, 2, 1, 7],      # i - ii - i - VII (Mystery)
        [1, 6, 3, 7],      # i - VI - III - VII (Epic)
        [1, 5, 4, 1],      # I - V - IV - I (Triumphant)
        [6, 3, 4, 1],      # vi - iii - IV - I (Emotional)
        [1, 2, 4, 5],      # I - ii - IV - V (Wonder)
        [4, 1, 6, 5],      # IV - I - vi - V (Swell)
        [1, 7, 6, 5],      # I - VII - vi - V (Descent)
        [1, 4, 2, 5]       # I - IV - ii - V
    ],
    "house": [
        [1, 3, 6, 4],      # I - iii - vi - IV (Uplifting)
        [6, 4, 1, 5],      # vi - IV - I - V (Anthem)
        [2, 5, 1, 6],      # ii - V - I - vi (Deep House)
        [1, 7, 6, 7],      # i - VII - VI - VII (Classic)
        [1, 4, 1, 5],      # i - iv - i - v
        [1, 3, 4, 5],      # I - iii - IV - V
        [1, 6, 4, 5],      # I - vi - IV - V (Piano House)
        [4, 1, 5, 6],      # IV - I - V - vi
        [6, 5, 4, 1],      # vi - V - IV - I
        [2, 6, 1, 5],      # ii - vi - I - V
        [1, 5, 2, 6],      # I - V - ii - vi
        [4, 5, 3, 6]       # IV - V - iii - vi
    ],
    "pop": [
        [1, 5, 6, 4],      # I - V - vi - IV (The "Axis of Awesome")
        [6, 4, 1, 5],      # vi - IV - I - V (Sensitive Pop)
        [1, 6, 4, 5],      # I - vi - IV - V (50s Progression)
        [1, 4, 5, 4],      # I - IV - V - IV
        [2, 5, 1, 6],      # ii - V - I - vi
        [4, 1, 5, 6],      # IV - I - V - vi (Modern Hit)
        [1, 5, 2, 4],      # I - V - ii - IV
        [6, 5, 4, 5],      # vi - V - IV - V
        [1, 3, 4, 1],      # I - iii - IV - I
        [1, 2, 5, 1],      # I - ii - V - I
        [4, 5, 1, 6],      # IV - V - I - vi
        [6, 2, 4, 5]       # vi - ii - IV - V
    ],
    "future_bass": [
        [4, 5, 3, 6],      # IV - V - iii - vi (Royal Road / Kawaii)
        [4, 5, 6, 1],      # IV - V - vi - I (Rising)
        [6, 4, 1, 5],      # vi - IV - I - V (Emotional)
        [1, 5, 6, 4],      # I - V - vi - IV (Anthem)
        [4, 1, 5, 6],      # IV - I - V - vi
        [2, 5, 1, 6]       # ii - V - I - vi
    ],
    "neo_soul": [
        [2, 5, 1, 6],      # ii9 - V13 - Imaj9 - vi7 (Classic Jazz/Soul)
        [4, 3, 2, 1],      # IVmaj7 - iii7 - ii7 - Imaj7 (Descending)
        [6, 2, 5, 1],      # vi7 - ii9 - V13 - Imaj9
        [1, 4, 3, 6],      # Imaj9 - IVmaj7 - iii7 - vi7
        [3, 6, 2, 5],      # iii7 - vi7 - ii9 - V13
        [2, 5, 3, 6]       # ii9 - V13 - iii7 - vi7
    ],
    "reggaeton": [
        [6, 4, 5, 5],      # vi - IV - V - V (Gasolina style)
        [1, 6, 4, 5],      # i - VI - iv - v (Minor pop)
        [1, 7, 6, 5],      # i - VII - VI - v (Andalusian)
        [2, 3, 4, 5],      # ii - iii - iv - v
        [6, 5, 6, 5],      # vi - V - vi - V (Simple loop)
        [1, 4, 5, 1]       # i - iv - v - i
    ],
    "techno": [
        [1, 1, 1, 1],      # i - i - i - i (Drone/Static)
        [1, 7, 1, 7],      # i - VII - i - VII (Minimal movement)
        [1, 2, 1, 6],      # i - ii - i - VI (Dark)
        [1, 5, 1, 4],      # i - v - i - iv
        [1, 3, 1, 6]       # i - III - i - VI
    ],
    "gospel": [
        [1, 4, 1, 5],      # I - IV - I - V (Praise)
        [1, 6, 2, 5],      # I - vi - ii - V (Turnaround)
        [4, 5, 6, 1],      # IV - V - vi - I
        [6, 3, 4, 1],      # vi - iii - IV - I
        [2, 5, 1, 4],      # ii - V - I - IV
        [1, 3, 4, 2]       # I - iii - IV - ii
    ],
    "synthwave": [
        [1, 6, 3, 7],      # i - VI - III - VII (Epic)
        [6, 4, 1, 5],      # vi - IV - I - V (Driving)
        [1, 7, 6, 5],      # i - VII - VI - v (Sunset)
        [4, 5, 3, 6],      # IV - V - iii - vi (Nostalgic)
        [1, 3, 4, 5],      # i - III - iv - v
        [1, 5, 6, 4]       # i - v - VI - iv
    ],
    "dubstep": [
        [1, 6, 4, 5],      # i - VI - iv - v
        [1, 3, 6, 7],      # i - III - VI - VII
        [1, 7, 6, 5],      # i - VII - VI - v (Descending)
        [1, 1, 6, 6],      # i - i - VI - VI (Sustain)
        [1, 4, 1, 5]       # i - iv - i - v
    ],
    "trance": [
        [1, 6, 3, 7],      # i - VI - III - VII (Epic Trance)
        [6, 4, 1, 5],      # vi - IV - I - V (Uplifting)
        [1, 5, 6, 4],      # i - v - VI - iv
        [1, 7, 6, 7],      # i - VII - VI - VII
        [4, 1, 5, 6]       # IV - I - V - vi
    ],
    "dnb": [
        [1, 6, 4, 7],      # i - VI - iv - VII (Liquid)
        [1, 7, 6, 5],      # i - VII - VI - v
        [1, 3, 4, 6],      # i - III - iv - VI
        [1, 4, 1, 5],      # i - iv - i - v
        [2, 5, 1, 6]       # ii - V - I - vi (Jazzy DnB)
    ],
    "progressive_house": [
        [6, 4, 1, 5],      # vi - IV - I - V (Deadmau5 style)
        [1, 5, 6, 4],      # I - V - vi - IV
        [4, 1, 5, 6],      # IV - I - V - vi
        [1, 3, 6, 4],      # I - iii - vi - IV
        [1, 6, 3, 7]       # i - VI - III - VII
    ],
    "big_room": [
        [1, 1, 1, 1],      # i - i - i - i (Drop focused)
        [1, 6, 1, 6],      # i - VI - i - VI
        [1, 7, 6, 5],      # i - VII - VI - v
        [1, 4, 5, 1]       # i - iv - v - i
    ],
    "electro_house": [
        [1, 4, 1, 5],      # i - iv - i - v
        [1, 6, 7, 1],      # i - VI - VII - i
        [1, 3, 4, 6],      # i - III - iv - VI
        [1, 7, 6, 5]       # i - VII - VI - v
    ],
    "tropical_house": [
        [1, 5, 6, 4],      # I - V - vi - IV (Kygo style)
        [4, 1, 5, 6],      # IV - I - V - vi
        [6, 4, 1, 5],      # vi - IV - I - V
        [1, 4, 5, 1],      # I - IV - V - I
        [2, 5, 1, 6]       # ii - V - I - vi
    ],
    "hardstyle": [
        [1, 6, 3, 7],      # i - VI - III - VII (Euphoric)
        [6, 4, 1, 5],      # vi - IV - I - V
        [1, 7, 6, 5],      # i - VII - VI - v
        [1, 3, 6, 4]       # i - III - VI - iv
    ],
    "melodic_dubstep": [
        [6, 4, 1, 5],      # vi - IV - I - V (Seven Lions style)
        [4, 5, 6, 1],      # IV - V - vi - I
        [1, 5, 6, 4],      # I - V - vi - IV
        [4, 1, 5, 6],      # IV - I - V - vi
        [2, 5, 1, 6]       # ii - V - I - vi
    ]
}

def generate_procedural_progression(scale_type: str = "minor", mood: str = "dark_trap", length: int = 4) -> List[int]:
    """
    Generates a unique, valid chord progression based on transition probabilities.
    This allows for infinite variations beyond static templates.
    """
    # Transition Rules (Simplified Markov Chain)
    # Key: Current Degree -> Value: List of likely Next Degrees
    transitions = {}
    
    if scale_type == "major":
        transitions = {
            1: [4, 5, 6, 2, 3], # I goes to almost anything
            2: [5, 6],          # ii -> V (classic), vi
            3: [6, 4],          # iii -> vi, IV
            4: [1, 5, 2],       # IV -> I, V, ii
            5: [1, 6, 4],       # V -> I (resolve), vi (deceptive), IV
            6: [2, 4, 5],       # vi -> ii, IV, V
            7: [1, 6]           # vii -> I, vi
        }
    else: # minor
        transitions = {
            1: [6, 7, 4, 5, 3], # i -> VI, VII, iv, v, III
            2: [5, 7],          # ii -> v, VII
            3: [6, 7],          # III -> VI, VII
            4: [5, 1, 6],       # iv -> v, i, VI
            5: [1, 6],          # v -> i, VI
            6: [7, 5, 4, 1],    # VI -> VII, v, iv, i
            7: [1, 6]           # VII -> i (natural minor), VI
        }

    # Genre-specific overrides/weights could be added here
    if "trap" in mood:
        transitions[1] = [6, 4, 5] # Dark Trap bias
    elif "jazz" in mood or "rnb" in mood:
        transitions[2] = [5] # Strong ii-V
        transitions[5] = [1] # Strong V-I
        
    progression = [1] # Start on Tonic
    current = 1
    
    for _ in range(length - 1):
        options = transitions.get(current, [1])
        # Filter options to avoid immediate repetition if possible
        valid_options = [o for o in options if o != current]
        if not valid_options: valid_options = options
        
        next_chord = random.choice(valid_options)
        progression.append(next_chord)
        current = next_chord
        
    # Ensure reasonable loop (last chord shouldn't be too resolved if we want a loop, 
    # or should lead back to 1)
    # For now, random walk is fine for variety.
    
    return progression

def generate_progression(key: str, scale: str, mood: str, length: int = 4, complexity: float = 0.5, pattern_override: List[int] = None) -> Dict[str, Any]:
    """
    Generates a chord progression based on key, scale, and mood.
    """
    
    # Defaults for Random/None
    if not scale or scale == "Random":
        scale = random.choice(["major", "minor", "dorian", "phrygian"])
        
    if not mood or mood == "Random":
        mood = random.choice(list(PROGRESSIONS.keys()))

    # Fallback for pentatonic scales (which don't support 7-degree chord logic)
    if "pentatonic" in scale:
        scale = "minor"

    # 1. Select a progression pattern
    mood_key = mood.lower().replace(" ", "_").replace("-", "_")

    # Handle Random Key
    if not key or key == "Random":
        if "drill" in mood_key:
            # Weighted probability for Drill: Fm, D#m, Cm favored
            drill_keys = ["F", "D#", "C", "A"]
            weights = [0.4, 0.3, 0.2, 0.1]
            key = random.choices(drill_keys, weights=weights, k=1)[0]
        else:
            key = random.choice(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])
    
    # Fallback map for similar genres
    if mood_key not in PROGRESSIONS:
        if "drill" in mood_key: mood_key = "uk_drill"
        elif "faded" in mood_key or "walker" in mood_key: mood_key = "walker"
        elif "lofi" in mood_key or "chill" in mood_key: mood_key = "lo_fi"
        elif "r&b" in mood_key or "soul" in mood_key: mood_key = "rnb"
        elif "jazz" in mood_key: mood_key = "jazz"
        elif "cinematic" in mood_key: mood_key = "cinematic"
        elif "house" in mood_key: mood_key = "house"
        elif "pop" in mood_key: mood_key = "pop"
        elif "future" in mood_key or "bass" in mood_key or "kawaii" in mood_key: mood_key = "future_bass"
        elif "neo" in mood_key or "soul" in mood_key: mood_key = "neo_soul"
        elif "reggaeton" in mood_key: mood_key = "reggaeton"
        elif "techno" in mood_key or "rave" in mood_key: mood_key = "techno"
        elif "gospel" in mood_key or "church" in mood_key: mood_key = "gospel"
        elif "synth" in mood_key or "wave" in mood_key or "retro" in mood_key: mood_key = "synthwave"
        elif "dubstep" in mood_key: mood_key = "dubstep"
        elif "trance" in mood_key: mood_key = "trance"
        elif "drum" in mood_key or "dnb" in mood_key: mood_key = "dnb"
        elif "progressive" in mood_key: mood_key = "progressive_house"
        elif "big" in mood_key and "room" in mood_key: mood_key = "big_room"
        elif "electro" in mood_key: mood_key = "electro_house"
        elif "tropical" in mood_key: mood_key = "tropical_house"
        elif "hardstyle" in mood_key: mood_key = "hardstyle"
        elif "melodic" in mood_key and "dubstep" in mood_key: mood_key = "melodic_dubstep"
        elif scale == "phrygian": mood_key = "dark_trap"
        elif scale == "dorian": mood_key = "boom_bap"
        else: mood_key = "dark_trap" # Default
            
    if not pattern_override:
        # Default mood inference
        pass

    if pattern_override:
        # Don't truncate pattern_override if it's the same length
        full_pattern = pattern_override
        
        # Only pad if shorter
        if len(full_pattern) < length:
            full_pattern = (full_pattern * (length // len(full_pattern) + 1))[:length]
    else:
        templates = PROGRESSIONS.get(mood_key, PROGRESSIONS["dark_trap"])
        pattern = random.choice(templates)
        
        # Loop pattern if length > 4
        full_pattern = (pattern * (length // 4 + 1))[:length]
    
    chords_output = []
    
    for i, degree in enumerate(full_pattern):
        # Default duration
        duration = 4.0
        
        # --- Advanced Harmonic Insertion (Passing Chords / Secondary Dominants) ---
        # Only if complexity is high enough
        inserted_chord = None
        
        if i > 0 and complexity > 0.65:
            prev_chord = chords_output[-1]
            
            # 1. Secondary Dominant (V/X) OR Tritone Substitution (bII/X)
            # Insert V7 (or bII7) of current chord before current chord
            # Steals 2 beats from previous chord
            if prev_chord["duration"] >= 3.0 and random.random() < (complexity * 0.4):
                
                is_tritone_sub = False
                # Jazz/Neo Soul/Lo-Fi often use Tritone Subs
                if any(m in mood_key for m in ["jazz", "neo_soul", "lo_fi"]) and random.random() < 0.3:
                    is_tritone_sub = True

                if is_tritone_sub:
                    # bII7 of target (Tritone Sub)
                    # Target root + 1 semitone
                    root_val = get_note_index(key)
                    intervals = get_scale_intervals(scale)
                    target_interval = intervals[degree - 1]
                    # Estimate target MIDI (Octave 4)
                    target_root_midi = (4 + 1) * 12 + root_val + target_interval
                    
                    sub_root_midi = target_root_midi + 1
                    dom_intervals = [0, 4, 7, 10] # Dom7
                    sec_dom_notes = [sub_root_midi + k for k in dom_intervals]
                    ins_degree_name = f"bII/{degree}"
                else:
                    # V of target (Secondary Dominant)
                    sec_dom_notes = get_secondary_dominant(degree, key, scale, octave=4)
                    ins_degree_name = f"V/{degree}"
                
                # Update previous chord duration
                prev_chord["duration"] -= 2.0
                
                # Create Inserted Chord
                inserted_chord = {
                    "degree": ins_degree_name,
                    "notes": sec_dom_notes,
                    "duration": 2.0,
                    "velocity": 75
                }
            
            # 2. Passing Diminished Chord
            # If moving by whole step (e.g. 1 -> 2), insert #1dim7
            # Ensure degrees are integers (skip if previous was a secondary dominant)
            elif isinstance(prev_chord["degree"], int) and prev_chord["duration"] >= 3.0 and random.random() < (complexity * 0.4):
                pass_notes = get_passing_chord(prev_chord["degree"], degree, key, scale, octave=4)
                if pass_notes:
                    prev_chord["duration"] -= 1.0 # Passing chords are quick
                    
                    inserted_chord = {
                        "degree": "dim7",
                        "notes": pass_notes,
                        "duration": 1.0,
                        "velocity": 70
                    }
        
        # If we created an inserted chord, append it now (it comes after prev, before current)
        if inserted_chord:
            chords_output.append(inserted_chord)

        # --- Current Chord Generation ---
        
        # Generate Notes
        # Use octave 3 or 4 depending on mood. Trap/Drill/Walker usually lower.
        octave = 3 if any(x in mood_key for x in ["trap", "dark", "drill", "walker"]) else 4
        
        # Determine Extension Strategy
        if isinstance(degree, int):
            extension = get_smart_extension(degree, mood_key)
        else:
            extension = "7" # Secondary dominants usually need the tritone (7th)
        
        # Override for specific feels not covered by smart extension
        if "cinematic" in mood_key:
             extension = "triad" # Clean triads usually, maybe sus2/sus4 handled elsewhere
        elif "pop" in mood_key:
             extension = random.choice(["triad", "add9"]) # Add9 is common in pop
        elif "walker" in mood_key or "epic" in mood_key:
             # Wide, open voicing for emotion
             extension = "triad" # We will manually adjust voicing later
                 
        elif "future_bass" in mood_key:
             # Future Bass loves thick 7ths and 9ths
             extension = random.choice(["7", "9", "add9"])
        elif "trap" in mood_key and complexity > 0.7:
             # Complex Trap uses 9ths for spookiness
             extension = "9"
        elif "neo_soul" in mood_key:
             extension = random.choice(["9", "11", "7", "11"])
        elif "reggaeton" in mood_key:
             extension = random.choice(["triad", "7"])
        elif "techno" in mood_key:
             extension = "triad" # Clean, driving
        elif "gospel" in mood_key:
             extension = random.choice(["7", "9", "13", "11"])
        elif "synthwave" in mood_key:
             extension = random.choice(["triad", "7", "add9"])
        elif "dubstep" in mood_key:
             extension = random.choice(["triad", "7"])
        elif "trance" in mood_key:
             extension = random.choice(["triad", "sus4", "sus2"]) # Trance loves sus chords
        elif "dnb" in mood_key:
             extension = random.choice(["7", "9", "triad"]) # Liquid DnB loves 7ths
        elif "progressive" in mood_key:
             extension = random.choice(["triad", "7", "add9"])
        elif "big_room" in mood_key:
             extension = "triad" # Simple power
        elif "electro" in mood_key:
             extension = random.choice(["triad", "7"])
        elif "tropical" in mood_key:
             extension = random.choice(["triad", "6", "add9"]) # 6th chords are nice here
        elif "hardstyle" in mood_key:
             extension = "triad" # Detuned saws don't like complex intervals
        elif "melodic_dubstep" in mood_key:
             extension = random.choice(["7", "9", "add9"]) # Big emotional supersaws
        
        notes = get_extended_chord_notes(key, scale, degree, octave=octave, extension=extension)


        # Apply Voicings (The "Sauce")
        
        # 1. Genre-Specific Voicings
        if "drill" in mood_key:
            # Drill Voicing: "Advanced Drill Trick" & Thinner Chords
            
            original_root = notes[0]
            
            # "Remove 5th note sometimes" (make chords thinner)
            # 30% chance to remove the 5th (index 2 in a triad/7th)
            # Be careful with indices if we have extensions
            if len(notes) >= 3 and random.random() < 0.3:
                # The 5th is usually at index 2
                notes.pop(2)
            
            # Add Sub-Bass Root (Left Hand)
            notes.insert(0, original_root - 12)
            
            # Remove the original root (now index 1) to clear up the mud
            # So we get [Sub-Bass, 3rd, 5th, (7th)]
            if len(notes) > 2: 
                 notes.pop(1)
            
        elif "trap" in mood_key:
            # Trap Voicing: Spread chords (Open Voicing)
            # Move the middle note (3rd) up an octave
            if len(notes) >= 3: # Need at least 3 notes
                # Index 1 is usually the 3rd
                mid_note = notes.pop(1)
                notes.append(mid_note + 12)
            
            # Add deep root
            notes.insert(0, notes[0] - 12)
            
        elif "rnb" in mood_key or "lo_fi" in mood_key or "jazz" in mood_key:
            # Neo Soul / Jazz Voicings
            # Spread: Drop 2 (Move 2nd highest note down an octave)
            if len(notes) >= 4:
                 # Drop 2 voicing
                 second_highest = notes.pop(-2)
                 notes.insert(0, second_highest - 12)
            elif len(notes) == 3:
                 # Open triad
                 mid = notes.pop(1)
                 notes.append(mid + 12)
                 
        elif "house" in mood_key:
             # Deep House: Parallel minor 7ths usually, close voicing but low
             # Add sub root
             notes.insert(0, notes[0] - 12)
             
        elif "cinematic" in mood_key:
             # Wide spread
             # Root, 5th, Root(+1), 3rd(+1)
             # Current: Root, 3rd, 5th
             if len(notes) >= 3:
                 root = notes[0]
                 third = notes[1]
                 fifth = notes[2]
                 
                 notes = [root - 12, root, fifth, third + 12] # Open voicing
                 
        elif "pop" in mood_key:
             # Standard piano voicing: Left hand root, Right hand triad
             notes.insert(0, notes[0] - 12)

        elif "future_bass" in mood_key:
             # Thick Super Saw Voicing
             # Add deep root
             notes.insert(0, notes[0] - 12)
             
             # Double the 3rd an octave up for brightness (Index 2 is 3rd after insert)
             if len(notes) >= 3:
                 notes.append(notes[2] + 12)
             # Sometimes double the 5th too
             if len(notes) >= 4 and random.random() > 0.5:
                 notes.append(notes[3] + 12)

        elif "walker" in mood_key or "epic" in mood_key:
             # Wide, open voicing for emotion
             # Root (Sub), Root, 5th, 3rd (+1 octave)
             
             # Add deep root
             notes.insert(0, notes[0] - 12)
             
             # If we have a 3rd (usually index 2 after insert), move it up an octave
             # [SubRoot, Root, 3rd, 5th] -> [SubRoot, Root, 5th, 3rd+12]
             if len(notes) >= 4:
                 third = notes.pop(2) 
                 notes.append(third + 12)
        
        # 2. Inversions for smooth voice leading (only if not Drill/Trap/Techno which like parallel motion)
        # Also exclude Walker/Epic which have manual wide voicing
        if i > 0 and not any(g in mood_key for g in ["drill", "trap", "techno", "house", "dubstep", "walker", "epic"]):
            # Check against the *last* chord added
            prev_notes = chords_output[-1]["notes"]
            notes = smooth_voice_leading(notes, prev_notes)
                
        chord_name = f"{degree}" # Placeholder name
        
        chords_output.append({
            "degree": degree,
            "notes": notes,
            "duration": duration,
            "velocity": 80 + random.randint(-5, 5) # Humanize slightly
        })
        
    return {
        "key": key,
        "scale": scale,
        "mood": mood,
        "progression": chords_output
    }

def generate_track_data(key: str, scale: str, mood: str, length: int = 4, complexity: float = 0.5, melody: bool = True, tempo: int = 140, pattern_override: List[int] = None) -> Dict[str, Any]:
    """
    Generates a full track including chords (potentially rhythmic) and melody.
    """
    # 1. Generate basic chord progression
    prog_data = generate_progression(key, scale, mood, length, complexity, pattern_override=pattern_override)
    chords_output = prog_data["progression"]
    
    # Update key, scale, mood if they were randomized/defaulted
    key = prog_data["key"]
    scale = prog_data["scale"]
    mood = prog_data["mood"]
    
    # 2. Apply Rhythmic Patterns / Complex Playing to Chords
    # We convert block chords into a stream of note events
    chord_events = []
    
    mood_key = mood.lower()
    
    # Normalize mood_key to ensure it matches genre_rhythms keys
    if "drill" in mood_key: mood_key = "drill"
    elif "lofi" in mood_key or "chill" in mood_key: mood_key = "lo_fi"
    elif "r&b" in mood_key or "soul" in mood_key: mood_key = "rnb"
    elif "future" in mood_key or "bass" in mood_key or "kawaii" in mood_key: mood_key = "future_bass"
    elif "techno" in mood_key or "rave" in mood_key: mood_key = "techno"
    elif "synth" in mood_key or "wave" in mood_key: mood_key = "synthwave"
    elif "drum" in mood_key or "dnb" in mood_key: mood_key = "dnb"
    elif "reggaeton" in mood_key: mood_key = "reggaeton"
    elif "dubstep" in mood_key: mood_key = "dubstep"
    elif "trance" in mood_key: mood_key = "trance"
    elif "house" in mood_key: mood_key = "house"
    elif "pop" in mood_key: mood_key = "pop"
    elif "cinematic" in mood_key: mood_key = "cinematic"
    elif "walker" in mood_key or "faded" in mood_key: mood_key = "walker"
    elif "jazz" in mood_key: mood_key = "jazz"
    elif "trap" in mood_key: mood_key = "trap"

    current_time = 0.0 # Track time dynamically as chords vary in duration
    
    # --- Genre Rhythm Strategies ---
    # Define available rhythm patterns for each genre
    genre_rhythms = {
        "walker": ["walker_piano", "walker_arp"], # Steady chords or emotional arps
        "drill": ["drill_stabs", "drill_sustained", "drill_counter"],
        "future_bass": ["future_bass_wub", "future_bass_saw", "future_bass_16th"],
        "trap": ["trap_bounce", "drill_sustained", "basic"],
        "rnb": ["neo_soul", "rnb_strum", "basic"],
        "lo_fi": ["lofi_chop", "jazz_swing", "basic"],
        "house": ["house_stab", "house_piano", "basic"],
        "techno": ["techno_drive", "techno_rumble"],
        "pop": ["pop_strum", "basic", "pop_arpeggio"],
        "cinematic": ["cinematic_swell", "basic"],
        "reggaeton": ["reggaeton", "reggaeton_bounce"],
        "jazz": ["jazz_swing", "neo_soul"],
        "dnb": ["dnb_pad", "dnb_stab"],
        "dubstep": ["dubstep_wub", "drill_sustained"],
        "trance": ["euro_trance", "trance_gate"],
        "synthwave": ["synthwave_pulse", "synthwave_arps"]
    }

    # Determine rhythm key
    rhythm_key = "basic"
    for key_name in genre_rhythms:
        if key_name in mood_key:
            rhythm_key = key_name
            break
    
    print(f"DEBUG: mood_key={mood_key}, rhythm_key={rhythm_key}")

    # Select a strategy for the whole track or per chord?
    # Let's mix it up. 70% chance to stick to one pattern, 30% to vary per chord.
    main_pattern = random.choice(genre_rhythms.get(rhythm_key, ["basic"]))
    vary_per_chord = random.random() > 0.7
    
    # Define patterns that sound bad/gappy on short chords (< 3.0 beats)
    unsafe_patterns = [
        "drill_counter", # Starts late
        "dnb_stab",      # Big gaps
        "techno_rumble", # Gappy
        "euro_trance",   # Gappy
        "house_stab",    # Staccato, might feel empty
        "future_bass_16th" # Ends early
    ]

    for i, chord in enumerate(chords_output):
        duration = chord["duration"]
        
        # Decide pattern for this chord
        if vary_per_chord:
            available_patterns = genre_rhythms.get(rhythm_key, ["basic"])
            # Filter unsafe patterns for short chords (avoid initial silence)
            if duration < 3.0:
                 available_patterns = [p for p in available_patterns if p not in unsafe_patterns]
                 if not available_patterns: available_patterns = ["basic"]
            
            pattern_name = random.choice(available_patterns)
        else:
            pattern_name = main_pattern
            # Fallback for short chords if main pattern is unsafe
            if duration < 3.0 and pattern_name in unsafe_patterns:
                pattern_name = "basic"

        # Special Case: Arpeggios for certain genres/sections
        use_arpeggio = False
        if "pop" in mood_key and random.random() < 0.2: use_arpeggio = True
        if "synthwave" in mood_key and random.random() < 0.4: use_arpeggio = True
        if "trance" in mood_key and random.random() < 0.5: use_arpeggio = True
        if "trap" in mood_key and complexity > 0.7 and random.random() < 0.3: use_arpeggio = True

        if use_arpeggio:
            # Apply Arpeggio
            arp_type = random.choice(["up", "down", "up_down", "converge", "diverge"])
            rate = 0.25
            if "trap" in mood_key: rate = 0.125 # Fast trap arps
            events = apply_arpeggio(chord["notes"], pattern_type=arp_type, length=duration, rate=rate) 
        elif "walker" in mood_key and len(chord["notes"]) >= 3:
            # Walker Special: Split Bass and Chords for clarity
            # Notes structure from walker voicing: [SubRoot, Root, 5th, 3rd(high)]
            
            print(f"DEBUG: Processing Walker Special for chord {i}")

            # 1. Bass (Bottom 1 note) - Deep Pulse
            bass_notes = [chord["notes"][0]]
            # Pattern: Sustained bass
            bass_pattern_name = "basic" 
            bass_events = apply_rhythm(bass_notes, bass_pattern_name, duration, strum_speed=0.0)
            
            # 2. Chords (Top notes) - Rhythmic Piano
            # Include the Root, 5th, and High 3rd for a fuller sound
            chord_notes = chord["notes"][1:]
            # Pattern: walker_piano (8th notes)
            chord_pattern_name = "walker_piano"
            upper_events = apply_rhythm(chord_notes, chord_pattern_name, duration, strum_speed=0.0)
            
            events = bass_events + upper_events
            print(f"DEBUG: Walker events generated: {len(events)}")
            
        else:
            # Apply Rhythm Pattern
            # Special strum speeds
            strum = 0.0
            if "rnb" in mood_key: strum = 0.03
            if "lofi" in mood_key: strum = 0.05
            
            events = apply_rhythm(chord["notes"], pattern_name, duration, strum_speed=strum)
                
        # Shift events to absolute time
        if not events:
            print(f"DEBUG: No events generated for chord {i}")
        
        for event in events:
            event["time"] += current_time
            # Ensure time is never negative (Tone.js doesn't like negative time)
            if event["time"] < 0:
                event["time"] = 0.0
            chord_events.append(event)
            
        current_time += duration
    
    print(f"DEBUG: Total chord_events: {len(chord_events)}")

    # 3. Generate Melody (if requested)
    melody_events = []
    if melody:
        melody_events = generate_melody(key, scale, chords_output, complexity, mood)

    # 4. Generate Bass Line
    bass_events = []
    current_bass_time = 0.0
    
    for i, chord in enumerate(chords_output):
        duration = chord["duration"]
        if not chord["notes"]:
            current_bass_time += duration
            continue
            
        # Extract root (lowest note usually)
        root = chord["notes"][0]
        
        # Drop to Bass Range (approx E1-G2: 28-43)
        bass_note = root
        while bass_note > 45: # A2
            bass_note -= 12
        while bass_note < 28: # E1 (extended range for deep bass)
            bass_note += 12
            
        # Intervals
        fifth_note = bass_note + 7
        octave_note = bass_note + 12
        
        # Determine Bass Rhythm based on Mood
        b_events = []
        
        mood_lower = mood.lower()
        
        if "house" in mood_lower or "techno" in mood_lower or "trance" in mood_lower or "dance" in mood_lower:
            # Driving Offbeat Bass with Octaves
            # Pattern: Rest, Root, Rest, Octave...
            step = 0.5
            for t in range(int(duration / step)):
                if t % 2 != 0: # Offbeat
                    note_to_play = bass_note
                    # Add octave jump variation every 4th beat or randomly
                    if t % 4 == 3 or random.random() < 0.3:
                        note_to_play = octave_note
                        
                    b_events.append({
                        "note": note_to_play,
                        "time": t * step,
                        "duration": step * 0.8,
                        "velocity": 100 + random.randint(-5, 5)
                    })

        elif "drill" in mood_lower or "trap" in mood_lower or "hip hop" in mood_lower:
            # 808 Style: Long sustained notes with rhythmic glides/fills
            # Pattern: Boom....... (fill)
            
            # Main sustain
            b_events.append({
                "note": bass_note,
                "time": 0.0,
                "duration": duration * 0.85, # Leave a small gap
                "velocity": 110
            })
            
            # Occasional fill at the end of the bar (last 16th or 8th)
            if duration >= 2.0 and random.random() < 0.4:
                # Add a quick note at the end to lead to next chord
                b_events.append({
                    "note": bass_note, # Or slide?
                    "time": duration - 0.5,
                    "duration": 0.25,
                    "velocity": 90
                })
                b_events.append({
                    "note": bass_note, 
                    "time": duration - 0.25,
                    "duration": 0.2,
                    "velocity": 80
                })

        elif "future_bass" in mood_lower or "dubstep" in mood_lower:
            # Rhythmic following of chords, but mono
            # Dotted rhythms: 3/16, 3/16, 2/16 (3+3+2)
            if random.random() < 0.6:
                # 3+3+2 pattern (on 16th notes: 0, 0.75, 1.5)
                # Scaled to 8th notes step = 0.5. 
                # 3+3+2 in 16ths = 1.5 beats + 1.5 beats + 1 beat = 4 beats
                
                # Beat 1
                b_events.append({"note": bass_note, "time": 0.0, "duration": 0.7, "velocity": 110})
                # Beat 2.5 (dotted quarter)
                b_events.append({"note": bass_note, "time": 1.5, "duration": 0.7, "velocity": 105})
                # Beat 4 (quarter) - wait, 1.5+1.5=3. So beat 4 is next.
                b_events.append({"note": bass_note, "time": 3.0, "duration": 0.9, "velocity": 100})
            else:
                # Simple Sustain
                b_events.append({
                    "note": bass_note,
                    "time": 0.0,
                    "duration": duration * 0.9,
                    "velocity": 110
                })

        elif "pop" in mood_lower or "rock" in mood_lower or "punk" in mood_lower:
            # Driving 8th notes with Root-Fifth alternation
            step = 0.5
            for t in range(int(duration / step)):
                note_to_play = bass_note
                
                # Rock/Punk: Straight 8ths, downpicking (consistent velocity)
                # Pop: Root on 1, Fifth on 3 maybe?
                
                # Variation: Play 5th on weak beats sometimes
                if t % 4 == 2 and random.random() < 0.3: # Beat 2
                     note_to_play = fifth_note
                elif t % 4 == 3 and random.random() < 0.3: # Beat 2.5
                     note_to_play = octave_note
                     
                # Velocity accents on downbeats (0, 2, 4...)
                vel = 100 if t % 2 == 0 else 85
                
                b_events.append({
                    "note": note_to_play,
                    "time": t * step,
                    "duration": step * 0.7, # Slightly staccato
                    "velocity": vel + random.randint(-5, 5)
                })

        elif "funk" in mood_lower or "disco" in mood_lower:
            # Syncopated 16th notes, Octaves, Ghost notes
            # Simplified: Root on 1, Octave on 1.5, rests
            
            # Beat 1: Root
            b_events.append({"note": bass_note, "time": 0.0, "duration": 0.4, "velocity": 105})
            
            # Beat 1.75 (16th pickup to 2)? Or Beat 2?
            # Let's do Root - Octave pattern
            if duration >= 2.0:
                 # Beat 2: Octave (short)
                 b_events.append({"note": octave_note, "time": 1.0, "duration": 0.2, "velocity": 95})
                 # Beat 2.5: Root
                 b_events.append({"note": bass_note, "time": 1.5, "duration": 0.4, "velocity": 100})
                 # Beat 3.5: Octave
                 b_events.append({"note": octave_note, "time": 2.5, "duration": 0.2, "velocity": 95})
                 # Beat 3.75: Octave
                 b_events.append({"note": octave_note, "time": 2.75, "duration": 0.2, "velocity": 90})

        elif "walker" in mood_lower or "cinematic" in mood_lower:
             # Deep, long, low
             bass_note_deep = bass_note
             if bass_note_deep > 36: bass_note_deep -= 12
             b_events.append({
                "note": bass_note_deep,
                "time": 0.0,
                "duration": duration,
                "velocity": 95
            })
             
        elif "lo_fi" in mood_lower or "rnb" in mood_lower or "neo_soul" in mood_lower:
            # Laid back, late
            # Root on 1
            b_events.append({
                "note": bass_note,
                "time": random.uniform(0.05, 0.12), # Laid back
                "duration": duration * 0.4,
                "velocity": 85
            })
            
            # Maybe a pickup note at the end?
            if random.random() < 0.5 and duration >= 2:
                 b_events.append({
                    "note": fifth_note if random.random() < 0.5 else octave_note,
                    "time": duration - 0.5,
                    "duration": 0.4,
                    "velocity": 75
                })

        else:
            # Basic fallback: Root note on downbeat, maybe repeat on beat 3
            b_events.append({
                "note": bass_note,
                "time": 0.0,
                "duration": duration * 0.45,
                "velocity": 90
            })
            if duration >= 2.0:
                b_events.append({
                    "note": bass_note,
                    "time": duration / 2, # Halfway
                    "duration": duration * 0.45,
                    "velocity": 85
                })
            
        # Shift events to absolute time and add to main list
        for event in b_events:
            # Make sure we don't exceed chord duration
            if event["time"] < duration:
                # Clip duration if it goes over
                if event["time"] + event["duration"] > duration:
                    event["duration"] = duration - event["time"]
                    
                event["time"] += current_bass_time
                bass_events.append(event)
            
        current_bass_time += duration

    return {
        "key": key,
        "scale": scale,
        "mood": mood,
        "chords": chord_events,
        "melody": melody_events,
        "bass": bass_events,
        "raw_progression": chords_output,
        "progression": chords_output, # Alias for frontend compatibility
        "tempo": tempo
    }
