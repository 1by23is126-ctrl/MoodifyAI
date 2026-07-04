"""ASGI wrapper that exposes the existing Flask app to uvicorn.

The supervisor config runs `uvicorn server:app`. We keep the original
Flask architecture (app.py) untouched and simply wrap it with asgiref so
the platform's ingress (which expects port 8001) can serve it.
"""
from asgiref.wsgi import WsgiToAsgi

from app import app as flask_app

app = WsgiToAsgi(flask_app)
