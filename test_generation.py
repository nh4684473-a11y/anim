
import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

try:
    from app.logic.chords import generate_track_data
    print("Successfully imported generate_track_data")
except ImportError as e:
    print(f"Error importing generate_track_data: {e}")
    sys.exit(1)

def test_generation():
    print("Testing generation...")
    test_cases = [
        {"key": "C", "scale": "minor", "mood": "drill", "complexity": 0.8},
        {"key": "Random", "scale": "Random", "mood": "Random", "complexity": 0.5},
        {"key": "F#", "scale": "major", "mood": "happy", "complexity": 0.3},
        {"key": "A", "scale": "dorian", "mood": "jazz", "complexity": 0.9},
    ]

    for i, case in enumerate(test_cases):
        print(f"\n--- Test Case {i+1}: {case} ---")
        try:
            data = generate_track_data(
                key=case["key"],
                scale=case["scale"],
                mood=case["mood"],
                length=4,
                complexity=case["complexity"],
                melody=True,
                tempo=140
            )
            print("Generation successful!")
            print(f"Keys in result: {list(data.keys())}")
            print(f"Chords events: {len(data['chords'])}")
            print(f"Melody events: {len(data['melody'])}")
            
            # Validate data types
            if not isinstance(data['chords'], list):
                print("Error: chords is not a list")
            if not isinstance(data['melody'], list):
                print("Error: melody is not a list")
                
        except Exception as e:
            print(f"Generation failed for case {case}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_generation()
