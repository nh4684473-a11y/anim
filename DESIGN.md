# Hip-Hop Composition Engine - Design Document

## 1. Product Vision
A local, offline, browser-based tool for hip-hop producers to generate dark/trap/boom-bap chords and melodies. It focuses on "controlled generation" rather than pure randomness.

## 2. Architecture (Database-Free Local App)
This application follows a **Local Client-Server Architecture**.

### Components:
1.  **Frontend (UI)**:
    *   **Tech Stack**: React + Vite + Tailwind CSS.
    *   **Role**: Handles user interaction (Key, Scale, Mood selection), visualizes the chords/melody (piano roll or simple blocks), and plays back MIDI preview (using `Web MIDI API` or a soundfont player like `tone.js` or `smplr`).
    *   **State**: Local state (React Context/Zustand). No persistent database required for session; users export MIDI to save.

2.  **Backend (Logic)**:
    *   **Tech Stack**: Python (FastAPI).
    *   **Role**: Performs the "Music Math".
    *   **Why Python?**: Superior libraries for music theory (`music21`, `mido`, `pretty_midi`) and future AI integration (PyTorch/TensorFlow).
    *   **Endpoints**:
        *   `POST /generate/chords`: Inputs (Key, Scale, Mood) -> Returns Chord Progression (MIDI data + JSON metadata).
        *   `POST /generate/melody`: Inputs (Chords, Scale, Complexity) -> Returns Melody (MIDI data + JSON metadata).
        *   `GET /download/midi`: Converts generated data to a .mid file for download.

3.  **Data Storage**:
    *   **Database-Free**: All generation is on-the-fly.
    *   **Presets**: Stored as JSON files in a `presets/` directory.
    *   **User Projects**: Users can "Save" a project, which simply downloads a `.json` file containing their settings and generated notes, which they can re-upload to load the state.

## 3. Chord Generation Algorithm (The "Hip-Hop Brain")

Hip-hop isn't just random chords. It relies on specific **Harmonic Function** and **Mood**.

### Step 1: Scale Derivation
*   **Input**: Root Note (e.g., C), Scale Type (e.g., Minor).
*   **Logic**: Map intervals to chromatic notes.
    *   *Natural Minor*: 0, 2, 3, 5, 7, 8, 10
    *   *Harmonic Minor*: 0, 2, 3, 5, 7, 8, 11 (Crucial for dark trap)
    *   *Phrygian*: 0, 1, 3, 5, 7, 8, 10 (Very dark, aggressive)

### Step 2: Progression Selection (Weighted Probability)
Instead of pure random, we use "Style Templates" or "Transition Tables".

*   **Transition Table Approach (Markov Chain Light)**:
    *   If current is `i` (minor tonic), next is likely: `VI` (50%), `iv` (30%), `v` (10%), `III` (10%).
    *   If current is `V` (dominant), next is likely: `i` (80%), `VI` (20%).

*   **Style Templates (Hardcoded Patterns with Variation)**:
    *   *Dark Trap*: `i - VI - i - VII`
    *   *Sad/Emotional*: `i - VI - III - VII`
    *   *Boom Bap*: `ii - V - i` (Jazz influence)

### Step 3: Voicing & Extensions (The "Juice")
Standard triads (1-3-5) sound basic. Hip-hop needs "color".
*   **Algorithm**:
    1.  Generate basic triad (Root, 3rd, 5th).
    2.  **Extension Logic**:
        *   If style is "Jazz/Lo-Fi" -> Add 7th (Minor 7, Major 7).
        *   If style is "Dark" -> Keep triad, maybe add a flat 9 for tension (if Phrygian).
    3.  **Inversion Logic**:
        *   Keep bass notes (Root) low (C2-C3 range).
        *   Move upper notes to keep "voice leading" smooth (minimize distance between consecutive chords' top notes).

## 4. AI Training Approach (Phase 3)

Transitioning from Rules to AI.

### Dataset Strategy
1.  **Source**: Collect MIDI files of hip-hop beats (freely available datasets, e.g., Lakh MIDI Dataset, or scrape specific genre MIDIs).
2.  **Preprocessing**:
    *   Quantize to 16th notes.
    *   Transpose all to C Minor (key normalization) so the model learns relative patterns, not specific keys.
    *   Separate Chords (sustained notes) and Melody (moving notes).

### Model Architecture
1.  **LSTM (Long Short-Term Memory)**:
    *   Good for sequential data.
    *   Input: Sequence of [Pitch, Duration, Velocity, TimeShift].
    *   Output: Next note probability.
2.  **Transformer (MusicTransformer/GPT-2)**:
    *   Better for long-term structure (e.g., repeating a motif 4 bars later).
    *   Attention mechanism helps understand "call and response".

### Training Loop
1.  **Tokenization**: Convert MIDI events to tokens (e.g., `NOTE_ON_60`, `TIME_DELTA_120`).
2.  **Training**: Predict next token.
3.  **Fine-Tuning**: Train on a specific sub-genre (e.g., "Drill") to create style-specific models.

## 5. Folder Structure
```
project-midi/
├── backend/                # Python FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # Entry point
│   │   ├── models.py       # Pydantic models for API requests
│   │   ├── logic/          # Core music logic
│   │   │   ├── __init__.py
│   │   │   ├── scales.py   # Scale definitions
│   │   │   ├── chords.py   # Chord generation algorithms
│   │   │   └── melody.py   # Melody generation algorithms
│   │   └── utils/
│   │       └── midi_export.py # MIDI file creation
│   ├── requirements.txt
│   └── venv/               # Python virtual environment
├── frontend/               # React + Vite Frontend
│   ├── public/
│   ├── src/
│   │   ├── components/     # UI Components
│   │   │   ├── PianoRoll.jsx
│   │   │   └── Controls.jsx
│   │   ├── api/            # API client
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── presets/                # JSON presets for styles
├── generated/              # Temp folder for generated MIDI files
├── DESIGN.md               # This document
└── README.md
```
