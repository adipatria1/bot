from flask import Flask, send_from_directory
from src.routes import bp
import subprocess
import sys
import os

try:
    import instagrapi
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "instagrapi"])

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.register_blueprint(bp)

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    if os.getenv('FLASK_ENV') == 'production':
        app.run(host='0.0.0.0', port=8000)
    else:
        app.run(debug=True)