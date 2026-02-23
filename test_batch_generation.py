
import sys
import os
import shutil
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.logic.chords import generate_track_data

def test_batch_generation():
    print("Starting Batch Generation Test (50 samples)...")
    
    output_dir = Path("test_batch_output")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir()
    
    genres = ["walker", "drill", "future_bass", "piano", "cinematic"]
    keys = ["C", "F#", "A", "D#", "G"]
    
    success_count = 0
    errors = []
    
    for i in range(50):
        genre = genres[i % len(genres)]
        key = keys[i % len(keys)]
        scale = "minor"
        
        filename = f"Batch_{i}_{genre}_{key}.mid"
        filepath = output_dir / filename
        
        try:
            # 1. Generate Data
            track_data = generate_track_data(
                key=key,
                scale=scale,
                mood=genre,
                length=8,
                complexity=0.7,
                melody=True
            )
            
            # 2. Generate MIDI
            from app.utils.midi_export import create_midi_file
            
            # create_midi_file returns a temp path
            temp_midi_path = create_midi_file(track_data, tempo=track_data.get("tempo", 120), mood=genre)
            
            # Move to our output directory
            shutil.move(temp_midi_path, filepath)
            
            if filepath.exists() and filepath.stat().st_size > 100:
                success_count += 1
                if i % 10 == 0:
                    print(f"Generated {i+1}/50: {filename} - OK")
            else:
                errors.append(f"{filename}: File too small or missing")
                
        except Exception as e:
            errors.append(f"{filename}: {str(e)}")
            import traceback
            traceback.print_exc()
            
    print(f"\nBatch Test Complete.")
    print(f"Success: {success_count}/50")
    if errors:
        print("Errors:")
        for err in errors:
            print(err)
            
    # Cleanup
    # shutil.rmtree(output_dir)

if __name__ == "__main__":
    test_batch_generation()
