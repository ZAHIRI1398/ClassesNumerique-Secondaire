#!/usr/bin/env python3
"""
App Flask ultra-minimale pour diagnostic Railway
"""

import os
import sys
import traceback
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ App minimale - Railway fonctionne !"

@app.route('/test')
def test():
    return "✅ Route test - OK !"

@app.route('/env')
def env_check():
    """Vérification des variables d'environnement"""
    try:
        env_vars = []
        
        # Variables critiques
        critical_vars = ['DATABASE_URL', 'SECRET_KEY', 'FLASK_ENV', 'PORT']
        
        for var in critical_vars:
            value = os.environ.get(var)
            if value:
                if 'SECRET' in var or 'KEY' in var or 'DATABASE' in var:
                    display_value = f"DEFINIE ({len(value)} chars)"
                else:
                    display_value = value
            else:
                display_value = "❌ NON DEFINIE"
                
            env_vars.append(f"{var}: {display_value}")
        
        env_vars.append(f"Python: {sys.version}")
        env_vars.append(f"CWD: {os.getcwd()}")
        
        return "<pre>" + "\n".join(env_vars) + "</pre>"
        
    except Exception as e:
        return f"❌ Erreur env: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"

@app.route('/debug')
def debug():
    """Debug complet"""
    try:
        debug_info = []
        debug_info.append("=== DEBUG RAILWAY ===")
        debug_info.append(f"Python version: {sys.version}")
        debug_info.append(f"Working directory: {os.getcwd()}")
        debug_info.append(f"Files in directory: {os.listdir('.')}")
        
        # Test imports critiques
        try:
            from flask import render_template
            debug_info.append("✅ Flask render_template OK")
        except Exception as e:
            debug_info.append(f"❌ Flask render_template: {str(e)}")
            
        try:
            from flask_login import LoginManager
            debug_info.append("✅ Flask-Login OK")
        except Exception as e:
            debug_info.append(f"❌ Flask-Login: {str(e)}")
            
        try:
            from flask_sqlalchemy import SQLAlchemy
            debug_info.append("✅ Flask-SQLAlchemy OK")
        except Exception as e:
            debug_info.append(f"❌ Flask-SQLAlchemy: {str(e)}")
            
        # Variables d'environnement
        debug_info.append("\n=== VARIABLES D'ENVIRONNEMENT ===")
        for key, value in os.environ.items():
            if any(keyword in key.upper() for keyword in ['SECRET', 'KEY', 'DATABASE', 'FLASK', 'PORT']):
                if 'SECRET' in key or 'KEY' in key:
                    debug_info.append(f"{key}: DEFINIE ({len(value)} chars)")
                else:
                    debug_info.append(f"{key}: {value}")
        
        return "<pre>" + "\n".join(debug_info) + "</pre>"
        
    except Exception as e:
        return f"❌ Erreur debug: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"

if __name__ == '__main__':
    try:
        port = int(os.environ.get('PORT', 5000))
        print(f"🚀 Démarrage app minimale sur port {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print(f"❌ Erreur critique: {str(e)}")
        print(f"Traceback:\n{traceback.format_exc()}")
        sys.exit(1)
