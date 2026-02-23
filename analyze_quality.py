import mido
import os
import sys
import numpy as np
from typing import List, Dict

def analyze_midi(file_path):
    try:
        mid = mido.MidiFile(file_path)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

    stats = {
        "filename": os.path.basename(file_path),
        "total_notes": 0,
        "velocity_std_dev": 0,
        "timing_humanization": 0, # Avg deviation from perfect grid
        "chord_complexity": 0,    # Avg notes per simultaneous chord
        "pitch_range": 0,
        "duration_sec": mid.length
    }

    notes = []
    velocities = []
    start_times = []
    
    current_time = 0
    
    # Analyze Track 1 (usually chords) or first non-empty track
    target_track = None
    for track in mid.tracks:
        has_notes = False
        for msg in track:
            if msg.type == 'note_on':
                has_notes = True
                break
        if has_notes:
            target_track = track
            break
            
    if not target_track:
        return stats

    # Parse notes
    # We need absolute times
    abs_time = 0
    ticks_per_beat = mid.ticks_per_beat
    
    # note_starts = {} # key: note, value: start_tick
    
    # For chord detection, we group notes by start time
    chord_groups = {} # time -> count
    
    for msg in target_track:
        abs_time += msg.time
        
        if msg.type == 'note_on' and msg.velocity > 0:
            notes.append(msg.note)
            velocities.append(msg.velocity)
            start_times.append(abs_time)
            
            # Chord Grouping (allow window for strumming)
            # Strumming can spread a chord over ~50-60 ticks
            quant_grid = 120 # Approx 1/4 beat tolerance to catch all strummed notes
            found_group_key = None
            
            # Check existing keys
            for t in list(chord_groups.keys()):
                if abs(t - abs_time) < quant_grid:
                    found_group_key = t
                    break
            
            if found_group_key is not None:
                chord_groups[found_group_key] += 1
            else:
                chord_groups[abs_time] = 1

    if not notes:
        return stats

    stats["total_notes"] = len(notes)
    
    # 1. Velocity Analysis (Humanization)
    if velocities:
        stats["velocity_std_dev"] = np.std(velocities)
        
    # 2. Timing Analysis (Humanization)
    # Check deviation from perfect 16th note grid
    # 1 beat = ticks_per_beat
    # 16th note = ticks_per_beat / 4
    grid_unit = ticks_per_beat / 4
    deviations = []
    for t in start_times:
        # Find distance to nearest grid line
        dist = min(t % grid_unit, grid_unit - (t % grid_unit))
        deviations.append(dist)
    
    if deviations:
        # Avg deviation in percentage of a 16th note
        stats["timing_humanization"] = (np.mean(deviations) / grid_unit) * 100

    # 3. Chord Complexity
    if chord_groups:
        avg_density = np.mean(list(chord_groups.values()))
        stats["chord_complexity"] = avg_density
        
    # 4. Pitch Range
    if notes:
        stats["pitch_range"] = max(notes) - min(notes)

    return stats

def print_report(file_path):
    stats = analyze_midi(file_path)
    if not stats: return

    print(f"\n🎵 Analysis of: {stats['filename']}")
    print("-" * 40)
    
    # Interpretation
    print(f"  • Velocity Dynamics (Humanization): {stats['velocity_std_dev']:.2f}")
    if stats['velocity_std_dev'] > 5:
        print("    ✅ HIGH (Pro Level Humanization)")
    elif stats['velocity_std_dev'] > 0:
        print("    ⚠️ MEDIUM (Some Variation)")
    else:
        print("    ❌ LOW (Robotic/Flat)")

    print(f"  • Timing 'Swing' / Off-Grid: {stats['timing_humanization']:.2f}%")
    if stats['timing_humanization'] > 1.0:
         print("    ✅ DETECTED (Natural Groove)")
    else:
         print("    ⚠️ QUANTIZED (Robotic Precision)")

    print(f"  • Harmonic Density (Avg Notes/Chord): {stats['chord_complexity']:.2f}")
    if stats['chord_complexity'] >= 3.5:
        print("    ✅ JAZZ/NEO-SOUL (Complex Voicings: 7ths/9ths)")
    elif stats['chord_complexity'] >= 3.0:
        print("    ✅ STANDARD (Triads)")
    else:
        print("    ⚠️ SIMPLE (Power Chords/Melody)")

    print("-" * 40)

if __name__ == "__main__":
    # Find some files
    import glob
    files = glob.glob("backend/midi_samples/**/*.mid", recursive=True)
    if not files:
        print("No MIDI files found in backend/midi_samples")
        sys.exit(1)
        
    # Pick random 3
    import random
    targets = random.sample(files, min(3, len(files)))
    
    print("\n🔍 PRO LEVEL MIDI VERIFICATION REPORT")
    print("========================================")
    for f in targets:
        print_report(f)
