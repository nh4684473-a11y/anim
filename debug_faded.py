
import sys
import os
import json

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'backend')))

from app.logic.top_hits import generate_top_hit_track

try:
    track_data = generate_top_hit_track("faded_alan_walker")
    
    # Print a summary of the first few chord events
    print("Track Data Generated Successfully")
    print(f"Key: {track_data.get('key')}")
    print(f"Scale: {track_data.get('scale')}")
    print(f"Mood: {track_data.get('mood')}")
    
    chord_events = track_data.get("chord_events", [])
    print(f"Total Chord Events: {len(chord_events)}")
    
    if chord_events:
        print("First 10 Chord Events:")
        for event in chord_events[:10]:
            print(event)
            
    # Check if velocities are reasonable
    low_vel = [e for e in chord_events if e['velocity'] < 40]
    high_vel = [e for e in chord_events if e['velocity'] > 100]
    print(f"Events with velocity < 40: {len(low_vel)}")
    print(f"Events with velocity > 100: {len(high_vel)}")

except Exception as e:
    print(f"Error: {e}")
