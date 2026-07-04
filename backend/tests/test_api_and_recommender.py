import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app
from services.recommender import recommend_for_mood
from services.sentiment import analyze_text
from services.music_database import get_catalog, get_language_tracks, SUPPORTED_LANGUAGES
from services.spotify import select_best_track_result


class MoodifyApiTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health_endpoint(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'ok')

    def test_analyze_requires_text(self):
        response = self.client.post('/api/analyze', json={})
        self.assertEqual(response.status_code, 400)
        payload = response.get_json()
        self.assertIn('error', payload)

    def test_analyze_returns_recommendations_payload(self):
        response = self.client.post('/api/analyze', json={'text': 'I feel calm, reflective, and a little nostalgic tonight.'})
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn('tracks', payload)
        self.assertGreaterEqual(len(payload['tracks']), 1)
        self.assertIn('recommendationsByLanguage', payload)


class RecommenderTests(unittest.TestCase):
    def test_recommend_for_mood_returns_multilingual_recommendations(self):
        result = recommend_for_mood({
            'mood': 'Chill',
            'scores': {'Energy': 28, 'Happiness': 72},
            'nuancedLabel': 'Soft Calm',
            'primaryEmotion': 'Calmness',
            'secondary': 'Nostalgia',
            'hiddenUndertone': 'Serenity',
            'dimensions': {'energy': 28, 'emotionalDepth': 64, 'introspection': 72},
        })

        self.assertIn('recommendationsByLanguage', result)
        self.assertTrue(any(tracks for tracks in result['recommendationsByLanguage'].values()))
        self.assertGreaterEqual(len(result['fallback_tracks']), 1)

    def test_emotion_analysis_understands_contextual_prompts(self):
        analysis = analyze_text('I feel empty after getting rejected and I cannot sleep.')
        self.assertIn(analysis['primaryEmotion'], {'Emotional Numbness', 'Hopelessness', 'Sadness', 'Loneliness'})
        self.assertGreaterEqual(analysis['dimensions']['emotionalDepth'], 55)

    def test_catalog_contains_large_supported_language_library(self):
        catalog = get_catalog()
        self.assertGreaterEqual(len(catalog), 350)
        languages = {track['language'] for track in catalog}
        self.assertTrue(languages.issubset(set(SUPPORTED_LANGUAGES)))
        for language in ['English', 'Hindi', 'Tamil', 'Telugu', 'Kannada']:
            self.assertGreaterEqual(len(get_language_tracks(language)), 60)

    def test_playlist_selection_is_diverse_and_duplicate_free(self):
        analysis = {
            'mood': 'Chill',
            'scores': {'Calmness': 70, 'Nostalgia': 55, 'Introspection': 60},
            'nuancedLabel': 'Soft Calm',
            'primaryEmotion': 'Calmness',
            'secondary': 'Nostalgia',
            'hiddenUndertone': 'Serenity',
            'dimensions': {'energy': 24, 'emotionalDepth': 72, 'introspection': 68},
        }
        result = recommend_for_mood(analysis, session_id='session-diversity')
        tracks = result['recommendationsByLanguage']['English']
        self.assertEqual(len(tracks), len({track['title'] for track in tracks}))
        self.assertLessEqual(len({track['artist'] for track in tracks}), len(tracks))

    def test_selected_language_recommendations_are_strictly_scoped(self):
        analysis = {
            'mood': 'Chill',
            'scores': {'Calmness': 70, 'Nostalgia': 55, 'Introspection': 60},
            'dimensions': {'energy': 24, 'emotionalDepth': 72, 'introspection': 68},
        }

        for language in SUPPORTED_LANGUAGES:
            result = recommend_for_mood(analysis, session_id=f'session-{language}', language=language)
            self.assertEqual(list(result['recommendationsByLanguage'].keys()), [language])
            tracks = result['recommendationsByLanguage'][language]
            self.assertGreaterEqual(len(tracks), 1)
            self.assertEqual({track['language'] for track in tracks}, {language})
            self.assertEqual({track['language'] for track in result['fallback_tracks']}, {language})

    def test_spotify_result_selector_prefers_official_artwork(self):
        candidates = [
            {
                'name': 'Wrong Song',
                'artists': [{'name': 'The 1975'}],
                'album': {'name': 'A', 'images': [{'url': '', 'width': 0, 'height': 0}]},
                'external_urls': {'spotify': 'https://open.spotify.com/track/1'}
            },
            {
                'name': 'Somebody Else',
                'artists': [{'name': 'The 1975'}],
                'album': {'name': 'I Like It When You Sleep...', 'images': [{'url': 'https://i.scdn.co/image/abc123', 'width': 640, 'height': 640}]},
                'external_urls': {'spotify': 'https://open.spotify.com/track/2'}
            },
        ]

        selected = select_best_track_result(candidates, 'Somebody Else', 'The 1975')
        self.assertEqual(selected['name'], 'Somebody Else')
        self.assertTrue(selected['album']['images'][0]['url'])


if __name__ == '__main__':
    unittest.main()
