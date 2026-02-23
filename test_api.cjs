
const API_BASE_URL = 'http://localhost:8000';

const getSamples = async () => {
    try {
        console.log(`Fetching from ${API_BASE_URL}/list/samples`);
        const response = await fetch(`${API_BASE_URL}/list/samples`);
        console.log("Status:", response.status);
        const data = await response.json();
        console.log("Data keys:", Object.keys(data));
        const samples = data.samples;
        console.log("Samples count:", samples.length);
        if (samples.length > 0) {
            console.log("First sample:", samples[0]);
        }
    } catch (error) {
        console.error("Error fetching samples:", error.message);
    }
};

getSamples();
