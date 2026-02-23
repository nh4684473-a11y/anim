from typing import List, Dict, Any
import random
import os
from app.logic.chords import generate_progression, generate_track_data
from app.logic.melody import generate_melody
from app.utils.midi_parser import parse_midi_file

TOP_HITS_TEMPLATES = [
    {
        "id": "despacito_latin",
        "name": "Despacito (Latin Pop)",
        "description": "The global smash hit progression (i-VI-III-VII). Perfect for Reggaeton.",
        "key": "B",
        "scale": "minor",
        "progression": [1, 6, 3, 7],
        "tempo": 89,
        "mood": "Reggaeton"
    },
    {
        "id": "shape_of_you",
        "name": "Shape of You (Pop)",
        "description": "Tropical marimba vibes (i-iv-VI-VII). Dancehall rhythm.",
        "key": "C#",
        "scale": "minor",
        "progression": [1, 4, 6, 7],
        "tempo": 96,
        "mood": "Tropical House"
    },
    {
        "id": "alan_walker_faded",
        "name": "Faded (Alan Walker)",
        "description": "Electronic ballad with iconic piano/pluck melody. (vi-IV-I-V)",
        "key": "D#",
        "scale": "minor",
        "progression": [6, 4, 1, 5],
        "tempo": 90,
        "mood": "EDM"
    },
    {
        "id": "blinding_lights",
        "name": "Blinding Lights (80s)",
        "description": "Retro synthwave energy (i-v-VII-IV). Fast and driving.",
        "key": "F",
        "scale": "minor",
        "progression": [1, 5, 7, 4],
        "tempo": 171,
        "mood": "Synthwave"
    },
    {
        "id": "dr_dre_still_dre",
        "name": "Still D.R.E. (Hip Hop)",
        "description": "The iconic West Coast piano riff. Classic 90s vibes.",
        "key": "A",
        "scale": "minor",
        "progression": [1, 6, 1, 6],
        "tempo": 93,
        "mood": "West Coast"
    },
    {
        "id": "linkin_park_numb",
        "name": "Numb (Linkin Park)",
        "description": "Powerful rock anthem (i-VI-III-VII). Emotional and heavy.",
        "key": "F#",
        "scale": "minor",
        "progression": [1, 6, 3, 7],
        "tempo": 110,
        "mood": "Rock"
    },
    {
        "id": "titanic",
        "name": "My Heart Will Go On (Titanic)",
        "description": "The ultimate cinematic love song. Flute and strings. (I-V-vi-IV)",
        "key": "E",
        "scale": "major",
        "progression": [1, 5, 6, 4],
        "tempo": 99,
        "mood": "Cinematic"
    },
    {
        "id": "backstreet_boys_i_want_it_that_way",
        "name": "I Want It That Way (BSB)",
        "description": "The quintessential boy band ballad (vi-IV-I-V). Pure 90s pop.",
        "key": "A",
        "scale": "major",
        "progression": [6, 4, 1, 5],
        "tempo": 99,
        "mood": "Pop"
    },
    {
        "id": "all_of_me",
        "name": "All of Me (Ballad)",
        "description": "Soulful piano ballad (vi-IV-I-V). Emotional and deep.",
        "key": "G#",
        "scale": "major",
        "progression": [6, 4, 1, 5],
        "tempo": 96,
        "mood": "RnB"
    },
    {
        "id": "pop_anthem_1",
        "name": "The 4 Chords of Pop",
        "description": "The most famous progression in history (I-V-vi-IV). Used in thousands of hits.",
        "key": "C",
        "scale": "major",
        "progression": [1, 5, 6, 4],
        "tempo": 120,
        "mood": "Pop"
    },
    {
        "id": "sad_ballad",
        "name": "Emotional Ballad",
        "description": "The sensitive, emotional progression (vi-IV-I-V). Perfect for sad songs.",
        "key": "A",
        "scale": "minor",
        "progression": [1, 6, 3, 7], # relative to minor: i-VI-III-VII
        "tempo": 85,
        "mood": "Cinematic"
    },
    {
        "id": "trap_banger",
        "name": "Dark Trap Banger",
        "description": "Menacing, repetitive minor progression (i-VI-i-VI).",
        "key": "C#",
        "scale": "minor",
        "progression": [1, 6, 1, 6],
        "tempo": 140,
        "mood": "Dark Trap"
    },
    {
        "id": "rnb_soul",
        "name": "Smooth R&B",
        "description": "Classic ii-V-I jazz influence for smooth vibes.",
        "key": "Eb",
        "scale": "major",
        "progression": [2, 5, 1, 6],
        "tempo": 95,
        "mood": "R&B"
    },
    {
        "id": "doo_wop",
        "name": "50s Doo-Wop",
        "description": "The 'Stand By Me' progression (I-vi-IV-V). Retro and nostalgic.",
        "key": "G",
        "scale": "major",
        "progression": [1, 6, 4, 5],
        "tempo": 110,
        "mood": "Pop"
    },
    {
        "id": "canon",
        "name": "Pachelbel's Canon",
        "description": "The classical progression that's in everything (I-V-vi-iii-IV-I-IV-V).",
        "key": "D",
        "scale": "major",
        "progression": [1, 5, 6, 3, 4, 1, 4, 5],
        "tempo": 100,
        "mood": "Cinematic"
    },
    {
        "id": "epic_anime",
        "name": "Royal Road (Anime)",
        "description": "The 'Royal Road' progression (IV-V-iii-vi). Huge in J-Pop and Anime.",
        "key": "F",
        "scale": "major",
        "progression": [4, 5, 3, 6],
        "tempo": 160,
        "mood": "Future Bass"
    },
    {
        "id": "blues_12_bar",
        "name": "12-Bar Blues",
        "description": "The foundation of Rock and Jazz (I-I-I-I-IV-IV-I-I-V-IV-I-V).",
        "key": "E",
        "scale": "major", # Dom7s usually, but major scale base
        "progression": [1, 1, 1, 1, 4, 4, 1, 1, 5, 4, 1, 5],
        "tempo": 110,
        "mood": "Jazz"
    },
    {
        "id": "chainsmokers",
        "name": "EDM Hype",
        "description": "Uplifting, festival-ready progression (vi-IV-I-V).",
        "key": "F#",
        "scale": "major",
        "progression": [6, 4, 1, 5],
        "tempo": 128,
        "mood": "Future Bass"
    },
    {
        "id": "faded_alan_walker",
        "name": "Faded (Alan Walker)",
        "description": "The iconic electro-ballad progression (i-VI-III-VII).",
        "key": "F#",
        "scale": "minor",
        "progression": [1, 6, 3, 7],
        "tempo": 90,
        "mood": "Walker Ballad"
    },
    {
        "id": "flamenco",
        "name": "Andalusian Cadence",
        "description": "Spanish/Flamenco feel (i-VII-VI-V).",
        "key": "A",
        "scale": "minor",
        "progression": [1, 7, 6, 5],
        "tempo": 130,
        "mood": "Lo-Fi"
    }
]

def get_top_hits_templates() -> List[Dict[str, Any]]:
    """Returns the list of available Top 100 templates."""
    return TOP_HITS_TEMPLATES

# --- HARDCODED PATTERNS FOR EXACT REPLICAS ---
# This allows us to serve the actual melodies/basslines for famous songs
# instead of generating them randomly.

def get_despacito_pattern():
    # Key: B Minor
    # Chords: Bm - G - D - A (i - VI - III - VII)
    # Tempo: 89 BPM
    # Length: 4 bars
    
    # 1. Chords (Arpeggiated / Plucked Pattern)
    # Instead of block chords, let's do a rhythmic strum/pluck
    # Bm: B3, D4, F#4
    # Pattern: 16th notes: Root - Chord - Root - Chord...
    
    chords = []
    
    def add_arpeggio(start_time, notes, velocity=85):
        # notes is [root, third, fifth]
        # Pattern: Root (0.0), Third+Fifth (0.25), Root (0.5), Third+Fifth (0.75)...
        # But let's do something more "Guitar-like": Root, Fifth, Third, Fifth
        root, third, fifth = notes
        
        # 16th note duration = 0.25 beats
        dur = 0.25
        
        # Beat 1
        chords.append({"note": root, "time": start_time + 0.0, "duration": dur, "velocity": velocity})
        chords.append({"note": fifth, "time": start_time + 0.25, "duration": dur, "velocity": velocity - 5})
        chords.append({"note": third, "time": start_time + 0.5, "duration": dur, "velocity": velocity - 5})
        chords.append({"note": fifth, "time": start_time + 0.75, "duration": dur, "velocity": velocity - 5})
        
        # Beat 2
        chords.append({"note": root, "time": start_time + 1.0, "duration": dur, "velocity": velocity})
        chords.append({"note": fifth, "time": start_time + 1.25, "duration": dur, "velocity": velocity - 5})
        chords.append({"note": third, "time": start_time + 1.5, "duration": dur, "velocity": velocity - 5})
        chords.append({"note": fifth, "time": start_time + 1.75, "duration": dur, "velocity": velocity - 5})
        
        # Beat 3
        chords.append({"note": root, "time": start_time + 2.0, "duration": dur, "velocity": velocity})
        chords.append({"note": fifth, "time": start_time + 2.25, "duration": dur, "velocity": velocity - 5})
        chords.append({"note": third, "time": start_time + 2.5, "duration": dur, "velocity": velocity - 5})
        chords.append({"note": fifth, "time": start_time + 2.75, "duration": dur, "velocity": velocity - 5})
        
        # Beat 4
        chords.append({"note": root, "time": start_time + 3.0, "duration": dur, "velocity": velocity})
        chords.append({"note": fifth, "time": start_time + 3.25, "duration": dur, "velocity": velocity - 5})
        chords.append({"note": third, "time": start_time + 3.5, "duration": dur, "velocity": velocity - 5})
        chords.append({"note": fifth, "time": start_time + 3.75, "duration": dur, "velocity": velocity - 5})

    # Bar 1: Bm (B3, D4, F#4) -> (47, 50, 54)
    add_arpeggio(0.0, [47, 50, 54])
    
    # Bar 2: G (G3, B3, D4) -> (43, 47, 50)
    add_arpeggio(4.0, [43, 47, 50])
    
    # Bar 3: D (D3, F#3, A3) -> (50, 54, 57) - wait D3 is 38?
    # Let's use D4 range: D4 (50), F#4 (54), A4 (57)
    add_arpeggio(8.0, [50, 54, 57])
    
    # Bar 4: A (A3, C#4, E4) -> (45, 49, 52)
    add_arpeggio(12.0, [45, 49, 52])

    # 2. Bass (Reggaeton Rhythm: Dotted 8th, 16th, 8th tie... actually simpler: on 1, 1.75, 2.5, 3.5??)
    # Standard Reggaeton Beat: Kick on 1, 2, 3, 4. Snare on 1.75, 2.5, 3.75, 4.5.
    # Bass usually follows Kick (1, 2, 3, 4) OR syncopates.
    # Despacito Bass: Dotted Q, Eighth (Tie), Q, Q? No, it's simpler.
    # Let's do the "Tresillo" feel: 1, 1.75, 2.5 (3+3+2 16ths)
    bass = []
    roots = [35, 31, 38, 33] # B1, G1, D2, A1
    
    for i, root in enumerate(roots):
        offset = i * 4.0
        
        # 3-3-2 pattern in 16ths:
        # Note 1: 0.0 (Length 0.75)
        # Note 2: 0.75 (Length 0.75)
        # Note 3: 1.5 (Length 0.5)
        # This loops every 2 beats (half bar)
        
        # Half Bar 1
        bass.append({"note": root, "time": offset + 0.0, "duration": 0.7, "velocity": 100})
        bass.append({"note": root, "time": offset + 0.75, "duration": 0.7, "velocity": 90})
        bass.append({"note": root, "time": offset + 1.5, "duration": 0.5, "velocity": 95})
        
        # Half Bar 2
        bass.append({"note": root, "time": offset + 2.0, "duration": 0.7, "velocity": 100})
        bass.append({"note": root, "time": offset + 2.75, "duration": 0.7, "velocity": 90})
        bass.append({"note": root, "time": offset + 3.5, "duration": 0.5, "velocity": 95})

    # 3. Melody (The Hook)
    # Bm: F# F# F# F# F# B...
    # Main hook: "Des-pa-ci-to"
    # Notes: D C# B F# ... F# F# F# F# F# A B
    # Let's try to approximate the Chorus start.
    melody = []
    
    # Bar 1 (Bm): "Des-pa-ci-to"
    # D5, C#5, B4, F#4
    melody.append({"note": 74, "time": 0.0, "duration": 1.0, "velocity": 95}) # Des (D5) - Long
    melody.append({"note": 73, "time": 1.0, "duration": 0.5, "velocity": 90}) # pa (C#5)
    melody.append({"note": 71, "time": 1.5, "duration": 0.5, "velocity": 90}) # ci (B4)
    melody.append({"note": 66, "time": 2.0, "duration": 1.5, "velocity": 85}) # to (F#4) - Tie
    
    # Rapid part: "Quiero respirar tu cuello despacito" (F# F# F# F# F# A B)
    # Starts around beat 3.5 or next bar?
    # Let's simplify: F# F# F# A B (Pickup to next bar)
    melody.append({"note": 66, "time": 3.5, "duration": 0.25, "velocity": 80})
    melody.append({"note": 66, "time": 3.75, "duration": 0.25, "velocity": 80})

    # Bar 2 (G): "Deja que te diga cosas al oído"
    # G G G G G B C#?
    melody.append({"note": 66, "time": 4.0, "duration": 0.25, "velocity": 90}) # F#
    melody.append({"note": 66, "time": 4.25, "duration": 0.25, "velocity": 90})
    melody.append({"note": 66, "time": 4.5, "duration": 0.5, "velocity": 90})
    melody.append({"note": 71, "time": 5.0, "duration": 0.5, "velocity": 95}) # B
    melody.append({"note": 73, "time": 5.5, "duration": 1.0, "velocity": 95}) # C#
    
    # Bar 3 (D): "Para que te acuerdes si no estás conmigo"
    # D D D D D F# A
    melody.append({"note": 74, "time": 8.0, "duration": 0.25, "velocity": 90}) # D
    melody.append({"note": 74, "time": 8.25, "duration": 0.25, "velocity": 90})
    melody.append({"note": 74, "time": 8.5, "duration": 0.5, "velocity": 90})
    melody.append({"note": 78, "time": 9.0, "duration": 0.5, "velocity": 95}) # F#
    melody.append({"note": 81, "time": 9.5, "duration": 1.0, "velocity": 95}) # A
    
    # Bar 4 (A): (Instrumental filler or vocal run)
    # A G# F# E
    melody.append({"note": 81, "time": 12.0, "duration": 0.5, "velocity": 90}) # A
    melody.append({"note": 80, "time": 12.5, "duration": 0.5, "velocity": 90}) # G#
    melody.append({"note": 78, "time": 13.0, "duration": 0.5, "velocity": 90}) # F#
    melody.append({"note": 76, "time": 13.5, "duration": 2.0, "velocity": 85}) # E

    return {
        "key": "B",
        "scale": "minor",
        "mood": "Reggaeton",
        "tempo": 89,
        "chords": chords,
        "bass": bass,
        "melody": melody,
        "progression": [1, 6, 3, 7],
        "instruments": {
            "chords": "guitar",
            "melody": "guitar",
            "bass": "bass"
        }
    }

def get_shape_of_you_pattern():
    # Key: C# Minor
    # Chords: C#m - F#m - A - B (i - iv - VI - VII)
    # Tempo: 96 BPM
    # The riff is 2 bars long, repeats.
    # Riff: C# E C# E C# E C# B(low)
    
    chords = []
    bass = []
    melody = []
    
    # 2 Bar Loop, repeated twice = 4 bars
    for loop in range(2):
        bar_offset = loop * 8.0 # 2 bars = 8 beats
        
        # Chords (Plucky, short) - C#m, F#m, A, B
        # Beat 0: C#m
        chords.append({"note": 61, "time": bar_offset + 0.0, "duration": 0.5, "velocity": 80}) # C#4
        chords.append({"note": 64, "time": bar_offset + 0.0, "duration": 0.5, "velocity": 80}) # E4
        chords.append({"note": 68, "time": bar_offset + 0.0, "duration": 0.5, "velocity": 80}) # G#4
        
        # Beat 2: F#m
        chords.append({"note": 66, "time": bar_offset + 2.0, "duration": 0.5, "velocity": 80}) # F#4
        chords.append({"note": 69, "time": bar_offset + 2.0, "duration": 0.5, "velocity": 80}) # A4
        chords.append({"note": 73, "time": bar_offset + 2.0, "duration": 0.5, "velocity": 80}) # C#5
        
        # Beat 4: A
        chords.append({"note": 69, "time": bar_offset + 4.0, "duration": 0.5, "velocity": 80}) # A4
        chords.append({"note": 73, "time": bar_offset + 4.0, "duration": 0.5, "velocity": 80}) # C#5
        chords.append({"note": 76, "time": bar_offset + 4.0, "duration": 0.5, "velocity": 80}) # E5
        
        # Beat 6: B
        chords.append({"note": 71, "time": bar_offset + 6.0, "duration": 0.5, "velocity": 80}) # B4
        chords.append({"note": 75, "time": bar_offset + 6.0, "duration": 0.5, "velocity": 80}) # D#5
        chords.append({"note": 78, "time": bar_offset + 6.0, "duration": 0.5, "velocity": 80}) # F#5

        # Bass (Simple, follows root)
        # C# (0), F# (2), A (4), B (6)
        bass.append({"note": 37, "time": bar_offset + 0.0, "duration": 1.5, "velocity": 90}) # C#2
        bass.append({"note": 42, "time": bar_offset + 2.0, "duration": 1.5, "velocity": 90}) # F#2
        bass.append({"note": 45, "time": bar_offset + 4.0, "duration": 1.5, "velocity": 90}) # A2
        bass.append({"note": 47, "time": bar_offset + 6.0, "duration": 1.5, "velocity": 90}) # B2

        # Melody (The Marimba Riff)
        # C#4 (61), E4 (64), B3 (59)
        # Pattern: C# E C# E C# E C# B(low)
        # Rhythm: 
        # 0.0: C#
        # 0.5: E
        # 0.75: C#
        # 1.25: E
        # 1.5: C#
        # 2.0: E
        # 2.5: C#
        # 2.75: B
        
        # Notes
        n_c = 61
        n_e = 64
        n_b = 59
        
        # Bar 1 (C#m / F#m)
        melody.append({"note": n_c, "time": bar_offset + 0.0, "duration": 0.25, "velocity": 95})
        melody.append({"note": n_e, "time": bar_offset + 0.5, "duration": 0.25, "velocity": 90})
        melody.append({"note": n_c, "time": bar_offset + 0.75, "duration": 0.25, "velocity": 95})
        melody.append({"note": n_e, "time": bar_offset + 1.25, "duration": 0.25, "velocity": 90})
        melody.append({"note": n_c, "time": bar_offset + 1.5, "duration": 0.25, "velocity": 95})
        
        melody.append({"note": n_e, "time": bar_offset + 2.0, "duration": 0.25, "velocity": 90})
        melody.append({"note": n_c, "time": bar_offset + 2.5, "duration": 0.25, "velocity": 95})
        melody.append({"note": n_b, "time": bar_offset + 2.75, "duration": 0.25, "velocity": 85})

        # Bar 2 (A / B) - Same riff usually repeats or varies slightly
        # "Oh I oh I oh I" follows same rhythm
        melody.append({"note": n_c, "time": bar_offset + 4.0, "duration": 0.25, "velocity": 95})
        melody.append({"note": n_e, "time": bar_offset + 4.5, "duration": 0.25, "velocity": 90})
        melody.append({"note": n_c, "time": bar_offset + 4.75, "duration": 0.25, "velocity": 95})
        melody.append({"note": n_e, "time": bar_offset + 5.25, "duration": 0.25, "velocity": 90})
        melody.append({"note": n_c, "time": bar_offset + 5.5, "duration": 0.25, "velocity": 95})
        
        melody.append({"note": n_e, "time": bar_offset + 6.0, "duration": 0.25, "velocity": 90})
        melody.append({"note": n_c, "time": bar_offset + 6.5, "duration": 0.25, "velocity": 95})
        melody.append({"note": n_b, "time": bar_offset + 6.75, "duration": 0.25, "velocity": 85})

    return {
        "key": "C#",
        "scale": "minor",
        "mood": "Tropical House",
        "tempo": 96,
        "chords": chords,
        "bass": bass,
        "melody": melody,
        "progression": [1, 4, 6, 7],
        "instruments": {
            "chords": "piano",
            "melody": "piano",
            "bass": "bass"
        }
    }

def generate_top_hit_track(template_id: str) -> Dict[str, Any]:
    """Generates a full track data dictionary based on a template ID."""
    
    # 0. Check for Alan Walker (Multi-file)
    if template_id == "alan_walker_faded":
        base_path = os.path.join(os.getcwd(), "app", "data", "midi")
        chords_path = os.path.join(base_path, "alan_walker_faded_chords.mid")
        melody_path = os.path.join(base_path, "alan_walker_faded_melody.mid")
        pluck_path = os.path.join(base_path, "alan_walker_faded_pluck.mid")
        
        if os.path.exists(chords_path) or os.path.exists(melody_path):
            print("Found Alan Walker MIDI files, merging...")
            combined_data = {
                "tempo": 90,
                "key": "D#",
                "scale": "minor",
                "mood": "EDM",
                "chords": [],
                "melody": [],
                "bass": [],
                "instruments": {"chords": "piano", "melody": "piano", "bass": "bass"}
            }
            
            # Helper to merge all notes from a parsed file
            def get_all_notes(parsed):
                if not parsed: return []
                return parsed.get("chords", []) + parsed.get("melody", []) + parsed.get("bass", [])

            # Load Chords
            if os.path.exists(chords_path):
                c_data = parse_midi_file(chords_path)
                if c_data:
                    combined_data["chords"].extend(get_all_notes(c_data))
                    if c_data.get("tempo") and c_data["tempo"] != 120: combined_data["tempo"] = c_data["tempo"]

            # Load Melody
            if os.path.exists(melody_path):
                m_data = parse_midi_file(melody_path)
                if m_data:
                    combined_data["melody"].extend(get_all_notes(m_data))
            
            # Load Pluck (add to chords for texture)
            if os.path.exists(pluck_path):
                p_data = parse_midi_file(pluck_path)
                if p_data:
                    combined_data["chords"].extend(get_all_notes(p_data))
            
            return combined_data

    # 1. Check for MIDI File Override
    # Look for a file named {template_id}.mid in app/data/midi/
    midi_filename = f"{template_id}.mid"
    base_dir = os.path.dirname(os.path.dirname(__file__)) # app/
    midi_path = os.path.join(base_dir, "data", "midi", midi_filename)
    
    if os.path.exists(midi_path):
        print(f"Found MIDI file override: {midi_path}")
        midi_data = parse_midi_file(midi_path)
        if midi_data:
            # Optional: Override instruments/metadata for specific templates
            if template_id == "despacito_latin":
                midi_data["instruments"] = {"chords": "guitar", "melody": "guitar", "bass": "bass"}
                midi_data["mood"] = "Reggaeton"
            elif template_id == "shape_of_you":
                midi_data["instruments"] = {"chords": "piano", "melody": "piano", "bass": "bass"}
                midi_data["mood"] = "Tropical House"
            elif template_id == "blinding_lights":
                midi_data["instruments"] = {"chords": "synth", "melody": "synth", "bass": "synth"}
                midi_data["mood"] = "Synthwave"
            elif template_id == "dr_dre_still_dre":
                midi_data["instruments"] = {"chords": "piano", "melody": "piano", "bass": "bass"}
                midi_data["mood"] = "West Coast"
            elif template_id == "linkin_park_numb":
                midi_data["instruments"] = {"chords": "synth", "melody": "synth", "bass": "bass"}
                midi_data["mood"] = "Rock"
            elif template_id == "titanic":
                midi_data["instruments"] = {"chords": "synth", "melody": "piano", "bass": "bass"}
                midi_data["mood"] = "Cinematic"
            elif template_id == "backstreet_boys_i_want_it_that_way":
                midi_data["instruments"] = {"chords": "guitar", "melody": "piano", "bass": "bass"}
                midi_data["mood"] = "Pop"
            return midi_data
    
    # 1. Check for Exact Replicas first
    if template_id == "despacito_latin":
        return get_despacito_pattern()
    elif template_id == "shape_of_you":
        return get_shape_of_you_pattern()
        
    template = next((t for t in TOP_HITS_TEMPLATES if t["id"] == template_id), None)
    if not template:
        raise ValueError(f"Template {template_id} not found")

    # Use generate_track_data to ensure full compatibility with playback logic (including note events)
    track_data = generate_track_data(
        key=template["key"],
        scale=template["scale"],
        mood=template["mood"],
        length=len(template["progression"]), # Match template length
        complexity=0.5,
        melody=True,
        tempo=template["tempo"],
        pattern_override=template["progression"]
    )
    
    return track_data
