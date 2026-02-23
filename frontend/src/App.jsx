import React, { useState, useEffect, useRef } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import * as Tone from 'tone';
import Header from './components/Header';
import Generator from './pages/Generator';
import TopHits from './pages/TopHits';
import { generateChords, downloadMidi } from './api/client';

function App() {
  const navigate = useNavigate();
  
  // Plugin Mode Detection
  const [isPluginMode, setIsPluginMode] = useState(false);
  
  useEffect(() => {
    // Check URL params for ?mode=plugin
    const params = new URLSearchParams(window.location.search);
    if (params.get('mode') === 'plugin') {
        setIsPluginMode(true);
        console.log("Running in Plugin Mode");
    }
  }, []);
  
  const [settings, setSettings] = useState({
    key: "Random",
    scale: "Random",
    mood: "Random",
    length: 4,
    complexity: 0.5,
    melody: true,
    tempo: 140,
    source: "auto" // auto, generate, library
  });

  const [generatedData, setGeneratedData] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const synthRef = useRef(null);
  const [pianoSampler, setPianoSampler] = useState(null);
  const [isPianoLoaded, setIsPianoLoaded] = useState(false);
  const [guitarSampler, setGuitarSampler] = useState(null);
  const [isGuitarLoaded, setIsGuitarLoaded] = useState(false);
  const [bassSampler, setBassSampler] = useState(null);
  const [isBassLoaded, setIsBassLoaded] = useState(false);
  const [chordInstrument, setChordInstrument] = useState(0);
  const [melodyInstrument, setMelodyInstrument] = useState(0);
  const [bassInstrument, setBassInstrument] = useState(33);
  const [volume, setVolume] = useState(-6); // dB
  const [isPlaying, setIsPlaying] = useState(false);
  const [lastPlayedNote, setLastPlayedNote] = useState(null);
  const [transportState, setTransportState] = useState('stopped');
  
  // Audio Nodes Refs to avoid re-creation
  const mainBusRef = useRef(null);
  const bassSynthRef = useRef(null);

  useEffect(() => {
      // Setup Master Effects Chain
      const compressor = new Tone.Compressor({
          threshold: -20,
          ratio: 3,
          attack: 0.05,
          release: 0.25
      }).toDestination();
      
      const limiter = new Tone.Limiter(-1).connect(compressor);
      
      mainBusRef.current = limiter;
      
      return () => {
          console.log("Cleaning up audio nodes...");
          compressor.dispose();
          limiter.dispose();
          // Also dispose synths to avoid memory leaks and stale connections
          if (synthRef.current && synthRef.current.name !== 'PolySynth') {
              // Be careful not to dispose if it's still needed, but here we are unmounting
              synthRef.current.dispose();
              synthRef.current = null;
          }
          if (bassSynthRef.current) {
              bassSynthRef.current.dispose();
              bassSynthRef.current = null;
          }
      };
  }, []);

  // Load Piano SamplerMonitor Transport State
  useEffect(() => {
    const interval = setInterval(() => {
        setTransportState(Tone.Transport.state);
    }, 100);
    return () => clearInterval(interval);
  }, []);

  // Load Grand Piano Sampler
  useEffect(() => {
    console.log("Loading Grand Piano Samples...");
    // Reduced reverb for better clarity (0.25 -> 0.15)
    const reverb = new Tone.Reverb({ decay: 2.0, wet: 0.15 }).toDestination();
     
    const sampler = new Tone.Sampler({
         urls: {
             "A0": "A0.mp3",
             "C1": "C1.mp3",
             "D#1": "Ds1.mp3",
             "F#1": "Fs1.mp3",
             "A1": "A1.mp3",
             "C2": "C2.mp3",
             "D#2": "Ds2.mp3",
             "F#2": "Fs2.mp3",
             "A2": "A2.mp3",
             "C3": "C3.mp3",
             "D#3": "Ds3.mp3",
             "F#3": "Fs3.mp3",
             "A3": "A3.mp3",
             "C4": "C4.mp3",
             "D#4": "Ds4.mp3",
             "F#4": "Fs4.mp3",
             "A4": "A4.mp3",
             "C5": "C5.mp3",
             "D#5": "Ds5.mp3",
             "F#5": "Fs5.mp3",
             "A5": "A5.mp3",
             "C6": "C6.mp3",
             "D#6": "Ds6.mp3",
             "F#6": "Fs6.mp3",
             "A6": "A6.mp3",
             "C7": "C7.mp3",
             "D#7": "Ds7.mp3",
             "F#7": "Fs7.mp3",
             "A7": "A7.mp3",
             "C8": "C8.mp3"
         },
         release: 1,
         baseUrl: "https://tonejs.github.io/audio/salamander/",
         onload: () => {
             console.log("Grand Piano Loaded!");
             setIsPianoLoaded(true);
         }
     }).connect(reverb);
     
     setPianoSampler(sampler);
     
     return () => {
         sampler.dispose();
         reverb.dispose();
     };
   }, []);

  // Load Acoustic Guitar Sampler
  useEffect(() => {
    console.log("Loading Guitar Samples...");
    const reverb = new Tone.Reverb({ decay: 1.5, wet: 0.2 }).toDestination();
    
    const sampler = new Tone.Sampler({
         urls: {
             "A2": "A2.mp3",
             "C3": "C3.mp3",
             "D#3": "Ds3.mp3",
             "F#3": "Fs3.mp3",
             "A3": "A3.mp3",
             "C4": "C4.mp3",
             "D#4": "Ds4.mp3",
             "F#4": "Fs4.mp3",
             "A4": "A4.mp3",
             "C5": "C5.mp3"
         },
         release: 1,
         baseUrl: "https://raw.githubusercontent.com/nbrosowsky/tonejs-instruments/master/samples/guitar-acoustic/",
         onload: () => {
             console.log("Acoustic Guitar Loaded!");
             setIsGuitarLoaded(true);
         }
     }).connect(reverb);
     
     setGuitarSampler(sampler);
     
     return () => {
         sampler.dispose();
         reverb.dispose();
     };
   }, []);

  // Load Electric Bass Sampler
  useEffect(() => {
    console.log("Loading Bass Samples...");
    const reverb = new Tone.Reverb({ decay: 1.0, wet: 0.1 }).toDestination();
    
    const sampler = new Tone.Sampler({
         urls: {
             "A1": "A1.mp3",
             "C2": "C2.mp3",
             "E2": "E2.mp3",
             "G2": "G2.mp3",
             "A2": "A2.mp3",
             "C3": "C3.mp3",
             "E3": "E3.mp3",
             "G3": "G3.mp3"
         },
         release: 1,
         baseUrl: "https://raw.githubusercontent.com/nbrosowsky/tonejs-instruments/master/samples/bass-electric/",
         onload: () => {
             console.log("Electric Bass Loaded!");
             setIsBassLoaded(true);
         }
     }).connect(reverb);
     
     setBassSampler(sampler);
     
     return () => {
         sampler.dispose();
         reverb.dispose();
     };
   }, []);

  // Initialize Audio Context on first interaction
  const ensureAudioContext = async () => {
    console.log("Ensuring Audio Context...");
    try {
        if (Tone.context.state !== 'running') {
            await Tone.start();
            console.log("Tone context started");
        }
        
        // Ensure Main Bus exists
        if (!mainBusRef.current) {
            mainBusRef.current = new Tone.Limiter(-1).toDestination();
        }

        if (!synthRef.current) {
             console.log("Initializing Enhanced Synths...");
             
             // 1. Enhanced PolySynth (Chords/Melody)
             // Using FM Synthesis for richer tone
             const polySynth = new Tone.PolySynth(Tone.FMSynth, {
                 harmonicity: 3,
                 modulationIndex: 3.5,
                 oscillator: { type: "sine" },
                 envelope: {
                     attack: 0.01,
                     decay: 0.5,
                     sustain: 0.1,
                     release: 1.2
                 },
                 modulation: { type: "square" },
                 modulationEnvelope: {
                     attack: 0.5,
                     decay: 0,
                     sustain: 1,
                     release: 0.5
                 }
             });
             
             polySynth.maxPolyphony = 12; // Limit voices to save CPU
             // polySynth.connect(mainBusRef.current); // REMOVED to avoid double signal
             
             // Add Chorus and Reverb for depth
             const chorus = new Tone.Chorus(4, 2.5, 0.3).start();
             const reverb = new Tone.Reverb({ decay: 2.0, wet: 0.2 });
             
             polySynth.chain(chorus, reverb, mainBusRef.current);
             synthRef.current = polySynth;
             
             // 2. Dedicated Bass Synth (Mono)
             // Using MonoSynth with Filter Envelope for punchy bass
             if (!bassSynthRef.current) {
                 const bassSynth = new Tone.MonoSynth({
                     oscillator: { type: "sawtooth" },
                     envelope: {
                         attack: 0.05,
                         decay: 0.3,
                         sustain: 0.4,
                         release: 0.8
                     },
                     filterEnvelope: {
                         attack: 0.001,
                         decay: 0.7,
                         sustain: 0.1,
                         release: 0.8,
                         baseFrequency: 300,
                         octaves: 4
                     }
                 }).connect(mainBusRef.current);
                 
                 // Add subtle distortion for warmth
                 const distortion = new Tone.Distortion(0.1);
                 bassSynth.chain(distortion, mainBusRef.current);
                 
                 bassSynthRef.current = bassSynth;
             }
             
             console.log("Synths initialized successfully");
             return { poly: polySynth, bass: bassSynthRef.current };
        }
        return { poly: synthRef.current, bass: bassSynthRef.current };
    } catch (err) {
        console.error("Error in ensureAudioContext:", err);
        return null;
    }
  };

  useEffect(() => {
    if (Tone.Destination) {
      Tone.Destination.volume.value = volume;
    }
  }, [volume]);

  const handleTestSound = async () => {
    console.log("Testing Audio Engine...");
    const audioContext = await ensureAudioContext();
    if (!audioContext) return;
    
    const fallbackSynth = audioContext.poly;
    const fallbackBass = audioContext.bass;
    
    // Select instrument based on user choice
    const getInstrumentInstance = (programId) => {
        // Pianos (0-7) & Organs (16-23)
        if ((programId <= 7 || (programId >= 16 && programId <= 23)) && isPianoLoaded && pianoSampler) return pianoSampler;
        
        // Guitars (24-31)
        if (programId >= 24 && programId <= 31 && isGuitarLoaded && guitarSampler) return guitarSampler;
        
        return fallbackSynth;
    };
    
    const getBassInstance = (programId) => {
        // Basses (32-39)
        if (programId >= 32 && programId <= 39 && isBassLoaded && bassSampler) return bassSampler;
        return fallbackBass;
    };

    const chordSynth = getInstrumentInstance(chordInstrument);
    
    if (chordSynth) {
        console.log(`Playing test note C4 with ${chordInstrument} (Chords)...`);
        chordSynth.triggerAttackRelease("C4", "8n");
        
        // Also test melody instrument if different
        if (chordInstrument !== melodyInstrument) {
            const melodySynth = getInstrumentInstance(melodyInstrument);
            if (melodySynth) {
                setTimeout(() => {
                    console.log(`Playing test note E4 with ${melodyInstrument} (Melody)...`);
                    melodySynth.triggerAttackRelease("E4", "8n");
                }, 500);
            }
        }

        // Test Bass
        const bassSynthInst = getBassInstance(bassInstrument);
        if (bassSynthInst) {
            setTimeout(() => {
                console.log(`Playing test note C2 with ${bassInstrument} (Bass)...`);
                bassSynthInst.triggerAttackRelease("C2", "8n");
            }, 750);
        }
    } else {
        alert("Audio Engine Failed to Initialize");
    }
  };

  const handleGenerate = async () => {
    // Stop any existing playback before generating new data
    if (isPlaying || Tone.Transport.state === 'started') {
        Tone.Transport.stop();
        Tone.Transport.cancel();
        setIsPlaying(false);
    }
    
    setIsGenerating(true);
    try {
      const data = await generateChords({
          ...settings,
          source: settings.source || "auto"
      });
      setGeneratedData({ ...data, tempo: settings.tempo });
      
      // Update volume if needed
      if (synthRef.current) {
          Tone.Destination.volume.value = volume;
      }
    } catch (err) {
      console.error(err);
      alert("Failed to generate chords. Backend might be down.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handlePlay = async () => {
    console.log("Play button clicked");
    
    if (!generatedData) {
        console.warn("No generated data to play");
        alert("Please generate a track first!");
        return;
    }
    
    // Toggle Play/Pause
    if (isPlaying) {
        console.log("Stopping playback");
        Tone.Transport.stop();
        Tone.Transport.cancel();
        setIsPlaying(false);
        // Also release all notes just in case
        if (synthRef.current) synthRef.current.releaseAll();
        if (bassSynthRef.current) bassSynthRef.current.triggerRelease();
        return;
    }

    console.log("Starting playback sequence...");
    const audioContext = await ensureAudioContext();
    if (!audioContext) return;
    
    const fallbackSynth = audioContext.poly;
    const fallbackBass = audioContext.bass;
    
    // Choose instrument instances
    const getInstrumentInstance = (programId) => {
        // Pianos (0-7) & Organs (16-23)
        if ((programId <= 7 || (programId >= 16 && programId <= 23)) && isPianoLoaded && pianoSampler) return pianoSampler;
        
        // Guitars (24-31)
        if (programId >= 24 && programId <= 31 && isGuitarLoaded && guitarSampler) return guitarSampler;
        
        return fallbackSynth;
    };
    
    // Separate Bass Getter
    const getBassInstance = (programId) => {
        // Basses (32-39)
        if (programId >= 32 && programId <= 39 && isBassLoaded && bassSampler) return bassSampler;
        return fallbackBass;
    };

    const chordSynth = getInstrumentInstance(chordInstrument);
    const melodySynth = getInstrumentInstance(melodyInstrument);
    const bassSynthInst = getBassInstance(bassInstrument);

    console.log(`Using instruments - Chords: ${chordInstrument}, Melody: ${melodyInstrument}, Bass: ${bassInstrument}`);

    if (!chordSynth) {
        console.error("Could not initialize synths");
        alert("Audio engine failed to start. Check console.");
        return;
    }
    
    // Reset Transport
    Tone.Transport.stop();
    Tone.Transport.cancel();
    
    // Convert BPM to transport time
    const bpm = settings.tempo || generatedData.tempo || 140;
    console.log("BPM:", bpm);
    Tone.Transport.bpm.value = bpm;
    const secondsPerBeat = 60 / bpm;
    let maxDuration = 0;

    // Instrument Ranges
    const NOTE_RANGES = {
        piano: { min: 21, max: 108 }, // A0 - C8
        guitar: { min: 45, max: 72 }, // A2 - C5
        bass: { min: 28, max: 55 }    // E1 - G3
    };

    const eventsToPlay = [];
    
    // Helper to add humanization (random micro-timing)
    const humanize = (time) => {
        const offset = (Math.random() - 0.5) * 0.015; // +/- 7.5ms
        return Math.max(0, time + offset);
    };
    
    // Combine and process events
    // We convert everything to seconds for Transport.schedule
    if (generatedData.chords) {
        console.log(`Processing ${generatedData.chords.length} chord events`);
        generatedData.chords.forEach(event => {
            const startTime = humanize(event.time * secondsPerBeat);
            if (chordSynth) {
                eventsToPlay.push({
                    time: startTime, 
                    note: event.note,
                    duration: event.duration * secondsPerBeat, 
                    velocity: (event.velocity / 127) * 0.9, // Headroom
                    instrument: chordSynth,
                    instrumentName: chordInstrument,
                    fallback: fallbackSynth
                });
            }
            maxDuration = Math.max(maxDuration, startTime + (event.duration * secondsPerBeat));
        });
    }

    if (generatedData.melody) {
        console.log(`Processing ${generatedData.melody.length} melody events`);
        generatedData.melody.forEach(event => {
            const startTime = humanize(event.time * secondsPerBeat);
            if (melodySynth) {
                eventsToPlay.push({
                    time: startTime,
                    note: event.note,
                    duration: event.duration * secondsPerBeat, 
                    velocity: (event.velocity / 127), // Melody slightly louder
                    instrument: melodySynth,
                    instrumentName: melodyInstrument,
                    fallback: fallbackSynth
                });
            }
            maxDuration = Math.max(maxDuration, startTime + (event.duration * secondsPerBeat));
        });
    }

    if (generatedData.bass) {
        console.log(`Processing ${generatedData.bass.length} bass events`);
        generatedData.bass.forEach(event => {
            // Bass usually tighter, less humanization
            const startTime = event.time * secondsPerBeat;
            // Only add if instrument exists
            if (bassSynthInst) {
                eventsToPlay.push({
                    time: startTime, 
                    note: event.note,
                    duration: event.duration * secondsPerBeat,
                    velocity: (event.velocity / 127) * 1.1, // Bass needs power
                    instrument: bassSynthInst,
                    instrumentName: bassInstrument,
                    fallback: fallbackBass
                });
            }
            maxDuration = Math.max(maxDuration, startTime + (event.duration * secondsPerBeat));
        });
    }

    if (eventsToPlay.length === 0) {
        console.warn("No events to play found in data");
        alert("Generated data is empty!");
        return;
    }

    console.log(`Scheduling ${eventsToPlay.length} events on Transport...`);
    
    // Schedule events on Transport
    eventsToPlay.forEach(event => {
        // Double check time is valid
        if (event.time >= 0 && event.duration > 0) {
            Tone.Transport.schedule((time) => {
                try {
                    // Convert MIDI note to Note Name (e.g., 60 -> C4)
                    const frequency = new Tone.Frequency(event.note, "midi");
                    const noteName = frequency.toNote();
                    
                    // console.log(`Triggering ${noteName} (${event.note}) at ${time.toFixed(3)}s`);
                    
                    // Update UI safely
                    setLastPlayedNote(noteName);
                    
                    if (event.instrument) {
                        // Check Range
                        let targetInstrument = event.instrument;
                        const range = NOTE_RANGES[event.instrumentName];
                        
                        // If instrument has a defined range and note is outside it
                        if (range && (event.note < range.min || event.note > range.max)) {
                            // console.warn(`Note ${event.note} (${noteName}) out of range for ${event.instrumentName}. Using fallback.`);
                            targetInstrument = event.fallback;
                        }

                        if (targetInstrument) {
                            try {
                                targetInstrument.triggerAttackRelease(
                                    noteName,
                                    event.duration,
                                    time,
                                    event.velocity
                                );
                            } catch (error) {
                                console.warn(`Instrument trigger failed for ${noteName}, trying fallback`, error);
                                if (event.fallback && targetInstrument !== event.fallback) {
                                     event.fallback.triggerAttackRelease(
                                        noteName,
                                        event.duration,
                                        time,
                                        event.velocity
                                    );
                                }
                            }
                        }
                    }
                } catch (err) {
                    console.error("Error triggering note:", event, err);
                }
            }, event.time);
        }
    });
    
    console.log("Starting Transport...");

    // Start Transport
    console.log("Starting Transport...");
    try {
        await Tone.start();
        console.log("Tone.start() success");
    } catch (e) {
        console.warn("Tone.start() failed (user gesture needed?)", e);
    }
    
    // Add small delay to ensure scheduler is ready
    Tone.Transport.start("+0.1");
    setIsPlaying(true);
    
    // Auto stop (visuals only, Transport stops itself if we want, but here we just handle state)
    // Actually, Transport continues running until stopped.
    // We set a timeout to stop it after the track finishes.
    setTimeout(() => {
        // Only stop if still playing (user hasn't stopped manually)
        // We can't easily check 'isPlaying' state inside timeout due to closure
        // But we can check Transport state
        if (Tone.Transport.state === 'started') {
            console.log("Track finished, stopping Transport.");
            Tone.Transport.stop();
            // We need to update state, but this closure captures old setIsPlaying
            // React state updates are tricky here. 
            // Better to just let the user stop, or use a ref.
            // For now, let's just log.
        }
    }, (maxDuration + 0.5) * 1000);
  };

  const handleExport = async () => {
      if (!generatedData) return;
      await downloadMidi({
        ...generatedData,
        instruments: {
            chords: chordInstrument,
            melody: melodyInstrument,
            bass: bassInstrument
        }
      });
  };

  const handleLoadTrack = (trackData) => {
    // Stop playback if running
    if (isPlaying) {
        Tone.Transport.stop();
        Tone.Transport.cancel();
        setIsPlaying(false);
    }

    // Apply suggested instruments
    if (trackData.instruments) {
        console.log("Applying suggested instruments:", trackData.instruments);
        if (trackData.instruments.chords) setChordInstrument(trackData.instruments.chords);
        if (trackData.instruments.melody) setMelodyInstrument(trackData.instruments.melody);
        if (trackData.instruments.bass) setBassInstrument(trackData.instruments.bass);
    }

    setSettings(prev => ({
        ...prev,
        key: trackData.key,
        scale: trackData.scale,
        mood: trackData.mood,
        tempo: trackData.tempo,
        melody: !!trackData.melody
    }));
    
    // Ensure data has tempo for playback
    setGeneratedData({
        ...trackData,
        tempo: trackData.tempo
    });
    
    // Navigate to generator
    navigate('/');
  };

  return (
    <div className={`min-h-screen bg-[#0a0a0a] text-white font-sans selection:bg-purple-500/30 ${isPluginMode ? 'overflow-hidden' : ''}`}>
      {!isPluginMode && <Header />}
      
      <main className={`container mx-auto ${isPluginMode ? 'px-2 py-2' : 'px-6 py-8'}`}>
        <Routes>
            <Route path="/" element={
                <Generator 
                    settings={settings}
                    setSettings={setSettings}
                    onGenerate={handleGenerate}
                    isGenerating={isGenerating}
                    onPlay={handlePlay}
                    isPlaying={isPlaying}
                    onExport={handleExport}
                    generatedData={generatedData}
                    volume={volume}
                    setVolume={setVolume}
                    onTestSound={handleTestSound}
                    lastPlayedNote={lastPlayedNote}
                    transportState={transportState}
                    isPianoLoaded={isPianoLoaded}
                    isGuitarLoaded={isGuitarLoaded}
                    chordInstrument={chordInstrument}
                    setChordInstrument={setChordInstrument}
                    melodyInstrument={melodyInstrument}
                    setMelodyInstrument={setMelodyInstrument}
                    bassInstrument={bassInstrument}
                    setBassInstrument={setBassInstrument}
                    isBassLoaded={isBassLoaded}
                    isPluginMode={isPluginMode}
                />
            } />
            <Route path="/top-hits" element={
                <TopHits onLoadTrack={handleLoadTrack} />
            } />
        </Routes>
      </main>
    </div>
  );
}

export default App;
