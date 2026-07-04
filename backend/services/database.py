import json
import os
import sqlite3
from collections import Counter
from datetime import datetime, timedelta, timezone

DB_PATH = os.getenv('DATABASE_URL', 'sqlite:///moodify.db').replace('sqlite:///', '')


def _connect():
    directory = os.path.dirname(DB_PATH)
    if directory:
        os.makedirs(directory, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _connect()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS moods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            mood TEXT,
            scores_json TEXT,
            text TEXT,
            playlist_title TEXT,
            genres_json TEXT,
            queries_json TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            google_id TEXT UNIQUE,
            email TEXT,
            name TEXT,
            picture TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS mood_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            timestamp TEXT,
            mood TEXT,
            prompt TEXT,
            language TEXT,
            recommended_songs_json TEXT,
            top_song_json TEXT,
            confidence REAL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            timestamp TEXT,
            mood TEXT,
            prompt TEXT,
            note TEXT,
            recommended_songs_json TEXT,
            updated_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS spotify_connections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            spotify_user_id TEXT,
            display_name TEXT,
            profile_url TEXT,
            country TEXT,
            followers INTEGER,
            premium INTEGER,
            access_token TEXT,
            refresh_token TEXT,
            expires_at INTEGER,
            scopes TEXT,
            updated_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            settings_json TEXT,
            updated_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()


def create_or_update_user(google_id, email, name, picture):
    conn = _connect()
    c = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    c.execute('SELECT id FROM users WHERE google_id = ?', (google_id,))
    row = c.fetchone()
    if row:
        user_id = row['id']
        c.execute(
            'UPDATE users SET email = ?, name = ?, picture = ?, updated_at = ? WHERE id = ?',
            (email, name, picture, now, user_id)
        )
    else:
        c.execute(
            'INSERT INTO users (google_id, email, name, picture, created_at, updated_at) VALUES (?,?,?,?,?,?)',
            (google_id, email, name, picture, now, now)
        )
        user_id = c.lastrowid
    conn.commit()
    conn.close()
    return user_id


def get_user_by_google_id(google_id):
    conn = _connect()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE google_id = ?', (google_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id):
    conn = _connect()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def save_mood(mood, scores, text, playlist_title, genres, queries, user_id=None, language='English', recommended_songs=None, top_song=None, confidence=None):
    conn = _connect()
    c = conn.cursor()
    timestamp = datetime.now(timezone.utc).isoformat()
    c.execute(
        'INSERT INTO moods (timestamp,mood,scores_json,text,playlist_title,genres_json,queries_json) VALUES (?,?,?,?,?,?,?)',
        (
            timestamp,
            mood,
            json.dumps(scores),
            text,
            playlist_title,
            json.dumps(genres),
            json.dumps(queries)
        )
    )
    if user_id:
        c.execute(
            'INSERT INTO mood_history (user_id,timestamp,mood,prompt,language,recommended_songs_json,top_song_json,confidence) VALUES (?,?,?,?,?,?,?,?)',
            (
                user_id,
                timestamp,
                mood,
                text,
                language,
                json.dumps(recommended_songs or []),
                json.dumps(top_song or {}),
                confidence if confidence is not None else None
            )
        )
    conn.commit()
    conn.close()


def fetch_recent(limit=20, user_id=None, search=None, mood=None, start_date=None, end_date=None):
    conn = _connect()
    c = conn.cursor()
    if user_id:
        query = 'SELECT * FROM mood_history WHERE user_id = ?'
        params = [user_id]
        if search:
            query += ' AND (prompt LIKE ? OR mood LIKE ? OR language LIKE ?)'
            term = f'%{search}%'
            params.extend([term, term, term])
        if mood:
            query += ' AND mood = ?'
            params.append(mood)
        if start_date:
            query += ' AND timestamp >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND timestamp <= ?'
            params.append(end_date)
        query += ' ORDER BY id DESC LIMIT ?'
        params.append(limit)
        c.execute(query, params)
        rows = [dict(row) for row in c.fetchall()]
        conn.close()
        for row in rows:
            row['recommended_songs'] = json.loads(row.pop('recommended_songs_json') or '[]')
            row['top_song'] = json.loads(row.pop('top_song_json') or '{}')
        return rows
    c.execute('SELECT timestamp,mood,scores_json,text,playlist_title,genres_json,queries_json FROM moods ORDER BY id DESC LIMIT ?', (limit,))
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    for row in rows:
        row['scores'] = json.loads(row.pop('scores_json'))
        row['genres'] = json.loads(row.pop('genres_json'))
        row['queries'] = json.loads(row.pop('queries_json'))
    return rows


def fetch_analytics():
    conn = _connect()
    c = conn.cursor()
    c.execute('SELECT timestamp,mood FROM moods ORDER BY timestamp DESC')
    rows = [dict(row) for row in c.fetchall()]
    conn.close()

    mood_counts = Counter()
    daily = Counter()
    now = datetime.now(timezone.utc)
    seven_days_ago = now - timedelta(days=7)

    for row in rows:
        mood_counts[row['mood']] += 1
        try:
            day = datetime.fromisoformat(row['timestamp']).date()
        except ValueError:
            continue
        if day >= seven_days_ago.date():
            daily[str(day)] += 1

    trend = [{'date': str((now.date() - timedelta(days=i))), 'count': daily.get(str((now.date() - timedelta(days=i))), 0)} for i in reversed(range(7))]
    common_mood = mood_counts.most_common(1)[0][0] if mood_counts else None

    return {
        'total_entries': sum(mood_counts.values()),
        'mood_counts': dict(mood_counts),
        'weekly_trend': trend,
        'common_mood': common_mood
    }


def delete_history_entry(entry_id, user_id):
    conn = _connect()
    c = conn.cursor()
    c.execute('DELETE FROM mood_history WHERE id = ? AND user_id = ?', (entry_id, user_id))
    conn.commit()
    conn.close()


def clear_history(user_id):
    conn = _connect()
    c = conn.cursor()
    c.execute('DELETE FROM mood_history WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()


def save_journal_entry(user_id, mood, prompt, note, recommended_songs=None, entry_id=None):
    conn = _connect()
    c = conn.cursor()
    timestamp = datetime.now(timezone.utc).isoformat()
    if entry_id:
        c.execute(
            'UPDATE journal_entries SET mood = ?, prompt = ?, note = ?, recommended_songs_json = ?, updated_at = ? WHERE id = ? AND user_id = ?',
            (
                mood,
                prompt,
                note,
                json.dumps(recommended_songs or []),
                timestamp,
                entry_id,
                user_id
            )
        )
    else:
        c.execute(
            'INSERT INTO journal_entries (user_id,timestamp,mood,prompt,note,recommended_songs_json,updated_at) VALUES (?,?,?,?,?,?,?)',
            (
                user_id,
                timestamp,
                mood,
                prompt,
                note,
                json.dumps(recommended_songs or []),
                timestamp
            )
        )
        entry_id = c.lastrowid
    conn.commit()
    conn.close()
    return entry_id


def fetch_journal_entries(user_id, search=None, mood=None, month=None, limit=50):
    conn = _connect()
    c = conn.cursor()
    query = 'SELECT * FROM journal_entries WHERE user_id = ?'
    params = [user_id]
    if search:
        query += ' AND (prompt LIKE ? OR note LIKE ? OR mood LIKE ?)'
        term = f'%{search}%'
        params.extend([term, term, term])
    if mood:
        query += ' AND mood = ?'
        params.append(mood)
    if month:
        query += ' AND strftime("%Y-%m", timestamp) = ?'
        params.append(month)
    query += ' ORDER BY timestamp DESC LIMIT ?'
    params.append(limit)
    c.execute(query, params)
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    for row in rows:
        row['recommended_songs'] = json.loads(row.pop('recommended_songs_json') or '[]')
    return rows


def delete_journal_entry(entry_id, user_id):
    conn = _connect()
    c = conn.cursor()
    c.execute('DELETE FROM journal_entries WHERE id = ? AND user_id = ?', (entry_id, user_id))
    conn.commit()
    conn.close()


def upsert_spotify_connection(user_id, spotify_user_id, display_name, profile_url, country, followers, premium, access_token, refresh_token, expires_at, scopes):
    conn = _connect()
    c = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    c.execute('SELECT id FROM spotify_connections WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    if row:
        c.execute(
            'UPDATE spotify_connections SET spotify_user_id = ?, display_name = ?, profile_url = ?, country = ?, followers = ?, premium = ?, access_token = ?, refresh_token = ?, expires_at = ?, scopes = ?, updated_at = ? WHERE user_id = ?',
            (spotify_user_id, display_name, profile_url, country, followers, premium, access_token, refresh_token, expires_at, scopes, now, user_id)
        )
    else:
        c.execute(
            'INSERT INTO spotify_connections (user_id, spotify_user_id, display_name, profile_url, country, followers, premium, access_token, refresh_token, expires_at, scopes, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
            (user_id, spotify_user_id, display_name, profile_url, country, followers, premium, access_token, refresh_token, expires_at, scopes, now)
        )
    conn.commit()
    conn.close()


def get_spotify_connection(user_id):
    conn = _connect()
    c = conn.cursor()
    c.execute('SELECT * FROM spotify_connections WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    data = dict(row)
    data['premium'] = bool(data.get('premium'))
    return data


def save_user_settings(user_id, settings):
    conn = _connect()
    c = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    c.execute('SELECT id FROM user_settings WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    if row:
        c.execute('UPDATE user_settings SET settings_json = ?, updated_at = ? WHERE user_id = ?', (json.dumps(settings), now, user_id))
    else:
        c.execute('INSERT INTO user_settings (user_id, settings_json, updated_at) VALUES (?,?,?)', (user_id, json.dumps(settings), now))
    conn.commit()
    conn.close()


def get_user_settings(user_id):
    conn = _connect()
    c = conn.cursor()
    c.execute('SELECT settings_json FROM user_settings WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return {}
    try:
        return json.loads(row['settings_json'] or '{}')
    except Exception:
        return {}


def fetch_user_analytics(user_id):
    conn = _connect()
    c = conn.cursor()
    c.execute('SELECT mood, timestamp, language, recommended_songs_json FROM mood_history WHERE user_id = ? ORDER BY timestamp DESC', (user_id,))
    rows = [dict(row) for row in c.fetchall()]
    conn.close()

    mood_counts = Counter()
    daily = Counter()
    weekday = Counter()
    language_counts = Counter()
    recommended_counts = Counter()
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1)

    for row in rows:
        mood = row['mood']
        language = row.get('language')
        recommendations = []
        if row.get('recommended_songs_json'):
            try:
                recommendations = json.loads(row['recommended_songs_json'])
            except Exception:
                recommendations = []

        mood_counts[mood] += 1
        if language:
            language_counts[language] += 1

        for item in recommendations:
            if isinstance(item, dict):
                title = item.get('title') or item.get('name') or item.get('track') or item.get('song')
            else:
                title = str(item)
            if title:
                recommended_counts[title] += 1

        try:
            ts = datetime.fromisoformat(row['timestamp'])
        except ValueError:
            continue
        day = ts.date()
        daily[str(day)] += 1
        weekday[ts.strftime('%A')] += 1

    weekly_trend = [{'date': str((now.date() - timedelta(days=i))), 'count': daily.get(str((now.date() - timedelta(days=i))), 0)} for i in reversed(range(7))]
    monthly_trend = []
    for offset in range(0, 5):
        sample_date = (month_start - timedelta(days=offset * 30)).strftime('%Y-%m')
        monthly_trend.append({'month': sample_date, 'count': sum(1 for row in rows if row['timestamp'].startswith(sample_date))})
    common_mood = mood_counts.most_common(1)[0][0] if mood_counts else None
    favorite_language = language_counts.most_common(1)[0][0] if language_counts else None
    favorite_song = recommended_counts.most_common(1)[0][0] if recommended_counts else None

    streak = 0
    last_day = None
    for row in rows:
        try:
            ts = datetime.fromisoformat(row['timestamp']).date()
        except ValueError:
            continue
        if last_day is None:
            streak = 1
            last_day = ts
        elif (last_day - ts).days == 1:
            streak += 1
            last_day = ts
        elif ts == last_day:
            continue
        else:
            break

    return {
        'total_entries': sum(mood_counts.values()),
        'mood_counts': dict(mood_counts),
        'weekly_trend': weekly_trend,
        'monthly_trend': monthly_trend,
        'most_common_mood': common_mood,
        'favorite_mood': common_mood,
        'weekday_distribution': dict(weekday),
        'current_streak': streak,
        'favorite_language': favorite_language,
        'favorite_song': favorite_song
    }
