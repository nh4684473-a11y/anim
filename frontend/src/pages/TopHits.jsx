import React, { useState, useEffect } from 'react';
import { getTopHits, generateTopHit } from '../api/client';
import { Play, Loader2, Music2, ArrowRight } from 'lucide-react';

const TopHits = ({ onLoadTrack }) => {
    const [hits, setHits] = useState([]);
    const [loading, setLoading] = useState(true);
    const [generatingId, setGeneratingId] = useState(null);

    useEffect(() => {
        const fetchHits = async () => {
            try {
                const data = await getTopHits();
                setHits(data);
            } catch (err) {
                console.error("Failed to load top hits", err);
            } finally {
                setLoading(false);
            }
        };
        fetchHits();
    }, []);

    const handleLoad = async (hit) => {
        setGeneratingId(hit.id);
        try {
            const data = await generateTopHit(hit.id);
            // Transform data to match App.jsx expectation if needed
            // The generateTopHit returns { chords, melody, key, scale, tempo }
            // App.jsx expects { progression, chords, melody, tempo, key, scale, mood }
            // Note: 'progression' in App.jsx usually refers to the list of degrees or chords.
            // The backend returns 'chords' as the event list, and 'progression' might be the degree list.
            // Let's check backend return format.
            
            onLoadTrack(data);
        } catch (err) {
            console.error("Failed to generate track", err);
            alert("Failed to load track. Please try again.");
        } finally {
            setGeneratingId(null);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 text-purple-500 animate-spin" />
            </div>
        );
    }

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div className="flex flex-col gap-2">
                <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                    <Music2 className="w-6 h-6 text-purple-400" />
                    Top 100 Billboard Templates
                </h2>
                <p className="text-gray-400">
                    Instantly generate tracks using the legendary chord progressions and motifs behind the world's biggest hits.
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {hits.map((hit) => (
                    <div 
                        key={hit.id}
                        className="group bg-white/5 border border-white/10 hover:border-purple-500/50 hover:bg-white/10 rounded-xl p-5 transition-all cursor-pointer relative overflow-hidden"
                        onClick={() => handleLoad(hit)}
                    >
                        {/* Background Gradient on Hover */}
                        <div className="absolute inset-0 bg-gradient-to-br from-purple-500/0 to-blue-500/0 group-hover:from-purple-500/10 group-hover:to-blue-500/10 transition-all duration-500" />

                        <div className="relative z-10 flex flex-col h-full justify-between gap-4">
                            <div>
                                <div className="flex justify-between items-start mb-2">
                                    <span className="px-2 py-1 rounded-md bg-white/10 text-[10px] font-bold uppercase tracking-wider text-purple-300 border border-white/5">
                                        {hit.mood}
                                    </span>
                                    <span className="text-xs text-gray-500 font-mono">
                                        {hit.tempo} BPM
                                    </span>
                                </div>
                                <h3 className="text-lg font-bold text-white group-hover:text-purple-300 transition-colors">
                                    {hit.name}
                                </h3>
                                <p className="text-sm text-gray-400 mt-1 line-clamp-2">
                                    {hit.description}
                                </p>
                            </div>

                            <div className="flex items-center justify-between mt-2 pt-4 border-t border-white/5">
                                <div className="flex flex-col">
                                    <span className="text-[10px] text-gray-500 uppercase font-bold">Key</span>
                                    <span className="text-sm font-mono text-gray-300">{hit.key} {hit.scale}</span>
                                </div>
                                <button 
                                    className={`w-10 h-10 rounded-full flex items-center justify-center transition-all ${
                                        generatingId === hit.id 
                                        ? 'bg-purple-500 text-white' 
                                        : 'bg-white/10 text-white group-hover:bg-purple-500 group-hover:scale-110'
                                    }`}
                                >
                                    {generatingId === hit.id ? (
                                        <Loader2 className="w-5 h-5 animate-spin" />
                                    ) : (
                                        <Play className="w-5 h-5 fill-current ml-0.5" />
                                    )}
                                </button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default TopHits;
