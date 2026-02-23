import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Music, Zap, Radio } from 'lucide-react';

const Header = () => {
    const location = useLocation();

    const isActive = (path) => location.pathname === path;

    return (
        <header className="flex items-center justify-between py-6 px-8 border-b border-white/5 bg-black/20 backdrop-blur-md sticky top-0 z-50">
            <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-purple-500/20">
                    <Music className="w-6 h-6 text-white" />
                </div>
                <div>
                    <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
                        MIDI GEN
                    </h1>
                    <span className="text-[10px] uppercase tracking-widest text-gray-500 font-bold">
                        Pro Edition
                    </span>
                </div>
            </div>

            <nav className="flex items-center gap-1 bg-black/40 p-1 rounded-xl border border-white/5">
                <Link 
                    to="/" 
                    className={`px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2 transition-all ${
                        isActive('/') 
                        ? 'bg-purple-600 text-white shadow-lg' 
                        : 'text-gray-400 hover:text-white hover:bg-white/5'
                    }`}
                >
                    <Zap className="w-4 h-4" />
                    Generator
                </Link>
                <Link 
                    to="/top-hits" 
                    className={`px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2 transition-all ${
                        isActive('/top-hits') 
                        ? 'bg-purple-600 text-white shadow-lg' 
                        : 'text-gray-400 hover:text-white hover:bg-white/5'
                    }`}
                >
                    <Radio className="w-4 h-4" />
                    Top 100 Hits
                </Link>
            </nav>
        </header>
    );
};

export default Header;
