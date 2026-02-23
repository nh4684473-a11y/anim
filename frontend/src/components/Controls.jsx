
import React, { useState } from 'react';
import { RefreshCw, Play, Download, ChevronDown, Sliders, Sparkles } from 'lucide-react';

const KEYS = ["Random", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
const SCALES = ["Random", "minor", "harmonic_minor", "phrygian", "dorian", "minor_pentatonic", "major"];
const MOODS = [
  "Random",
  "Dark Trap", "Boom Bap", "Drill", "Lo-Fi", "R&B / Soul", 
  "Jazz", "Cinematic", "House", "Pop", "Future Bass", "Neo Soul", "Reggaeton",
  "Dubstep", "Trance", "Techno", "Drum & Bass", "Progressive House", 
  "Big Room", "Electro House", "Tropical House", "Hardstyle", "Melodic Dubstep",
  "Walker"
];

const Select = ({ label, name, value, options, onChange }) => (
  <div className="flex flex-col gap-2">
    <label className="text-gray-400 text-xs font-bold uppercase tracking-wider">{label}</label>
    <div className="relative group">
      <select 
        name={name} 
        value={value} 
        onChange={onChange}
        className="w-full appearance-none bg-black/40 text-white p-4 rounded-xl border border-white/10 focus:border-purple-500 focus:outline-none transition-all cursor-pointer hover:bg-black/60 font-medium"
      >
        {options.map((opt, i) => {
          const val = typeof opt === 'object' ? opt.value : opt;
          const lab = typeof opt === 'object' ? opt.label : opt.replace ? opt.replace('_', ' ') : opt;
          return (
            <option key={i} value={val}>
              {lab}
            </option>
          );
        })}
      </select>
      <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none">
        <ChevronDown className="w-4 h-4 text-gray-500 group-hover:text-purple-400 transition-colors" />
      </div>
    </div>
  </div>
);

const Controls = ({ 
  settings, 
  setSettings, 
  onGenerate, 
  isGenerating, 
  onPlay, 
  isPlaying, 
  onExport, 
  hasData, 
  onTestSound, 
  isPianoLoaded, 
  isGuitarLoaded,
  chordInstrument,
  setChordInstrument,
  melodyInstrument,
  setMelodyInstrument,
  bassInstrument,
  setBassInstrument,
  isBassLoaded
}) => {
  const [showContext, setShowContext] = useState(
      settings.key !== "Random" || settings.scale !== "Random" || settings.mood !== "Random"
  );

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    let finalValue = value;
    
    if (type === 'checkbox') {
        finalValue = checked;
    } else if (type === 'range') {
        finalValue = parseFloat(value);
        // Ensure integer values for specific fields
        if (name === 'tempo' || name === 'length') {
            finalValue = Math.round(finalValue);
        }
    }

    setSettings(prev => ({ 
      ...prev, 
      [name]: finalValue
    }));
  };

  const toggleContext = () => {
    const newState = !showContext;
    setShowContext(newState);
    if (!newState) {
        // Reset to Random when hiding context
        setSettings(prev => ({
            ...prev,
            key: "Random",
            scale: "Random",
            mood: "Random"
        }));
    }
  };

  return (
    <div className="flex flex-col gap-6">
      
      {/* Section: Musical Context */}
      <div className="space-y-4">
        {/* Source Selector */}
        <div className="bg-black/20 p-1 rounded-lg flex border border-white/5 mb-4">
            {[
                { val: 'auto', label: 'Auto' },
                { val: 'generate', label: 'Generate New' },
                { val: 'library', label: 'Library Pick' }
            ].map((opt) => (
                <button
                    key={opt.val}
                    onClick={() => handleChange({ target: { name: 'source', value: opt.val } })}
                    className={`flex-1 py-2 text-[10px] font-bold uppercase tracking-wider rounded-md transition-all ${
                        settings.source === opt.val
                        ? 'bg-purple-500 text-white shadow-lg' 
                        : 'text-gray-500 hover:text-gray-300'
                    }`}
                >
                    {opt.label}
                </button>
            ))}
        </div>

        <div 
            className="flex items-center justify-between cursor-pointer group" 
            onClick={toggleContext}
        >
            <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider flex items-center gap-2">
            <span className="w-8 h-[1px] bg-gray-700"></span>
            Musical Context
            <span className="flex-1 h-[1px] bg-gray-700"></span>
            </h3>
            <div className={`p-2 rounded-full transition-all ${showContext ? 'bg-purple-500/20 text-purple-400' : 'bg-gray-800 text-gray-500 group-hover:text-gray-300'}`}>
                <Sliders className="w-4 h-4" />
            </div>
        </div>

        {!showContext ? (
            <div 
                onClick={toggleContext}
                className="p-6 rounded-xl border border-dashed border-white/10 bg-white/5 hover:bg-white/10 hover:border-purple-500/30 transition-all cursor-pointer flex flex-col items-center justify-center gap-3 text-center group"
            >
                <div className="p-3 rounded-full bg-gradient-to-br from-purple-500/20 to-blue-500/20 group-hover:scale-110 transition-transform">
                    <Sparkles className="w-6 h-6 text-purple-400" />
                </div>
                <div>
                    <h4 className="font-bold text-white text-sm">Surprise Me Mode</h4>
                    <p className="text-xs text-gray-400 mt-1">Generating random style & key</p>
                </div>
                <span className="text-[10px] uppercase font-bold text-purple-400 tracking-wider bg-purple-500/10 px-3 py-1 rounded-full">
                    Click to Customize
                </span>
            </div>
        ) : (
            <div className="space-y-4 animate-in fade-in slide-in-from-top-4 duration-300">
                <div className="grid grid-cols-2 gap-3">
                <Select 
                    label="Root Key" 
                    name="key" 
                    value={settings.key} 
                    options={KEYS} 
                    onChange={handleChange} 
                />
                
                <Select 
                    label="Scale" 
                    name="scale" 
                    value={settings.scale} 
                    options={SCALES} 
                    onChange={handleChange} 
                />
                </div>

                <Select 
                label="Genre / Mood" 
                name="mood" 
                value={settings.mood} 
                options={MOODS} 
                onChange={handleChange} 
                />
            </div>
        )}
      </div>

      {/* Section: Parameters */}
      <div className="space-y-4">
        <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
          <span className="w-8 h-[1px] bg-gray-700"></span>
          Parameters
          <span className="flex-1 h-[1px] bg-gray-700"></span>
        </h3>

        <div className="bg-black/20 p-4 rounded-xl border border-white/5 space-y-4">
            <div className="flex flex-col gap-2">
               <label className="text-gray-400 text-xs font-bold uppercase tracking-wider flex justify-between">
                 <span>Tempo</span>
                 <span className="text-purple-400 font-mono">{settings.tempo} BPM</span>
               </label>
               <input 
                 type="range" 
                 name="tempo"
                 min="60" 
                 max="180" 
                 step="1"
                 value={settings.tempo} 
                 onChange={handleChange}
                 className="w-full accent-purple-500 h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer hover:accent-purple-400 transition-all"
               />
            </div>

            {/* Complexity Slider */}
            <div className="flex flex-col gap-2">
               <label className="text-gray-400 text-xs font-bold uppercase tracking-wider flex justify-between">
                 <span>Complexity</span>
                 <span className="text-purple-400 font-mono">{Math.round(settings.complexity * 100)}%</span>
               </label>
               <input 
                 type="range" 
                 name="complexity" 
                 min="0" 
                 max="1" 
                 step="0.1" 
                 value={settings.complexity} 
                 onChange={handleChange}
                 className="w-full accent-purple-500 h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer hover:accent-purple-400 transition-all"
               />
            </div>
        </div>

        {/* Melody Toggle */}
        <div className="flex items-center justify-between p-4 bg-gradient-to-r from-purple-900/20 to-blue-900/20 rounded-xl border border-white/5 hover:border-purple-500/30 transition-colors cursor-pointer" onClick={() => handleChange({ target: { name: 'melody', type: 'checkbox', checked: !settings.melody } })}>
           <div className="flex flex-col">
             <label className="text-gray-200 font-bold text-sm cursor-pointer">Generate Melody</label>
             <span className="text-xs text-gray-500">Create a top-line melody</span>
           </div>
           <div className="relative inline-block w-10 h-5 transition duration-200 ease-in-out">
             <input 
               type="checkbox" 
               name="melody" 
               id="melody-toggle"
               checked={settings.melody}
               onChange={handleChange}
               className="peer absolute opacity-0 w-0 h-0"
             />
             <div className={`block w-full h-full rounded-full transition-colors ${settings.melody ? 'bg-purple-500' : 'bg-gray-700'}`} />
             <div className={`absolute top-1 left-1 w-3 h-3 bg-white rounded-full transition-transform shadow-sm ${settings.melody ? 'translate-x-5' : 'translate-x-0'}`} />
           </div>
        </div>
      </div>

      <div className="pt-4 border-t border-white/5 space-y-3">
        <button 
          onClick={onGenerate}
          disabled={isGenerating}
          className={`w-full py-4 rounded-xl font-bold text-lg flex items-center justify-center gap-2 transition-all shadow-lg relative overflow-hidden group ${
            isGenerating 
              ? 'bg-gray-800 text-gray-500 cursor-not-allowed' 
              : !showContext 
                ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:from-purple-500 hover:to-pink-500 shadow-purple-500/20'
                : 'bg-white text-black hover:bg-gray-200 shadow-white/10'
          }`}
        >
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
          {isGenerating ? <RefreshCw className="w-5 h-5 animate-spin" /> : (
            !showContext ? <Sparkles className="w-5 h-5" /> : <RefreshCw className="w-5 h-5" />
          )}
          {isGenerating ? 'Generating...' : (!showContext ? 'Surprise Me!' : 'Generate Track')}
        </button>


        <div className="grid grid-cols-2 gap-3">
          <button 
            onClick={onPlay}
            disabled={!hasData}
            className={`py-3 rounded-xl font-bold flex items-center justify-center gap-2 transition-all ${
              !hasData 
                ? 'bg-gray-800 text-gray-600 cursor-not-allowed' 
                : isPlaying
                    ? 'bg-red-500/20 text-red-400 border border-red-500/50 hover:bg-red-500/30'
                    : 'bg-white/10 text-white hover:bg-white/20 border border-white/10'
            }`}
          >
            {isPlaying ? <span className="w-3 h-3 bg-current rounded-sm" /> : <Play className="w-4 h-4 fill-current" />}
            {isPlaying ? 'Stop' : 'Play'}
          </button>

          <button 
            onClick={onExport}
            disabled={!hasData}
            className={`py-3 rounded-xl font-bold flex items-center justify-center gap-2 transition-all ${
              !hasData 
                ? 'bg-gray-800 text-gray-600 cursor-not-allowed' 
                : 'bg-white/10 text-white hover:bg-white/20 border border-white/10'
            }`}
          >
            <Download className="w-4 h-4" />
            MIDI
          </button>
        </div>
        
        {/* Instrument Selectors */}
        <div className="bg-black/20 p-2 rounded-lg border border-white/5 mb-4">
            <label className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-2 block">
                Chord Instrument
            </label>
            <div className="flex gap-2 mb-4">
                <button
                    onClick={() => setChordInstrument('synth')}
                    className={`flex-1 py-1.5 px-3 rounded text-[10px] font-bold uppercase transition-colors ${
                        chordInstrument === 'synth' 
                        ? 'bg-purple-500 text-white shadow-lg' 
                        : 'bg-white/5 text-gray-400 hover:bg-white/10'
                    }`}
                >
                    Synth
                </button>
                <button
                    onClick={() => setChordInstrument('piano')}
                    className={`flex-1 py-1.5 px-3 rounded text-[10px] font-bold uppercase transition-colors flex items-center justify-center gap-1 ${
                        chordInstrument === 'piano' 
                        ? 'bg-purple-500 text-white shadow-lg' 
                        : 'bg-white/5 text-gray-400 hover:bg-white/10'
                    }`}
                >
                    Piano
                    {isPianoLoaded && <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" title="Samples Loaded"></span>}
                </button>
                <button
                    onClick={() => setChordInstrument('guitar')}
                    className={`flex-1 py-1.5 px-3 rounded text-[10px] font-bold uppercase transition-colors flex items-center justify-center gap-1 ${
                        chordInstrument === 'guitar' 
                        ? 'bg-purple-500 text-white shadow-lg' 
                        : 'bg-white/5 text-gray-400 hover:bg-white/10'
                    }`}
                >
                    Guitar
                    {isGuitarLoaded && <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" title="Samples Loaded"></span>}
                </button>
            </div>

            <label className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-2 block">
                Melody Instrument
            </label>
            <div className="flex gap-2">
                <button
                    onClick={() => setMelodyInstrument('synth')}
                    className={`flex-1 py-1.5 px-3 rounded text-[10px] font-bold uppercase transition-colors ${
                        melodyInstrument === 'synth' 
                        ? 'bg-purple-500 text-white shadow-lg' 
                        : 'bg-white/5 text-gray-400 hover:bg-white/10'
                    }`}
                >
                    Synth
                </button>
                <button
                    onClick={() => setMelodyInstrument('piano')}
                    className={`flex-1 py-1.5 px-3 rounded text-[10px] font-bold uppercase transition-colors flex items-center justify-center gap-1 ${
                        melodyInstrument === 'piano' 
                        ? 'bg-purple-500 text-white shadow-lg' 
                        : 'bg-white/5 text-gray-400 hover:bg-white/10'
                    }`}
                >
                    Piano
                    {isPianoLoaded && <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" title="Samples Loaded"></span>}
                </button>
                <button
                    onClick={() => setMelodyInstrument('guitar')}
                    className={`flex-1 py-1.5 px-3 rounded text-[10px] font-bold uppercase transition-colors flex items-center justify-center gap-1 ${
                        melodyInstrument === 'guitar' 
                        ? 'bg-purple-500 text-white shadow-lg' 
                        : 'bg-white/5 text-gray-400 hover:bg-white/10'
                    }`}
                >
                    Guitar
                    {isGuitarLoaded && <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" title="Samples Loaded"></span>}
                </button>
            </div>

            <label className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-2 block mt-4">
                Bass Instrument
            </label>
            <div className="flex gap-2">
                <button
                    onClick={() => setBassInstrument('synth')}
                    className={`flex-1 py-1.5 px-3 rounded text-[10px] font-bold uppercase transition-colors ${
                        bassInstrument === 'synth' 
                        ? 'bg-purple-500 text-white shadow-lg' 
                        : 'bg-white/5 text-gray-400 hover:bg-white/10'
                    }`}
                >
                    Synth
                </button>
                <button
                    onClick={() => setBassInstrument('bass')}
                    className={`flex-1 py-1.5 px-3 rounded text-[10px] font-bold uppercase transition-colors flex items-center justify-center gap-1 ${
                        bassInstrument === 'bass' 
                        ? 'bg-purple-500 text-white shadow-lg' 
                        : 'bg-white/5 text-gray-400 hover:bg-white/10'
                    }`}
                >
                    Bass
                    {isBassLoaded && <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" title="Samples Loaded"></span>}
                </button>
            </div>
        </div>

        {/* Test Audio Button */}
        <button 
            onClick={onTestSound}
            className="w-full py-2 text-xs uppercase tracking-wider font-bold text-gray-500 hover:text-white transition-colors flex items-center justify-center gap-2 border border-white/5 rounded-lg hover:bg-white/5"
        >
            <span className="w-2 h-2 rounded-full bg-green-500/50"></span>
            Test Audio Engine
        </button>
      </div>
    </div>
  );
};

export default Controls;
