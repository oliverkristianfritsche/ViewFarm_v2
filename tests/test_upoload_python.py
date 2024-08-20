from flask import Flask, redirect, request, session, url_for
import os
import base64
import hashlib
import secrets
import requests
import urllib.parse
from flask_session import Session
import redis

# Configuration
CLIENT_KEY = 'sbawtwmtorfz4zb7r0'
CLIENT_SECRET = 'vhZqrchFXw2spwDgWuPoTMEjA0xghZMZ'
REDIRECT_URI = 'http://localhost:8080/callback'
PORT = 8080
SCOPE = "user.info.basic,video.publish,video.upload,user.info.profile,user.info.stats,video.list"

# Flask app setup
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Session configuration
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.StrictRedis(host='localhost', port=6379, db=0)
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'tiktok_'
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True if using HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
Session(app)

def generate_code_verifier():
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b'=').decode('utf-8')

def generate_code_challenge(code_verifier):
    code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(code_challenge).rstrip(b'=').decode('utf-8')

@app.route('/')
def index():
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)
    session['code_verifier'] = code_verifier

    csrf_state = secrets.token_urlsafe(16)
    session['csrf_state'] = csrf_state

    authorization_url = (
        f"https://www.tiktok.com/v2/auth/authorize/"
        f"?client_key={CLIENT_KEY}"
        f"&response_type=code"
        f"&scope={urllib.parse.quote(SCOPE)}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&state={csrf_state}"
        f"&code_challenge={code_challenge}"
        f"&code_challenge_method=S256"
    )
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    state = request.args.get('state')

    if state != session.get('csrf_state'):
        return "Invalid state parameter", 400

    authorization_code = request.args.get('code')
    if not authorization_code:
        return "No authorization code found", 400

    access_token = exchange_code_for_access_token(authorization_code)
    if not access_token:
        return "Failed to obtain access token.", 400

    return f"Access token obtained successfully: {access_token}"

def exchange_code_for_access_token(authorization_code):
    code_verifier = session.get('code_verifier')
    token_url = 'https://open.tiktokapis.com/v2/oauth/token/'
    data = {
        'client_key': CLIENT_KEY,
        'client_secret': CLIENT_SECRET,
        'code': authorization_code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI,
        'code_verifier': code_verifier
    }
    response = requests.post(token_url, data=data)
    if response.status_code != 200:
        return None
    return response.json().get('access_token')

if __name__ == '__main__':
    app.run(port=PORT)
