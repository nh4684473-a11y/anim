import mido
import os
from typing import Dict, List, Any

def parse_midi_file(file_path: str) -> Dict[str, Any]:
    """
    Parses a MIDI file and extracts chords, melody, and bass.
    Returns a dictionary in the format expected by the frontend.
    """
    if not os.path.exists(file_path):
        return None

    try:
        mid = mido.MidiFile(file_path)
    except Exception as e:
        print(f"Error parsing MIDI file {file_path}: {e}")
        return None

    # Default values
    tempo = 120
    ticks_per_beat = mid.ticks_per_beat
    
    chords = []
    melody = []
    bass = []
    
    # Temporary storage for tracks before final assignment
    tracks_data = []

    # Iterate through tracks
    for i, track in enumerate(mid.tracks):
        track_name = track.name.strip().lower()
        notes = []
        current_time = 0
        active_notes = {}
        is_drum = False
        
        for msg in track:
            current_time += msg.time
            
            if msg.type == 'set_tempo':
                new_tempo = mido.tempo2bpm(msg.tempo)
                if tempo == 120 or i == 0:
                    tempo = new_tempo
            
            if hasattr(msg, 'channel') and msg.channel == 9:
                is_drum = True
                continue

            if msg.type == 'note_on' and msg.velocity > 0:
                active_notes[msg.note] = {
                    "start": current_time,
                    "velocity": msg.velocity
                }
            elif (msg.type == 'note_off') or (msg.type == 'note_on' and msg.velocity == 0):
                if msg.note in active_notes:
                    start_info = active_notes.pop(msg.note)
                    duration_ticks = current_time - start_info["start"]
                    
                    if duration_ticks > 0:
                        start_beat = start_info["start"] / ticks_per_beat
                        duration_beat = duration_ticks / ticks_per_beat
                        
                        notes.append({
                            "note": msg.note,
                            "time": float(f"{start_beat:.3f}"),
                            "duration": float(f"{duration_beat:.3f}"),
                            "velocity": start_info["velocity"]
                        })
        
        if not notes or is_drum:
            continue
            
        avg_pitch = sum(n["note"] for n in notes) / len(notes)
        tracks_data.append({
            "name": track_name,
            "notes": notes,
            "avg_pitch": avg_pitch,
            "count": len(notes)
        })

    # Intelligent Assignment
    # 1. Find Bass: Lowest avg pitch, preferably with "bass" in name
    bass_candidates = [t for t in tracks_data if "bass" in t["name"]]
    if not bass_candidates:
        bass_candidates = [t for t in tracks_data if t["avg_pitch"] < 48]
    
    if bass_candidates:
        # Pick the one with the most notes? Or lowest pitch?
        # Usually bass track is singular.
        best_bass = min(bass_candidates, key=lambda x: x["avg_pitch"])
        bass.extend(best_bass["notes"])
        tracks_data.remove(best_bass)

    # 2. Find Melody: Highest avg pitch, preferably with "melody"/"vocal"/"lead" in name
    melody_candidates = [t for t in tracks_data if any(k in t["name"] for k in ["melody", "vocal", "lead"])]
    if not melody_candidates:
        # If no explicit melody, pick the highest pitch track remaining
        if tracks_data:
            best_melody = max(tracks_data, key=lambda x: x["avg_pitch"])
            # Heuristic: Melody usually has fewer notes than full piano accompaniment, but not always.
            # But high pitch is a strong indicator.
            melody.extend(best_melody["notes"])
            tracks_data.remove(best_melody)
    else:
        best_melody = max(melody_candidates, key=lambda x: x["count"]) # Or pitch?
        melody.extend(best_melody["notes"])
        tracks_data.remove(best_melody)

    # 3. Everything else -> Chords
    for t in tracks_data:
        chords.extend(t["notes"])

    # If no notes classified, maybe put everything in chords?
    if not chords and not melody and not bass:
        return None
        
    return {
        "tempo": int(tempo),
        "key": "C", # Default
        "scale": "major",
        "mood": "Imported",
        "chords": chords,
        "melody": melody,
        "bass": bass,
        "instruments": {
            "chords": "piano",
            "melody": "piano",
            "bass": "bass"
        }
    }
