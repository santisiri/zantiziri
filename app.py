from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import os
from scraper import WebScraper
from ai_handler import AIHandler
from config import GPT_MODELS
import requests
from flask_cors import CORS
from openai import OpenAI
import json
from PIL import Image
import io
import base64

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

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

@app.route('/generate-image-prompt', methods=['POST'])
def generate_image_prompt():
    try:
        script = request.json.get('script')
        if not script:
            return jsonify({'success': False, 'error': 'No script provided'})

        # Generate a prompt using GPT
        response = client.chat.completions.create(
            model="gpt-4",  # or gpt-3.5-turbo
            messages=[
                {"role": "system", "content": """You are an expert at creating image generation prompts. 
                Given a script, create a detailed, visual prompt that would generate an engaging image 
                related to the main theme or message. Focus on visual elements, style, and mood."""},
                {"role": "user", "content": f"Create an image generation prompt for this script:\n\n{script}"}
            ],
            max_tokens=100,
            temperature=0.7
        )

        prompt = response.choices[0].message.content.strip()
        return jsonify({
            'success': True,
            'prompt': prompt
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/generate-images', methods=['POST'])
def generate_images():
    try:
        data = request.json
        prompt = data.get('prompt')
        style = data.get('style', 'natural')
        count = min(data.get('count', 4), 4)  # Limit to 4 images max

        if not prompt:
            return jsonify({'success': False, 'error': 'No prompt provided'})

        # Enhance prompt based on selected style
        style_prompts = {
            'natural': 'Create a natural, realistic image of',
            'digital-art': 'Create a digital art illustration of',
            'illustration': 'Create a detailed illustration of',
            'photographic': 'Create a professional photograph of'
        }
        
        enhanced_prompt = f"{style_prompts.get(style, '')} {prompt}"

        # Generate images using DALL-E
        images = []
        for _ in range(count):
            response = client.images.generate(
                model="dall-e-3",
                prompt=enhanced_prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )

            image_url = response.data[0].url
            images.append({
                'url': image_url,
                'prompt': prompt
            })

        return jsonify({
            'success': True,
            'images': images
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/download-image', methods=['POST'])
def download_image():
    try:
        url = request.json.get('url')
        if not url:
            return jsonify({'success': False, 'error': 'No image URL provided'})

        # Download the image
        response = requests.get(url)
        if response.status_code != 200:
            return jsonify({'success': False, 'error': 'Failed to download image'})

        # Convert to base64 for frontend download
        image_base64 = base64.b64encode(response.content).decode('utf-8')
        
        return jsonify({
            'success': True,
            'image': image_base64
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
