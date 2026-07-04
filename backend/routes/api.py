import logging
import os
import re
import time
from collections import defaultdict
from urllib.parse import quote_plus

import requests
from flask import Blueprint, request, jsonify, make_response, redirect
from dotenv import load_dotenv
from werkzeug.exceptions import BadRequest

from services.auth import create_session_token, load_current_user, SESSION_MAX_AGE
from services.sentiment import analyze_text
from services.recommender import recommend_for_mood, MULTILINGUAL_CATALOG
from services.music_database import normalize_language, rebuild_spotify_catalog_cache
from services.spotify import (
    search_spotify_tracks,
    enrich_recommendations_by_language,
    is_available
)
from services.database import (
    init_db,
    save_mood,
    fetch_recent,
    fetch_analytics,
    create_or_update_user,
    get_user_by_google_id,
    get_user_by_id,
    delete_history_entry,
    clear_history,
    save_journal_entry,
    fetch_journal_entries,
    delete_journal_entry,
    upsert_spotify_connection,
    get_spotify_connection,
    save_user_settings,
    get_user_settings,
    fetch_user_analytics
)

logger = logging.getLogger(__name__)

load_dotenv()
api = Blueprint('api', __name__, url_prefix='/api')

_RATE_LIMIT_WINDOW_SECONDS = 60
_RATE_LIMIT_MAX_REQUESTS = 60
_RATE_LIMIT_BUCKETS = defaultdict(list)

SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize'
SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'
SPOTIFY_USER_PROFILE_URL = 'https://api.spotify.com/v1/me'
SPOTIFY_USER_SAVE_URL = 'https://api.spotify.com/v1/me/tracks'
SPOTIFY_USER_QUEUE_URL = 'https://api.spotify.com/v1/me/player/queue'
SPOTIFY_PLAYLIST_ADD_URL = 'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'


def safe_json(data):
    try:
        return jsonify(data)
    except Exception:
        return jsonify({'error': 'Failed to serialize response'}), 500


def _error_response(message, status_code=400, details=None):
    payload = {'error': message}
    if details is not None:
        payload['details'] = details
    return jsonify(payload), status_code


def _verify_google_token(id_token):
    if not id_token:
        return None, 'Missing Google ID token.'

    try:
        response = requests.get(
            'https://oauth2.googleapis.com/tokeninfo',
            params={'id_token': id_token},
            timeout=10
        )
        data = response.json()
    except Exception as e:
        return None, f'Failed to validate Google token: {str(e)}'

    if response.status_code != 200:
        return None, data.get('error_description') or data.get('error') or 'Invalid Google token.'

    expected_audience = os.getenv('GOOGLE_CLIENT_ID')
    if expected_audience and data.get('aud') != expected_audience:
        return None, 'Google token audience mismatch.'

    if data.get('iss') not in ('accounts.google.com', 'https://accounts.google.com'):
        return None, 'Google token issuer is not trusted.'

    email_verified = str(data.get('email_verified', '')).lower()
    if email_verified not in ('true', '1'):
        return None, 'Google account email must be verified.'

    return data, None


def _spotify_redirect_uri():
    return os.getenv('SPOTIFY_REDIRECT_URI') or f"{request.url_root.rstrip('/')}/api/spotify/callback"


def _spotify_auth_credentials():
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    if not client_id or not client_secret:
        return None, None
    return client_id, client_secret


def _refresh_spotify_access_token(connection):
    client_id, client_secret = _spotify_auth_credentials()
    if not client_id or not client_secret or not connection:
        return None

    refresh_token = connection.get('refresh_token')
    if not refresh_token:
        return None

    try:
        resp = requests.post(
            SPOTIFY_TOKEN_URL,
            data={
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            },
            auth=(client_id, client_secret),
            timeout=10
        )
        resp.raise_for_status()
        token_data = resp.json()
    except Exception as e:
        logger.warning('Failed to refresh Spotify token: %s', str(e))
        return None

    access_token = token_data.get('access_token')
    expires_in = int(token_data.get('expires_in', 3600))
    expires_at = int(time.time() + expires_in)
    scopes = token_data.get('scope') or connection.get('scopes')

    upsert_spotify_connection(
        connection['user_id'],
        connection.get('spotify_user_id'),
        connection.get('display_name'),
        connection.get('profile_url'),
        connection.get('country'),
        connection.get('followers'),
        int(connection.get('premium', False)),
        access_token,
        refresh_token,
        expires_at,
        scopes
    )

    updated_connection = get_spotify_connection(connection['user_id'])
    return updated_connection


def _get_spotify_user_token(user_id):
    connection = get_spotify_connection(user_id)
    if not connection:
        return None

    expires_at = connection.get('expires_at') or 0
    if expires_at and time.time() > expires_at - 60:
        connection = _refresh_spotify_access_token(connection)

    return connection.get('access_token') if connection else None


def _set_auth_cookie(response, token, max_age=SESSION_MAX_AGE):
    secure_cookie = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() in ('1', 'true', 'yes')
    response.set_cookie(
        'moodify_auth_token',
        token,
        max_age=max_age,
        httponly=True,
        secure=secure_cookie,
        samesite='None',
        path='/'
    )
    return response


def _rate_limited():
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr or 'unknown')
    now = time.time()
    requests = _RATE_LIMIT_BUCKETS[client_ip]
    requests[:] = [stamp for stamp in requests if now - stamp < _RATE_LIMIT_WINDOW_SECONDS]
    if len(requests) >= _RATE_LIMIT_MAX_REQUESTS:
        return True
    requests.append(now)
    return False


@api.errorhandler(BadRequest)
def handle_bad_request(error):
    return _error_response('Invalid request payload', 400, str(error))


@api.route('/analyze', methods=['POST'])
def analyze():
    if _rate_limited():
        return _error_response('Rate limit exceeded. Please wait a moment before retrying.', 429)

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return _error_response('JSON body with a text field is required.', 400)

    text = str(payload.get('text', '') or '').strip()
    source = str(payload.get('source', 'text') or 'text').strip()
    if not text:
        return _error_response('No text provided.', 400)
    if len(text) > 1200:
        return _error_response('Text is too long. Please keep it to 1200 characters or fewer.', 400)
    if not re.search(r'[A-Za-z]', text):
        return _error_response('Please provide a text snippet with letters so the mood analysis can run.', 400)

    session_id = str(payload.get('session_id') or request.headers.get('X-Session-Id') or request.args.get('session_id') or 'default').strip() or 'default'
    selected_language = normalize_language(payload.get('language') or request.args.get('language'))
    analysis = analyze_text(text)
    recommendation = recommend_for_mood(analysis, session_id=session_id, language=selected_language)

    mood = analysis['mood']
    scores = analysis['scores']
    queries = recommendation['queries']
    recommendations_by_language = enrich_recommendations_by_language(recommendation.get('recommendationsByLanguage', {}))
    response_language = selected_language or recommendation.get('selectedLanguage') or 'English'
    tracks = recommendations_by_language.get(response_language) or recommendation.get('fallback_tracks') or []

    current_user, _ = load_current_user(request)
    save_mood(
        mood,
        scores,
        text,
        recommendation['title'],
        recommendation['genres'],
        queries,
        user_id=current_user['id'] if current_user else None,
        language=response_language,
        recommended_songs=tracks,
        top_song=tracks[0] if tracks else {},
        confidence=analysis.get('confidence')
    )

    logger.info('Returning analysis payload with %d tracks; spotify_active=%s; user_id=%s', len(tracks), is_available(), current_user['id'] if current_user else 'anonymous')

    payload = {
        'mood': mood,
        'primaryEmotion': analysis.get('primaryEmotion'),
        'secondary': analysis.get('secondary'),
        'hiddenUndertone': analysis.get('hiddenUndertone'),
        'nuancedLabel': analysis.get('nuancedLabel'),
        'archetype': analysis.get('archetype'),
        'intensity': analysis.get('intensity'),
        'context': analysis.get('context'),
        'dimensions': analysis.get('dimensions'),
        'scores': scores,
        'confidence': analysis['confidence'],
        'genres': recommendation['genres'],
        'playlists': recommendation['playlists'],
        'title': recommendation['title'],
        'recommendationsByLanguage': recommendations_by_language,
        'tracks': tracks,
        'selectedLanguage': selected_language or recommendation.get('selectedLanguage'),
        'explanation': recommendation['explanation'],
        'spotify_active': is_available(),
        'source': source,
        'session_id': session_id,
    }
    return safe_json(payload)


@api.route('/recommendations', methods=['GET'])
def recommendations():
    mood = (request.args.get('mood', 'Chill') or 'Chill').strip()
    time_of_day = request.args.get('time_of_day')
    selected_language = normalize_language(request.args.get('language'))
    try:
        score_data = {
            'energy': float(request.args.get('energy', 50)),
            'happiness': float(request.args.get('happiness', 50))
        }
    except ValueError:
        return _error_response('Energy and happiness must be numeric values.', 400)

    session_id = request.args.get('session_id') or request.headers.get('X-Session-Id') or 'default'
    result = recommend_for_mood({'mood': mood, 'scores': score_data}, time_of_day, session_id=session_id, language=selected_language)
    result['recommendationsByLanguage'] = enrich_recommendations_by_language(result.get('recommendationsByLanguage', {}))
    return safe_json(result)


@api.route('/history', methods=['GET'])
def history():
    try:
        limit = int(request.args.get('limit', 50))
    except ValueError:
        return _error_response('Limit must be an integer.', 400)

    current_user, _ = load_current_user(request)
    search = request.args.get('search', '').strip() or None
    mood = request.args.get('mood', '').strip() or None
    start_date = request.args.get('start_date', '').strip() or None
    end_date = request.args.get('end_date', '').strip() or None

    entries = fetch_recent(
        limit,
        user_id=current_user['id'] if current_user else None,
        search=search,
        mood=mood,
        start_date=start_date,
        end_date=end_date
    )
    return safe_json({'history': entries})


@api.route('/history/<int:entry_id>', methods=['DELETE'])
def delete_history_entry_route(entry_id):
    current_user, _ = load_current_user(request)
    if not current_user:
        return _error_response('Authentication required.', 401)

    delete_history_entry(entry_id, current_user['id'])
    return safe_json({'status': 'deleted'})


@api.route('/history/clear', methods=['POST'])
def clear_history_route():
    current_user, _ = load_current_user(request)
    if not current_user:
        return _error_response('Authentication required.', 401)

    clear_history(current_user['id'])
    return safe_json({'status': 'cleared'})


@api.route('/analytics', methods=['GET'])
def analytics():
    current_user, _ = load_current_user(request)
    data = fetch_user_analytics(current_user['id']) if current_user else fetch_analytics()
    return safe_json(data)


@api.route('/search', methods=['GET'])
def search_catalog():
    query = request.args.get('q', '').strip()
    if not query:
        return _error_response('Query required', 400)

    try:
        limit = int(request.args.get('limit', 8))
    except ValueError:
        return _error_response('Limit must be an integer.', 400)

    limit = max(1, min(limit, 20))
    normalized_query = re.sub(r'[^a-z0-9]+', ' ', query.lower()).split()
    matches = []

    for track in MULTILINGUAL_CATALOG:
        haystack = ' '.join([
            track.get('title', ''),
            track.get('artist', ''),
            track.get('language', ''),
            ' '.join(track.get('moodTags', []))
        ]).lower()

        score = 0
        for token in normalized_query:
            if token in haystack:
                score += 4
        if query.lower() in haystack:
            score += 2

        if score:
            matches.append((score, track))

    matches.sort(key=lambda item: (-item[0], item[1].get('title', '').lower()))
    results = [
        {
            'title': track.get('title'),
            'artist': track.get('artist'),
            'language': track.get('language'),
            'moodTags': track.get('moodTags', []),
            'energyLevel': track.get('energyLevel')
        }
        for _, track in matches[:limit]
    ]
    return safe_json({'results': results, 'query': query})


@api.route('/spotify/search', methods=['GET'])
def spotify_search():
    query = request.args.get('q', '').strip()
    if not query:
        return _error_response('Query required', 400)
    try:
        results = search_spotify_tracks(query)
        return safe_json({'results': results})
    except Exception as e:
        return _error_response('Spotify search failed', 502, str(e))


@api.route('/catalog/rebuild-artwork', methods=['POST'])
def rebuild_artwork():
    """Force re-fetch of real Spotify artwork for every cached track, replacing
    any placeholder/generated images. Use this once after confirming Spotify
    credentials are valid (e.g. via /api/spotify/search) to fix a catalog that
    was built while Spotify was unreachable."""
    if not is_available():
        return _error_response(
            'Spotify credentials are not configured (SPOTIFY_CLIENT_ID / SPOTIFY_CLIENT_SECRET missing)',
            503
        )
    try:
        report = rebuild_spotify_catalog_cache()
        return safe_json({'status': 'ok', 'report': report})
    except Exception as e:
        logger.error(f'Catalog rebuild failed: {str(e)}')
        return _error_response('Catalog rebuild failed', 500, str(e))


@api.route('/auth/google', methods=['POST'])
def auth_google():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return _error_response('Invalid request body for Google authentication.', 400)

    id_token = str(payload.get('id_token') or payload.get('credential') or '')
    token_data, error = _verify_google_token(id_token)
    if error:
        return _error_response(error, 401)

    google_id = token_data.get('sub')
    email = token_data.get('email') or ''
    name = token_data.get('name') or ''
    picture = token_data.get('picture') or ''

    if not google_id or not email:
        return _error_response('Google token did not contain required user information.', 400)

    user_id = create_or_update_user(google_id, email, name, picture)
    auth_token = create_session_token(user_id)

    response = make_response(jsonify({
        'user': {
            'id': user_id,
            'google_id': google_id,
            'email': email,
            'name': name,
            'picture': picture
        },
        'auth_token': auth_token
    }))
    return _set_auth_cookie(response, auth_token)


@api.route('/auth/logout', methods=['POST'])
def auth_logout():
    response = make_response(jsonify({'status': 'logged_out'}))
    response.set_cookie('moodify_auth_token', '', expires=0, path='/', httponly=True, secure=False, samesite='None')
    return response


@api.route('/auth/me', methods=['GET'])
def auth_me():
    current_user, _ = load_current_user(request)
    if not current_user:
        return _error_response('Authentication required.', 401)

    spotify_conn = get_spotify_connection(current_user['id'])
    return safe_json({
        'user': {
            'id': current_user['id'],
            'google_id': current_user['google_id'],
            'email': current_user['email'],
            'name': current_user['name'],
            'picture': current_user['picture'],
            'spotify': spotify_conn or {}
        }
    })


@api.route('/user/settings', methods=['GET', 'POST'])
def user_settings():
    current_user, _ = load_current_user(request)
    if not current_user:
        return _error_response('Authentication required.', 401)

    if request.method == 'POST':
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return _error_response('JSON body required.', 400)
        save_user_settings(current_user['id'], payload)
        return safe_json({'status': 'settings_saved'})

    settings = get_user_settings(current_user['id'])
    return safe_json({'settings': settings})


@api.route('/user/journal', methods=['GET', 'POST'])
def user_journal():
    current_user, _ = load_current_user(request)
    if not current_user:
        return _error_response('Authentication required.', 401)

    if request.method == 'POST':
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return _error_response('JSON body required.', 400)

        mood = str(payload.get('mood', '') or '').strip()
        prompt = str(payload.get('prompt', '') or '').strip()
        note = str(payload.get('note', '') or '').strip()
        recommended_songs = payload.get('recommended_songs') if isinstance(payload.get('recommended_songs'), list) else []
        entry_id = payload.get('id')

        if not mood or not prompt:
            return _error_response('Journal entry requires mood and prompt text.', 400)

        saved_id = save_journal_entry(
            current_user['id'],
            mood,
            prompt,
            note,
            recommended_songs=recommended_songs,
            entry_id=entry_id
        )
        return safe_json({'status': 'saved', 'entry_id': saved_id})

    search = request.args.get('search', '').strip() or None
    mood = request.args.get('mood', '').strip() or None
    month = request.args.get('month', '').strip() or None
    entries = fetch_journal_entries(current_user['id'], search=search, mood=mood, month=month)
    return safe_json({'entries': entries})


@api.route('/user/journal/<int:entry_id>', methods=['DELETE'])
def delete_user_journal(entry_id):
    current_user, _ = load_current_user(request)
    if not current_user:
        return _error_response('Authentication required.', 401)

    delete_journal_entry(entry_id, current_user['id'])
    return safe_json({'status': 'deleted'})


@api.route('/spotify/authorize', methods=['GET'])
def spotify_authorize():
    current_user, _ = load_current_user(request)
    if not current_user:
        return _error_response('Authentication required.', 401)

    client_id, client_secret = _spotify_auth_credentials()
    if not client_id or not client_secret:
        return _error_response('Spotify OAuth is not configured on the server.', 503)

    redirect_uri = _spotify_redirect_uri()
    scopes = 'user-read-private user-read-email user-library-modify user-read-playback-state user-modify-playback-state playlist-modify-private playlist-modify-public'
    authorize_url = (
        f"{SPOTIFY_AUTH_URL}?client_id={quote_plus(client_id)}"
        f"&response_type=code&redirect_uri={quote_plus(redirect_uri)}"
        f"&scope={quote_plus(scopes)}"
        f"&show_dialog=true"
    )
    return safe_json({'authorize_url': authorize_url})


@api.route('/spotify/callback', methods=['GET'])
def spotify_callback():
    current_user, _ = load_current_user(request)
    if not current_user:
        return _error_response('Authentication required during Spotify callback.', 401)

    if request.args.get('error'):
        return _error_response(f"Spotify authorization failed: {request.args.get('error')}", 400)

    code = request.args.get('code')
    if not code:
        return _error_response('Spotify authorization code is missing.', 400)

    client_id, client_secret = _spotify_auth_credentials()
    if not client_id or not client_secret:
        return _error_response('Spotify OAuth is not configured on the server.', 503)

    redirect_uri = _spotify_redirect_uri()
    try:
        token_response = requests.post(
            SPOTIFY_TOKEN_URL,
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': redirect_uri
            },
            auth=(client_id, client_secret),
            timeout=10
        )
        token_response.raise_for_status()
        token_data = token_response.json()
    except Exception as e:
        return _error_response('Unable to fetch Spotify access token.', 502, str(e))

    access_token = token_data.get('access_token')
    refresh_token = token_data.get('refresh_token')
    expires_in = int(token_data.get('expires_in', 3600))
    expires_at = int(time.time() + expires_in)
    scope = token_data.get('scope', '')

    try:
        profile_resp = requests.get(
            SPOTIFY_USER_PROFILE_URL,
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10
        )
        profile_resp.raise_for_status()
        profile_data = profile_resp.json()
    except Exception as e:
        return _error_response('Unable to fetch Spotify profile.', 502, str(e))

    upsert_spotify_connection(
        current_user['id'],
        profile_data.get('id', ''),
        profile_data.get('display_name', ''),
        profile_data.get('external_urls', {}).get('spotify', ''),
        profile_data.get('country', ''),
        int((profile_data.get('followers') or {}).get('total', 0)),
        1 if str(profile_data.get('product', '')).lower() == 'premium' else 0,
        access_token,
        refresh_token,
        expires_at,
        scope
    )

    frontend_url = os.getenv('FRONTEND_URL') or os.getenv('VITE_APP_URL') or 'http://localhost:5173'
    return redirect(frontend_url)


@api.route('/user/spotify', methods=['GET'])
def user_spotify():
    current_user, _ = load_current_user(request)
    if not current_user:
        return _error_response('Authentication required.', 401)

    connection = get_spotify_connection(current_user['id'])
    return safe_json({'spotify': connection or {}})


@api.route('/spotify/save', methods=['POST'])
def spotify_save_track():
    current_user, _ = load_current_user(request)
    if not current_user:
        return _error_response('Authentication required.', 401)

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return _error_response('JSON body required.', 400)

    track_id = str(payload.get('track_id') or '').strip()
    if not track_id:
        return _error_response('Track ID is required.', 400)

    access_token = _get_spotify_user_token(current_user['id'])
    if not access_token:
        return _error_response('Spotify account is not connected or token could not be refreshed.', 401)

    try:
        resp = requests.put(
            f"{SPOTIFY_USER_SAVE_URL}?ids={quote_plus(track_id)}",
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            },
            timeout=10
        )
        resp.raise_for_status()
        return safe_json({'status': 'saved'})
    except Exception as e:
        return _error_response('Unable to save track to Spotify your library.', 502, str(e))


@api.route('/spotify/queue', methods=['POST'])
def spotify_add_to_queue():
    current_user, _ = load_current_user(request)
    if not current_user:
        return _error_response('Authentication required.', 401)

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return _error_response('JSON body required.', 400)

    track_id = str(payload.get('track_id') or '').strip()
    if not track_id:
        return _error_response('Track ID is required.', 400)

    access_token = _get_spotify_user_token(current_user['id'])
    if not access_token:
        return _error_response('Spotify account is not connected or token could not be refreshed.', 401)

    try:
        resp = requests.post(
            f"{SPOTIFY_USER_QUEUE_URL}?uri=spotify:track:{quote_plus(track_id)}",
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10
        )
        resp.raise_for_status()
        return safe_json({'status': 'queued'})
    except Exception as e:
        return _error_response('Unable to add track to Spotify queue.', 502, str(e))


@api.route('/spotify/playlist', methods=['POST'])
def spotify_add_to_playlist():
    current_user, _ = load_current_user(request)
    if not current_user:
        return _error_response('Authentication required.', 401)

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return _error_response('JSON body required.', 400)

    track_id = str(payload.get('track_id') or '').strip()
    playlist_id = str(payload.get('playlist_id') or '').strip()
    if not track_id or not playlist_id:
        return _error_response('Track ID and playlist ID are required.', 400)

    access_token = _get_spotify_user_token(current_user['id'])
    if not access_token:
        return _error_response('Spotify account is not connected or token could not be refreshed.', 401)

    try:
        resp = requests.post(
            SPOTIFY_PLAYLIST_ADD_URL.format(playlist_id=quote_plus(playlist_id)),
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            },
            json={'uris': [f'spotify:track:{track_id}']},
            timeout=10
        )
        resp.raise_for_status()
        return safe_json({'status': 'playlist_updated'})
    except Exception as e:
        return _error_response('Unable to add track to Spotify playlist.', 502, str(e))
