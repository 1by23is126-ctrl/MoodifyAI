import logging
import os

from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.exceptions import HTTPException

from routes.api import api
from services.database import init_db

load_dotenv()

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
app.config.update(
    JSON_SORT_KEYS=False,
    MAX_CONTENT_LENGTH=2 * 1024 * 1024,
    SESSION_COOKIE_SAMESITE='None',
    SESSION_COOKIE_SECURE=False
)
CORS(app, supports_credentials=True)
init_db()
app.register_blueprint(api)


@app.errorhandler(HTTPException)
def handle_http_error(error):
    return jsonify({'error': error.description or 'Request failed', 'status_code': error.code}), error.code


@app.errorhandler(Exception)
def handle_unexpected_error(error):
    app.logger.exception('Unhandled backend exception', exc_info=error)
    return jsonify({'error': 'Internal server error', 'status_code': 500}), 500


@app.route('/')
def root():
    return jsonify({'status': 'Moodify AI backend active'})


@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'moodify-ai'})


if __name__ == '__main__':
    debug = os.getenv('FLASK_ENV', 'production') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
