
import axios from 'axios';

// Allow runtime configuration of API URL via window object (common pattern for embedded apps)
export const API_BASE_URL = window.PLUGIN_API_URL || import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export const generateChords = async (params) => {
    // Ensure integer fields are actually integers to prevent 422 errors
    // Also ensure required fields have defaults
    const safeParams = {
        ...params,
        key: params.key || "Random",
        scale: params.scale || "Random",
        mood: params.mood || "Random",
        tempo: Math.round(params.tempo || 120),
        length: Math.round(params.length || 4),
        source: params.source || "auto" // Add source parameter
    };
    try {
        const response = await axios.post(`${API_BASE_URL}/generate/chords`, safeParams);
        return response.data;
    } catch (error) {
        console.error("Error generating chords:", error);
        if (error.response) {
            console.error("Backend error detail:", error.response.data);
        }
        throw error;
    }
};

export const getTopHits = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/api/top-hits`);
        return response.data;
    } catch (error) {
        console.error("Error fetching top hits:", error);
        throw error;
    }
};

export const generateTopHit = async (templateId) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/generate/top-hit`, { template_id: templateId });
        return response.data;
    } catch (error) {
        console.error("Error generating top hit:", error);
        throw error;
    }
};

export const downloadMidi = async (data) => {
    try {
        // Handle both legacy (array) and new (object) formats
        let payload = {};
        
        if (Array.isArray(data)) {
             payload = { progression: data, tempo: 120 };
        } else {
             payload = {
                 progression: data.progression,
                 chords: data.chords,
                 melody: data.melody,
                 tempo: data.tempo || 120,
                 mood: data.mood || "neutral",
                 instruments: data.instruments || {}
             };
        }

        const response = await axios.post(`${API_BASE_URL}/download/midi`, payload, {
            responseType: 'blob', // Important for file download
        });
        
        // Create a link to download the file
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'progression.mid'); // Filename
        document.body.appendChild(link);
        link.click();
        link.remove();
    } catch (error) {
        console.error("Error downloading MIDI:", error);
        throw error;
    }
};
