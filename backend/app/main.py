
from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
import os
import mido
import random

# Add the parent directory to sys.path to allow imports from 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.logic.chords import generate_progression, generate_track_data
from app.logic.top_hits import get_top_hits_templates, generate_top_hit_track
from app.utils.midi_export import create_midi_file

app = FastAPI(title="Universal MIDI Generator")

app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"Validation error: {exc.errors()}")
    print(f"Body: {await request.body()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": str(await request.body())},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChordRequest(BaseModel):
    key: str = "Random"
    scale: str = "Random"
    mood: str = "Random"
    length: int = 4
    complexity: float = 0.5
    melody: bool = True
    tempo: int = 140
    source: str = "auto" # auto, generate, library

class NoteEvent(BaseModel):
    note: int
    time: float
    duration: float
    velocity: int = 80

class ChordData(BaseModel):
    notes: List[int]
    duration: float = 4.0
    velocity: int = 80
    name: Optional[str] = None

class MidiRequest(BaseModel):
    progression: Optional[List[ChordData]] = None
    chords: Optional[List[NoteEvent]] = None
    melody: Optional[List[NoteEvent]] = None
    tempo: int = 120
    mood: str = "neutral"

def midi_to_json(file_path):
    """Parses a MIDI file into the JSON format expected by the frontend."""
    mid = mido.MidiFile(file_path)
    tpb = mid.ticks_per_beat
    
    output = {"chords": [], "melody": [], "bass": [], "tempo": 120}
    
    # Extract Tempo
    for track in mid.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                output["tempo"] = int(mido.tempo2bpm(msg.tempo))
                break
    
    for track in mid.tracks:
        track_name = "unknown"
        # Find track name
        for msg in track:
            if msg.type == 'track_name':
                track_name = msg.name.lower()
                break
        
        # Parse notes
        abs_ticks = 0
        active_notes = {} # note -> start_tick
        events = []
        
        for msg in track:
            abs_ticks += msg.time
            
            if msg.type == 'note_on' and msg.velocity > 0:
                active_notes[msg.note] = (abs_ticks, msg.velocity)
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                if msg.note in active_notes:
                    start_tick, vel = active_notes.pop(msg.note)
                    duration_ticks = abs_ticks - start_tick
                    
                    events.append({
                        "note": msg.note,
                        "time": start_tick / tpb,
                        "duration": duration_ticks / tpb,
                        "velocity": vel
                    })
        
        if "chord" in track_name:
            output["chords"] = events
        elif "melody" in track_name:
            output["melody"] = events
        elif "bass" in track_name:
            output["bass"] = events
        else:
            # Fallback logic for unnamed tracks
            if len(events) > 0:
                # Heuristic Analysis
                avg_note = sum(e["note"] for e in events) / len(events)
                
                # Check Polyphony (max simultaneous notes)
                max_polyphony = 1
                # Sort by time to be safe
                sorted_events = sorted(events, key=lambda x: x["time"])
                
                for i in range(len(sorted_events)):
                    current_poly = 1
                    evt = sorted_events[i]
                    evt_end = evt["time"] + evt["duration"]
                    
                    # Look ahead for overlaps
                    for j in range(i + 1, len(sorted_events)):
                        next_evt = sorted_events[j]
                        if next_evt["time"] < evt_end:
                            current_poly += 1
                        else:
                            break # Sorted by time, so we can stop
                    
                    if current_poly > max_polyphony:
                        max_polyphony = current_poly

                # Assign based on characteristics
                # 1. Chords: Polyphonic OR named "chords" (handled above)
                if not output["chords"] and max_polyphony > 1:
                     output["chords"] = events
                
                # 2. Bass: Monophonic AND Low Pitch (Avg < 55 / G3)
                elif not output["bass"] and max_polyphony == 1 and avg_note <= 55:
                      output["bass"] = events
                      
                # 3. Melody: Monophonic AND Higher Pitch
                elif not output["melody"] and max_polyphony == 1 and avg_note > 55:
                     output["melody"] = events
                     
                # 4. Fallback: If still unassigned, put in chords if empty, else melody
                elif not output["chords"]:
                    output["chords"] = events
                elif not output["melody"]:
                    output["melody"] = events
                     
    return output

@app.get("/api/top-hits")
def get_top_hits():
    return get_top_hits_templates()

class TopHitRequest(BaseModel):
    template_id: str

@app.post("/generate/top-hit")
def generate_top_hit(request: TopHitRequest):
    data = generate_top_hit_track(request.template_id)
    # Return in standard format
    return {
        "chords": data.get("chords", []),
        "melody": data.get("melody", []),
        "bass": data.get("bass", []),
        "key": data["key"],
        "scale": data["scale"],
        "tempo": data["tempo"],
        "mood": data["mood"],
        "instruments": data.get("instruments", {})
    }

@app.get("/api/python")
def hello_python():
    return {"message": "Hello from Python!"}

@app.get("/")
def read_root():
    return {"message": "Universal MIDI Generator API is running"}

@app.post("/generate/chords")
def generate_chords(request: ChordRequest):
    print("Generating new track...")
    
    # Generate track data
    result = generate_track_data(
        key=request.key if request.key != "Random" else None,
        scale=request.scale if request.scale != "Random" else None,
        mood=request.mood if request.mood != "Random" else None,
        length=request.length,
        complexity=request.complexity,
        melody=request.melody,
        tempo=request.tempo
    )
    result["source"] = "Generated"
    return result

def remove_file(path: str):
    try:
        os.unlink(path)
    except Exception as e:
        print(f"Error removing file {path}: {e}")

@app.post("/download/midi")
def download_midi(request: MidiRequest, background_tasks: BackgroundTasks):
    print(f"Received MIDI download request. Chords events: {len(request.chords) if request.chords else 0}, Melody events: {len(request.melody) if request.melody else 0}")
    
    progression_data = {}
    
    if request.chords or request.melody:
        # New format
        if request.chords:
            progression_data["chords"] = [event.dict() for event in request.chords]
        if request.melody:
            progression_data["melody"] = [event.dict() for event in request.melody]
    elif request.progression:
        # Legacy format
        progression_data = [chord.dict() for chord in request.progression]
    else:
        # Empty?
        progression_data = []
        
    # Generate MIDI file
    file_path = create_midi_file(progression_data, request.tempo, request.mood)
    
    # Schedule file removal after response is sent
    background_tasks.add_task(remove_file, file_path)
    
    return FileResponse(
        path=file_path,
        filename="track.mid",
        media_type="audio/midi"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
