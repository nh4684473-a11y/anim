
import os
import sys
import random
import time
from tqdm import tqdm

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from app.logic.chords import generate_track_data
from app.utils.midi_export import create_midi_file

LIBRARY_DIR = os.path.join("backend", "midi_library")
if not os.path.exists(LIBRARY_DIR):
    os.makedirs(LIBRARY_DIR)

MOODS = [
  "Dark Trap", "Boom Bap", "Drill", "Lo-Fi", "R&B / Soul", 
  "Jazz", "Cinematic", "House", "Pop", "Future Bass", "Neo Soul", "Reggaeton",
  "Dubstep", "Trance", "Techno", "Drum & Bass", "Progressive House", 
  "Big Room", "Electro House", "Tropical House", "Hardstyle", "Melodic Dubstep"
]

KEYS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
SCALES = ["minor", "harmonic_minor", "phrygian", "dorian", "minor_pentatonic", "major"]

def generate_library(count=100):
    print(f"Generating {count} tracks for the library...")
    
    for i in tqdm(range(count)):
        try:
            # Randomize Parameters
            mood = random.choice(MOODS)
            key = random.choice(KEYS)
            scale = random.choice(SCALES)
            tempo = random.randint(70, 160)
            complexity = random.choice([0.3, 0.5, 0.7, 0.9])
            
            # Generate Data
            track_data = generate_track_data(
                key=key,
                scale=scale,
                mood=mood,
                length=4,
                complexity=complexity,
                melody=True,
                tempo=tempo
            )
            
            # Create Filename
            # Format: Name__mood_Mood__key_Key__scale_Scale__comp_Complexity__bpm_BPM.mid
            safe_mood = mood.replace(" ", "_").replace("/", "").lower()
            safe_key = key.replace("#", "sharp")
            filename = f"track_{i:04d}__mood_{safe_mood}__key_{safe_key}__scale_{scale}__comp_{complexity}__bpm_{tempo}.mid"
            filepath = os.path.join(LIBRARY_DIR, filename)
            
            # Create MIDI
            temp_path = create_midi_file(track_data, tempo=tempo, mood=mood)
            
            # Move to Library
            if os.path.exists(filepath):
                os.remove(filepath)
            os.rename(temp_path, filepath)
            
        except Exception as e:
            print(f"Error generating track {i}: {e}")
            continue

    print(f"Library generation complete! Files saved to {LIBRARY_DIR}")

if __name__ == "__main__":
    count = 10  # Default small batch for testing
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except:
            pass
            
    generate_library(count)
