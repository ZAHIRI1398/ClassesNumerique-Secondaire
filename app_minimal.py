#!/usr/bin/env python3
"""
Version minimale de l'application pour diagnostiquer le problème Railway
"""

from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-key'

@app.route('/')
def index():
    return "✅ Application Flask minimale fonctionne sur Railway !"

@app.route('/health')
def health():
    return "OK"

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
