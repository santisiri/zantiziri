from flask import Flask, render_template
from flask_socketio import SocketIO
import json

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    try:
        with open('hackernews_data.json', 'r') as f:
            data = json.load(f)
        data.sort(key=lambda x: x['score'], reverse=True)
    except FileNotFoundError:
        data = []
    return render_template('index.html', articles=data)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def emit_log(message):
    socketio.emit('log_update', {'message': message})

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)
