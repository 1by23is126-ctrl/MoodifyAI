import base64
import hashlib
import json
import os
from collections import defaultdict
from typing import Dict, List

from services.popular_catalog import POPULAR_TRACKS
from services.spotify import clear_spotify_cache, enrich_catalog_artwork, enrich_track_if_available, is_available, search_spotify_tracks

CACHE_FILE = os.path.join(os.path.dirname(__file__), '..', 'music_catalog_cache.json')

LANGUAGE_FALLBACK_PALETTES = {
    'English': ['#2D66FF', '#59C6FF', '#7C46FF', '#4820E2', '#10B981'],
    'Hindi': ['#F97316', '#EA580C', '#FBBF24', '#DC2626', '#C026D3'],
    'Tamil': ['#2563EB', '#6366F1', '#34D399', '#0EA5E9', '#A855F7'],
    'Telugu': ['#10B981', '#14B8A6', '#0EA5E9', '#8B5CF6', '#EC4899'],
    'Kannada': ['#F43F5E', '#F97316', '#EAB308', '#22C55E', '#38BDF8']
}

LANGUAGE_FALLBACK_TEXT_PALETTE = {
    'English': ['#E0F2FE', '#FFFFFF'],
    'Hindi': ['#FFF7ED', '#FEF3C7'],
    'Tamil': ['#EFF6FF', '#EEF2FF'],
    'Telugu': ['#ECFDF5', '#F0F9FF'],
    'Kannada': ['#FEF3C7', '#FFEDD5']
}

SUPPORTED_LANGUAGES = [
    'English', 'Hindi', 'Tamil', 'Telugu', 'Kannada'
]

CATALOG_CACHE_VERSION = 5

LANGUAGE_ALIASES = {
    'english': 'English',
    'en': 'English',
    'eng': 'English',
    'english songs': 'English',
    'hindi': 'Hindi',
    'hi': 'Hindi',
    'hin': 'Hindi',
    'hindi songs': 'Hindi',
    'hindi music': 'Hindi',
    'kannada': 'Kannada',
    'kn': 'Kannada',
    'kan': 'Kannada',
    'kannad': 'Kannada',
    'kannada songs': 'Kannada',
    'kannada music': 'Kannada',
    'tamil': 'Tamil',
    'ta': 'Tamil',
    'tam': 'Tamil',
    'tamil songs': 'Tamil',
    'tamil music': 'Tamil',
    'telugu': 'Telugu',
    'te': 'Telugu',
    'tel': 'Telugu',
    'telugu songs': 'Telugu',
    'telugu music': 'Telugu',
}

MOOD_CATEGORIES = [
    'Happy', 'Sad', 'Heartbreak', 'Romantic', 'Lonely', 'Motivated', 'Energetic', 'Chill', 'Focus',
    'Party', 'Late Night', 'Rainy', 'Travel', 'Gym', 'Confidence', 'Nostalgia', 'Study', 'Sleep',
    'Anxiety Relief', 'Healing', 'Breakup Recovery'
]

TARGET_LANGUAGE_COUNTS = {
    'English': 60,
    'Hindi': 60,
    'Tamil': 60,
    'Telugu': 60,
    'Kannada': 60,
}

LANGUAGE_SEARCH_QUERIES = {
    'English': [
        'English heartbreak songs', 'English love ballads', 'English motivational anthems',
        'English chill songs', 'English rainy day songs', 'English high energy pop'
    ],
    'Hindi': [
        'Hindi heartbreak songs', 'Hindi romantic songs', 'Hindi motivational songs',
        'Hindi chill songs', 'Hindi sad songs', 'Hindi party songs'
    ],
    'Tamil': [
        'Tamil love songs', 'Tamil sad songs', 'Tamil energetic songs', 'Tamil romantic songs',
        'Tamil motivational songs', 'Tamil chill songs'
    ],
    'Telugu': [
        'Telugu love songs', 'Telugu sad songs', 'Telugu energetic songs',
        'Telugu romantic songs', 'Telugu motivational songs', 'Telugu party songs'
    ],
    'Kannada': [
        'Kannada love songs', 'Kannada sad songs', 'Kannada energetic songs',
        'Kannada chill songs', 'Kannada romantic songs', 'Kannada motivational songs'
    ],
}

_SEED_TRACKS = [
    {
        'title': 'Someone Like You',
        'artist': 'Adele',
        'language': 'English',
        'moodTags': ['Heartbreak', 'Sadness', 'Nostalgia'],
        'energyLevel': 30,
        'releaseYear': 2011
    },
    {
        'title': 'Glimpse of Us',
        'artist': 'Joji',
        'language': 'English',
        'moodTags': ['Heartbreak', 'Nostalgia', 'Lonely'],
        'energyLevel': 28,
        'releaseYear': 2022
    },
    {
        'title': 'Apocalypse',
        'artist': 'Cigarettes After Sex',
        'language': 'English',
        'moodTags': ['Romantic', 'Melancholy', 'Lonely'],
        'energyLevel': 26,
        'releaseYear': 2019
    },
    {
        'title': 'Yellow',
        'artist': 'Coldplay',
        'language': 'English',
        'moodTags': ['Romantic', 'Hopefulness', 'Warmth'],
        'energyLevel': 48,
        'releaseYear': 2000
    },
    {
        'title': 'Fix You',
        'artist': 'Coldplay',
        'language': 'English',
        'moodTags': ['Sadness', 'Healing', 'Hopefulness'],
        'energyLevel': 44,
        'releaseYear': 2005
    },
    {
        'title': 'Ocean Eyes',
        'artist': 'Billie Eilish',
        'language': 'English',
        'moodTags': ['Romantic', 'Serenity', 'Melancholy'],
        'energyLevel': 28,
        'releaseYear': 2016
    },
    {
        'title': 'Somebody Else',
        'artist': 'The 1975',
        'language': 'English',
        'moodTags': ['Lonely', 'Nostalgia', 'Heartbreak'],
        'energyLevel': 32,
        'releaseYear': 2016
    },
    {
        'title': 'After Hours',
        'artist': 'The Weeknd',
        'language': 'English',
        'moodTags': ['Night', 'Melancholy', 'Confidence'],
        'energyLevel': 62,
        'releaseYear': 2020
    },
    {
        'title': 'Sweater Weather',
        'artist': 'The Neighbourhood',
        'language': 'English',
        'moodTags': ['Romantic', 'Nostalgia', 'Chill'],
        'energyLevel': 54,
        'releaseYear': 2013
    },
    {
        'title': 'Daylight',
        'artist': 'Taylor Swift',
        'language': 'English',
        'moodTags': ['Hopefulness', 'Calmness', 'Romantic'],
        'energyLevel': 40,
        'releaseYear': 2019
    },
    {
        'title': 'Agar Tum Saath Ho',
        'artist': 'Alka Yagnik, Arijit Singh',
        'language': 'Hindi',
        'moodTags': ['Heartbreak', 'Sadness', 'Romantic'],
        'energyLevel': 28,
        'releaseYear': 2015
    },
    {
        'title': 'Channa Mereya',
        'artist': 'Arijit Singh',
        'language': 'Hindi',
        'moodTags': ['Heartbreak', 'Sadness', 'Nostalgia'],
        'energyLevel': 34,
        'releaseYear': 2016
    },
    {
        'title': 'Shayad',
        'artist': 'Arijit Singh',
        'language': 'Hindi',
        'moodTags': ['Romantic', 'Hopefulness', 'Introspection'],
        'energyLevel': 46,
        'releaseYear': 2020
    },
    {
        'title': 'Kesariya',
        'artist': 'Arijit Singh',
        'language': 'Hindi',
        'moodTags': ['Romantic', 'Warmth', 'Hopefulness'],
        'energyLevel': 52,
        'releaseYear': 2022
    },
    {
        'title': 'O Maahi',
        'artist': 'Prateek Kuhad',
        'language': 'Hindi',
        'moodTags': ['Romantic', 'Calmness', 'Nostalgia'],
        'energyLevel': 38,
        'releaseYear': 2022
    },
    {
        'title': 'Hawayein',
        'artist': 'Arijit Singh',
        'language': 'Hindi',
        'moodTags': ['Hopefulness', 'Romantic', 'Serenity'],
        'energyLevel': 46,
        'releaseYear': 2018
    },
    {
        'title': 'Phir Le Aya Dil',
        'artist': 'Arijit Singh',
        'language': 'Hindi',
        'moodTags': ['Nostalgia', 'Melancholy', 'Sadness'],
        'energyLevel': 24,
        'releaseYear': 2012
    },
    {
        'title': 'Ilahi',
        'artist': 'Arijit Singh',
        'language': 'Hindi',
        'moodTags': ['Travel', 'Hopefulness', 'Energy'],
        'energyLevel': 68,
        'releaseYear': 2012
    },
    {
        'title': 'Safarnama',
        'artist': 'Lucky Ali',
        'language': 'Hindi',
        'moodTags': ['Travel', 'Introspection', 'Hopefulness'],
        'energyLevel': 52,
        'releaseYear': 2007
    },
    {
        'title': 'Kho Gaye Hum Kahan',
        'artist': 'Jasleen Royal, Prateek Kuhad',
        'language': 'Hindi',
        'moodTags': ['Introspection', 'Nostalgia', 'Calmness'],
        'energyLevel': 36,
        'releaseYear': 2023
    },
    {
        'title': 'Naan Pizhai',
        'artist': 'Anirudh Ravichander',
        'language': 'Tamil',
        'moodTags': ['Heartbreak', 'Lonely', 'Sadness'],
        'energyLevel': 36,
        'releaseYear': 2023
    },
    {
        'title': 'Megham Karukatha',
        'artist': 'S. P. Balasubrahmanyam',
        'language': 'Tamil',
        'moodTags': ['Nostalgia', 'Romantic', 'Melancholy'],
        'energyLevel': 28,
        'releaseYear': 2000
    },
    {
        'title': 'Kannazhaga',
        'artist': 'Dhanush, Shruti Haasan',
        'language': 'Tamil',
        'moodTags': ['Romantic', 'Nostalgia', 'Calmness'],
        'energyLevel': 38,
        'releaseYear': 2014
    },
    {
        'title': 'Maruvaarthai',
        'artist': 'Sid Sriram',
        'language': 'Tamil',
        'moodTags': ['Melancholy', 'Romantic', 'Lonely'],
        'energyLevel': 32,
        'releaseYear': 2018
    },
    {
        'title': 'Thalli Pogathey',
        'artist': 'Sid Sriram',
        'language': 'Tamil',
        'moodTags': ['Romantic', 'Anxiety', 'Melancholy'],
        'energyLevel': 54,
        'releaseYear': 2016
    },
    {
        'title': 'New York Nagaram',
        'artist': 'A.R. Rahman',
        'language': 'Tamil',
        'moodTags': ['Lonely', 'Nostalgia', 'Melancholy'],
        'energyLevel': 30,
        'releaseYear': 2010
    },
    {
        'title': 'Kaathalae Kaathalae',
        'artist': 'Chinmayi, Govind Vasantha',
        'language': 'Tamil',
        'moodTags': ['Romantic', 'Serenity', 'Emotional Depth'],
        'energyLevel': 34,
        'releaseYear': 2019
    },
    {
        'title': 'Aaradhike',
        'artist': 'Vijay Yesudas',
        'language': 'Malayalam',
        'moodTags': ['Romantic', 'Serenity', 'Hopefulness'],
        'energyLevel': 46,
        'releaseYear': 2017
    },
    {
        'title': 'Malare',
        'artist': 'Vijay Yesudas',
        'language': 'Malayalam',
        'moodTags': ['Romantic', 'Nostalgia', 'Serenity'],
        'energyLevel': 40,
        'releaseYear': 2014
    },
    {
        'title': 'Pavizha Mazha',
        'artist': 'K S Harisankar',
        'language': 'Malayalam',
        'moodTags': ['Romantic', 'Calmness', 'Hopefulness'],
        'energyLevel': 44,
        'releaseYear': 2016
    },
    {
        'title': 'Darshana',
        'artist': 'Vijay Yesudas',
        'language': 'Malayalam',
        'moodTags': ['Romantic', 'Serenity', 'Hopefulness'],
        'energyLevel': 42,
        'releaseYear': 2015
    },
    {
        'title': 'Cherathukal',
        'artist': 'Sithara Krishnakumar, Sushin Shyam',
        'language': 'Malayalam',
        'moodTags': ['Melancholy', 'Serenity', 'Emotional Depth'],
        'energyLevel': 28,
        'releaseYear': 2021
    },
    {
        'title': 'Neela Nilave',
        'artist': 'Vishal Dadlani',
        'language': 'Malayalam',
        'moodTags': ['Romantic', 'Nostalgia', 'Calmness'],
        'energyLevel': 38,
        'releaseYear': 2011
    },
    {
        'title': 'Uyiril Thodum',
        'artist': 'Vijay Yesudas',
        'language': 'Malayalam',
        'moodTags': ['Romantic', 'Serenity', 'Nostalgia'],
        'energyLevel': 42,
        'releaseYear': 2014
    },
    {
        'title': 'Butta Bomma',
        'artist': 'Armaan Malik',
        'language': 'Telugu',
        'moodTags': ['Romantic', 'Confidence', 'Energy'],
        'energyLevel': 76,
        'releaseYear': 2020
    },
    {
        'title': 'Samajavaragamana',
        'artist': 'Sid Sriram',
        'language': 'Telugu',
        'moodTags': ['Romantic', 'Hopefulness', 'Energy'],
        'energyLevel': 70,
        'releaseYear': 2022
    },
    {
        'title': 'Naatu Naatu',
        'artist': 'M. M. Keeravani',
        'language': 'Telugu',
        'moodTags': ['Energy', 'Excitement', 'Party'],
        'energyLevel': 92,
        'releaseYear': 2022
    },
    {
        'title': 'Priyathama',
        'artist': 'Anurag Kulkarni',
        'language': 'Telugu',
        'moodTags': ['Romantic', 'Nostalgia', 'Calmness'],
        'energyLevel': 46,
        'releaseYear': 2020
    },
    {
        'title': 'Inkem Inkem Inkem Kaavaale',
        'artist': 'Sid Sriram',
        'language': 'Telugu',
        'moodTags': ['Romantic', 'Nostalgia', 'Serenity'],
        'energyLevel': 34,
        'releaseYear': 2018
    },
    {
        'title': 'Laung Laachi',
        'artist': 'Mannat Noor',
        'language': 'Punjabi',
        'moodTags': ['Romantic', 'Tradition', 'Nostalgia'],
        'energyLevel': 44,
        'releaseYear': 2018
    },
    {
        'title': '3 Peg',
        'artist': 'Sharry Mann',
        'language': 'Punjabi',
        'moodTags': ['Party', 'Energy', 'Confidence'],
        'energyLevel': 86,
        'releaseYear': 2016
    },
    {
        'title': 'Lamberghini',
        'artist': 'The Doorbeen',
        'language': 'Punjabi',
        'moodTags': ['Party', 'Confidence', 'Romantic'],
        'energyLevel': 84,
        'releaseYear': 2018
    },
    {
        'title': 'Khaab',
        'artist': 'Akull',
        'language': 'Punjabi',
        'moodTags': ['Romantic', 'Calmness', 'Nostalgia'],
        'energyLevel': 40,
        'releaseYear': 2016
    },
    {
        'title': 'Spring Day',
        'artist': 'BTS',
        'language': 'Korean',
        'moodTags': ['Nostalgia', 'Lonely', 'Hopefulness'],
        'energyLevel': 42,
        'releaseYear': 2017
    },
    {
        'title': 'Love Scenario',
        'artist': 'iKON',
        'language': 'Korean',
        'moodTags': ['Nostalgia', 'Romantic', 'Chill'],
        'energyLevel': 54,
        'releaseYear': 2018
    },
    {
        'title': 'Snow Flower',
        'artist': 'V',
        'language': 'Korean',
        'moodTags': ['Romantic', 'Calmness', 'Serenity'],
        'energyLevel': 32,
        'releaseYear': 2023
    },
    {
        'title': 'Dynamite',
        'artist': 'BTS',
        'language': 'Korean',
        'moodTags': ['Energy', 'Party', 'Confidence'],
        'energyLevel': 86,
        'releaseYear': 2020
    },
    {
        'title': 'Lemon',
        'artist': 'Kenshi Yonezu',
        'language': 'Japanese',
        'moodTags': ['Nostalgia', 'Melancholy', 'Romantic'],
        'energyLevel': 40,
        'releaseYear': 2018
    },
    {
        'title': 'First Love',
        'artist': 'Utada Hikaru',
        'language': 'Japanese',
        'moodTags': ['Romantic', 'Nostalgia', 'Melancholy'],
        'energyLevel': 34,
        'releaseYear': 1999
    },
    {
        'title': 'Pretender',
        'artist': 'Official HIGE DANDism',
        'language': 'Japanese',
        'moodTags': ['Romantic', 'Sadness', 'Nostalgia'],
        'energyLevel': 54,
        'releaseYear': 2019
    },
    {
        'title': 'Nandemonaiya',
        'artist': 'RADWIMPS',
        'language': 'Japanese',
        'moodTags': ['Nostalgia', 'Hopefulness', 'Emotional Depth'],
        'energyLevel': 38,
        'releaseYear': 2016
    },
]

_CATALOG_CACHE: List[Dict] = []


def normalize_language(value: str, default: str = None) -> str:
    key = ' '.join(str(value or '').strip().lower().replace('_', ' ').replace('-', ' ').split())
    normalized = LANGUAGE_ALIASES.get(key)
    if normalized:
        return normalized
    if default is not None:
        return normalize_language(default)
    return ''


def _track_identity(track: Dict) -> str:
    return f"{track.get('language', '').strip().lower()}|{track.get('artist', '').strip().lower()}|{track.get('title', '').strip().lower()}"


def _load_catalog_cache() -> List[Dict]:
    if not os.path.exists(CACHE_FILE):
        return []

    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as handle:
            data = json.load(handle)
            if isinstance(data, dict):
                if data.get('version') != CATALOG_CACHE_VERSION:
                    return []
                data = data.get('tracks', [])
            else:
                return []
            return [t for t in data if isinstance(t, dict)]
    except Exception:
        return []


def _save_catalog_cache(catalog: List[Dict]) -> None:
    try:
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, 'w', encoding='utf-8') as handle:
            json.dump({'version': CATALOG_CACHE_VERSION, 'tracks': catalog}, handle, indent=2, ensure_ascii=False)
    except Exception:
        pass


def _fallback_album_art(language: str, title: str, artist: str, mood_tags: List[str] = None, variant: int = 0) -> str:
    language_key = normalize_language(language, default='English')
    colors = LANGUAGE_FALLBACK_PALETTES.get(language_key, LANGUAGE_FALLBACK_PALETTES['English'])
    text_colors = LANGUAGE_FALLBACK_TEXT_PALETTE.get(language_key, LANGUAGE_FALLBACK_TEXT_PALETTE['English'])
    palette_seed = f"{language_key}|{title}|{artist}|{','.join(mood_tags or [])}|v{variant}"
    digest = hashlib.sha256(palette_seed.encode('utf-8')).hexdigest()
    primary_color = colors[int(digest[0:2], 16) % len(colors)]
    secondary_color = colors[int(digest[2:4], 16) % len(colors)]
    accent_color = colors[int(digest[4:6], 16) % len(colors)]
    title_color = text_colors[0]
    subtitle_color = text_colors[1]

    svg = f"""
<svg width='720' height='720' viewBox='0 0 720 720' xmlns='http://www.w3.org/2000/svg'>
  <defs>
    <linearGradient id='bg' x1='0' y1='0' x2='1' y2='1'>
      <stop offset='0%' stop-color='{primary_color}' />
      <stop offset='60%' stop-color='{secondary_color}' />
      <stop offset='100%' stop-color='{accent_color}' />
    </linearGradient>
    <linearGradient id='shine' x1='0' y1='0' x2='1' y2='1'>
      <stop offset='0%' stop-color='rgba(255,255,255,0.14)' />
      <stop offset='100%' stop-color='rgba(255,255,255,0)' />
    </linearGradient>
  </defs>
  <rect width='720' height='720' rx='64' fill='url(#bg)' />
  <circle cx='360' cy='220' r='170' fill='rgba(255,255,255,0.08)' />
  <circle cx='540' cy='120' r='90' fill='rgba(255,255,255,0.06)' />
  <circle cx='180' cy='540' r='100' fill='rgba(255,255,255,0.05)' />
  <rect x='60' y='480' width='600' height='120' rx='40' fill='rgba(255,255,255,0.06)' />
  <rect x='50' y='430' width='620' height='28' rx='14' fill='rgba(255,255,255,0.08)' />
  <rect x='120' y='560' width='120' height='16' rx='8' fill='rgba(255,255,255,0.08)' />
  <rect x='240' y='590' width='220' height='12' rx='6' fill='rgba(255,255,255,0.08)' />
  <rect x='490' y='560' width='120' height='16' rx='8' fill='rgba(255,255,255,0.08)' />
  <path d='M120 200 C180 120 320 120 380 200 C440 280 560 280 620 200' fill='none' stroke='rgba(255,255,255,0.18)' stroke-width='15' stroke-linecap='round' />
  <path d='M120 260 C180 190 320 190 380 260 C440 330 560 330 620 260' fill='none' stroke='rgba(255,255,255,0.12)' stroke-width='12' stroke-linecap='round' />
  <path d='M160 320 L240 240 L320 320 L400 240 L480 320' fill='none' stroke='rgba(255,255,255,0.12)' stroke-width='14' stroke-linecap='round' />
  <path d='M200 380 L260 340 L320 420 L380 360 L440 440' fill='none' stroke='rgba(255,255,255,0.12)' stroke-width='10' stroke-linecap='round' />
  <rect x='80' y='120' width='560' height='360' rx='40' fill='url(#shine)' />
  <text x='360' y='420' text-anchor='middle' font-family='Inter, sans-serif' font-size='64' font-weight='700' fill='{title_color}'>
    {title[:18]}
  </text>
  <text x='360' y='500' text-anchor='middle' font-family='Inter, sans-serif' font-size='28' fill='{subtitle_color}' opacity='0.92'>
    {artist[:32]}
  </text>
</svg>
"""
    svg_bytes = svg.encode('utf-8')
    encoded = base64.b64encode(svg_bytes).decode('ascii')
    return f'data:image/svg+xml;base64,{encoded}'


def _normalize_track(track: Dict, language: str = None, release_year: int = None) -> Dict:
    language = normalize_language(language or track.get('language'))
    if not language:
        return None
    title = str(track.get('title') or track.get('name') or '').strip()
    artist = str(track.get('artist') or track.get('artists') or '').strip()
    spotify_query = str(track.get('spotifyQuery') or f"{artist} {title}".strip())

    album_art = track.get('albumArt') or track.get('album_art') or track.get('image') or ''
    artwork_source = track.get('artworkSource') or ('spotify' if album_art else '')
    return {
        'title': title,
        'artist': artist,
        'language': language,
        'moodTags': [str(tag).strip() for tag in track.get('moodTags', []) if tag],
        'energyLevel': int(track.get('energyLevel', track.get('energy', 50) or 50)),
        'emotionalWeight': float(track.get('emotionalWeight', 0) or 0),
        'spotifyQuery': spotify_query,
        'albumArt': album_art,
        'albumArtHD': track.get('albumArtHD') or album_art,
        'albumArtMedium': track.get('albumArtMedium') or album_art,
        'albumArtThumb': track.get('albumArtThumb') or album_art,
        'artworkSource': artwork_source,
        'releaseYear': int(track.get('releaseYear') or release_year or 0),
        'spotifyUrl': track.get('spotifyUrl') or track.get('spotify_url') or '',
        'spotify_url': track.get('spotifyUrl') or track.get('spotify_url') or '',
        'spotifyId': track.get('spotifyId') or track.get('track_id') or track.get('trackId') or '',
        'track_id': track.get('track_id') or track.get('spotifyId') or track.get('trackId') or '',
        'trackId': track.get('trackId') or track.get('spotifyId') or track.get('track_id') or '',
        'isrc': track.get('isrc') or '',
        'previewUrl': track.get('previewUrl') or track.get('preview_url') or '',
        'preview_url': track.get('previewUrl') or track.get('preview_url') or '',
        'albumName': track.get('albumName') or track.get('album') or '',
        'album': track.get('album') or track.get('albumName') or '',
        'genre': track.get('genre') or track.get('genreName') or 'Indie',
        'subgenre': track.get('subgenre') or track.get('subGenre') or 'Contemporary',
        'valence': float(track.get('valence') or track.get('valenceScore') or 0.5),
        'acousticness': float(track.get('acousticness') or 0.5),
        'instrumentalness': float(track.get('instrumentalness') or 0.1),
        'popularityScore': int(track.get('popularityScore') or track.get('popularity') or 70),
        'popularity': track.get('popularity'),
        'artistImage': track.get('artistImage', ''),
        'artistGenres': track.get('artistGenres', []),
        'artistPopularity': track.get('artistPopularity'),
        'spotifyEnriched': bool(track.get('spotifyEnriched')),
        'artworkFailureReason': track.get('artworkFailureReason', ''),
        'artworkSource': artwork_source
    }


def _build_generated_catalog(language: str, target_count: int) -> List[Dict]:
    language = normalize_language(language)
    if not language:
        return []

    generated = []
    seen = set()
    for index, item in enumerate(POPULAR_TRACKS.get(language, [])):
        title, artist, mood_tags, energy_level, release_year, popularity_score = item
        track = {
            'title': title,
            'artist': artist,
            'language': language,
            'moodTags': list(mood_tags),
            'energyLevel': energy_level,
            'releaseYear': release_year,
            'genre': 'Popular',
            'subgenre': 'Curated hits',
            'valence': 0.72 if energy_level >= 70 else 0.42 if energy_level <= 40 else 0.58,
            'acousticness': 0.25 if energy_level >= 70 else 0.58,
            'instrumentalness': 0.02,
            'popularityScore': popularity_score,
            'albumName': '',
            'previewUrl': ''
        }
        normalized = _normalize_track(track, language=language, release_year=release_year)
        if not normalized:
            continue
        if not normalized.get('albumArt'):
            normalized['albumArt'] = _fallback_album_art(language, normalized['title'], normalized['artist'], normalized.get('moodTags'), index)
            normalized['album_art'] = normalized['albumArt']
            normalized['albumArtHD'] = normalized['albumArt']
            normalized['albumArtMedium'] = normalized['albumArt']
            normalized['albumArtThumb'] = normalized['albumArt']
            normalized['artworkSource'] = 'generated'
        identity = _track_identity(normalized)
        if identity in seen:
            continue
        seen.add(identity)
        normalized['emotionalWeight'] = normalized.get('emotionalWeight') or 72
        generated.append(normalized)
    return generated


def _seed_catalog() -> List[Dict]:
    seen = set()
    catalog = []
    for track in _SEED_TRACKS:
        normalized = _normalize_track(track)
        if not normalized:
            continue
        identity = _track_identity(normalized)
        if identity in seen:
            continue
        seen.add(identity)
        normalized['emotionalWeight'] = normalized.get('emotionalWeight') or 76
        catalog.append(normalized)

    for language in SUPPORTED_LANGUAGES:
        target_count = TARGET_LANGUAGE_COUNTS.get(language, 180)
        current_count = sum(1 for track in catalog if track['language'] == language)
        if current_count >= target_count:
            continue
        generated_tracks = _build_generated_catalog(language, target_count - current_count)
        for track in generated_tracks:
            identity = _track_identity(track)
            if identity in seen:
                continue
            seen.add(identity)
            catalog.append(track)
    return catalog


def _spotify_metadata_changed(before: Dict, after: Dict) -> bool:
    fields = [
        'albumArt', 'albumArtHD', 'albumArtMedium', 'albumArtThumb',
        'spotifyUrl', 'spotifyId', 'track_id', 'albumName', 'album',
        'popularity', 'popularityScore', 'artworkSource', 'artworkFailureReason'
    ]
    return any((before.get(field) or '') != (after.get(field) or '') for field in fields)


def _expand_catalog(catalog: List[Dict], force_spotify: bool = False) -> List[Dict]:
    expanded = list(catalog)
    changed = False

    if is_available():
        artwork_ready = enrich_catalog_artwork(expanded, force=force_spotify)
        changed = changed or any(
            _spotify_metadata_changed(before, after)
            for before, after in zip(expanded, artwork_ready)
        )
        expanded = artwork_ready

    if changed:
        _save_catalog_cache(expanded)

    expanded = _validate_unique_artwork(expanded)

    deduped = {}
    for track in expanded:
        deduped[_track_identity(track)] = track
    return list(deduped.values())


def rebuild_spotify_catalog_cache() -> Dict:
    global _CATALOG_CACHE
    clear_spotify_cache()
    catalog = _seed_catalog()
    enriched, report = enrich_catalog_artwork(catalog, force=True, return_report=True)
    normalized_catalog = []
    seen = set()
    for track in enriched:
        normalized = _normalize_track(track)
        if not normalized:
            continue
        identity = _track_identity(normalized)
        if identity in seen:
            continue
        seen.add(identity)
        normalized_catalog.append(normalized)
    _save_catalog_cache(normalized_catalog)
    _CATALOG_CACHE = normalized_catalog
    return report


def _validate_unique_artwork(catalog: List[Dict]) -> List[Dict]:
    artwork_assets = {}
    for track in catalog:
        art = track.get('albumArt')
        if not art:
            continue
        identity = _track_identity(track)
        if art not in artwork_assets:
            artwork_assets[art] = [track]
        else:
            artwork_assets[art].append(track)

    for art, tracks in artwork_assets.items():
        if len(tracks) < 2:
            continue
        for track in tracks[1:]:
            if not track.get('artworkSource'):
                track['artworkSource'] = ''
    return catalog


def get_catalog() -> List[Dict]:
    global _CATALOG_CACHE
    if _CATALOG_CACHE:
        return _CATALOG_CACHE

    cached_catalog = _load_catalog_cache()
    if cached_catalog and len(cached_catalog) >= 300:
        catalog = cached_catalog
        if is_available() and any(
            not track.get('spotifyId')
            or not track.get('spotifyUrl')
            or str(track.get('albumArt') or '').startswith('data:')
            or track.get('artworkSource') == 'generated'
            for track in catalog
        ):
            catalog = _expand_catalog(catalog)
    else:
        catalog = _seed_catalog()
        catalog = _expand_catalog(catalog)

    if not catalog or len(catalog) < 300:
        catalog = _seed_catalog()
        catalog = _expand_catalog(catalog)

    if not catalog:
        catalog = _seed_catalog()

    normalized_catalog = []
    seen = set()
    for track in catalog:
        normalized = _normalize_track(track)
        if not normalized:
            continue
        identity = _track_identity(normalized)
        if identity in seen:
            continue
        seen.add(identity)
        normalized_catalog.append(normalized)

    _CATALOG_CACHE = normalized_catalog
    return _CATALOG_CACHE


def get_language_tracks(language: str) -> List[Dict]:
    language = normalize_language(language)
    if not language:
        return []
    return [
        track for track in get_catalog()
        if normalize_language(track.get('language')) == language
    ]


def get_fallback_tracks(mood: str, limit: int = 5, language: str = 'English') -> List[Dict]:
    mood = str(mood or 'Chill').strip()
    language = normalize_language(language, default='English')
    candidates = [
        track for track in get_language_tracks(language)
        if any(str(tag).strip().lower() == mood.lower() for tag in track.get('moodTags', []))
    ]
    if not candidates:
        candidates = get_language_tracks(language)

    candidates = sorted(
        candidates,
        key=lambda track: (-('Chill' in track.get('moodTags', [])), track.get('energyLevel', 50))
    )

    selected = []
    identity_set = set()
    for track in candidates:
        identity = _track_identity(track)
        if identity in identity_set:
            continue
        selected.append(track)
        identity_set.add(identity)
        if len(selected) >= limit:
            break

    return [
        {
            'title': track['title'],
            'name': track['title'],
            'artist': track['artist'],
            'language': track.get('language', language),
            'albumArt': track.get('albumArt', ''),
            'album_art': track.get('albumArt', ''),
            'spotifyUrl': track.get('spotifyUrl', ''),
            'spotify_url': track.get('spotifyUrl', ''),
            'preview_url': track.get('previewUrl', '')
        }
        for track in selected
    ]


def get_target_language_count(language: str) -> int:
    return TARGET_LANGUAGE_COUNTS.get(normalize_language(language, default='English'), 150)