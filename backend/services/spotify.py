import os
import time
import json
import requests
import logging
import re
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'
SPOTIFY_SEARCH_URL = 'https://api.spotify.com/v1/search'
SPOTIFY_ARTIST_URL = 'https://api.spotify.com/v1/artists/{id}'
SPOTIFY_TRACK_URL = 'https://api.spotify.com/v1/tracks/{id}'
SPOTIFY_ALBUM_URL = 'https://api.spotify.com/v1/albums/{id}'
CACHE_TTL_SECONDS = 60 * 60 * 12
SPOTIFY_CACHE_FILE = os.path.join(os.path.dirname(__file__), '..', 'spotify_cache.json')
SPOTIFY_ARTWORK_REPORT_FILE = os.path.join(os.path.dirname(__file__), '..', 'spotify_artwork_report.json')

UNOFFICIAL_VERSION_TERMS = (
    'karaoke', 'tribute', 'cover', 'remix', 'live', 'instrumental', 'sped up',
    'slowed', 'reverb', 'lofi', 'lo-fi', '8d', 'nightcore', 'refix', 'mashup',
    'concert', 'performance', 'version'
)


class SpotifyRateLimited(RuntimeError):
    pass

_token_cache = {'token': None, 'expires': 0}
_track_cache = {}
_artist_cache = {}
_spotify_persistent_cache = {}
_token_lock = Lock()
_cache_lock = Lock()
_persistent_cache_loaded = False
_rate_limited_until = 0


def is_available():
    return bool(os.getenv('SPOTIFY_CLIENT_ID') and os.getenv('SPOTIFY_CLIENT_SECRET'))


def _cache_key(query):
    return ' '.join(str(query or '').lower().strip().split())


def _metadata_cache_key(query, title='', artist='', album=''):
    return _cache_key('|'.join([str(title or ''), str(artist or ''), str(album or ''), str(query or '')]))


def get_token():
    if not is_available():
        logger.warning('Spotify credentials missing (SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET)')
        return None

    now = time.time()
    with _token_lock:
        if _token_cache['token'] and now < _token_cache['expires']:
            return _token_cache['token']

        logger.info('Spotify credentials are present, requesting token')
        cid = os.getenv('SPOTIFY_CLIENT_ID')
        secret = os.getenv('SPOTIFY_CLIENT_SECRET')

        try:
            resp = requests.post(
                SPOTIFY_TOKEN_URL,
                data={'grant_type': 'client_credentials'},
                auth=(cid, secret),
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()
            token = data.get('access_token')
            expires = now + data.get('expires_in', 3400) - 60

            _token_cache['token'] = token
            _token_cache['expires'] = expires
            logger.info('Successfully fetched new Spotify token')
            return token
        except Exception as e:
            logger.error(f'Failed to fetch Spotify token: {str(e)}')
            return None


def _load_persistent_cache():
    global _spotify_persistent_cache, _persistent_cache_loaded
    if not os.path.exists(SPOTIFY_CACHE_FILE):
        _persistent_cache_loaded = True
        return
    try:
        with open(SPOTIFY_CACHE_FILE, 'r', encoding='utf-8') as handle:
            data = json.load(handle)
            if isinstance(data, dict):
                _spotify_persistent_cache = data
    except Exception:
        _spotify_persistent_cache = {}
    _persistent_cache_loaded = True


def _ensure_persistent_cache_loaded():
    if not _persistent_cache_loaded:
        _load_persistent_cache()


def _cache_miss(query):
    return {
        'cachedMiss': True,
        'query': query,
        'albumArt': '',
        'spotifyUrl': '',
        'artworkSource': 'spotify-miss',
        'artworkFailureReason': 'Song not found on Spotify'
    }


def _is_cached_miss(value):
    return isinstance(value, dict) and value.get('cachedMiss') is True


def _save_persistent_cache():
    try:
        os.makedirs(os.path.dirname(SPOTIFY_CACHE_FILE), exist_ok=True)
        with open(SPOTIFY_CACHE_FILE, 'w', encoding='utf-8') as handle:
            json.dump(_spotify_persistent_cache, handle, indent=2, ensure_ascii=False)
    except Exception:
        pass


def _resolve_album_images(images):
    if not images:
        return {
            'albumArtHD': '',
            'albumArtMedium': '',
            'albumArtThumb': '',
            'albumArt': ''
        }

    sorted_images = sorted(images, key=lambda img: (img.get('width') or 0, img.get('height') or 0), reverse=True)
    album_art_hd = sorted_images[0].get('url', '')
    album_art_thumb = sorted_images[-1].get('url', '')
    album_art_medium = sorted_images[len(sorted_images) // 2].get('url', '')
    return {
        'albumArtHD': album_art_hd,
        'albumArtMedium': album_art_medium,
        'albumArtThumb': album_art_thumb,
        'albumArt': album_art_hd or album_art_medium or album_art_thumb
    }


def _best_album_image(images):
    return _resolve_album_images(images)['albumArt']


def _fetch_artist_profile(artist_id, token):
    if not artist_id or not token:
        return {}

    now = time.time()
    with _cache_lock:
        cached = _artist_cache.get(artist_id)
        if cached and now - cached['time'] < CACHE_TTL_SECONDS:
            return cached['profile']

    try:
        headers = {'Authorization': f'Bearer {token}'}
        resp = requests.get(SPOTIFY_ARTIST_URL.format(id=artist_id), headers=headers, timeout=6)
        resp.raise_for_status()
        artist = resp.json()
        profile = {
            'artistImage': _best_album_image(artist.get('images', [])),
            'artistGenres': artist.get('genres', [])[:4],
            'artistPopularity': artist.get('popularity')
        }
    except Exception as e:
        logger.warning(f'Artist metadata lookup failed for {artist_id}: {str(e)}')
        profile = {}

    with _cache_lock:
        _artist_cache[artist_id] = {'time': now, 'profile': profile}
    return profile


def _fetch_track_by_id(track_id, token):
    if not track_id or not token:
        return None
    headers = {'Authorization': f'Bearer {token}'}
    data = _fetch_with_retry(SPOTIFY_TRACK_URL.format(id=track_id), headers, {'market': 'IN'})
    return data if isinstance(data, dict) and data.get('id') else None


def _fetch_album_images(album_id, token):
    if not album_id or not token:
        return []
    headers = {'Authorization': f'Bearer {token}'}
    data = _fetch_with_retry(SPOTIFY_ALBUM_URL.format(id=album_id), headers, {'market': 'IN'})
    return data.get('images', []) if isinstance(data, dict) else []


def _normalize_text(value):
    return ' '.join(str(value or '').lower().strip().split())


def _normalize_match_text(value):
    text = str(value or '').lower()
    text = re.sub(r'\([^)]*\)|\[[^\]]*\]', ' ', text)
    text = re.sub(r'[^a-z0-9]+', ' ', text)
    return ' '.join(text.split())


def _tokens(value):
    return {token for token in _normalize_match_text(value).split() if token}


def _primary_artist(value):
    return str(value or '').split(',')[0].split('&')[0].strip()


def _has_unwanted_version(candidate_name, album_name, requested_title):
    requested = _normalize_match_text(requested_title)
    candidate = _normalize_match_text(f'{candidate_name} {album_name}')
    for term in UNOFFICIAL_VERSION_TERMS:
        normalized_term = _normalize_match_text(term)
        if normalized_term in candidate and normalized_term not in requested:
            return True
    return False


def _artist_overlap_score(expected_artist, candidate_artist):
    expected = _tokens(expected_artist)
    candidate = _tokens(candidate_artist)
    if not expected or not candidate:
        return 0
    if expected == candidate:
        return 12
    overlap = expected & candidate
    if _normalize_match_text(_primary_artist(expected_artist)) in _normalize_match_text(candidate_artist):
        return 10
    return len(overlap) * 3


def _title_match_score(expected_title, candidate_title):
    expected = _normalize_match_text(expected_title)
    candidate = _normalize_match_text(candidate_title)
    if not expected or not candidate:
        return 0
    if expected == candidate:
        return 24
    expected_tokens = set(expected.split())
    candidate_tokens = set(candidate.split())
    if expected_tokens and expected_tokens.issubset(candidate_tokens):
        return 16
    overlap = expected_tokens & candidate_tokens
    return len(overlap) * 3


def select_best_track_result(items, title=None, artist=None, album=None):
    if not items:
        return None

    normalized_title = _normalize_match_text(title)
    normalized_artist = _normalize_match_text(artist)
    normalized_album = _normalize_match_text(album)
    has_expected_metadata = bool(normalized_title or normalized_artist)

    def score_item(item):
        if not isinstance(item, dict):
            return -999

        name = str(item.get('name') or item.get('title') or '').strip()
        artists = item.get('artists') or []
        artist_names = ' '.join([str(a.get('name') or '').strip() for a in artists if a.get('name')]).strip()
        album_info = item.get('album') or {}
        album_name = str(album_info.get('name') or '').strip()
        images = album_info.get('images') or []
        image_urls = [img.get('url') for img in images if isinstance(img, dict) and img.get('url')]
        has_artwork = bool(image_urls)

        score = 0
        if _has_unwanted_version(name, album_name, title):
            score -= 55
        if has_artwork:
            score += 24
        score += _title_match_score(title, name)
        score += _artist_overlap_score(artist, artist_names)
        if normalized_album and _normalize_match_text(album_name) == normalized_album:
            score += 10
        elif normalized_album and album_name:
            score += 2 * len(set(normalized_album.split()) & set(_normalize_match_text(album_name).split()))
        if item.get('external_urls', {}).get('spotify'):
            score += 2
        if item.get('popularity') is not None:
            score += min(12, int(item.get('popularity') or 0) / 8)
        return score

    ranked = sorted(items, key=score_item, reverse=True)
    best = ranked[0] if ranked else None
    if not best:
        return None
    if has_expected_metadata and score_item(best) < 18:
        return None
    return best


def _build_track(item, token=None):
    try:
        album = item.get('album') or {}
        album_images = album.get('images', [])
        if not album_images and token:
            album_images = _fetch_album_images(album.get('id'), token)
            if album_images:
                album['images'] = album_images
        title = item.get('name') or 'Unknown Title'
        artists = item.get('artists', [])
        artist = ', '.join([a.get('name', 'Unknown Artist') for a in artists]) or 'Unknown Artist'
        primary_artist_id = artists[0].get('id') if artists else None
        artist_profile = _fetch_artist_profile(primary_artist_id, token) if token else {}
        spotify_url = item.get('external_urls', {}).get('spotify', '')
        release_date = album.get('release_date') or ''
        release_year = 0
        if release_date:
            try:
                release_year = int(release_date.split('-')[0])
            except ValueError:
                release_year = 0

        album_images = _resolve_album_images(album.get('images', []))
        return {
            'title': title,
            'name': title,
            'artist': artist,
            'album': album.get('name', ''),
            'albumName': album.get('name', ''),
            'album_art': album_images['albumArt'],
            'albumArt': album_images['albumArt'],
            'albumArtHD': album_images['albumArtHD'],
            'albumArtMedium': album_images['albumArtMedium'],
            'albumArtThumb': album_images['albumArtThumb'],
            'image': album_images['albumArt'],
            'thumbnail': album_images['albumArtThumb'],
            'preview_url': item.get('preview_url'),
            'previewUrl': item.get('preview_url'),
            'spotify_url': spotify_url,
            'spotifyUrl': spotify_url,
            'spotifyId': item.get('id'),
            'track_id': item.get('id'),
            'trackId': item.get('id'),
            'isrc': (item.get('external_ids') or {}).get('isrc', ''),
            'durationMs': item.get('duration_ms'),
            'popularity': item.get('popularity'),
            'releaseYear': release_year,
            'artistImage': artist_profile.get('artistImage', ''),
            'artistGenres': artist_profile.get('artistGenres', []),
            'artistPopularity': artist_profile.get('artistPopularity'),
            'artworkSource': 'spotify' if album_images['albumArt'] else ''
        }
    except Exception as e:
        logger.error(f'Error building track object: {str(e)}')
        return None


def _fetch_with_retry(url, headers, params, max_retries=2):
    global _rate_limited_until
    now = time.time()
    if now < _rate_limited_until:
        retry_after = int(_rate_limited_until - now)
        raise SpotifyRateLimited(f'Spotify rate limited; retry after {retry_after}s')

    for attempt in range(max_retries + 1):
        try:
            r = requests.get(url, headers=headers, params=params, timeout=10)
            if r.status_code == 429:
                retry_after = int(r.headers.get('Retry-After', 2))
                if retry_after > 10:
                    _rate_limited_until = time.time() + retry_after
                    logger.warning(
                        'Spotify rate limited with Retry-After=%ss; skipping lookup to keep recommendations responsive',
                        retry_after
                    )
                    raise SpotifyRateLimited(f'Spotify rate limited; retry after {retry_after}s')
                logger.warning(f'Spotify rate limited. Retrying after {retry_after}s')
                time.sleep(retry_after)
                continue
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            if attempt == max_retries:
                logger.error(f'Spotify API request failed after {max_retries} retries: {str(e)}')
                raise
            backoff = 2 ** attempt
            logger.warning(f'Spotify API request failed. Retrying in {backoff}s... (Attempt {attempt+1}/{max_retries})')
            time.sleep(backoff)
    return None


def _search_one(query, token, title=None, artist=None, album=None, force=False):
    _ensure_persistent_cache_loaded()
    key = _metadata_cache_key(query, title, artist, album)
    now = time.time()

    if not force:
        with _cache_lock:
            cached = _track_cache.get(key)
            if cached and now - cached['time'] < CACHE_TTL_SECONDS:
                return cached['track']
            cached = _spotify_persistent_cache.get(key)
            if cached and not _is_cached_miss(cached):
                return cached

    headers = {'Authorization': f'Bearer {token}'}
    params = {'q': query, 'type': 'track', 'limit': 10, 'market': 'IN'}
    data = _fetch_with_retry(SPOTIFY_SEARCH_URL, headers, params)
    items = data.get('tracks', {}).get('items', []) if data else []
    best_item = select_best_track_result(items, title=title, artist=artist, album=album)
    track = _build_track(best_item, token) if best_item else None

    if track:
        logger.info(
            f"Spotify search [{query}] returned artwork={bool(track.get('albumArt'))} "
            f"albumArtUrl={track.get('albumArt')} spotifyUrl={track.get('spotifyUrl')}"
        )
    else:
        logger.info(f"Spotify search [{query}] returned no results")

    with _cache_lock:
        _track_cache[key] = {'time': now, 'track': track}
        if track is not None:
            _spotify_persistent_cache[key] = track
        _save_persistent_cache()
    return track


def search_tracks_if_available(queries):
    _ensure_persistent_cache_loaded()

    token = get_token()
    if not token:
        logger.warning('Skipping Spotify search (no token available)')
        return []

    tracks = []
    for q in queries:
        try:
            track = _search_one(q, token)
            if track:
                tracks.append(track)
        except Exception as e:
            logger.error(f"Error searching for query '{q}': {str(e)}")
            continue
    return tracks


def search_spotify_tracks(query, limit=5):
    _ensure_persistent_cache_loaded()
    token = get_token()
    if not token:
        raise RuntimeError('Spotify credentials are missing or token fetch failed')

    headers = {'Authorization': f'Bearer {token}'}
    params = {'q': query, 'type': 'track', 'limit': limit, 'market': 'IN'}

    try:
        data = _fetch_with_retry(SPOTIFY_SEARCH_URL, headers, params)
        if data:
            items = data.get('tracks', {}).get('items', [])
            if items:
                best_item = select_best_track_result(items)
                if best_item:
                    track = _build_track(best_item, token)
                    if track:
                        return [track]
            return [t for t in [_build_track(item, token) for item in items] if t is not None]
    except Exception as e:
        logger.error(f'Error in search_spotify_tracks: {str(e)}')
        raise RuntimeError(f'Spotify search failed: {str(e)}')

    return []


def _has_spotify_artwork(track):
    if not track:
        return False
    album_art = track.get('albumArt') or track.get('album_art') or ''
    return (
        bool(album_art)
        and str(album_art).startswith('http')
        and bool(track.get('spotifyUrl') or track.get('spotify_url'))
        and bool(track.get('spotifyId') or track.get('track_id') or track.get('trackId'))
    )


def _missing_artwork_reason(track):
    if not track:
        return 'Invalid metadata'
    if not (track.get('title') or track.get('name')) or not track.get('artist'):
        return 'Invalid metadata'
    if track.get('artworkFailureReason'):
        return track.get('artworkFailureReason')
    if not is_available():
        return 'Spotify credentials unavailable'
    return 'Song not found on Spotify'


def _candidate_queries(title, artist, album):
    queries = []
    primary_artist = _primary_artist(artist)
    if title and primary_artist:
        queries.extend([
            f'track:"{title}" artist:"{primary_artist}"',
            f'{title} {primary_artist}',
            f'{primary_artist} {title}',
        ])
    if title and artist and artist != primary_artist:
        queries.extend([f'{title} {artist}', f'{artist} {title}'])
    if title and album:
        queries.append(f'{title} {album}')
    return list(dict.fromkeys(q.strip() for q in queries if q and q.strip()))


def enrich_track_if_available(track, force=False):
    if not track:
        return track

    if not _spotify_persistent_cache:
        _ensure_persistent_cache_loaded()

    token = get_token()
    if not token:
        logger.warning(
            f"Skipping Spotify enrichment for '{track.get('title', '')}' by "
            f"'{track.get('artist', '')}' — no valid Spotify token available"
        )
        return track

    title = track.get('title') or track.get('name') or ''
    artist = track.get('artist') or track.get('artists') or ''
    album = track.get('albumName') or track.get('album') or ''
    if not title or not artist:
        return track

    if _has_spotify_artwork(track) and not force:
        return track

    candidate_queries = []
    spotify_id = track.get('spotifyId') or track.get('track_id') or track.get('trackId')
    if spotify_id:
        try:
            item = _fetch_track_by_id(spotify_id, token)
            spotify_track = _build_track(item, token) if item else None
            if spotify_track and spotify_track.get('albumArt'):
                candidate_queries = []
            else:
                spotify_track = None
        except SpotifyRateLimited as e:
            missed = dict(track)
            missed['artworkFailureReason'] = str(e)
            return missed
        except Exception as e:
            logger.warning(f"Spotify track ID lookup failed for '{title}' ({spotify_id}): {str(e)}")
            spotify_track = None
    else:
        spotify_track = None

    query = track.get('spotifyQuery') or f'{title} {artist}'.strip()
    candidate_queries.extend(_candidate_queries(title, artist, album))
    if query:
        candidate_queries.append(query)
    isrc = track.get('isrc')
    if isrc:
        candidate_queries.insert(0, f'isrc:{isrc}')
    candidate_queries = list(dict.fromkeys(q for q in candidate_queries if q))

    if not spotify_track:
        for candidate_query in candidate_queries:
            try:
                spotify_track = _search_one(
                    candidate_query,
                    token,
                    title=title,
                    artist=artist,
                    album=album,
                    force=force
                )
            except SpotifyRateLimited as e:
                missed = dict(track)
                missed['artworkFailureReason'] = str(e)
                return missed
            except Exception as e:
                logger.error(f"Spotify enrichment failed for '{candidate_query}': {str(e)}")
                continue
            if spotify_track and spotify_track.get('albumArt'):
                break

    if not spotify_track:
        missed = dict(track)
        missed['artworkFailureReason'] = 'Song not found on Spotify or official artist/title match failed'
        return missed

    album_art = spotify_track.get('albumArt') or spotify_track.get('album_art') or track.get('albumArt') or track.get('album_art') or ''
    enriched = dict(track)
    enriched.update({
        'title': title,
        'name': title,
        'artist': artist,
        'language': track.get('language'),
        'album': spotify_track.get('album') or track.get('album', ''),
        'albumName': spotify_track.get('albumName') or track.get('albumName', ''),
        'albumArt': album_art,
        'albumArtHD': spotify_track.get('albumArtHD') or spotify_track.get('albumArt') or spotify_track.get('album_art') or track.get('albumArtHD') or album_art,
        'albumArtMedium': spotify_track.get('albumArtMedium') or track.get('albumArtMedium') or album_art,
        'albumArtThumb': spotify_track.get('albumArtThumb') or track.get('albumArtThumb') or album_art,
        'album_art': album_art,
        'image': spotify_track.get('image') or track.get('image', ''),
        'thumbnail': spotify_track.get('thumbnail') or track.get('thumbnail', ''),
        'preview_url': spotify_track.get('preview_url'),
        'previewUrl': spotify_track.get('previewUrl'),
        'spotifyUrl': spotify_track.get('spotifyUrl') or track.get('spotifyUrl'),
        'spotify_url': spotify_track.get('spotify_url') or track.get('spotify_url'),
        'spotifyId': spotify_track.get('spotifyId'),
        'track_id': spotify_track.get('track_id') or spotify_track.get('spotifyId'),
        'trackId': spotify_track.get('trackId') or spotify_track.get('spotifyId'),
        'isrc': spotify_track.get('isrc') or track.get('isrc', ''),
        'durationMs': spotify_track.get('durationMs'),
        'popularity': spotify_track.get('popularity'),
        'popularityScore': spotify_track.get('popularity') or track.get('popularityScore'),
        'artistImage': spotify_track.get('artistImage') or track.get('artistImage', ''),
        'artistGenres': spotify_track.get('artistGenres') or track.get('artistGenres', []),
        'artistPopularity': spotify_track.get('artistPopularity'),
        'artworkSource': spotify_track.get('artworkSource') or track.get('artworkSource', ''),
        'spotifyEnriched': True,
        'artworkFailureReason': ''
    })
    return enriched


def enrich_recommendations_by_language(recommendations):
    if not is_available():
        return recommendations

    enriched = {}
    for language, tracks in (recommendations or {}).items():
        ordered = list(tracks or [])
        language_results = [None] * len(ordered)
        with ThreadPoolExecutor(max_workers=6) as executor:
            future_map = {
                executor.submit(enrich_track_if_available, track): idx
                for idx, track in enumerate(ordered)
            }
            for future in as_completed(future_map):
                idx = future_map[future]
                try:
                    language_results[idx] = future.result()
                except Exception as e:
                    logger.error(f'Spotify enrichment worker failed: {str(e)}')
                    language_results[idx] = ordered[idx]
        enriched[language] = [track for track in language_results if track]
    return enriched


def clear_spotify_cache():
    global _spotify_persistent_cache, _track_cache, _artist_cache, _persistent_cache_loaded, _rate_limited_until
    with _cache_lock:
        _spotify_persistent_cache = {}
        _track_cache = {}
        _artist_cache = {}
        _persistent_cache_loaded = True
        _rate_limited_until = 0
        _save_persistent_cache()


def _write_artwork_report(report):
    try:
        os.makedirs(os.path.dirname(SPOTIFY_ARTWORK_REPORT_FILE), exist_ok=True)
        with open(SPOTIFY_ARTWORK_REPORT_FILE, 'w', encoding='utf-8') as handle:
            json.dump(report, handle, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.warning(f'Failed to write Spotify artwork report: {str(e)}')


def _report_for_catalog(catalog):
    by_language = {}
    missing = []
    enriched_count = 0
    for track in catalog or []:
        language = track.get('language') or 'Unknown'
        by_language.setdefault(language, {'total': 0, 'enriched': 0, 'missing': 0})
        by_language[language]['total'] += 1
        if _has_spotify_artwork(track):
            enriched_count += 1
            by_language[language]['enriched'] += 1
        else:
            reason = _missing_artwork_reason(track)
            by_language[language]['missing'] += 1
            missing.append({
                'title': track.get('title') or track.get('name') or '',
                'artist': track.get('artist') or '',
                'language': language,
                'reason': reason
            })
    return {
        'total': len(catalog or []),
        'enriched': enriched_count,
        'missing': len(missing),
        'byLanguage': by_language,
        'missingTracks': missing
    }


def enrich_catalog_artwork(catalog, force=False, return_report=False):
    if not is_available():
        report = _report_for_catalog(catalog)
        _write_artwork_report(report)
        if return_report:
            return catalog, report
        return catalog

    ordered = list(catalog or [])
    needs_lookup = [
        (idx, track)
        for idx, track in enumerate(ordered)
        if track
        and (
            force
            or not _has_spotify_artwork(track)
            or track.get('artworkSource') == 'generated'
            or str(track.get('albumArt') or '').startswith('data:')
        )
    ]
    if not needs_lookup:
        report = _report_for_catalog(ordered)
        _write_artwork_report(report)
        if return_report:
            return ordered, report
        return ordered

    enriched = list(ordered)
    with ThreadPoolExecutor(max_workers=6) as executor:
        future_map = {
            executor.submit(enrich_track_if_available, track, force): idx
            for idx, track in needs_lookup
        }
        for future in as_completed(future_map):
            idx = future_map[future]
            try:
                enriched[idx] = future.result() or ordered[idx]
            except Exception as e:
                logger.error(f'Catalog artwork enrichment failed: {str(e)}')
                failed = dict(ordered[idx])
                failed['artworkFailureReason'] = str(e)
                enriched[idx] = failed

    report = _report_for_catalog(enriched)
    _write_artwork_report(report)
    logger.info(
        'Spotify catalog artwork report: total=%s enriched=%s missing=%s',
        report['total'],
        report['enriched'],
        report['missing']
    )
    if return_report:
        return enriched, report
    return enriched