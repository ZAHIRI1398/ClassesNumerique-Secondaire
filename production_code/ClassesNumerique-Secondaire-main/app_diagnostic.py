#!/usr/bin/env python3
"""
App de diagnostic minimal pour identifier les erreurs Railway
"""

import os
import sys
import traceback
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ App de diagnostic - Flask fonctionne !"

@app.route('/test-imports')
def test_imports():
    """Test des imports critiques"""
    try:
        # Test imports Flask
        from flask import render_template, request, redirect, url_for, flash, jsonify
        from flask_login import LoginManager, login_user, logout_user, login_required, current_user
        from flask_sqlalchemy import SQLAlchemy
        from flask_migrate import Migrate
        from flask_wtf import FlaskForm
        
        # Test imports Python standards
        import json
        import datetime
        import secrets
        import hashlib
        
        return "✅ Tous les imports critiques fonctionnent !"
        
    except Exception as e:
        return f"❌ Erreur import: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"

@app.route('/test-env')
def test_env():
    """Test des variables d'environnement"""
    try:
        env_vars = {
            'DATABASE_URL': os.environ.get('DATABASE_URL', 'NON_DEFINIE'),
            'SECRET_KEY': 'DEFINIE' if os.environ.get('SECRET_KEY') else 'NON_DEFINIE',
            'STRIPE_SECRET_KEY': 'DEFINIE' if os.environ.get('STRIPE_SECRET_KEY') else 'NON_DEFINIE',
            'FLASK_ENV': os.environ.get('FLASK_ENV', 'NON_DEFINIE'),
            'PORT': os.environ.get('PORT', 'NON_DEFINIE')
        }
        
        result = "🔍 Variables d'environnement:\n"
        for key, value in env_vars.items():
            result += f"- {key}: {value}\n"
            
        return f"<pre>{result}</pre>"
        
    except Exception as e:
        return f"❌ Erreur env: {str(e)}"

if __name__ == '__main__':
    try:
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print(f"❌ Erreur critique au démarrage: {str(e)}")
        print(f"Traceback complet:\n{traceback.format_exc()}")
        sys.exit(1)
