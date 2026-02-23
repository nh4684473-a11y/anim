
import React, { useRef, useEffect } from 'react';
import * as Tone from 'tone';
import { Play, Square } from 'lucide-react';

const NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];

const PianoRoll = ({ data, onPlay, isPlaying, tempo = 120 }) => {
  const containerRef = useRef(null);
  const playheadRef = useRef(null);

  // Normalize data to a list of events: { note, start, duration, type }
  // Type: 'chord' or 'melody'
  
  // Constants for drawing
  const rowHeight = 24; // Increased height
  const beatWidth = 80; // Width per beat
  
  // Playback Animation Loop
  useEffect(() => {
    let animationFrame;

    const updatePlayhead = () => {
        // If not playing, don't update
        // But we should allow one update to reset if !isPlaying
        
        if (isPlaying) {
             // Get current time from Tone Transport
            // Tone.Transport.seconds is the current time in seconds
            // Convert to beats: seconds * (tempo / 60)
            const currentSeconds = Tone.Transport.seconds;
            const currentBeat = currentSeconds * (tempo / 60);
            const x = currentBeat * beatWidth;
            
            // Update Playhead Position
            if (playheadRef.current) {
                playheadRef.current.style.transform = `translateX(${x}px)`;
            }

            // Auto-Scroll Logic
            // Keep playhead centered in the view
            if (containerRef.current) {
                const container = containerRef.current;
                const containerWidth = container.clientWidth;
                // const scrollLeft = container.scrollLeft; // unused
                
                // Calculate desired scroll position (center the playhead)
                // But don't scroll if playhead is near the start
                const targetScroll = x - (containerWidth / 2);
                
                if (targetScroll > 0) {
                    // Simple centering:
                    container.scrollLeft = targetScroll;
                } else {
                    container.scrollLeft = 0;
                }
            }
            
            animationFrame = requestAnimationFrame(updatePlayhead);
        }
    };

    if (isPlaying) {
        // Start Loop
        animationFrame = requestAnimationFrame(updatePlayhead);
    } else {
        // Reset playhead if stopped
        if (playheadRef.current) {
             playheadRef.current.style.transform = `translateX(0px)`;
        }
        // Reset scroll
        if (containerRef.current) {
            containerRef.current.scrollLeft = 0;
        }
    }

    return () => {
        if (animationFrame) cancelAnimationFrame(animationFrame);
    };
  }, [isPlaying, tempo, beatWidth]);

  let events = [];
  let totalDuration = 0;

  if (!data) {
     // Empty state
  } else if (Array.isArray(data)) {
      // Legacy: Block Chords
      let currentBeat = 0;
      data.forEach(chord => {
          chord.notes.forEach(note => {
              events.push({
                  note: note,
                  start: currentBeat,
                  duration: chord.duration,
                  type: 'chord'
              });
          });
          currentBeat += chord.duration;
      });
      totalDuration = currentBeat;
  } else if (data.chords || data.melody || data.bass) {
      // New Format: Event Streams
      if (data.chords) {
          data.chords.forEach(e => {
              events.push({
                  note: e.note,
                  start: e.time,
                  duration: e.duration,
                  type: 'chord'
              });
              totalDuration = Math.max(totalDuration, e.time + e.duration);
          });
      }
      if (data.melody) {
          data.melody.forEach(e => {
              events.push({
                  note: e.note,
                  start: e.time,
                  duration: e.duration,
                  type: 'melody'
              });
              totalDuration = Math.max(totalDuration, e.time + e.duration);
          });
      }
      if (data.bass) {
          data.bass.forEach(e => {
              events.push({
                  note: e.note,
                  start: e.time,
                  duration: e.duration,
                  type: 'bass'
              });
              totalDuration = Math.max(totalDuration, e.time + e.duration);
          });
      }
  } else if (data.progression) {
       // Fallback to legacy progression in object
      let currentBeat = 0;
      data.progression.forEach(chord => {
          chord.notes.forEach(note => {
              events.push({
                  note: note,
                  start: currentBeat,
                  duration: chord.duration,
                  type: 'chord'
              });
          });
          currentBeat += chord.duration;
      });
      totalDuration = currentBeat;
  }

  if (events.length === 0) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-gray-500 gap-4">
        <div className="w-16 h-16 rounded-full bg-gray-800/50 flex items-center justify-center border border-white/5 animate-pulse">
          <div className="w-8 h-8 bg-gray-700 rounded-full" />
        </div>
        <p className="font-medium text-sm">Generate a progression to see the notes</p>
      </div>
    );
  }

  // Find min/max pitch to scale the view
  const allPitches = events.map(e => e.note);
  const minPitch = Math.min(...allPitches) - 2;
  const maxPitch = Math.max(...allPitches) + 2;
  const range = maxPitch - minPitch + 1;
  const totalWidth = totalDuration * beatWidth;

  const getNoteName = (midi) => {
    const note = NOTE_NAMES[midi % 12];
    const octave = Math.floor(midi / 12) - 1;
    return { note, octave, full: `${note}${octave}` };
  };

  const isBlackKey = (midi) => {
    const n = midi % 12;
    return [1, 3, 6, 8, 10].includes(n);
  };

  return (
    <div className="h-full flex flex-col relative group/pianoroll">
        {/* Floating Play Button */}
        <div className="absolute bottom-6 right-6 z-50">
            <button
                onClick={onPlay}
                className={`w-14 h-14 rounded-full shadow-2xl backdrop-blur-md transition-all duration-300 transform hover:scale-105 border flex items-center justify-center ${
                    isPlaying 
                        ? 'bg-red-500 text-white border-red-400 shadow-red-500/40' 
                        : 'bg-white text-black hover:bg-gray-100 border-white/20'
                }`}
            >
                {isPlaying ? (
                    <Square className="w-6 h-6 fill-current" />
                ) : (
                    <Play className="w-6 h-6 fill-current ml-1" />
                )}
            </button>
        </div>

      <div ref={containerRef} className="flex-1 overflow-auto custom-scrollbar relative bg-[#111] rounded-xl border border-white/5 shadow-inner">
        <div 
          className="relative"
          style={{ 
            height: `${range * rowHeight}px`,
            width: `${Math.max(totalWidth, 100)}px`,
            minWidth: '100%'
          }}
        >
          {/* Playhead Indicator */}
          <div 
            ref={playheadRef}
            className="absolute top-0 bottom-0 w-0.5 bg-red-500 z-50 shadow-[0_0_10px_rgba(239,68,68,0.8)] pointer-events-none will-change-transform"
            style={{ left: 0 }}
          >
            {/* Playhead Cap */}
            <div className="absolute -top-1 -left-1.5 w-3 h-3 bg-red-500 rounded-full shadow-lg" />
          </div>

          {/* Piano Keys Background (Left Fixed? No, just background rows) */}
          {Array.from({ length: range }).map((_, i) => {
            const pitch = maxPitch - i;
            const isBlack = isBlackKey(pitch);
            const noteInfo = getNoteName(pitch);
            
            return (
              <div 
                key={pitch}
                className={`absolute w-full border-b border-white/[0.03] flex items-center ${
                  isBlack ? 'bg-white/[0.02]' : 'bg-transparent'
                }`}
                style={{ 
                  top: `${i * rowHeight}px`,
                  height: `${rowHeight}px`
                }}
              >
                {/* Note Labels */}
                <div className={`sticky left-0 px-2 text-[10px] font-mono z-20 w-16 text-right flex items-center justify-end h-full border-r border-white/5 ${
                    isBlack ? 'bg-[#1a1a1a] text-gray-500' : 'bg-[#222] text-gray-300'
                }`}>
                  <span className={noteInfo.note.includes('#') ? 'text-gray-600' : ''}>
                    {noteInfo.note}
                  </span>
                  <span className="text-[9px] opacity-50 ml-0.5">{noteInfo.octave}</span>
                </div>
              </div>
            );
          })}

          {/* Vertical Beat Lines */}
          {Array.from({ length: Math.ceil(totalDuration) + 1 }).map((_, i) => (
            <div 
              key={i}
              className={`absolute top-0 bottom-0 pointer-events-none z-0 ${
                  i % 4 === 0 ? 'border-r border-white/10' : 'border-r border-white/[0.02]'
              }`}
              style={{ left: `${i * beatWidth}px` }}
            >
                {i % 4 === 0 && (
                    <span className="absolute top-0 left-1 text-[9px] text-gray-600 font-mono">
                        {i / 4 + 1}
                    </span>
                )}
            </div>
          ))}

          {/* Notes */}
          {events.map((event, idx) => {
            const top = (maxPitch - event.note) * rowHeight;
            const left = event.start * beatWidth;
            const width = event.duration * beatWidth;
            const isChord = event.type === 'chord';
            const isBass = event.type === 'bass';

            return (
              <div
                key={idx}
                className={`absolute rounded-sm shadow-sm transition-all hover:brightness-125 z-10 ${
                    isChord 
                        ? 'bg-purple-600/90 border border-purple-400/30' 
                        : isBass
                            ? 'bg-amber-500/90 border border-amber-300/30 shadow-[0_0_10px_rgba(245,158,11,0.3)]'
                            : 'bg-cyan-400/90 border border-cyan-200/50 shadow-[0_0_10px_rgba(34,211,238,0.3)]'
                }`}
                style={{
                  top: `${top + 1}px`,
                  left: `${left}px`,
                  width: `${Math.max(width - 1, 1)}px`,
                  height: `${rowHeight - 2}px`,
                }}
                title={`${getNoteName(event.note).full}`}
              />
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default PianoRoll;
