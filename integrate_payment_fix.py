"""
Script d'intégration de la correction pour le paiement des abonnements enseignants.
Ce script modifie l'application Flask pour utiliser la route corrigée.
"""

import sys
import os
from flask import Flask, redirect, url_for, request, flash
import logging
from logging.handlers import RotatingFileHandler
import traceback

def setup_logging(app):
    """Configure le système de logging"""
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler('logs/payment_fix.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Initialisation du système de logging')

def create_app():
    """Crée une instance de l'application Flask"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
    
    # Configuration de la base de données
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configuration du logging
    setup_logging(app)
    
    return app

def integrate_fix():
    """Intègre la correction dans l'application principale"""
    try:
        # Importer l'application principale
        sys.path.append(os.path.abspath('production_code/ClassesNumerique-Secondaire-main'))
        from app import app
        
        # Importer la correction
        from fix_payment_teacher_subscription import register_blueprint
        
        # Enregistrer le blueprint de correction
        with app.app_context():
            register_blueprint(app)
            
            # Créer une route de redirection pour remplacer la route originale
            @app.route('/payment/create-checkout-session', methods=['POST'])
            def redirect_to_fixed_route():
                app.logger.info("[PAYMENT_FIX] Redirection vers la route corrigée")
                return redirect(url_for('fix_payment.create_checkout_session'), code=307)  # 307 préserve la méthode POST
            
            app.logger.info("[PAYMENT_FIX] Redirection configurée avec succès")
        
        print("[SUCCÈS] Correction intégrée avec succès dans l'application")
        return True
    
    except Exception as e:
        print(f"[ERREUR] Échec de l'intégration: {str(e)}")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = integrate_fix()
    sys.exit(0 if success else 1)
