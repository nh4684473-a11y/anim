
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.logic.chords import generate_track_data

def test_walker():
    print("Testing Walker Chord Logic...")
    try:
        data = generate_track_data(
            key="F#",
            scale="minor",
            mood="walker",
            length=4,
            complexity=0.8,
            melody=False
        )
        
        print(f"Generated {len(data['chords'])} chord events.")
        
        # Analyze the first few events to check the split
        # We expect bass notes (long duration) and chord notes (short duration)
        
        bass_count = 0
        chord_count = 0
        
        for event in data['chords']:
            if event['time'] < 4.0: # First bar
                dur = event['duration']
                note = event['note']
                vel = event['velocity']
                print(f"Time: {event['time']:.2f}, Note: {note}, Dur: {dur}, Vel: {vel}")
                
                if dur >= 3.0:
                    bass_count += 1
                else:
                    chord_count += 1
                    
        print(f"Bass notes in bar 1: {bass_count}")
        print(f"Chord notes in bar 1: {chord_count}")
        
        if bass_count > 0 and chord_count > 0:
            print("SUCCESS: Split logic is working.")
        else:
            print("FAILURE: Split logic seems off.")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_walker()
