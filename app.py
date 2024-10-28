from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import os
from scraper import WebScraper
from ai_handler import AIHandler
from config import GPT_MODELS

app = Flask(__name__)
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

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
