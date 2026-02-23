import React from 'react';
import Controls from '../components/Controls';
import PianoRoll from '../components/PianoRoll';
import { Volume2, Info } from 'lucide-react';

const Generator = ({ 
    settings, 
    setSettings, 
    onGenerate, 
    isGenerating, 
    onPlay, 
    isPlaying, 
    onExport, 
    generatedData,
    volume,
    setVolume,
    onTestSound,
    lastPlayedNote,
    transportState,
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
    return (
        <div className="flex flex-col gap-6 w-full max-w-6xl mx-auto">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Left Panel: Controls */}
                <div className="lg:col-span-4 space-y-6">
                    <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-2xl">
                        <Controls 
                            settings={settings}
                            setSettings={setSettings}
                            onGenerate={onGenerate}
                            isGenerating={isGenerating}
                            onPlay={onPlay}
                            isPlaying={isPlaying}
                            onExport={onExport}
                            hasData={!!generatedData}
                            onTestSound={onTestSound}
                            isPianoLoaded={isPianoLoaded}
                            isGuitarLoaded={isGuitarLoaded}
                            isBassLoaded={isBassLoaded}
                            chordInstrument={chordInstrument}
                            setChordInstrument={setChordInstrument}
                            melodyInstrument={melodyInstrument}
                            setMelodyInstrument={setMelodyInstrument}
                            bassInstrument={bassInstrument}
                            setBassInstrument={setBassInstrument}
                        />
                        
                        {/* Debug Info */}
                        <div className="mt-4 p-3 bg-black/50 rounded-lg text-[10px] font-mono text-gray-500 flex justify-between">
                            <span>Status: <span className={transportState === 'started' ? 'text-green-400' : 'text-yellow-400'}>{transportState || 'stopped'}</span></span>
                            <span>Note: <span className="text-purple-400">{lastPlayedNote || '-'}</span></span>
                            <span>Piano: <span className={isPianoLoaded ? 'text-green-400' : 'text-yellow-400'}>{isPianoLoaded ? 'Ready' : 'Loading...'}</span></span>
                        </div>
                    </div>

                {/* Info Card */}
                <div className="bg-gradient-to-br from-purple-900/20 to-blue-900/20 border border-white/5 rounded-2xl p-6 relative overflow-hidden group">
                    <div className="absolute inset-0 bg-white/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                    <h3 className="text-white font-bold flex items-center gap-2 mb-2">
                        <Info className="w-4 h-4 text-purple-400" />
                        Pro Tip
                    </h3>
                    <p className="text-sm text-gray-400 leading-relaxed">
                        Try combining a <span className="text-white font-bold">Neo Soul</span> mood with a <span className="text-white font-bold">minor 9th</span> scale for lush, emotional chords.
                    </p>
                </div>
            </div>

            {/* Right Panel: Piano Roll & Visualization */}
            <div className="lg:col-span-8 flex flex-col gap-4 h-[1000px]">
                {generatedData ? (
                    <>
                        {/* Chords Section */}
                        <div className="flex-1 bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-1 shadow-2xl relative overflow-hidden flex flex-col min-h-0">
                            <div className="h-10 bg-black/40 flex items-center px-4 border-b border-white/10 justify-between shrink-0 z-20 relative">
                                <div className="flex items-center gap-2">
                                    <div className="w-2 h-2 rounded-full bg-purple-500 animate-pulse"></div>
                                    <span className="text-sm font-bold text-white/90 tracking-wider">CHORDS</span>
                                </div>
                                <div className="flex items-center gap-4">
                                    {/* Volume Control */}
                                    <div className="flex items-center gap-2 bg-black/40 px-2 py-1 rounded border border-white/5">
                                        <Volume2 className="w-3 h-3 text-gray-400" />
                                        <input 
                                            type="range" 
                                            min="-60" 
                                            max="0" 
                                            value={volume} 
                                            onChange={(e) => setVolume(parseFloat(e.target.value))}
                                            className="w-16 accent-purple-500 h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                                        />
                                    </div>
                                    <div className="text-xs text-white/40 font-mono">
                                        {generatedData.tempo} BPM
                                    </div>
                                </div>
                            </div>
                            
                            <div className="flex-1 rounded-xl overflow-hidden bg-[#1a1a1a] relative">
                                <PianoRoll 
                                    data={{ chords: generatedData.chords }} 
                                    isPlaying={isPlaying} 
                                    onPlay={onPlay}
                                    tempo={generatedData.tempo}
                                />
                            </div>
                        </div>

                        {/* Melody Section */}
                        <div className="flex-1 bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-1 shadow-2xl relative overflow-hidden flex flex-col min-h-0">
                            <div className="h-10 bg-black/40 flex items-center px-4 border-b border-white/10 justify-between shrink-0 z-20 relative">
                                <div className="flex items-center gap-2">
                                    <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></div>
                                    <span className="text-sm font-bold text-white/90 tracking-wider">MELODY</span>
                                    <span className="text-xs text-white/40 ml-2">({melodyInstrument === 'piano' ? 'Piano' : 'Guitar'})</span>
                                </div>
                            </div>
                            
                            <div className="flex-1 rounded-xl overflow-hidden bg-[#1a1a1a] relative">
                                <PianoRoll 
                                    data={{ melody: generatedData.melody }} 
                                    isPlaying={isPlaying} 
                                    onPlay={onPlay}
                                    tempo={generatedData.tempo}
                                />
                            </div>
                        </div>

                        {/* Bass Section */}
                        <div className="flex-1 bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-1 shadow-2xl relative overflow-hidden flex flex-col min-h-0">
                            <div className="h-10 bg-black/40 flex items-center px-4 border-b border-white/10 justify-between shrink-0 z-20 relative">
                                <div className="flex items-center gap-2">
                                    <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></div>
                                    <span className="text-sm font-bold text-white/90 tracking-wider">BASS</span>
                                    <span className="text-xs text-white/40 ml-2">({bassInstrument === 'bass' ? 'Bass' : 'Synth'})</span>
                                </div>
                            </div>
                            
                            <div className="flex-1 rounded-xl overflow-hidden bg-[#1a1a1a] relative">
                                <PianoRoll 
                                    data={{ bass: generatedData.bass }} 
                                    isPlaying={isPlaying} 
                                    onPlay={onPlay}
                                    tempo={generatedData.tempo}
                                />
                            </div>
                        </div>
                    </>
                ) : (
                    <div className="h-full bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-1 shadow-2xl relative overflow-hidden flex flex-col">
                        <div className="flex-1 rounded-xl overflow-hidden bg-[#1a1a1a] relative flex items-center justify-center group">
                            <div className="text-center space-y-4 relative z-10">
                                <div className="w-20 h-20 rounded-full bg-purple-500/10 flex items-center justify-center mx-auto border border-purple-500/20 group-hover:scale-110 transition-transform duration-500">
                                    <svg className="w-10 h-10 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                                    </svg>
                                </div>
                                <div>
                                    <h3 className="text-xl font-bold text-white mb-2">Ready to Create</h3>
                                    <p className="text-white/40 max-w-xs mx-auto text-sm leading-relaxed">
                                        Configure your settings on the left and click Generate to create a new track with separate Chord and Melody sections.
                                    </p>
                                </div>
                            </div>
                            
                            {/* Animated Background */}
                            <div className="absolute inset-0 bg-gradient-to-br from-purple-900/5 via-transparent to-cyan-900/5 opacity-50" />
                            <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-[0.03]" />
                        </div>
                    </div>
                )}
            </div>
        </div>
        </div>
    );
};

export default Generator;
