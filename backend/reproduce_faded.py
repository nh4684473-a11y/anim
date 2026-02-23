
import sys
import os
import json

# Add project root to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "backend"))

from backend.app.logic.top_hits import generate_top_hit_track
from backend.app.utils.midi_export import create_midi_file

def test_faded_generation():
    print("Generating Faded track data...")
    try:
        track_data = generate_top_hit_track("faded_alan_walker")
        
        print(f"Keys in track_data: {track_data.keys()}")
        
        if "chords" in track_data:
            print(f"Number of chord events: {len(track_data['chords'])}")
            if len(track_data['chords']) > 0:
                print(f"First 3 chord events: {track_data['chords'][:3]}")
                
                # Check velocities
                velocities = [e["velocity"] for e in track_data["chords"]]
                print(f"Velocity range: {min(velocities)} - {max(velocities)}")
                
                # Check notes
                notes = [e["note"] for e in track_data["chords"]]
                print(f"Note range: {min(notes)} - {max(notes)}")
                
        if "melody" in track_data:
            print(f"Number of melody events: {len(track_data['melody'])}")
            
        # Try to export to MIDI
        print("Exporting to MIDI...")
        midi_path = create_midi_file(track_data, tempo=track_data["tempo"], mood=track_data["mood"])
        print(f"MIDI exported to: {midi_path}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_faded_generation()
