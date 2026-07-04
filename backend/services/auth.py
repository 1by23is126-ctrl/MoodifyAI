import os
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from datetime import timedelta

from services.database import get_user_by_id

SECRET_KEY = os.getenv('SECRET_KEY') or os.getenv('FLASK_SECRET_KEY') or 'moodify-ai-secret'
SESSION_SALT = 'moodify-ai-session'
SESSION_MAX_AGE = int(os.getenv('SESSION_MAX_AGE_SECONDS', 60 * 60 * 24 * 30))


def _get_serializer():
    return URLSafeTimedSerializer(SECRET_KEY, salt=SESSION_SALT)


def create_session_token(user_id):
    serializer = _get_serializer()
    return serializer.dumps({'user_id': int(user_id)})


def parse_session_token(token, max_age=SESSION_MAX_AGE):
    serializer = _get_serializer()
    try:
        data = serializer.loads(token, max_age=max_age)
        return int(data.get('user_id')) if data and data.get('user_id') is not None else None
    except (BadSignature, SignatureExpired):
        return None


def load_current_user(request):
    token = None
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header[len('Bearer '):].strip()
    elif request.cookies.get('moodify_auth_token'):
        token = request.cookies.get('moodify_auth_token')
    elif request.args.get('auth_token'):
        token = request.args.get('auth_token')

    if not token:
        return None, None
    user_id = parse_session_token(token)
    if not user_id:
        return None, None
    return get_user_by_id(user_id), token
