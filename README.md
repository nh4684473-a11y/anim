# Universal MIDI Generator

A browser-based tool for music producers to generate chords and melodies across various genres (Trap, Pop, Jazz, House, etc.).

## Features
- **Multi-Genre Support**: Generate progressions for Trap, Drill, Lo-Fi, R&B, Jazz, House, Pop, and more.
- **Customizable**: Adjust Root Key, Scale, Mood, Complexity, and Tempo (BPM).
- **Instant Preview**: Listen to generated chords and melodies directly in the browser.
- **MIDI Export**: Download the generated MIDI file to use in your DAW.
- **Sample Library**: Browse and download pre-generated MIDI samples (Local/Docker only).

## Getting Started

### Local Development

#### Backend (Python)
1.  Navigate to `backend/`.
2.  Create a virtual environment: `python -m venv venv`
3.  Activate it: `source venv/bin/activate` (Mac/Linux) or `venv\Scripts\activate` (Windows)
4.  Install dependencies: `pip install -r requirements.txt`
5.  Run the server: `python app/main.py` (or `uvicorn app.main:app --reload`)

#### Frontend (React)
1.  Navigate to `frontend/`.
2.  Install dependencies: `npm install`
3.  Run the dev server: `npm run dev`

### Deployment (Docker)

You can run the entire stack using Docker Compose:

```bash
docker-compose up --build
```

The app will be available at `http://localhost:3000`.

### Vercel Deployment (Monorepo)

You can deploy the entire project (Frontend + Backend) to Vercel with a single push.

1.  Install Vercel CLI: `npm i -g vercel`
2.  Run `vercel` in the root directory.
3.  Vercel will detect the `vercel.json` configuration and deploy both the React frontend and Python backend.

**Note**: The MIDI samples library is excluded from Vercel deployment to stay within serverless function size limits. The core generation features will work fully.

### Cloud Deployment (Split)

#### Backend (Render/Railway/Heroku)
1.  Deploy the `backend` folder.
2.  The `Procfile` is included for Heroku/Render compatibility.
3.  Set the environment variables if necessary.

#### Frontend (Vercel/Netlify)
1.  Deploy the `frontend` folder.
2.  Set the `VITE_API_URL` environment variable to your deployed backend URL (e.g., `https://your-backend.onrender.com`).
3.  Vercel will automatically detect the Vite config and build command.

## Documentation
See [DESIGN.md](DESIGN.md) for the detailed architecture, algorithms, and roadmap.
