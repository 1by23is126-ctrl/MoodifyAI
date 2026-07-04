from datetime import datetime
from services.music_database import get_fallback_tracks, get_language_tracks, normalize_language, SUPPORTED_LANGUAGES
from urllib.parse import quote
from collections import Counter, defaultdict, deque
import hashlib
import random
import time

MOOD_MAP = {
    'Happy': {
        'genres': ['Pop', 'Indie Pop', 'Synthwave', 'Dance-Pop'],
        'queries': ['Pharrell Williams Happy', 'Dua Lipa Levitating', 'Lizzo Good as Hell', 'Uptown Funk', 'Walking on Sunshine', "Can't Stop the Feeling"],
        'playlists': ['Neon Daydream', 'Bright Energy', 'Sun-Drenched']
    },
    'Sad': {
        'genres': ['Indie', 'Acoustic', 'Piano', 'Dream Pop'],
        'queries': ['Adele Someone Like You', 'Bon Iver Holocene', 'Sam Smith Stay With Me', 'Coldplay Fix You', 'Lord Huron The Night We Met', 'Sufjan Stevens'],
        'playlists': ['Midnight Reflection', 'Rainy Window', 'Quiet Tears']
    },
    'Angry': {
        'genres': ['Rock', 'Metal', 'Alternative', 'Punk'],
        'queries': ['Rage Against The Machine', 'Metallica Enter Sandman', 'Slipknot Duality', 'System of a Down Chop Suey', 'Limp Bizkit Break Stuff', 'Deftones'],
        'playlists': ['Voltage Surge', 'Riot Pulse', 'Catharsis']
    },
    'Chill': {
        'genres': ['Ambient', 'Lo-Fi', 'Downtempo', 'Chillwave'],
        'queries': ['Tycho Awake', 'Lo-fi Beats', 'Bonobo Cirrus', 'Petit Biscuit Sunset Lover', 'M83 Midnight City', 'The xx Intro'],
        'playlists': ['Moonlit Calm', 'Warm Glow', 'Drifting']
    },
    'Romantic': {
        'genres': ['R&B', 'Soul', 'Dream Pop', 'Acoustic'],
        'queries': ['Sade No Ordinary Love', 'Norah Jones Come Away', 'John Legend All of Me', 'Ed Sheeran Perfect', 'Taylor Swift Lover', 'Hozier'],
        'playlists': ['Velvet Heart', 'Soft Focus', 'Intimate Hours']
    },
    'Motivated': {
        'genres': ['Hip-Hop', 'Pop', 'Electro', 'Rock'],
        'queries': ['Eminem Lose Yourself', 'Kanye Stronger', 'Survivor Eye of the Tiger', 'Fort Minor Remember The Name', 'Eminem Till I Collapse', 'Neffex'],
        'playlists': ['Ascend', 'Power Burst', 'Unstoppable']
    },
    'Lonely': {
        'genres': ['Singer-Songwriter', 'Indie', 'Ambient', 'Folk'],
        'queries': ['The National I Need My Girl', 'Damien Rice', 'Cigarettes After Sex', 'Bon Iver Skinny Love', 'Lorde Liability', 'Phoebe Bridgers'],
        'playlists': ['Solitude Sphere', 'Quiet Roads', 'Echoes']
    },
    'Energetic': {
        'genres': ['Electronic', 'Dance', 'Pop', 'House'],
        'queries': ['Calvin Harris Summer', 'Chemical Brothers Go', 'David Guetta Titanium', 'Queen Dont Stop Me Now', 'Avicii Levels', 'Daft Punk One More Time'],
        'playlists': ['Neon Rush', 'After Hours', 'High Voltage']
    },
    'Focus': {
        'genres': ['Ambient', 'Classical', 'Lo-Fi', 'Electronic'],
        'queries': ['Marconi Union Weightless', 'Brian Eno', 'Aphex Twin Avril 14th', 'Erik Satie Gymnopedie', 'Hans Zimmer Time', 'Max Richter'],
        'playlists': ['Deep Flow', 'Cognitive Prism', 'Study Space']
    },
    'Late Night': {
        'genres': ['Synthwave', 'R&B', 'Dark Pop', 'Chillwave'],
        'queries': ['Kavinsky Nightcall', 'The Weeknd Starboy', 'HOME Resonance', 'The Weeknd After Hours', 'Sidewalks and Skeletons Goth', 'Joji'],
        'playlists': ['Night Drive', '2AM Cruising', 'Neon Shadows']
    },
    'Rainy': {
        'genres': ['Acoustic', 'Lo-Fi', 'Indie Folk', 'Ambient'],
        'queries': ['Massive Attack Teardrop', 'Radiohead All I Need', 'Rufus Wainwright Cigarettes', 'Bon Iver Rosyln', 'Coldplay The Scientist', 'Novo Amor'],
        'playlists': ['Grey Skies', 'Raindrops', 'Cozy Indoors']
    },
    'Party': {
        'genres': ['Pop', 'Hip-Hop', 'Dance', 'Reggaeton'],
        'queries': ['Black Eyed Peas I Gotta Feeling', 'Usher Yeah', 'Don Omar Danza Kuduro', 'The Killers Mr Brightside', 'LMFAO Party Rock', 'Pitbull'],
        'playlists': ['Weekend Anthem', 'House Party', 'Turn Up']
    }
}

TIME_THEMES = {
    'morning': 'Morning',
    'afternoon': 'Day',
    'evening': 'Evening',
    'night': 'Night'
}

EMOTION_QUERY_MAP = {
    'Melancholy': ['Bon Iver Holocene', 'Massive Attack Teardrop', 'Novo Amor Anchor'],
    'Introspection': ['Max Richter On The Nature Of Daylight', 'The xx Intro', 'Brian Eno An Ending'],
    'Calmness': ['Tycho Awake', 'Marconi Union Weightless', 'Bonobo Cirrus'],
    'Loneliness': ['The National I Need My Girl', 'Cigarettes After Sex Apocalypse', 'Lorde Liability'],
    'Nostalgia': ['Lord Huron The Night We Met', 'M83 Wait', 'Sufjan Stevens Mystery of Love'],
    'Hopefulness': ['Coldplay Fix You', 'Sigur Ros Hoppipolla', 'Florence Dog Days Are Over'],
    'Confidence': ['Eminem Lose Yourself', 'Kanye West Stronger', 'Fort Minor Remember The Name'],
    'Energy': ['Daft Punk One More Time', 'Avicii Levels', 'Calvin Harris Summer'],
    'Excitement': ['Dua Lipa Levitating', 'The Chemical Brothers Go', 'Queen Dont Stop Me Now'],
    'Romantic Warmth': ['Sade No Ordinary Love', 'Hozier Like Real People Do', 'Norah Jones Come Away With Me'],
    'Anxiety': ['Radiohead Everything In Its Right Place', 'Massive Attack Angel', 'Jon Hopkins Abandon Window'],
    'Anger': ['Rage Against The Machine Killing In The Name', 'Deftones Change', 'System of a Down Chop Suey'],
    'Motivation': ['Survivor Eye of the Tiger', 'Hans Zimmer Time', 'Eminem Till I Collapse'],
    'Serenity': ['Erik Satie Gymnopedie', 'Aphex Twin Avril 14th', 'Brian Eno 1/1'],
    'Sadness': ['Adele Someone Like You', 'Bon Iver Skinny Love', 'Coldplay The Scientist']
}

EMOTION_GENRE_MAP = {
    'Melancholy': ['Ambient', 'Indie Folk'],
    'Introspection': ['Modern Classical', 'Ambient'],
    'Calmness': ['Downtempo', 'Lo-Fi'],
    'Loneliness': ['Singer-Songwriter', 'Dream Pop'],
    'Nostalgia': ['Indie', 'Dream Pop'],
    'Hopefulness': ['Indie Pop', 'Post-Rock'],
    'Confidence': ['Hip-Hop', 'Electro'],
    'Energy': ['Electronic', 'Dance'],
    'Excitement': ['Dance-Pop', 'House'],
    'Romantic Warmth': ['R&B', 'Soul'],
    'Anxiety': ['Trip-Hop', 'Ambient'],
    'Anger': ['Alternative Rock', 'Metal'],
    'Motivation': ['Cinematic', 'Hip-Hop'],
    'Serenity': ['Classical', 'Ambient'],
    'Sadness': ['Piano', 'Acoustic']
}

LANGUAGES = list(SUPPORTED_LANGUAGES)
RECENT_TRACKS = deque(maxlen=180)
TRACK_EXPOSURE = Counter()
SESSION_TRACK_HISTORY = defaultdict(list)

EMOTION_AFFINITY = {
    'Burnout': {'Calmness': 0.45, 'Serenity': 0.34, 'Introspection': 0.28, 'Sadness': 0.18},
    'Mental Fatigue': {'Calmness': 0.42, 'Serenity': 0.36, 'Focus': 0.22, 'Introspection': 0.18},
    'Hopelessness': {'Sadness': 0.42, 'Melancholy': 0.32, 'Loneliness': 0.28, 'Hopefulness': -0.14},
    'Emotional Numbness': {'Melancholy': 0.34, 'Introspection': 0.30, 'Serenity': 0.20, 'Energy': -0.20},
    'Existential Emptiness': {'Introspection': 0.46, 'Melancholy': 0.34, 'Loneliness': 0.24, 'Serenity': 0.16},
    'Quiet Healing': {'Hopefulness': 0.42, 'Serenity': 0.34, 'Calmness': 0.30, 'Sadness': 0.16},
    'Grief Acceptance': {'Sadness': 0.34, 'Serenity': 0.30, 'Hopefulness': 0.24, 'Nostalgia': 0.22},
    'Late Night Overthinking': {'Introspection': 0.44, 'Anxiety': 0.28, 'Melancholy': 0.24, 'Calmness': 0.12},
    'Euphoric Confidence': {'Confidence': 0.46, 'Energy': 0.34, 'Excitement': 0.28, 'Motivation': 0.22},
}

def _track_identity(track):
    return f"{track.get('language', '')}:{track.get('artist', '')}:{track.get('title', '')}".lower()

def _rotation_seed(analysis, language):
    base = '|'.join([language, analysis.get('archetype', ''), analysis.get('nuancedLabel', ''), str(time.time_ns())])
    return int(hashlib.sha256(base.encode('utf-8')).hexdigest()[:12], 16)

# ──────────────────────────────────────────────────────────────────────────────
# MULTILINGUAL CATALOG  — 50 English + 50 Hindi + 50 Kannada
# ──────────────────────────────────────────────────────────────────────────────
MULTILINGUAL_CATALOG = [

    # ── ENGLISH (50 songs) ────────────────────────────────────────────────────
    # Melancholic / Introspective
    {'title': 'Holocene', 'artist': 'Bon Iver', 'language': 'English',
     'moodTags': ['Melancholy', 'Introspection', 'Calmness'], 'energyLevel': 24},
    {'title': 'Skinny Love', 'artist': 'Bon Iver', 'language': 'English',
     'moodTags': ['Loneliness', 'Melancholy', 'Sadness'], 'energyLevel': 28},
    {'title': 'Flume', 'artist': 'Bon Iver', 'language': 'English',
     'moodTags': ['Introspection', 'Serenity', 'Calmness'], 'energyLevel': 20},
    {'title': 'The Night We Met', 'artist': 'Lord Huron', 'language': 'English',
     'moodTags': ['Nostalgia', 'Sadness', 'Loneliness'], 'energyLevel': 22},
    {'title': 'Slow Burn', 'artist': 'Kacey Musgraves', 'language': 'English',
     'moodTags': ['Serenity', 'Hopefulness', 'Calmness'], 'energyLevel': 36},
    {'title': 'Teardrop', 'artist': 'Massive Attack', 'language': 'English',
     'moodTags': ['Melancholy', 'Anxiety', 'Introspection'], 'energyLevel': 42},
    {'title': 'Intro', 'artist': 'The xx', 'language': 'English',
     'moodTags': ['Introspection', 'Calmness', 'Loneliness'], 'energyLevel': 32},
    {'title': 'Apocalypse', 'artist': 'Cigarettes After Sex', 'language': 'English',
     'moodTags': ['Loneliness', 'Romantic Warmth', 'Melancholy'], 'energyLevel': 26},
    {'title': 'Nothing\'s Gonna Hurt You Baby', 'artist': 'Cigarettes After Sex', 'language': 'English',
     'moodTags': ['Romantic Warmth', 'Calmness', 'Serenity'], 'energyLevel': 22},
    {'title': 'Liability', 'artist': 'Lorde', 'language': 'English',
     'moodTags': ['Loneliness', 'Sadness', 'Introspection'], 'energyLevel': 28},

    # Sad / Healing
    {'title': 'Someone Like You', 'artist': 'Adele', 'language': 'English',
     'moodTags': ['Sadness', 'Nostalgia', 'Loneliness'], 'energyLevel': 30},
    {'title': 'Hello', 'artist': 'Adele', 'language': 'English',
     'moodTags': ['Sadness', 'Nostalgia', 'Introspection'], 'energyLevel': 34},
    {'title': 'Fix You', 'artist': 'Coldplay', 'language': 'English',
     'moodTags': ['Sadness', 'Hopefulness', 'Healing'], 'energyLevel': 44},
    {'title': 'The Scientist', 'artist': 'Coldplay', 'language': 'English',
     'moodTags': ['Sadness', 'Nostalgia', 'Introspection'], 'energyLevel': 30},
    {'title': 'Ghost', 'artist': 'Justin Bieber', 'language': 'English',
     'moodTags': ['Nostalgia', 'Sadness', 'Loneliness'], 'energyLevel': 38},
    {'title': 'Driver\'s License', 'artist': 'Olivia Rodrigo', 'language': 'English',
     'moodTags': ['Sadness', 'Nostalgia', 'Loneliness'], 'energyLevel': 32},
    {'title': 'Bleeding Out', 'artist': 'Imagine Dragons', 'language': 'English',
     'moodTags': ['Sadness', 'Melancholy', 'Hopefulness'], 'energyLevel': 52},
    {'title': 'I Will Follow You into the Dark', 'artist': 'Death Cab for Cutie', 'language': 'English',
     'moodTags': ['Romantic Warmth', 'Melancholy', 'Nostalgia'], 'energyLevel': 26},
    {'title': 'Mystery of Love', 'artist': 'Sufjan Stevens', 'language': 'English',
     'moodTags': ['Romantic Warmth', 'Nostalgia', 'Serenity'], 'energyLevel': 28},
    {'title': 'Motion Sickness', 'artist': 'Phoebe Bridgers', 'language': 'English',
     'moodTags': ['Introspection', 'Melancholy', 'Nostalgia'], 'energyLevel': 44},

    # Chill / Ambient
    {'title': 'Weightless', 'artist': 'Marconi Union', 'language': 'English',
     'moodTags': ['Serenity', 'Calmness', 'Introspection'], 'energyLevel': 12},
    {'title': 'Awake', 'artist': 'Tycho', 'language': 'English',
     'moodTags': ['Calmness', 'Focus', 'Serenity'], 'energyLevel': 46},
    {'title': 'Cirrus', 'artist': 'Bonobo', 'language': 'English',
     'moodTags': ['Calmness', 'Introspection', 'Serenity'], 'energyLevel': 50},
    {'title': 'Sunset Lover', 'artist': 'Petit Biscuit', 'language': 'English',
     'moodTags': ['Serenity', 'Calmness', 'Hopefulness'], 'energyLevel': 54},
    {'title': 'An Ending (Ascent)', 'artist': 'Brian Eno', 'language': 'English',
     'moodTags': ['Serenity', 'Introspection', 'Calmness'], 'energyLevel': 16},
    {'title': 'Slow Dancing in the Dark', 'artist': 'Joji', 'language': 'English',
     'moodTags': ['Melancholy', 'Loneliness', 'Romantic Warmth'], 'energyLevel': 30},
    {'title': 'Glimpse of Us', 'artist': 'Joji', 'language': 'English',
     'moodTags': ['Sadness', 'Nostalgia', 'Loneliness'], 'energyLevel': 26},
    {'title': 'Afterthought', 'artist': 'Joji', 'language': 'English',
     'moodTags': ['Melancholy', 'Loneliness', 'Introspection'], 'energyLevel': 34},

    # Romantic
    {'title': 'No Ordinary Love', 'artist': 'Sade', 'language': 'English',
     'moodTags': ['Romantic Warmth', 'Calmness', 'Nostalgia'], 'energyLevel': 38},
    {'title': 'Perfect', 'artist': 'Ed Sheeran', 'language': 'English',
     'moodTags': ['Romantic Warmth', 'Hopefulness', 'Nostalgia'], 'energyLevel': 44},
    {'title': 'Lover', 'artist': 'Taylor Swift', 'language': 'English',
     'moodTags': ['Romantic Warmth', 'Hopefulness', 'Excitement'], 'energyLevel': 52},
    {'title': 'Wildest Dreams', 'artist': 'Taylor Swift', 'language': 'English',
     'moodTags': ['Romantic Warmth', 'Nostalgia', 'Melancholy'], 'energyLevel': 56},
    {'title': 'Cornerstone', 'artist': 'Arctic Monkeys', 'language': 'English',
     'moodTags': ['Nostalgia', 'Loneliness', 'Romantic Warmth'], 'energyLevel': 38},
    {'title': 'Do I Wanna Know?', 'artist': 'Arctic Monkeys', 'language': 'English',
     'moodTags': ['Romantic Warmth', 'Anxiety', 'Introspection'], 'energyLevel': 56},
    {'title': 'Like Real People Do', 'artist': 'Hozier', 'language': 'English',
     'moodTags': ['Romantic Warmth', 'Serenity', 'Hopefulness'], 'energyLevel': 40},
    {'title': 'Cherry Wine', 'artist': 'Hozier', 'language': 'English',
     'moodTags': ['Melancholy', 'Romantic Warmth', 'Introspection'], 'energyLevel': 32},

    # Nostalgic / Late Night
    {'title': 'After Hours', 'artist': 'The Weeknd', 'language': 'English',
     'moodTags': ['Melancholy', 'Nostalgia', 'Loneliness'], 'energyLevel': 44},
    {'title': 'Blinding Lights', 'artist': 'The Weeknd', 'language': 'English',
     'moodTags': ['Nostalgia', 'Excitement', 'Energy'], 'energyLevel': 72},
    {'title': 'Starboy', 'artist': 'The Weeknd', 'language': 'English',
     'moodTags': ['Confidence', 'Introspection', 'Nostalgia'], 'energyLevel': 64},
    {'title': 'Nightcall', 'artist': 'Kavinsky', 'language': 'English',
     'moodTags': ['Introspection', 'Nostalgia', 'Calmness'], 'energyLevel': 54},
    {'title': 'bad guy', 'artist': 'Billie Eilish', 'language': 'English',
     'moodTags': ['Confidence', 'Excitement', 'Introspection'], 'energyLevel': 66},
    {'title': 'when the party\'s over', 'artist': 'Billie Eilish', 'language': 'English',
     'moodTags': ['Sadness', 'Loneliness', 'Introspection'], 'energyLevel': 20},
    {'title': 'Ocean Eyes', 'artist': 'Billie Eilish', 'language': 'English',
     'moodTags': ['Romantic Warmth', 'Melancholy', 'Serenity'], 'energyLevel': 28},

    # Energetic / Motivated
    {'title': 'Lose Yourself', 'artist': 'Eminem', 'language': 'English',
     'moodTags': ['Motivation', 'Confidence', 'Energy'], 'energyLevel': 88},
    {'title': 'HUMBLE.', 'artist': 'Kendrick Lamar', 'language': 'English',
     'moodTags': ['Confidence', 'Energy', 'Motivation'], 'energyLevel': 84},
    {'title': 'Dog Days Are Over', 'artist': 'Florence + The Machine', 'language': 'English',
     'moodTags': ['Hopefulness', 'Excitement', 'Energy'], 'energyLevel': 78},
    {'title': 'Shake It Out', 'artist': 'Florence + The Machine', 'language': 'English',
     'moodTags': ['Hopefulness', 'Energy', 'Motivation'], 'energyLevel': 74},
    {'title': 'Levitating', 'artist': 'Dua Lipa', 'language': 'English',
     'moodTags': ['Excitement', 'Energy', 'Confidence'], 'energyLevel': 82},
    {'title': 'Hoppípolla', 'artist': 'Sigur Rós', 'language': 'English',
     'moodTags': ['Hopefulness', 'Serenity', 'Emotional Depth'], 'energyLevel': 54},
    {'title': 'Everything In Its Right Place', 'artist': 'Radiohead', 'language': 'English',
     'moodTags': ['Anxiety', 'Introspection', 'Melancholy'], 'energyLevel': 44},
    {'title': 'On The Nature Of Daylight', 'artist': 'Max Richter', 'language': 'English',
     'moodTags': ['Serenity', 'Introspection', 'Emotional Depth'], 'energyLevel': 18},
    {'title': 'Gymnopédie No.1', 'artist': 'Erik Satie', 'language': 'English',
     'moodTags': ['Serenity', 'Calmness', 'Introspection'], 'energyLevel': 10},

    # ── HINDI (50 songs) ──────────────────────────────────────────────────────
    # Deep Emotional / Sad
    {'title': 'Agar Tum Saath Ho', 'artist': 'Alka Yagnik, Arijit Singh', 'language': 'Hindi',
     'moodTags': ['Sadness', 'Melancholy', 'Romantic Warmth'], 'energyLevel': 28},
    {'title': 'Channa Mereya', 'artist': 'Arijit Singh', 'language': 'Hindi',
     'moodTags': ['Sadness', 'Nostalgia', 'Loneliness'], 'energyLevel': 34},
    {'title': 'Phir Le Aya Dil', 'artist': 'Arijit Singh', 'language': 'Hindi',
     'moodTags': ['Nostalgia', 'Melancholy', 'Sadness'], 'energyLevel': 24},
    {'title': 'Tum Ho', 'artist': 'Mohit Chauhan', 'language': 'Hindi',
     'moodTags': ['Romantic Warmth', 'Nostalgia', 'Melancholy'], 'energyLevel': 32},
    {'title': 'Ae Dil Hai Mushkil', 'artist': 'Arijit Singh', 'language': 'Hindi',
     'moodTags': ['Sadness', 'Loneliness', 'Romantic Warmth'], 'energyLevel': 36},
    {'title': 'Tadap Tadap', 'artist': 'KK', 'language': 'Hindi',
     'moodTags': ['Sadness', 'Romantic Warmth', 'Nostalgia'], 'energyLevel': 30},
    {'title': 'Alvida', 'artist': 'KK', 'language': 'Hindi',
     'moodTags': ['Sadness', 'Nostalgia', 'Loneliness'], 'energyLevel': 28},
    {'title': 'Tu Jaane Na', 'artist': 'Atif Aslam', 'language': 'Hindi',
     'moodTags': ['Romantic Warmth', 'Sadness', 'Nostalgia'], 'energyLevel': 34},
    {'title': 'Dil Diyan Gallan', 'artist': 'Atif Aslam', 'language': 'Hindi',
     'moodTags': ['Romantic Warmth', 'Nostalgia', 'Hopefulness'], 'energyLevel': 44},
    {'title': 'Woh Lamhe', 'artist': 'Atif Aslam', 'language': 'Hindi',
     'moodTags': ['Nostalgia', 'Sadness', 'Melancholy'], 'energyLevel': 36},

    # Spiritual / Serene
    {'title': 'Kun Faya Kun', 'artist': 'A.R. Rahman, Javed Ali, Mohit Chauhan', 'language': 'Hindi',
     'moodTags': ['Serenity', 'Hopefulness', 'Introspection'], 'energyLevel': 30},
    {'title': 'Dil Se Re', 'artist': 'A.R. Rahman, Kavita Krishnamurthy', 'language': 'Hindi',
     'moodTags': ['Romantic Warmth', 'Introspection', 'Energy'], 'energyLevel': 62},
    {'title': 'Jai Ho', 'artist': 'A.R. Rahman', 'language': 'Hindi',
     'moodTags': ['Motivation', 'Hopefulness', 'Energy'], 'energyLevel': 76},
    {'title': 'Chaiyya Chaiyya', 'artist': 'Sukhwinder Singh, A.R. Rahman', 'language': 'Hindi',
     'moodTags': ['Energy', 'Excitement', 'Romantic Warmth'], 'energyLevel': 80},
    {'title': 'Iktara', 'artist': 'Amit Trivedi, Kavita Seth', 'language': 'Hindi',
     'moodTags': ['Calmness', 'Hopefulness', 'Introspection'], 'energyLevel': 44},

    # Indie / Lo-fi Hindi
    {'title': 'Baarishein', 'artist': 'Anuv Jain', 'language': 'Hindi',
     'moodTags': ['Melancholy', 'Calmness', 'Romantic Warmth'], 'energyLevel': 26},
    {'title': 'Gul', 'artist': 'Anuv Jain', 'language': 'Hindi',
     'moodTags': ['Calmness', 'Introspection', 'Nostalgia'], 'energyLevel': 30},
    {'title': 'Tere Baare', 'artist': 'Anuv Jain', 'language': 'Hindi',
     'moodTags': ['Romantic Warmth', 'Nostalgia', 'Calmness'], 'energyLevel': 34},
    {'title': 'Kasoor', 'artist': 'Prateek Kuhad', 'language': 'Hindi',
     'moodTags': ['Sadness', 'Nostalgia', 'Loneliness'], 'energyLevel': 28},
    {'title': 'Cold Mess', 'artist': 'Prateek Kuhad', 'language': 'Hindi',
     'moodTags': ['Introspection', 'Calmness', 'Nostalgia'], 'energyLevel': 32},
    {'title': 'O Mahi', 'artist': 'Prateek Kuhad', 'language': 'Hindi',
     'moodTags': ['Romantic Warmth', 'Hopefulness', 'Serenity'], 'energyLevel': 40},
    {'title': 'Roobaroo', 'artist': 'Jasleen Royal', 'language': 'Hindi',
     'moodTags': ['Hopefulness', 'Energy', 'Excitement'], 'energyLevel': 64},
    {'title': 'Kho Gaye Hum Kahan', 'artist': 'Jasleen Royal, Prateek Kuhad', 'language': 'Hindi',
     'moodTags': ['Introspection', 'Nostalgia', 'Calmness'], 'energyLevel': 36},

    # Romantic / Bollywood
    {'title': 'Kesariya', 'artist': 'Arijit Singh', 'language': 'Hindi',
     'moodTags': ['Romantic Warmth', 'Hopefulness', 'Calmness'], 'energyLevel': 52},
    {'title': 'Raabta', 'artist': 'Arijit Singh', 'language': 'Hindi',
     'moodTags': ['Romantic Warmth', 'Excitement', 'Hopefulness'], 'energyLevel': 58},
    {'title': 'Tum Se Hi', 'artist': 'Mohit Chauhan', 'language': 'Hindi',
     'moodTags': ['Romantic Warmth', 'Nostalgia', 'Hopefulness'], 'energyLevel': 54},
    {'title': 'Shayad', 'artist': 'Arijit Singh', 'language': 'Hindi',
     'moodTags': ['Romantic Warmth', 'Nostalgia', 'Melancholy'], 'energyLevel': 44},
    {'title': 'Tera Ban Jaunga', 'artist': 'Akhil Sachdeva, Tulsi Kumar', 'language': 'Hindi',
     'moodTags': ['Romantic Warmth', 'Hopefulness', 'Calmness'], 'energyLevel': 50},
    {'title': 'Mann Bharrya', 'artist': 'B Praak', 'language': 'Hindi',
     'moodTags': ['Sadness', 'Nostalgia', 'Loneliness'], 'energyLevel': 30},
    {'title': 'Filhaal', 'artist': 'B Praak, Akshay Kumar', 'language': 'Hindi',
     'moodTags': ['Sadness', 'Loneliness', 'Nostalgia'], 'energyLevel': 32},
    {'title': 'Duniyaa', 'artist': 'Akhil, Dhvani Bhanushali', 'language': 'Hindi',
     'moodTags': ['Romantic Warmth', 'Hopefulness', 'Excitement'], 'energyLevel': 62},

    # Calm / Shaam Vibes
    {'title': 'Shaam', 'artist': 'Amit Trivedi, Nikhil D\'Souza', 'language': 'Hindi',
     'moodTags': ['Calmness', 'Nostalgia', 'Serenity'], 'energyLevel': 42},
    {'title': 'Tujhe Kitna Chahne Lage', 'artist': 'Arijit Singh', 'language': 'Hindi',
     'moodTags': ['Romantic Warmth', 'Sadness', 'Nostalgia'], 'energyLevel': 38},
    {'title': 'Mere Naam Tu', 'artist': 'Abhijeet Srivastava', 'language': 'Hindi',
     'moodTags': ['Sadness', 'Nostalgia', 'Loneliness'], 'energyLevel': 28},
    {'title': 'Ik Vaari Aa', 'artist': 'Arijit Singh', 'language': 'Hindi',
     'moodTags': ['Nostalgia', 'Sadness', 'Melancholy'], 'energyLevel': 34},
    {'title': 'Hawayein', 'artist': 'Arijit Singh', 'language': 'Hindi',
     'moodTags': ['Romantic Warmth', 'Hopefulness', 'Serenity'], 'energyLevel': 46},
    {'title': 'Lut Gaye', 'artist': 'Jubin Nautiyal', 'language': 'Hindi',
     'moodTags': ['Romantic Warmth', 'Nostalgia', 'Sadness'], 'energyLevel': 40},
    {'title': 'Pehle Bhi Main', 'artist': 'Vishal Mishra', 'language': 'Hindi',
     'moodTags': ['Sadness', 'Nostalgia', 'Romantic Warmth'], 'energyLevel': 32},

    # Uplifting / Motivational
    {'title': 'Zinda', 'artist': 'Siddharth Mahadevan', 'language': 'Hindi',
     'moodTags': ['Motivation', 'Energy', 'Confidence'], 'energyLevel': 84},
    {'title': 'Lakshya', 'artist': 'Shankar Mahadevan', 'language': 'Hindi',
     'moodTags': ['Motivation', 'Confidence', 'Hopefulness'], 'energyLevel': 74},
    {'title': 'Ilahi', 'artist': 'Arijit Singh', 'language': 'Hindi',
     'moodTags': ['Hopefulness', 'Energy', 'Nostalgia'], 'energyLevel': 68},
    {'title': 'Phir Bhi Tumko Chaahunga', 'artist': 'Arijit Singh', 'language': 'Hindi',
     'moodTags': ['Romantic Warmth', 'Sadness', 'Nostalgia'], 'energyLevel': 36},
    {'title': 'Pal', 'artist': 'Arijit Singh, Shreya Ghoshal', 'language': 'Hindi',
     'moodTags': ['Nostalgia', 'Sadness', 'Romantic Warmth'], 'energyLevel': 34},
    {'title': 'Kabira', 'artist': 'Rekha Bhardwaj, Tochi Raina', 'language': 'Hindi',
     'moodTags': ['Introspection', 'Serenity', 'Nostalgia'], 'energyLevel': 40},
    {'title': 'Sooraj Dooba Hain', 'artist': 'Arijit Singh, Aditi Singh Sharma', 'language': 'Hindi',
     'moodTags': ['Romantic Warmth', 'Hopefulness', 'Excitement'], 'energyLevel': 60},
    {'title': 'Kya Hua Tera Wada', 'artist': 'Mohammed Rafi', 'language': 'Hindi',
     'moodTags': ['Nostalgia', 'Sadness', 'Loneliness'], 'energyLevel': 26},
    {'title': 'Agar Tu Hota', 'artist': 'Arijit Singh', 'language': 'Hindi',
     'moodTags': ['Loneliness', 'Sadness', 'Nostalgia'], 'energyLevel': 28},
    {'title': 'Naina', 'artist': 'Armaan Malik', 'language': 'Hindi',
     'moodTags': ['Sadness', 'Romantic Warmth', 'Loneliness'], 'energyLevel': 32},

    # ── KANNADA (50 songs) ────────────────────────────────────────────────────
    # Deep Emotional / Sad
    {'title': 'Soul of Dia', 'artist': 'B. Ajaneesh Loknath, Sanjith Hegde', 'language': 'Kannada',
     'moodTags': ['Melancholy', 'Romantic Warmth', 'Sadness'], 'energyLevel': 26},
    {'title': 'Ninnanu Nodida', 'artist': 'Vijay Prakash', 'language': 'Kannada',
     'moodTags': ['Melancholy', 'Nostalgia', 'Romantic Warmth'], 'energyLevel': 30},
    {'title': 'Kaagadada Doniyalli', 'artist': 'Vasuki Vaibhav', 'language': 'Kannada',
     'moodTags': ['Introspection', 'Melancholy', 'Nostalgia'], 'energyLevel': 28},
    {'title': 'Sapta Sagaradaache Ello Title Track', 'artist': 'Charan Raj', 'language': 'Kannada',
     'moodTags': ['Introspection', 'Melancholy', 'Serenity'], 'energyLevel': 24},
    {'title': 'Nee Hogi Bare', 'artist': 'Charan Raj', 'language': 'Kannada',
     'moodTags': ['Sadness', 'Loneliness', 'Melancholy'], 'energyLevel': 22},
    {'title': 'Yenagaagi', 'artist': 'Charan Raj, Sanjith Hegde', 'language': 'Kannada',
     'moodTags': ['Sadness', 'Nostalgia', 'Loneliness'], 'energyLevel': 26},
    {'title': 'Bettada Mele', 'artist': 'Rajesh Krishnan', 'language': 'Kannada',
     'moodTags': ['Nostalgia', 'Serenity', 'Calmness'], 'energyLevel': 38},
    {'title': 'Bannada Doni', 'artist': 'Vasuki Vaibhav', 'language': 'Kannada',
     'moodTags': ['Melancholy', 'Loneliness', 'Nostalgia'], 'energyLevel': 24},
    {'title': 'Modagaayi Preethiya', 'artist': 'Sanjith Hegde', 'language': 'Kannada',
     'moodTags': ['Romantic Warmth', 'Sadness', 'Nostalgia'], 'energyLevel': 32},
    {'title': 'Cheluve Ninna Nodalu', 'artist': 'Sonu Nigam', 'language': 'Kannada',
     'moodTags': ['Romantic Warmth', 'Nostalgia', 'Melancholy'], 'energyLevel': 34},

    # Romantic / Love
    {'title': 'Belageddu', 'artist': 'Vijay Prakash', 'language': 'Kannada',
     'moodTags': ['Romantic Warmth', 'Hopefulness', 'Calmness'], 'energyLevel': 56},
    {'title': 'Nee Sigoovaregu', 'artist': 'Sanjith Hegde', 'language': 'Kannada',
     'moodTags': ['Romantic Warmth', 'Calmness', 'Hopefulness'], 'energyLevel': 48},
    {'title': 'Minchagi Neenu', 'artist': 'Sonu Nigam', 'language': 'Kannada',
     'moodTags': ['Romantic Warmth', 'Nostalgia', 'Serenity'], 'energyLevel': 44},
    {'title': 'Love You Chinna', 'artist': 'Vasuki Vaibhav', 'language': 'Kannada',
     'moodTags': ['Romantic Warmth', 'Hopefulness', 'Calmness'], 'energyLevel': 46},
    {'title': 'Neene Modalu', 'artist': 'Sonu Nigam', 'language': 'Kannada',
     'moodTags': ['Romantic Warmth', 'Nostalgia', 'Calmness'], 'energyLevel': 42},
    {'title': 'Thumba Huccha Ninna Mele', 'artist': 'Rajesh Krishnan', 'language': 'Kannada',
     'moodTags': ['Romantic Warmth', 'Excitement', 'Hopefulness'], 'energyLevel': 60},
    {'title': 'Ninna Kanu Kaneyilli', 'artist': 'Vijay Prakash', 'language': 'Kannada',
     'moodTags': ['Romantic Warmth', 'Introspection', 'Nostalgia'], 'energyLevel': 36},
    {'title': 'Aa Ninna Mugilu', 'artist': 'Sanjith Hegde', 'language': 'Kannada',
     'moodTags': ['Romantic Warmth', 'Sadness', 'Nostalgia'], 'energyLevel': 28},
    {'title': 'Love Mocktail Title Track', 'artist': 'Nakul Abhyankar', 'language': 'Kannada',
     'moodTags': ['Romantic Warmth', 'Hopefulness', 'Serenity'], 'energyLevel': 50},
    {'title': 'Mungaaru Male Title Track', 'artist': 'Udit Narayan', 'language': 'Kannada',
     'moodTags': ['Nostalgia', 'Romantic Warmth', 'Melancholy'], 'energyLevel': 38},

    # Folk / Chill
    {'title': 'Katheyondu Shuruvagide', 'artist': 'Raghu Dixit', 'language': 'Kannada',
     'moodTags': ['Nostalgia', 'Hopefulness', 'Calmness'], 'energyLevel': 50},
    {'title': 'Aa Baa Kathe Heli', 'artist': 'Raghu Dixit', 'language': 'Kannada',
     'moodTags': ['Calmness', 'Hopefulness', 'Serenity'], 'energyLevel': 54},
    {'title': 'Ganesh Vandana', 'artist': 'Raghu Dixit', 'language': 'Kannada',
     'moodTags': ['Serenity', 'Hopefulness', 'Energy'], 'energyLevel': 58},
    {'title': 'Nenapu Taramara', 'artist': 'Vasuki Vaibhav', 'language': 'Kannada',
     'moodTags': ['Nostalgia', 'Introspection', 'Melancholy'], 'energyLevel': 32},
    {'title': 'Ondu Motteya Kathe', 'artist': 'Vasuki Vaibhav', 'language': 'Kannada',
     'moodTags': ['Introspection', 'Nostalgia', 'Calmness'], 'energyLevel': 38},
    {'title': 'Ee Gandhagaali', 'artist': 'Manjula Gururaj', 'language': 'Kannada',
     'moodTags': ['Serenity', 'Calmness', 'Nostalgia'], 'energyLevel': 34},
    {'title': 'Hennige Helidenu', 'artist': 'Rajesh Krishnan', 'language': 'Kannada',
     'moodTags': ['Calmness', 'Serenity', 'Romantic Warmth'], 'energyLevel': 40},

    # Energetic / Movie Anthems
    {'title': 'Bombe Helutaithe', 'artist': 'Vijay Prakash', 'language': 'Kannada',
     'moodTags': ['Hopefulness', 'Motivation', 'Energy'], 'energyLevel': 72},
    {'title': 'Hands Up', 'artist': 'Vijay Prakash, Shashank Sheshagiri', 'language': 'Kannada',
     'moodTags': ['Energy', 'Excitement', 'Confidence'], 'energyLevel': 88},
    {'title': 'Jackie Jackie', 'artist': 'Puneeth Rajkumar', 'language': 'Kannada',
     'moodTags': ['Energy', 'Excitement', 'Confidence'], 'energyLevel': 86},
    {'title': 'Kanasina Rajkumara', 'artist': 'Puneeth Rajkumar', 'language': 'Kannada',
     'moodTags': ['Confidence', 'Motivation', 'Hopefulness'], 'energyLevel': 74},
    {'title': 'Halli Naadu Huduga', 'artist': 'Puneeth Rajkumar', 'language': 'Kannada',
     'moodTags': ['Energy', 'Excitement', 'Hopefulness'], 'energyLevel': 78},
    {'title': 'Kirik Kirik', 'artist': 'Vijay Prakash, Sanchita Padukone', 'language': 'Kannada',
     'moodTags': ['Excitement', 'Energy', 'Romantic Warmth'], 'energyLevel': 76},
    {'title': 'Tagaru Banthu Tagaru', 'artist': 'Anthony Daasan', 'language': 'Kannada',
     'moodTags': ['Motivation', 'Energy', 'Confidence'], 'energyLevel': 80},
    {'title': 'Avane Srimannarayana Theme', 'artist': 'B. Ajaneesh Loknath', 'language': 'Kannada',
     'moodTags': ['Confidence', 'Energy', 'Excitement'], 'energyLevel': 76},

    # Introspective / Cinematic
    {'title': '777 Charlie Theme', 'artist': 'Nobin Paul', 'language': 'Kannada',
     'moodTags': ['Hopefulness', 'Serenity', 'Emotional Depth'], 'energyLevel': 38},
    {'title': 'Neene Nenapu', 'artist': 'Sanjith Hegde', 'language': 'Kannada',
     'moodTags': ['Nostalgia', 'Loneliness', 'Melancholy'], 'energyLevel': 28},
    {'title': 'Yelo Yelo', 'artist': 'B. Ajaneesh Loknath', 'language': 'Kannada',
     'moodTags': ['Sadness', 'Melancholy', 'Introspection'], 'energyLevel': 22},
    {'title': 'Obba Ondu Saari', 'artist': 'Charan Raj', 'language': 'Kannada',
     'moodTags': ['Sadness', 'Nostalgia', 'Loneliness'], 'energyLevel': 24},
    {'title': 'Kaanadanta', 'artist': 'Vasuki Vaibhav', 'language': 'Kannada',
     'moodTags': ['Loneliness', 'Introspection', 'Melancholy'], 'energyLevel': 26},
    {'title': 'Chanda Chanda', 'artist': 'Rajesh Krishnan', 'language': 'Kannada',
     'moodTags': ['Calmness', 'Serenity', 'Romantic Warmth'], 'energyLevel': 44},
    {'title': 'Mareyala Ninna Nenapu', 'artist': 'Sanjith Hegde', 'language': 'Kannada',
     'moodTags': ['Nostalgia', 'Sadness', 'Introspection'], 'energyLevel': 30},
    {'title': 'Nenapu Bidaradu', 'artist': 'Vasuki Vaibhav', 'language': 'Kannada',
     'moodTags': ['Introspection', 'Melancholy', 'Serenity'], 'energyLevel': 32},
    {'title': 'Paramathma Title Track', 'artist': 'V. Harikrishna', 'language': 'Kannada',
     'moodTags': ['Hopefulness', 'Energy', 'Serenity'], 'energyLevel': 56},
    {'title': 'Onde Ondhu Maru', 'artist': 'Sanjith Hegde, Vijay Prakash', 'language': 'Kannada',
     'moodTags': ['Nostalgia', 'Romantic Warmth', 'Calmness'], 'energyLevel': 42},
    {'title': 'Ninne Ninne', 'artist': 'Arjun Janya', 'language': 'Kannada',
     'moodTags': ['Romantic Warmth', 'Calmness', 'Nostalgia'], 'energyLevel': 46},
    {'title': 'Mugulu Nage', 'artist': 'V. Harikrishna', 'language': 'Kannada',
     'moodTags': ['Serenity', 'Romantic Warmth', 'Calmness'], 'energyLevel': 36},
    {'title': 'Ellindalo Bandavalu', 'artist': 'Vasuki Vaibhav', 'language': 'Kannada',
     'moodTags': ['Romantic Warmth', 'Nostalgia', 'Hopefulness'], 'energyLevel': 52},
    {'title': 'Mareyala', 'artist': 'B. Ajaneesh Loknath', 'language': 'Kannada',
     'moodTags': ['Sadness', 'Introspection', 'Emotional Depth'], 'energyLevel': 20},
]

EXTENDED_CATALOG = [
    {'title': 'Aaradhike', 'artist': 'Sooraj Santhosh, Madhuvanthi Narayan', 'language': 'Malayalam', 'moodTags': ['Romantic Warmth', 'Serenity', 'Hopefulness'], 'energyLevel': 46},
    {'title': 'Uyire', 'artist': 'Sid Sriram, Neha S Nair', 'language': 'Malayalam', 'moodTags': ['Romantic Warmth', 'Melancholy', 'Nostalgia'], 'energyLevel': 38},
    {'title': 'Malare', 'artist': 'Vijay Yesudas', 'language': 'Malayalam', 'moodTags': ['Romantic Warmth', 'Nostalgia', 'Serenity'], 'energyLevel': 40},
    {'title': 'Pavizha Mazha', 'artist': 'K S Harisankar', 'language': 'Malayalam', 'moodTags': ['Romantic Warmth', 'Calmness', 'Hopefulness'], 'energyLevel': 44},
    {'title': 'Cherathukal', 'artist': 'Sithara Krishnakumar, Sushin Shyam', 'language': 'Malayalam', 'moodTags': ['Melancholy', 'Serenity', 'Emotional Depth'], 'energyLevel': 28},
    {'title': 'Parayuvaan', 'artist': 'Sid Sriram, Neha S Nair', 'language': 'Malayalam', 'moodTags': ['Romantic Warmth', 'Nostalgia', 'Melancholy'], 'energyLevel': 42},
    {'title': 'Mizhiyil Ninnum', 'artist': 'Shahabaz Aman', 'language': 'Malayalam', 'moodTags': ['Melancholy', 'Calmness', 'Romantic Warmth'], 'energyLevel': 30},
    {'title': 'Theerame', 'artist': 'K S Harisankar, Shreya Ghoshal', 'language': 'Malayalam', 'moodTags': ['Romantic Warmth', 'Serenity', 'Nostalgia'], 'energyLevel': 48},
    {'title': 'Aaro Nenjil', 'artist': 'Gowry Lekshmi', 'language': 'Malayalam', 'moodTags': ['Calmness', 'Introspection', 'Hopefulness'], 'energyLevel': 34},
    {'title': 'Manikya Malaraya Poovi', 'artist': 'Vineeth Sreenivasan', 'language': 'Malayalam', 'moodTags': ['Nostalgia', 'Romantic Warmth', 'Calmness'], 'energyLevel': 50},
    {'title': 'Jeevamshamayi', 'artist': 'K S Harisankar, Shreya Ghoshal', 'language': 'Malayalam', 'moodTags': ['Romantic Warmth', 'Hopefulness', 'Serenity'], 'energyLevel': 46},
    {'title': 'Akale', 'artist': 'Karthik', 'language': 'Malayalam', 'moodTags': ['Loneliness', 'Melancholy', 'Nostalgia'], 'energyLevel': 26},
    {'title': 'Vathikkalu Vellaripravu', 'artist': 'Arjun Krishna, Nithya Mammen', 'language': 'Malayalam', 'moodTags': ['Romantic Warmth', 'Hopefulness', 'Calmness'], 'energyLevel': 52},
    {'title': 'Thaniye Mizhikal', 'artist': 'Sooraj Santhosh', 'language': 'Malayalam', 'moodTags': ['Loneliness', 'Sadness', 'Introspection'], 'energyLevel': 24},
    {'title': 'Nebulakal', 'artist': 'Sushin Shyam', 'language': 'Malayalam', 'moodTags': ['Introspection', 'Serenity', 'Calmness'], 'energyLevel': 32},
    {'title': 'Rakita Rakita Rakita', 'artist': 'Dhanush, Santhosh Narayanan, Dhee', 'language': 'Tamil', 'moodTags': ['Energy', 'Excitement', 'Confidence'], 'energyLevel': 88},
    {'title': 'Nenjukkul Peidhidum', 'artist': 'Hariharan, Harris Jayaraj', 'language': 'Tamil', 'moodTags': ['Romantic Warmth', 'Nostalgia', 'Serenity'], 'energyLevel': 44},
    {'title': 'New York Nagaram', 'artist': 'A.R. Rahman', 'language': 'Tamil', 'moodTags': ['Loneliness', 'Nostalgia', 'Melancholy'], 'energyLevel': 30},
    {'title': 'Munbe Vaa', 'artist': 'Shreya Ghoshal, Naresh Iyer', 'language': 'Tamil', 'moodTags': ['Romantic Warmth', 'Serenity', 'Nostalgia'], 'energyLevel': 42},
    {'title': 'Anbil Avan', 'artist': 'A.R. Rahman, Devan Ekambaram, Chinmayi', 'language': 'Tamil', 'moodTags': ['Romantic Warmth', 'Hopefulness', 'Excitement'], 'energyLevel': 60},
    {'title': 'Kannazhaga', 'artist': 'Dhanush, Shruti Haasan', 'language': 'Tamil', 'moodTags': ['Romantic Warmth', 'Melancholy', 'Nostalgia'], 'energyLevel': 38},
    {'title': 'Maruvaarthai', 'artist': 'Sid Sriram', 'language': 'Tamil', 'moodTags': ['Melancholy', 'Romantic Warmth', 'Loneliness'], 'energyLevel': 32},
    {'title': 'Thalli Pogathey', 'artist': 'Sid Sriram, Aaryan Dinesh Kanagaratnam, Aparna Narayanan', 'language': 'Tamil', 'moodTags': ['Romantic Warmth', 'Anxiety', 'Melancholy'], 'energyLevel': 54},
    {'title': 'Kaathalae Kaathalae', 'artist': 'Chinmayi, Govind Vasantha', 'language': 'Tamil', 'moodTags': ['Romantic Warmth', 'Serenity', 'Emotional Depth'], 'energyLevel': 34},
    {'title': 'The Life of Ram', 'artist': 'Pradeep Kumar', 'language': 'Tamil', 'moodTags': ['Introspection', 'Hopefulness', 'Serenity'], 'energyLevel': 40},
    {'title': 'Aaromale', 'artist': 'Alphons Joseph, A.R. Rahman', 'language': 'Tamil', 'moodTags': ['Romantic Warmth', 'Melancholy', 'Serenity'], 'energyLevel': 36},
    {'title': 'Pookkal Pookkum', 'artist': 'Roop Kumar Rathod, Harini, Andrea Jeremiah, G.V. Prakash Kumar', 'language': 'Tamil', 'moodTags': ['Nostalgia', 'Romantic Warmth', 'Serenity'], 'energyLevel': 46},
    {'title': 'Vaseegara', 'artist': 'Bombay Jayashri', 'language': 'Tamil', 'moodTags': ['Romantic Warmth', 'Calmness', 'Nostalgia'], 'energyLevel': 38},
    {'title': 'Enjoy Enjaami', 'artist': 'Dhee, Arivu', 'language': 'Tamil', 'moodTags': ['Energy', 'Hopefulness', 'Confidence'], 'energyLevel': 76},
    {'title': 'Thenmozhi', 'artist': 'Santhosh Narayanan, Anirudh Ravichander', 'language': 'Tamil', 'moodTags': ['Romantic Warmth', 'Hopefulness', 'Calmness'], 'energyLevel': 50},
]

MULTILINGUAL_CATALOG.extend(EXTENDED_CATALOG)

def _time_period(hour: int):
    if 5 <= hour < 12:
        return 'morning'
    if 12 <= hour < 17:
        return 'afternoon'
    if 17 <= hour < 22:
        return 'evening'
    return 'night'


def _spotify_search_url(artist, title):
    return f"https://open.spotify.com/search/{quote(f'{artist} {title}')}"


def _tag_score(track, emotion_weights, target_energy):
    """Weighted multi-tag scoring with emotion-fit, energy alignment, metadata richness, and freshness."""
    score = 0

    tags = track.get('moodTags', [])
    multipliers = [1.0, 0.70, 0.45]
    for idx, tag in enumerate(tags):
        mult = multipliers[idx] if idx < len(multipliers) else 0.30
        score += emotion_weights.get(tag, 0) * mult
        for source_emotion, affinities in EMOTION_AFFINITY.items():
            score += emotion_weights.get(source_emotion, 0) * affinities.get(tag, 0) * mult

    identity = _track_identity(track)
    score -= TRACK_EXPOSURE[identity] * 4.5
    if identity in RECENT_TRACKS:
        score -= 18

    if 'Healing' in tags:
        score += emotion_weights.get('Hopefulness', 0) * 0.72
        score += emotion_weights.get('Sadness', 0) * 0.28
    if 'Late Night' in tags:
        score += emotion_weights.get('Introspection', 0) * 0.34
        score += emotion_weights.get('Melancholy', 0) * 0.24
    if 'Focus' in tags:
        score += emotion_weights.get('Motivation', 0) * 0.44
        score += emotion_weights.get('Introspection', 0) * 0.34
    if 'Emotional Depth' in tags:
        score += emotion_weights.get('Melancholy', 0) * 0.40
        score += emotion_weights.get('Sadness', 0) * 0.30
        score += emotion_weights.get('Introspection', 0) * 0.22

    score -= abs(track.get('energyLevel', 50) - target_energy) * 0.18
    popularity_score = int(track.get('popularityScore') or track.get('popularity') or 70)
    score += max(0, popularity_score - 50) * 0.34
    if popularity_score < 75:
        score -= (75 - popularity_score) * 0.22
    if track.get('releaseYear'):
        score += max(0, (2026 - int(track.get('releaseYear', 2000)))) * 0.03
    if track.get('valence') is not None:
        score += (float(track.get('valence', 0.5)) - 0.5) * 14

    return score


INSIGHT_TAGS = {
    'Sadness': 'quiet grief',
    'Melancholy': 'nostalgic ache',
    'Nostalgia': 'memory glow',
    'Calmness': 'detached calm',
    'Loneliness': 'reflective loneliness',
    'Anxiety': 'restless mind',
    'Hopefulness': 'fragile hope',
    'Excitement': 'bright lift',
    'Anger': 'cathartic release',
    'Confidence': 'steady confidence',
    'Romantic Warmth': 'romantic warmth',
    'Energy': 'kinetic pulse',
    'Introspection': 'inner weather',
    'Serenity': 'soft stillness',
    'Motivation': 'forward motion',
    'Emotional Depth': 'cinematic depth',
    'Focus': 'deep focus',
    'Healing': 'quiet healing',
    'Burnout': 'silent burnout',
    'Mental Fatigue': 'exhausted clarity',
    'Hopelessness': 'low-light ache',
    'Emotional Numbness': 'emotional numbness',
    'Quiet Healing': 'quiet healing',
}


def _insight_tags(tags):
    return [INSIGHT_TAGS.get(tag, tag.lower()) for tag in tags[:3]]


def _tag_cluster(track):
    return tuple(track.get('moodTags', [])[:2])

def _structured_track(track, emotional_weight):
    spotify_query = track.get('spotifyQuery') or f"{track.get('artist', '')} {track.get('title', '')}".strip()
    spotify_url = track.get('spotifyUrl') or track.get('spotify_url') or _spotify_search_url(track.get('artist', ''), track.get('title', ''))
    preview_url = track.get('previewUrl') or track.get('preview_url')
    language = normalize_language(track.get('language'), default='English')
    return {
        'title': track.get('title', ''),
        'name': track.get('title', ''),
        'artist': track.get('artist', ''),
        'language': language,
        'moodTags': track.get('moodTags', []),
        'insightTags': _insight_tags(track.get('moodTags', [])),
        'emotionalWeight': round(emotional_weight, 1),
        'energyLevel': track.get('energyLevel', 50),
        'albumArt': track.get('albumArt') or track.get('album_art', ''),
        'albumArtHD': track.get('albumArtHD') or track.get('albumArt') or track.get('album_art', ''),
        'albumArtMedium': track.get('albumArtMedium') or track.get('albumArt') or track.get('album_art', ''),
        'albumArtThumb': track.get('albumArtThumb') or track.get('albumArt') or track.get('album_art', ''),
        'album_art': track.get('albumArt') or track.get('album_art', ''),
        'artworkSource': track.get('artworkSource', 'spotify' if track.get('albumArt') else ''),
        'album': track.get('album') or track.get('albumName') or '',
        'albumName': track.get('albumName') or track.get('album') or '',
        'spotifyId': track.get('spotifyId') or track.get('track_id') or track.get('trackId') or '',
        'track_id': track.get('track_id') or track.get('spotifyId') or track.get('trackId') or '',
        'trackId': track.get('trackId') or track.get('spotifyId') or track.get('track_id') or '',
        'isrc': track.get('isrc') or '',
        'popularity': track.get('popularity'),
        'popularityScore': track.get('popularityScore'),
        'artistImage': track.get('artistImage') or '',
        'artistGenres': track.get('artistGenres') or [],
        'artistPopularity': track.get('artistPopularity'),
        'spotifyEnriched': bool(track.get('spotifyEnriched')),
        'artworkFailureReason': track.get('artworkFailureReason', ''),
        'spotifyQuery': spotify_query,
        'spotifyUrl': spotify_url,
        'spotify_url': spotify_url,
        'preview_url': preview_url,
        'previewUrl': preview_url
    }


def _recommendations_by_language(analysis, limit=14, session_id=None, language=None):
    """Build a diverse, session-aware playlist per language using weighted randomization and strict repetition controls."""
    emotion_weights = analysis.get('scores', {})
    dimensions = analysis.get('dimensions', {})
    target_energy = dimensions.get('energy', 45)
    grouped = {}

    preferred_language = normalize_language(
        language or analysis.get('preferredLanguage') or (analysis.get('context') or {}).get('language')
    )
    languages = [preferred_language] if preferred_language else LANGUAGES
    session_key = str(session_id or 'global')
    session_history = SESSION_TRACK_HISTORY[session_key]
    recent_session_ids = set(session_history[-24:])

    for language in languages:
        language_tracks = get_language_tracks(language)
        if not language_tracks:
            language_tracks = [
                t for t in MULTILINGUAL_CATALOG
                if normalize_language(t.get('language')) == language
            ]
        language_tracks = [
            track for track in language_tracks
            if normalize_language(track.get('language')) == language
        ]

        rng = random.Random(_rotation_seed(analysis, language) + len(session_history))
        scored = []
        for track in language_tracks:
            freshness_jitter = rng.uniform(-5.5, 8.5)
            score = _tag_score(track, emotion_weights, target_energy) + freshness_jitter
            if preferred_language and language == preferred_language:
                score += 4.5
            scored.append((track, score))
        scored.sort(key=lambda x: x[1], reverse=True)

        selected = []
        selected_ids = set()
        artist_counts = Counter()
        cluster_counts = Counter()
        pool = scored[:max(40, limit * 4)]

        for _ in range(limit):
            candidates = []
            for track, weight in pool:
                identity = _track_identity(track)
                if identity in selected_ids:
                    continue

                artist = track.get('artist', '').split(',')[0].strip().lower()
                cluster = _tag_cluster(track)
                penalty = 0
                if identity in recent_session_ids or identity in RECENT_TRACKS:
                    penalty += 16
                if artist_counts[artist] >= 2:
                    penalty += 8
                if cluster_counts[cluster] >= 2:
                    penalty += 6
                if artist in {item.get('artist', '').split(',')[0].strip().lower() for item in selected}:
                    penalty += 4

                adjusted_weight = weight - penalty + rng.uniform(-1.5, 2.4)
                candidates.append((track, adjusted_weight))

            if not candidates:
                break

            weights = [max(0.8, score + 8) for _, score in candidates]
            chosen_track, chosen_weight = random.choices(candidates, weights=weights, k=1)[0]
            identity = _track_identity(chosen_track)
            selected_ids.add(identity)
            selected.append(_structured_track(chosen_track, max(8, chosen_weight)))
            artist = chosen_track.get('artist', '').split(',')[0].strip().lower()
            artist_counts[artist] += 1
            cluster_counts[_tag_cluster(chosen_track)] += 1
            session_history.append(identity)
            RECENT_TRACKS.append(identity)
            TRACK_EXPOSURE[identity] += 1
            pool = [(track, weight) for track, weight in pool if _track_identity(track) != identity]

        grouped[language] = selected

    return grouped


def recommend_for_mood(analysis: dict, time_of_day: str = None, session_id: str = None, language: str = None):
    if isinstance(analysis, str):
        analysis = {'mood': analysis, 'scores': {}}

    mood_label = analysis.get('mood', 'Chill')
    nuanced_label = analysis.get('nuancedLabel', mood_label)
    archetype = analysis.get('archetype') or nuanced_label
    primary_emotion = analysis.get('primaryEmotion')
    secondary_emotion = analysis.get('secondary')
    hidden_undertone = analysis.get('hiddenUndertone')
    dimensions = analysis.get('dimensions', {})
    intensity = analysis.get('intensity', 'moderate')
    context = analysis.get('context', {})
    selected_language = normalize_language(
        language or analysis.get('language') or analysis.get('preferredLanguage') or context.get('language')
    )
    analysis = dict(analysis)
    if selected_language:
        analysis['preferredLanguage'] = selected_language

    now = datetime.now()
    period = time_of_day or context.get('time') or _time_period(now.hour)

    base = MOOD_MAP.get(mood_label, MOOD_MAP['Chill'])
    energy_score = dimensions.get('energy', analysis.get('scores', {}).get('Energy', 50))
    depth_score = dimensions.get('emotionalDepth', 50)
    introspection_score = dimensions.get('introspection', 50)

    if intensity == 'extreme':
        energy_tone = 'overwhelming emotional depth' if energy_score < 40 else 'explosive momentum'
    elif intensity == 'high':
        energy_tone = 'pulsing intensity' if energy_score > 65 else 'deep emotional resonance'
    elif intensity == 'low':
        energy_tone = 'gentle drift' if energy_score < 40 else 'light motion'
    else:
        energy_tone = 'reflective motion' if introspection_score > 60 else 'balanced motion'

    time_label = TIME_THEMES.get(period, 'Day Rhythm')
    title = f"{archetype} | {time_label}"

    emotion_chain = [item for item in [primary_emotion, secondary_emotion, hidden_undertone] if item]
    emotion_queries, emotion_genres = [], []
    for emotion in emotion_chain:
        emotion_queries.extend(EMOTION_QUERY_MAP.get(emotion, [])[:2])
        emotion_genres.extend(EMOTION_GENRE_MAP.get(emotion, [])[:1])

    queries = list(dict.fromkeys(emotion_queries + base['queries']))[:6]
    genres = list(dict.fromkeys(emotion_genres + base['genres']))[:4]

    recommendations_by_language = _recommendations_by_language(
        analysis,
        limit=14,
        session_id=session_id,
        language=selected_language
    )

    explanation = (
        f"This playlist follows {nuanced_label.lower()}, with {primary_emotion or mood_label} leading"
        f"{f' and {secondary_emotion} underneath' if secondary_emotion else ''}. "
        f"It blends {', '.join(genres[:2])} textures with {period} atmosphere for {energy_tone}"
        f" and {depth_score}% emotional depth."
    )

    fallback_language = selected_language or 'English'
    fallback_tracks = recommendations_by_language.get(fallback_language) or get_fallback_tracks(
        mood_label,
        limit=14,
        language=fallback_language
    )

    return {
        'genres': genres,
        'playlists': base['playlists'],
        'queries': queries,
        'recommendationsByLanguage': recommendations_by_language,
        'selectedLanguage': selected_language,
        'title': title,
        'time_period': period,
        'explanation': explanation,
        'fallback_tracks': fallback_tracks
    }
