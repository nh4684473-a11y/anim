import os
import mido

def get_midi_length_in_bars(file_path):
    try:
        mid = mido.MidiFile(file_path)
        ticks_per_beat = mid.ticks_per_beat
        max_tick = 0
        
        for track in mid.tracks:
            current_tick = 0
            for msg in track:
                current_tick += msg.time
            
            if current_tick > max_tick:
                max_tick = current_tick
        
        # Assuming 4/4 time signature (4 beats per bar)
        beats = max_tick / ticks_per_beat
        bars = beats / 4
        return round(bars)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return 0

def verify_lengths():
    base_dir = "midi_samples"
    if not os.path.exists(base_dir):
        print("midi_samples directory not found.")
        return

    stats = {}

    for genre in os.listdir(base_dir):
        genre_path = os.path.join(base_dir, genre)
        if os.path.isdir(genre_path):
            stats[genre] = {}
            for filename in os.listdir(genre_path):
                if filename.endswith(".mid"):
                    file_path = os.path.join(genre_path, filename)
                    length = get_midi_length_in_bars(file_path)
                    stats[genre][length] = stats[genre].get(length, 0) + 1
    
    for genre, counts in stats.items():
        print(f"Genre: {genre}")
        for length, count in sorted(counts.items()):
            print(f"  {length} bars: {count} files")

if __name__ == "__main__":
    verify_lengths()
