# MoodifyAI — Product Requirements & Architecture

## Original Problem Statement
Transform an existing fully functional MoodifyAI emotional music recommendation app into a **startup-quality, premium AI product** (like OpenAI / Spotify / Linear / Arc / Vercel / Notion / Apple / Perplexity). UI/UX-only enhancements with strict rules:

* DO NOT change architecture, folder structure, file names, libraries, or business logic.
* DO NOT modify backend logic, API routes, recommendation algorithms, data flow, or remove features.
* ONLY improve UI, UX, animations, transitions, and visual polish while keeping every feature working exactly as before.

User design direction: **"surprise me"** → I selected an **Editorial AI Studio** aesthetic: deep obsidian with warm undertones, luminous mood-driven accents, Clash Display + Instrument Serif italic for editorial moments, refined 3-tier glass system, restrained cinematic motion, grain texture overlay.

## Architecture (untouched)
- **Frontend**: Vite + React 18 + Tailwind + framer-motion + recharts + react-three/fiber. Served on port 3000.
- **Backend**: Flask 2 (`app.py`) with blueprint at `/api/*`, wrapped as ASGI via `asgiref.WsgiToAsgi` (`server.py`) so supervisor's `uvicorn server:app` command works. Port 8001.
- **Storage**: SQLite (`moodify.db`) via `services/database.py`.
- **External**: Spotify Web API (client credentials), in-memory rate limiting.
- **Routing**: Kubernetes ingress sends `/api/*` to backend:8001, everything else to frontend:3000. Frontend uses `VITE_API_URL` (set to the preview URL).

## Tech Stack notes
- `package.json` script `start` added → runs `vite` so `yarn start` works under supervisor.
- `vite.config.js` configured with host 0.0.0.0, port 3000, `allowedHosts: true`, HMR over wss:443 for the preview proxy.

## User Personas
1. **Emotional listener** — types or speaks how they feel, gets a soundscape tuned to mood + time-of-day.
2. **Analytics-curious user** — checks their emotional trajectory over time.
3. **Multi-lingual** — picks between English / Hindi / Kannada / Tamil / Telugu recommendation tracks.

## Core Requirements (static)
- Single-page experience with phases: idle → analyzing → results → analytics.
- Premium dark aesthetic, mood-driven CSS variable theme (12 mood palettes).
- Cinematic transitions: blur + lift + scale.
- Glass elevation hierarchy (1, 2, 3).
- Spotify track cards with album artwork, hover shine, play overlay.
- Multilingual language tabs.
- Mood spectrum (emotion bars + dimension chips).
- Analytics dashboard with intensity chart + recent records.
- Custom cursor (desktop only), particle field, mood background blobs.
- Status banner for errors with dismiss.

## What's Been Implemented (Jan 2026 session)
- Replaced `/app/frontend` + `/app/backend` with the uploaded MoodifyAI codebase.
- Added `backend/server.py` ASGI shim → uvicorn loads Flask via asgiref.
- Added `backend/.env` with Spotify credentials + Mongo placeholders (Mongo not used).
- Updated `frontend/.env` with `VITE_API_URL` + `REACT_APP_BACKEND_URL` pointing at the preview URL.
- Patched `package.json` to expose `yarn start` and `vite.config.js` for the preview host.
- **Design system** (`src/styles/index.css`) rebuilt from scratch — palette, 3 glass tiers, typography hierarchy (Inter body, Clash Display headings, Instrument Serif italic accents), button + input + tabs + analytics styles, soft cinematic shadows, grain overlay, mood result hero monogram, ease curves.
- **HeroSection** — refined eyebrow chip, two-tone gradient accent, editorial italic on "inner".
- **MoodInput** — premium glass shell with focus ring gradient, cycling placeholders, voice mic + keyboard hint + char counter, refined Synthesize button.
- **AnalysisLoader** — cinematic rotating rings, breathing halo, status phases, progress dots.
- **EcosystemWidgets** — refined logo with tagline, time/date widget, analytics toggle, engine status indicator.
- **CinematicReveal** — editorial layout: mood result hero with monogram + italic accent on time, mood pills, explanation; MoodSpectrum panel; track grid with kicker + italic accent.
- **TrackCard** — refined album art frame, hover shine, play overlay, language pill.
- **MoodSpectrum** — emotion bars with smooth stagger fills, dimension chips.
- **AnalyticsDashboard** — uses `VITE_API_URL` (fixed hardcoded localhost), tolerates `{history: [...]}` or array payload; new layout: title with italic, big Total Logs counter, Most Frequent mood, area chart with mood-primary gradient, refined recent records list.
- **MoodBackground** — three soft blobs with longer float cycles, vignette.
- **Particles** — reduced density, softer easing.
- **CustomCursor** — refined size, smoother spring, mix-blend-screen.
- **StatusBanner** — premium animated entry with dismiss button.
- **VoiceMic** — refined hover/active states, double ping animation.
- **App.jsx** — orb hidden during analyzing phase so loader is unobstructed; faster phase transitions so the analyzing UI is visible long enough.

## Prioritized Backlog
### P1 — Nice to add
1. Save tracks to a personal favorites list (requires backend extension — out of UI-only scope this session).
2. Share button on results — copy a shareable link / image of the soundscape.
3. Light theme toggle.

### P2 — Polish
1. Reduced-motion alternative for the loader rings.
2. Skeleton loading for the analytics chart while history is empty.
3. Custom album-art fallback artwork (currently uses a placeholder).

## Verified by testing agent (Jan 2026)
- All happy paths verified end-to-end at 1920×1080 and 375×667.
- POST `/api/analyze`, GET `/api/history`, GET `/api/analytics` all healthy.
- All data-testids present and wired correctly.
- 0 functional defects. Only minor console warnings (now fixed: `fetchPriority` → `fetchpriority`, removed rgba from THREE.Color light prop).

## Next Action Items
1. Optional: implement P1 backlog items (favorites/share).
2. Optional: connect analytics chart to a richer metric (e.g., daily mood mix) for visual depth.
