import sys
import os
import json

# Add parent dir to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.logic.top_hits import generate_top_hit_track
from app.utils.midi_export import create_midi_file

def verify_faded():
    print("Verifying Faded Template Generation...")
    
    try:
        data = generate_top_hit_track("faded_alan_walker")
        
        print(f"Generated {len(data['chords'])} chord events")
        print(f"Generated {len(data['melody'])} melody events")
        
        # Check for Walker Special logic
        walker_special_found = False
        for event in data['chords']:
            # Walker special logic splits bass and chords
            # We can't easily check logic here, but we can check if we have events
            pass
            
        # Check melody range
        if data['melody']:
            min_note = min(e['note'] for e in data['melody'])
            max_note = max(e['note'] for e in data['melody'])
            print(f"Melody Range: {min_note} - {max_note}")
            
            # Faded melody should be relatively high?
            if max_note < 70:
                print("WARNING: Melody seems low for Faded?")
                
        # Check chords velocity
        if data['chords']:
            avg_vel = sum(e['velocity'] for e in data['chords']) / len(data['chords'])
            print(f"Avg Chord Velocity: {avg_vel:.2f}")
            
        # Create MIDI file to test
        midi_path = create_midi_file(data, tempo=data['tempo'], mood=data['mood'])
        print(f"Created MIDI file at: {midi_path}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_faded()
