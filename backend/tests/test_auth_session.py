import importlib
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def test_session_token_round_trip(monkeypatch):
    monkeypatch.setenv('SECRET_KEY', 'test-secret-key')
    import services.auth as auth
    importlib.reload(auth)

    token = auth.create_session_token(42)
    assert auth.parse_session_token(token) == 42
    assert auth.parse_session_token('invalid-token') is None
