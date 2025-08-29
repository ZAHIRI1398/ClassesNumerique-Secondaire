#!/usr/bin/env python3
"""
Application Flask pour le déploiement sur Railway
Version intermédiaire avec fonctionnalités essentielles
"""

import os
import logging
from datetime import datetime
from flask import Flask, jsonify, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialisation de l'application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_testing')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///instance/app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import des modèles et extensions après l'initialisation de l'app
try:
    from extensions import db
    db.init_app(app)
    from models import User, Exercise
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
        
    logger.info("Modèles et extensions chargés avec succès")
except Exception as e:
    logger.error(f"Erreur lors du chargement des modèles: {str(e)}")

# Routes de base
@app.route('/')
def home():
    """Page d'accueil"""
    try:
        if current_user.is_authenticated:
            return render_template('index.html')
        return render_template('landing.html')
    except Exception as e:
        logger.error(f"Erreur sur la page d'accueil: {str(e)}")
        return jsonify({
            'status': 'ok',
            'message': 'Application Classes Numériques en ligne',
            'environment': os.environ.get('RAILWAY_ENVIRONMENT', 'local'),
            'note': 'Mode de secours - Templates non disponibles'
        })

@app.route('/health')
def health():
    """Route de vérification de santé"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion"""
    try:
        if current_user.is_authenticated:
            return redirect(url_for('home'))
            
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            remember_me = request.form.get('remember_me') == '1'
            
            user = User.query.filter_by(email=email).first()
            
            if user and check_password_hash(user.password, password):
                login_user(user, remember=remember_me)
                next_page = request.args.get('next')
                return redirect(next_page or url_for('home'))
            else:
                flash('Email ou mot de passe incorrect', 'danger')
                
        return render_template('auth/login.html')
    except Exception as e:
        logger.error(f"Erreur sur la page de connexion: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Erreur de connexion',
            'error': str(e)
        }), 500

@app.route('/logout')
def logout():
    """Déconnexion"""
    logout_user()
    return redirect(url_for('home'))

@app.route('/api/status')
def api_status():
    """API de statut pour les vérifications"""
    try:
        db_status = "connected"
        try:
            # Vérifier la connexion à la base de données
            with app.app_context():
                db.engine.execute("SELECT 1")
        except Exception as e:
            db_status = f"error: {str(e)}"
            
        return jsonify({
            'status': 'online',
            'database': db_status,
            'environment': os.environ.get('FLASK_ENV', 'production'),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Gestionnaire d'erreurs
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

# Point d'entrée pour l'exécution locale
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
