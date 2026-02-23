import requests
import json
import time

url = "http://127.0.0.1:8000/generate/chords"
payload = {
    "key": "C",
    "scale": "minor",
    "mood": "drill",
    "length": 4,
    "complexity": 1.0, # Max complexity
    "melody": False,
    "tempo": 140
}

# Loop until we get inserted chords
max_tries = 10
for attempt in range(max_tries):
    print(f"Attempt {attempt+1}...")
    response = requests.post(url, json=payload)
    data = response.json()
    
    raw = data["raw_progression"]
    has_short = any(c["duration"] < 3.0 for c in raw)
    
    if has_short:
        print("Found progression with short chords!")
        events = data["chords"]
        events.sort(key=lambda x: x["time"])
        
        last_end = 0.0
        gaps = []
        
        for i, event in enumerate(events):
            start = event["time"]
            dur = event["duration"]
            if start > last_end + 0.1:
                gaps.append((last_end, start))
                print(f"GAP: {last_end:.2f} -> {start:.2f} (Dur: {start - last_end:.2f})")
            last_end = max(last_end, start + dur)
            
        print(f"Total duration: {last_end:.2f}")
        
        for i, chord in enumerate(raw):
            print(f"Chord {i}: {chord['degree']} (Dur: {chord['duration']})")
            
        break
    else:
        print("No short chords, retrying...")
