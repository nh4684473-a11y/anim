
import mido
from mido import MidiFile, MidiTrack, Message, MetaMessage
import tempfile
import os
import random

def humanize_track(events, mood="neutral", is_chords=False):
    """
    Applies humanization (velocity, timing, strumming) to a list of MIDI events.
    events: List of dicts with 'note', 'time', 'duration', 'velocity'
    """
    humanized_events = []
    
    # Humanization Parameters based on mood
    velocity_variance = 5
    timing_variance = 0.02 # in beats
    strum_delay = 0.0 # in beats
    
    if "lo_fi" in mood or "neo_soul" in mood or "jazz" in mood:
        velocity_variance = 12
        timing_variance = 0.04
        if is_chords:
            strum_delay = 0.03 # Slight roll
    elif "drill" in mood or "trap" in mood:
        velocity_variance = 8 # Hi-hats need dynamics
        timing_variance = 0.01 # Tight but not robotic
    elif "walker" in mood.lower() or "faded" in mood.lower():
        velocity_variance = 10 # Emotional dynamics
        timing_variance = 0.015 # Slight humanization
        if is_chords:
            strum_delay = 0.005 # Very tight, almost imperceptible strum
    elif "classical" in mood or "cinematic" in mood:
        velocity_variance = 15
        timing_variance = 0.05
    
    # Group events by start time for strumming (only for chords)
    events_by_time = {}
    if is_chords:
        for event in events:
            t = event["time"]
            if t not in events_by_time:
                events_by_time[t] = []
            events_by_time[t].append(event)
    
    # Process
    if is_chords:
        for t in sorted(events_by_time.keys()):
            chord_notes = events_by_time[t]
            # Sort by pitch (low to high) for strumming
            chord_notes.sort(key=lambda x: x["note"])
            
            # Randomize strum direction (mostly down, sometimes up)
            if random.random() < 0.2:
                chord_notes.reverse()
            
            current_strum_offset = 0.0
            
            for event in chord_notes:
                # Copy event
                new_event = event.copy()
                
                # Apply Timing Offset (Gaussian)
                offset = random.gauss(0, timing_variance)
                
                # Apply Strumming
                new_event["time"] += current_strum_offset + offset
                current_strum_offset += strum_delay + random.uniform(0, 0.01)
                
                # Apply Velocity Randomization
                vel_change = int(random.gauss(0, velocity_variance))
                new_event["velocity"] = max(1, min(127, new_event["velocity"] + vel_change))
                
                humanized_events.append(new_event)
    else:
        # Melody Processing
        for event in events:
            new_event = event.copy()
            
            # Apply Timing Offset
            offset = random.gauss(0, timing_variance)
            new_event["time"] += offset
            
            # Apply Velocity Randomization
            vel_change = int(random.gauss(0, velocity_variance))
            
            # Accent strong beats (Assuming 4/4)
            if round(event["time"]) % 1.0 < 0.1: # Downbeat
                vel_change += 10
            
            new_event["velocity"] = max(1, min(127, new_event["velocity"] + vel_change))
            humanized_events.append(new_event)
            
    return humanized_events

def create_midi_file(progression_data, tempo: int = 120, mood: str = "neutral", instruments: dict = None):
    """
    Creates a MIDI file from the progression data.
    progression_data: 
        - list of chords (legacy)
        - dict with keys "chords" and "melody" (new)
    Returns the path to the temporary file.
    """
    mid = MidiFile()
    
    # Default Instruments (General MIDI Program Numbers)
    # 0: Acoustic Grand Piano
    # 33: Electric Bass (finger)
    # 26: Electric Guitar (jazz)
    if instruments is None:
        instruments = {"chords": 0, "melody": 0, "bass": 33}
    tracks_data = {}
    
    if isinstance(progression_data, list):
        # Legacy format: List of block chords
        tracks_data["chords"] = progression_data
    elif isinstance(progression_data, dict):
        # New format: Dict with "chords" and "melody" lists of events
        if "chords" in progression_data:
            tracks_data["chords"] = progression_data["chords"]
        if "melody" in progression_data:
            tracks_data["melody"] = progression_data["melody"]
            
    # Ticks per beat (default is 480)
    ticks_per_beat = mid.ticks_per_beat
            
    for i, (track_name, track_events) in enumerate(tracks_data.items()):
        track = MidiTrack()
        mid.tracks.append(track)
        
        # Determine Channel
        channel = 0
        if track_name == "melody":
            channel = 1
        elif track_name == "chords":
            channel = 0
        else:
            channel = i % 16
        
        # Add Track Name
        track.append(MetaMessage('track_name', name=track_name.capitalize()))
        
        # Set Tempo
        us_per_beat = int(60_000_000 / tempo)
        track.append(MetaMessage('set_tempo', tempo=us_per_beat))
        
        # Set Instrument (Program Change)
        program_number = instruments.get(track_name, 0)
        # Ensure valid MIDI program (0-127)
        program_number = max(0, min(127, int(program_number)))
        
        track.append(Message('program_change', program=program_number, time=0, channel=channel))
        
        # Convert input data to MIDI events
        midi_events = []
        
        # Normalize to Event Stream if Block Chords
        is_block_chords = False
        if len(track_events) > 0 and "notes" in track_events[0]:
            is_block_chords = True
            
        processed_events = []
        
        if is_block_chords:
            current_beat_time = 0.0
            for chord in track_events:
                duration = chord.get("duration", 4.0)
                velocity = chord.get("velocity", 80)
                
                for note in chord["notes"]:
                    processed_events.append({
                        "note": note,
                        "time": current_beat_time,
                        "duration": duration,
                        "velocity": velocity
                    })
                current_beat_time += duration
        else:
            # Already event stream
            processed_events = track_events

        # Apply Humanization
        processed_events = humanize_track(processed_events, mood=mood, is_chords=(track_name == "chords"))

        # Convert to Mido Events
        for event in processed_events:
            start_ticks = int(event["time"] * ticks_per_beat)
            duration_ticks = int(event["duration"] * ticks_per_beat)
            
            midi_events.append({
                "type": "note_on", 
                "note": event["note"], 
                "velocity": event["velocity"], 
                "time": start_ticks
            })
            midi_events.append({
                "type": "note_off", 
                "note": event["note"], 
                "velocity": 0, 
                "time": start_ticks + duration_ticks
            })

        # --- Advanced MIDI CC Automation (Sustain, Expression) ---
        if track_name == "chords":
            # 1. Sustain Pedal (CC 64) for Piano/Keys genres
            if any(m in mood.lower() for m in ["lo_fi", "neo_soul", "jazz", "cinematic", "pop", "rnb", "ballad", "walker", "faded"]):
                # Group events by start time to avoid redundant pedal messages
                unique_starts = sorted(list(set(e["time"] for e in midi_events if e["type"] == "note_on")))
                
                for t_start in unique_starts:
                    # Legato Pedaling: Quick Up-Down transition at each chord change
                    # Pedal Up just before the chord
                    up_time = max(0, int(t_start - 5)) # 5 ticks before
                    midi_events.append({
                        "type": "control_change",
                        "control": 64, # Sustain Pedal
                        "value": 0,    # Off
                        "time": up_time
                    })
                    
                    # Pedal Down exactly at the chord (or slightly after for realism? No, simulataneous is fine for MIDI)
                    midi_events.append({
                        "type": "control_change",
                        "control": 64,
                        "value": 127,  # On
                        "time": t_start
                    })
            
            # 2. Expression (CC 11) for Cinematic Swells
            if "cinematic" in mood or "ambient" in mood:
                # Create a swell for each chord
                # Find chord durations
                # This is tricky with individual note events. 
                # Simplified: Swell volume over the whole track or per bar?
                # Let's do per bar swells (every 4 beats)
                total_duration = max(e["time"] for e in midi_events)
                bar_ticks = ticks_per_beat * 4
                
                for t in range(0, total_duration, bar_ticks):
                    # Swell Up
                    for i in range(0, bar_ticks // 2, 100): # Resolution of 100 ticks
                        val = 50 + int(77 * (i / (bar_ticks // 2))) # 50 to 127
                        midi_events.append({
                            "type": "control_change",
                            "control": 11,
                            "value": val,
                            "time": t + i
                        })
                    # Swell Down
                    for i in range(bar_ticks // 2, bar_ticks, 100):
                        val = 127 - int(77 * ((i - bar_ticks//2) / (bar_ticks // 2))) # 127 to 50
                        midi_events.append({
                            "type": "control_change",
                            "control": 11,
                            "value": val,
                            "time": t + i
                        })

        # Sort and Write
        midi_events.sort(key=lambda x: x["time"])
        
        last_event_time = 0
        for event in midi_events:
            delta = event["time"] - last_event_time
            if delta < 0: delta = 0
            
            # Write Message
            if event["type"] == "note_on":
                 note = max(0, min(127, int(event["note"])))
                 velocity = max(0, min(127, int(event["velocity"])))
                 track.append(Message('note_on', note=note, velocity=velocity, time=delta, channel=channel))
                 
            elif event["type"] == "note_off":
                 note = max(0, min(127, int(event["note"])))
                 track.append(Message('note_off', note=note, velocity=0, time=delta, channel=channel))
                 
            elif event["type"] == "control_change":
                 control = max(0, min(127, int(event["control"])))
                 value = max(0, min(127, int(event["value"])))
                 track.append(Message('control_change', control=control, value=value, time=delta, channel=channel))
            
            last_event_time = event["time"]

    # Create a temp file
    fd, path = tempfile.mkstemp(suffix=".mid")
    os.close(fd)
    mid.save(path)
        
    return path
