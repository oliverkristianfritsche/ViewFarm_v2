import hashlib
import base64
import os
from flask import Flask, redirect, request, make_response, jsonify
import random
import urllib.parse
import requests

app = Flask(__name__)

CLIENT_KEY = 'sbawtwmtorfz4zb7r0'  # Replace with your client key
CLIENT_SECRET = 'vhZqrchFXw2spwDgWuPoTMEjA0xghZMZ'  # Replace with your client secret
SERVER_ENDPOINT_REDIRECT = 'http://localhost:8080/callback'  # Replace with your registered redirect URI
TOKENS = {}  # This is a simple storage, replace with a more secure storage solution

def generate_random_string(length=60):
    characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~'
    return ''.join(random.choice(characters) for _ in range(length))

def generate_code_challenge_pair():
    code_verifier = generate_random_string(60)
    sha256_hash = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = sha256_hash.hex()  # Convert to hex string
    return code_verifier, code_challenge

CODE_VERIFIER, CODE_CHALLENGE = generate_code_challenge_pair()

@app.route('/')
def index():
    return redirect('/oauth')

@app.route('/oauth')
def oauth():
    csrf_state = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=16))
    response = make_response(redirect(build_oauth_url(csrf_state)))
    response.set_cookie('csrfState', csrf_state, max_age=60)
    return response

def build_oauth_url(csrf_state):
    params = {
        'client_key': CLIENT_KEY,
        'scope': 'user.info.basic,video.publish,video.upload,user.info.profile,user.info.stats,video.list',
        'response_type': 'code',
        'redirect_uri': SERVER_ENDPOINT_REDIRECT,
        'state': csrf_state,
        'code_challenge': CODE_CHALLENGE,
        'code_challenge_method': 'S256'
    }
    base_url = 'https://www.tiktok.com/v2/auth/authorize/'
    return base_url + '?' + urllib.parse.urlencode(params)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return jsonify({"error": "Authorization code not found"}), 400

    token_response = fetch_access_token(code)
    if "access_token" in token_response:
        TOKENS['access_token'] = token_response['access_token']
        TOKENS['refresh_token'] = token_response['refresh_token']
        return jsonify({"message": "Tokens obtained successfully. You can now post a video."})
    else:
        return jsonify(token_response), 400

def fetch_access_token(code):
    url = 'https://open.tiktokapis.com/v2/oauth/token/'
    data = {
        'client_key': CLIENT_KEY,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': SERVER_ENDPOINT_REDIRECT,
        'code_verifier': CODE_VERIFIER
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    response = requests.post(url, data=data, headers=headers)
    return response.json()

@app.route('/refresh_token')
def refresh_token():
    refresh_token = TOKENS.get('refresh_token')
    if not refresh_token:
        return jsonify({"error": "Refresh token not found"}), 400

    token_response = refresh_access_token(refresh_token)
    if "access_token" in token_response:
        TOKENS['access_token'] = token_response['access_token']
        TOKENS['refresh_token'] = token_response['refresh_token']
        return jsonify(token_response)
    else:
        return jsonify(token_response), 400

def refresh_access_token(refresh_token):
    url = 'https://open.tiktokapis.com/v2/oauth/token/'
    data = {
        'client_key': CLIENT_KEY,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    response = requests.post(url, data=data, headers=headers)
    return response.json()

@app.route('/post_video', methods=['POST'])
def post_video():
    # Ensure that the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Invalid request: Content-Type must be application/json"}), 400

    # Parse the JSON payload
    data = request.get_json()
    video_path = data.get('video_path', '/root/tmp/final_video.mp4')  # Changed to accept dynamic video path

    if not os.path.exists(video_path):
        return jsonify({"error": f"Video path {video_path} does not exist"}), 400

    access_token = TOKENS.get('access_token')
    if not access_token:
        return jsonify({"error": "Access token not found. Authenticate first."}), 400

    # Step 1: Post Video
    video_response = upload_video(access_token, video_path)
    return jsonify(video_response)

def upload_video(access_token, video_path):
    url = 'https://open.tiktokapis.com/v2/post/publish/video/init/'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json; charset=UTF-8'
    }
    
    video_size = os.path.getsize(video_path)

    # Ensure the post_info and source_info are correctly structured
    data = {
        "post_info": {
            "title": "This is a funny #cat video on your @tiktok #fyp",  # A non-empty title
            "privacy_level": "SELF_ONLY",  # Ensure this is a valid option returned by creator_info
            "video_cover_timestamp_ms": 1000  # 1 second into the video (adjust as needed)
        },
        "source_info": {
            "source": "FILE_UPLOAD",  # Specify the source as file upload
            "video_size": video_size,  # Correct video size in bytes
            "chunk_size": video_size,  # Assuming single chunk upload
            "total_chunk_count": 1  # Total chunk count set to 1 for single chunk
        }
    }
    
    # Send the POST request to initialize the video upload
    response = requests.post(url, json=data, headers=headers)
    upload_info = response.json()

    print("=====================================")
    print(upload_info)
    print("=====================================")

    if 'error' in upload_info and upload_info['error']['code'] == 'ok':
        if 'data' in upload_info and 'upload_url' in upload_info['data']:
            upload_url = upload_info['data']['upload_url']
            
            # Read the video file and upload it to the provided URL
            with open(video_path, 'rb') as video_file:
                video_data = video_file.read()

            upload_headers = {
                'Content-Range': f'bytes 0-{video_size-1}/{video_size}',
                'Content-Length': str(video_size),
                'Content-Type': 'video/mp4'
            }

            upload_response = requests.put(upload_url, headers=upload_headers, data=video_data)
            
            if upload_response.status_code == 201:
                return {"message": "Video posted successfully", "data": upload_response.json()}
            else:
                return {"error": "Failed to upload video", "details": upload_response.text}
    
    return {"error": "Failed to initialize video upload", "details": upload_info}

def query_creator_info(access_token):
    url = 'https://open.tiktokapis.com/v2/post/publish/creator_info/query/'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json; charset=UTF-8'
    }
    
    response = requests.post(url, headers=headers)
    return response.json()




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
