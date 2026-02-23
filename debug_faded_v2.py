
import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'backend')))

from app.logic.chords import generate_progression, generate_track_data
from app.logic.top_hits import TOP_HITS_TEMPLATES

def debug_faded():
    template_id = "faded_alan_walker"
    template = next((t for t in TOP_HITS_TEMPLATES if t["id"] == template_id), None)
    
    if not template:
        print("Template not found")
        return

    print(f"Generating progression for {template['key']} {template['scale']} {template['mood']}")
    
    prog_data = generate_progression(
        key=template["key"],
        scale=template["scale"],
        mood=template["mood"],
        length=len(template["progression"]),
        complexity=0.5,
        pattern_override=template["progression"]
    )
    
    print("Progression Generated:")
    for chord in prog_data["progression"]:
        print(f"Degree: {chord['degree']}, Duration: {chord['duration']}, Notes: {chord['notes']}")
        
    print("\nGenerating Track Data...")
    track_data = generate_track_data(
        key=template["key"],
        scale=template["scale"],
        mood=template["mood"],
        length=len(template["progression"]),
        complexity=0.5,
        melody=True,
        tempo=template["tempo"],
        pattern_override=template["progression"]
    )
    
    chord_events = track_data.get("chords", [])
    print(f"Total Chord Events: {len(chord_events)}")
    if not chord_events:
        print("Debugging apply_rhythm logic...")
        # Inspect mood_key and rhythm selection logic manually here if needed
        pass

if __name__ == "__main__":
    debug_faded()
