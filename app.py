from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import os
from scraper import WebScraper
from ai_handler import AIHandler
from config import GPT_MODELS
from heygen_api import HeyGenAPI
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html', gpt_models=GPT_MODELS)

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        data = request.json
        url = data.get('url', 'https://news.ycombinator.com/')
        model = data.get('model', 'gpt-3.5-turbo')
        prompt = data.get('prompt', '')

        # Initialize scraper and AI handler
        scraper = WebScraper()
        ai_handler = AIHandler(model)

        # Scrape content
        try:
            content = scraper.scrape(url)
            if not content or len(content.strip()) == 0:
                return jsonify({
                    'success': False,
                    'error': 'No content could be extracted from the provided URL'
                }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Scraping error: {str(e)}'
            }), 400

        # Generate summary and script
        try:
            summary = ai_handler.summarize(content)
            script = ai_handler.generate_script(summary, prompt)
            
            return jsonify({
                'success': True,
                'summary': summary,
                'script': script
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'AI processing error: {str(e)}'
            }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/verify-heygen-key', methods=['POST'])
def verify_heygen_key():
    try:
        api_key = request.json.get('api_key')
        if not api_key:
            return jsonify({'success': False, 'error': 'API key is required'})
        
        # Test the API key by making a request to HeyGen's API
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Try to fetch avatars as a verification method
        response = requests.get(
            'https://api.heygen.com/v1/avatars',
            headers=headers
        )
        
        if response.status_code == 200:
            return jsonify({'success': True})
        else:
            return jsonify({
                'success': False, 
                'error': 'Invalid API key'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/get-heygen-avatars', methods=['POST'])
def get_heygen_avatars():
    try:
        api_key = request.json.get('api_key')
        if not api_key:
            return jsonify({'success': False, 'error': 'API key is required'})
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            'https://api.heygen.com/v1/avatars',
            headers=headers
        )
        
        if response.status_code == 200:
            avatars = response.json().get('data', [])
            return jsonify({
                'success': True,
                'avatars': avatars
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch avatars'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/create-heygen-video', methods=['POST'])
def create_heygen_video():
    try:
        api_key = request.json.get('api_key')
        avatar_id = request.json.get('avatar_id')
        script = request.json.get('script')
        
        if not all([api_key, avatar_id, script]):
            return jsonify({
                'success': False,
                'error': 'Missing required parameters'
            })
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'script': {
                'text': script
            },
            'avatar': {
                'avatar_id': avatar_id
            },
            'background': {
                'type': 'color',
                'value': '#ffffff'
            }
        }
        
        response = requests.post(
            'https://api.heygen.com/v1/videos',
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'success': True,
                'video_id': data.get('data', {}).get('video_id')
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create video'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/check-heygen-video', methods=['POST'])
def check_heygen_video():
    try:
        api_key = request.json.get('api_key')
        video_id = request.json.get('video_id')
        
        if not all([api_key, video_id]):
            return jsonify({
                'success': False,
                'error': 'Missing required parameters'
            })
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f'https://api.heygen.com/v1/videos/{video_id}',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json().get('data', {})
            return jsonify({
                'success': True,
                'status': data.get('status'),
                'progress': data.get('progress', 0),
                'video_url': data.get('video_url')
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to check video status'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
