
import sys
import os
import random
import time
import shutil

# Add the backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from app.logic.chords import generate_track_data
from app.utils.midi_export import create_midi_file

# --- Configuration for "Top Production Level" Samples ---
# These are carefully curated presets mimicking top industry styles.

PRO_PRESETS = [
    # 0. NEW ADVANCED PRESETS
    {
        "name": "Complex_Jazz_Fusion",
        "genre": "Jazz",
        "mood": "jazz",
        "key": "Eb",
        "scale": "dorian",
        "tempo": 120,
        "complexity": 1.0, # Max complexity for extensions and passing chords
        "melody": True
    },
    {
        "name": "LoFi_Masterpiece",
        "genre": "Lo-Fi",
        "mood": "lo_fi",
        "key": "Ab",
        "scale": "major",
        "tempo": 82,
        "complexity": 0.9,
        "melody": True
    },
    {
        "name": "Orchestral_Epic",
        "genre": "Cinematic",
        "mood": "cinematic",
        "key": "D",
        "scale": "minor",
        "tempo": 110,
        "complexity": 0.8,
        "melody": True
    },

    # 1. The "OVO" Sound (Drake/Metro Boomin) - Dark Trap
    {
        "name": "OVO_Night_Drive",
        "genre": "Dark Trap",
        "mood": "dark_trap",
        "key": "C#",
        "scale": "minor",
        "tempo": 140,
        "complexity": 0.4, # Simple but effective
        "melody": True
    },
    {
        "name": "Metro_Gothic",
        "genre": "Dark Trap",
        "mood": "dark_trap",
        "key": "F",
        "scale": "phrygian", # The "evil" scale
        "tempo": 144,
        "complexity": 0.6,
        "melody": True
    },
    
    # 2. Modern Pop (Taylor Swift/Dua Lipa)
    {
        "name": "Radio_Anthem_1",
        "genre": "Pop",
        "mood": "pop",
        "key": "G",
        "scale": "major",
        "tempo": 120,
        "complexity": 0.5,
        "melody": True
    },
    {
        "name": "Retro_Future_Pop",
        "genre": "Pop",
        "mood": "pop",
        "key": "A",
        "scale": "minor",
        "tempo": 110,
        "complexity": 0.7,
        "melody": True
    },
    
    # 3. Future Bass (Flume/Illenium)
    {
        "name": "Super_Saw_Feels",
        "genre": "Future Bass",
        "mood": "future_bass",
        "key": "F",
        "scale": "major",
        "tempo": 150,
        "complexity": 0.8, # Needs 7ths/9ths
        "melody": True
    },
    {
        "name": "Kawaii_Bounce",
        "genre": "Future Bass",
        "mood": "future_bass",
        "key": "D#",
        "scale": "major",
        "tempo": 160,
        "complexity": 0.7,
        "melody": True
    },
    
    # 4. UK Drill (Central Cee/Pop Smoke)
    {
        "name": "London_Dungeon",
        "genre": "UK Drill",
        "mood": "uk_drill",
        "key": "C",
        "scale": "minor",
        "tempo": 142,
        "complexity": 0.5,
        "melody": True
    },
    {
        "name": "Sliding_808s_Vibe",
        "genre": "UK Drill",
        "mood": "uk_drill",
        "key": "D#",
        "scale": "phrygian",
        "tempo": 145,
        "complexity": 0.6,
        "melody": True
    },
    
    # 5. Neo Soul / R&B (H.E.R./SZA)
    {
        "name": "Sunday_Morning_Coffee",
        "genre": "Neo Soul",
        "mood": "neo_soul",
        "key": "Eb",
        "scale": "major",
        "tempo": 85,
        "complexity": 0.9, # Max extensions
        "melody": True
    },
    {
        "name": "Late_Night_Vibes",
        "genre": "R&B",
        "mood": "rnb",
        "key": "Bb",
        "scale": "minor",
        "tempo": 90,
        "complexity": 0.8,
        "melody": True
    },
    
    # 6. Lo-Fi Hip Hop (ChilledCow)
    {
        "name": "Study_Beats_Relax",
        "genre": "Lo-Fi",
        "mood": "lo_fi",
        "key": "Db",
        "scale": "major",
        "tempo": 80,
        "complexity": 0.7,
        "melody": True
    },
    
    # 7. Cinematic / Epic (Hans Zimmer Style)
    {
        "name": "Interstellar_Journey",
        "genre": "Cinematic",
        "mood": "cinematic",
        "key": "A",
        "scale": "minor",
        "tempo": 120,
        "complexity": 0.6,
        "melody": True
    },
    
    # 8. Melodic Dubstep (Seven Lions)
    {
        "name": "Emotional_Drop",
        "genre": "Melodic Dubstep",
        "mood": "melodic_dubstep",
        "key": "F#",
        "scale": "major",
        "tempo": 140,
        "complexity": 0.8,
        "melody": True
    },
    
    # 9. Deep House (Selected Style)
    {
        "name": "Ibiza_Sunset",
        "genre": "House",
        "mood": "house",
        "key": "A",
        "scale": "minor",
        "tempo": 124,
        "complexity": 0.5,
        "melody": True
    }
]

SAMPLES_ROOT = os.path.join(os.path.dirname(__file__), "backend", "midi_samples")

def generate_pro_samples():
    print(f"Generating {len(PRO_PRESETS)} Top Production Level Samples...")
    
    if not os.path.exists(SAMPLES_ROOT):
        os.makedirs(SAMPLES_ROOT)
        
    generated_count = 0
    
    for preset in PRO_PRESETS:
        print(f"Generating: {preset['name']} ({preset['genre']})...")
        
        # 1. Generate Data
        try:
            track_data = generate_track_data(
                key=preset["key"],
                scale=preset["scale"],
                mood=preset["mood"],
                length=8, # 8 bars for a full loop
                complexity=preset["complexity"],
                melody=preset["melody"],
                tempo=preset["tempo"]
            )
            
            # 2. Prepare for Export
            # New export format expects a dict with "chords" and "melody" lists
            export_data = {
                "chords": track_data["chords"],
                "melody": track_data["melody"]
            }
            
            # 3. Create MIDI File
            # Pass mood for humanization
            temp_path = create_midi_file(export_data, tempo=preset["tempo"], mood=preset["mood"])
            
            # 4. Save to Samples Directory
            # Create specific folder for "Pro_Level" or categorize by genre
            # Let's put them in a special "Pro_Level_Selection" folder for visibility,
            # OR mix them into their genres. User asked to "add them in sample".
            # Let's do both: Put in genre folders but with a prefix.
            
            genre_folder = preset["genre"].replace(" ", "_")
            target_dir = os.path.join(SAMPLES_ROOT, genre_folder)
            
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            
            # Use double underscore for safer parsing
            # Format: Name__Mood__Key__Scale__Complexity__BPM.mid
            # sanitize key (e.g. C# -> Csharp) if needed, but file systems usually handle #
            # Let's keep # for now.
            safe_key = preset['key'].replace("#", "sharp") 
            filename = f"{preset['name']}__mood_{preset['mood']}__key_{safe_key}__scale_{preset['scale']}__comp_{preset['complexity']}__bpm_{preset['tempo']}.mid"
            target_path = os.path.join(target_dir, filename)
            
            shutil.move(temp_path, target_path)
            print(f"  -> Saved to {target_path}")
            generated_count += 1
            
        except Exception as e:
            print(f"  -> Failed: {e}")
            import traceback
            traceback.print_exc()

    print(f"\nSuccessfully generated {generated_count} pro-level samples.")

if __name__ == "__main__":
    generate_pro_samples()
