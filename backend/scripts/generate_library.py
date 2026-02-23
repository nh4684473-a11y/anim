import sys
import os
import shutil
import random
import time

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.logic.chords import generate_track_data, PROGRESSIONS
    from app.utils.midi_export import create_midi_file
except ImportError:
    # If run from backend root
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from app.logic.chords import generate_track_data, PROGRESSIONS
    from app.utils.midi_export import create_midi_file

# Genres
GENRES = [
    "Dark Trap", "Boom Bap", "Emotional", "UK Drill", "Lo-Fi", "R&B", "Jazz", 
    "Cinematic", "House", "Pop", "Future Bass", "Neo Soul", "Reggaeton", 
    "Techno", "Gospel", "Synthwave"
]

# Keys
KEYS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
SCALES = ["minor", "major", "harmonic_minor", "dorian", "phrygian", "lydian", "mixolydian"]

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "midi_samples")

def generate_batch(total_count=10000):
    count_per_genre = total_count // len(GENRES)
    total_generated = 0
    
    print(f"Generating {total_count} MIDI files ({count_per_genre} per genre)...")
    
    for genre in GENRES:
        print(f"Generating {genre}...")
        genre_clean = genre.replace(" ", "_")
        genre_dir = os.path.join(SAMPLES_DIR, genre_clean)
        if not os.path.exists(genre_dir):
            os.makedirs(genre_dir)
            
        for i in range(count_per_genre):
            key = random.choice(KEYS)
            scale = random.choice(SCALES)
            mood = genre
            
            # Vary complexity and length
            complexity = random.uniform(0.4, 0.95)
            length = random.choice([4, 8])
            
            try:
                # 1. Generate Data
                data = generate_track_data(
                    key=key, 
                    scale=scale, 
                    mood=mood, 
                    length=length, 
                    complexity=complexity, 
                    melody=True
                )
                
                # 2. Format for export
                # Convert backend format to export format
                export_data = {}
                if "chords" in data:
                    export_data["chords"] = data["chords"]
                if "melody" in data:
                    export_data["melody"] = data["melody"]
                
                # 3. Create MIDI
                tempo = 120
                if "Trap" in genre: tempo = random.randint(130, 160)
                elif "Drill" in genre: tempo = random.randint(135, 145)
                elif "Lo-Fi" in genre: tempo = random.randint(70, 95)
                elif "House" in genre: tempo = random.randint(120, 130)
                elif "Techno" in genre: tempo = random.randint(125, 140)
                elif "Pop" in genre: tempo = random.randint(100, 128)
                elif "R&B" in genre: tempo = random.randint(80, 100)
                
                temp_path = create_midi_file(export_data, tempo=tempo)
                
                # 4. Move to final destination
                # Unique filename: Genre_Key_Scale_Length_Timestamp_Index.mid
                filename = f"{genre_clean}_{key}_{scale}_{length}bar_{int(time.time())}_{i}.mid"
                final_path = os.path.join(genre_dir, filename)
                
                # Use shutil.move instead of os.rename to handle cross-device issues if any
                shutil.move(temp_path, final_path)
                total_generated += 1
                
                # Print progress every 100
                if total_generated % 100 == 0:
                    print(f"Generated {total_generated} files...")
                
            except Exception as e:
                print(f"Failed to generate {genre} track: {e}")
                
    print(f"Successfully generated {total_generated} MIDI files.")

if __name__ == "__main__":
    count = 1000
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            print("Invalid count provided, using default 1000")
            
    generate_batch(total_count=count)
