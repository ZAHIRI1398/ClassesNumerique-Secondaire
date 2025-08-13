#!/usr/bin/env python3
"""
Test minimal pour Railway - Diagnostic des variables d'environnement
"""

import os
import sys
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Railway Test - Flask fonctionne !"

@app.route('/env-check')
def env_check():
    """Vérification des variables d'environnement Railway"""
    env_info = []
    
    # Variables critiques pour Railway
    critical_vars = [
        'DATABASE_URL',
        'SECRET_KEY', 
        'FLASK_ENV',
        'PORT',
        'STRIPE_SECRET_KEY',
        'STRIPE_WEBHOOK_SECRET'
    ]
    
    for var in critical_vars:
        value = os.environ.get(var)
        if value:
            # Masquer les valeurs sensibles
            if 'SECRET' in var or 'KEY' in var:
                display_value = f"DEFINIE ({len(value)} caractères)"
            elif 'DATABASE_URL' in var:
                display_value = "DEFINIE (URL masquée)"
            else:
                display_value = value
        else:
            display_value = "❌ NON DEFINIE"
            
        env_info.append(f"{var}: {display_value}")
    
    # Informations système
    env_info.append(f"Python version: {sys.version}")
    env_info.append(f"Working directory: {os.getcwd()}")
    
    return "<pre>" + "\n".join(env_info) + "</pre>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
