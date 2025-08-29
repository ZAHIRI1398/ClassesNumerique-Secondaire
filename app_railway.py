#!/usr/bin/env python3
"""
Application Flask minimale pour vérifier le déploiement Railway
"""

import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    """Route principale pour vérifier que l'application fonctionne"""
    return jsonify({
        'status': 'ok',
        'message': 'Application Classes Numériques en ligne',
        'environment': os.environ.get('RAILWAY_ENVIRONMENT', 'local')
    })

@app.route('/health')
def health():
    """Route de vérification de santé"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
