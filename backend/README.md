# Backend — Moodify AI

## Setup

1. Create a virtualenv and install dependencies:

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and add Spotify credentials if available.

3. Run the backend server:

```bash
python app.py
```

The backend listens on port `5000` by default.

## API Endpoints

- `POST /api/analyze`
  - Request JSON: `{ "text": "..." }`
  - Returns mood, scores, playlist title, genres, Spotify tracks, and explanation.

- `GET /api/history`
  - Returns recent mood entries stored in SQLite.

- `GET /api/analytics`
  - Returns weekly mood trends, total entries, and most common mood.

- `GET /api/recommendations?mood=Happy&energy=80`
  - Returns playlist recommendations and Spotify search queries for a given mood.

- `GET /api/spotify/search?q=track+name`
  - Performs a Spotify track lookup and returns album art, preview, and external URLs.
