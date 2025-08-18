"""
Script de test pour vérifier l'intégration du bouton École et du blueprint d'inscription d'école.
"""

import logging
import sys
from datetime import datetime
from flask import Flask, url_for
from flask_login import LoginManager

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'test_ecole_button_integration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

def create_test_app():
    """
    Crée une application Flask de test pour vérifier l'intégration du bouton École.
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.config['TESTING'] = True
    
    # Initialisation de Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    
    # Route de test pour la page d'accueil
    @app.route('/')
    def index():
        return "Page d'accueil de test"
    
    # Route de test pour la redirection register_school
    @app.route('/register/school')
    def register_school():
        return "Redirection vers l'inscription d'école"
    
    with app.app_context():
        # Import des modules nécessaires
        try:
            from school_registration_mod import school_registration_mod
            app.register_blueprint(school_registration_mod)
            logger.info("[OK] Module d'inscription d'école importé et initialisé avec succès.")
        except ImportError as e:
            logger.error(f"[ERREUR] Le module d'inscription d'école n'a pas pu être importé: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"[ERREUR] Erreur lors de l'initialisation du module d'inscription d'école: {str(e)}")
            return None
        
        # Intégration du module de paiement d'école
        try:
            from school_payment_integration import integrate_school_payment
            integrate_school_payment(app)
            logger.info("[OK] Module de paiement d'école intégré avec succès.")
        except ImportError as e:
            logger.error(f"[ERREUR] Le module de paiement d'école n'a pas pu être importé: {str(e)}")
        except Exception as e:
            logger.error(f"[ERREUR] Erreur lors de l'intégration du module de paiement d'école: {str(e)}")
    
    return app

def test_routes(app):
    """
    Teste les routes liées au bouton École et à l'inscription d'école.
    """
    with app.app_context():
        with app.test_request_context():
            try:
                # Vérification de la route register_school
                register_school_url = url_for('register_school')
                logger.info(f"[OK] URL pour register_school: {register_school_url}")
            except Exception as e:
                logger.error(f"[ERREUR] La route register_school n'est pas définie: {str(e)}")
            
            try:
                # Vérification des routes du blueprint school_registration_mod
                register_school_simplified_url = url_for('school_registration_mod.register_school_simplified')
                logger.info(f"[OK] URL pour register_school_simplified: {register_school_simplified_url}")
                
                register_school_connected_url = url_for('school_registration_mod.register_school_connected')
                logger.info(f"[OK] URL pour register_school_connected: {register_school_connected_url}")
            except Exception as e:
                logger.error(f"[ERREUR] Les routes du blueprint school_registration_mod ne sont pas définies: {str(e)}")
            
            try:
                # Vérification de la route de redirection school_payment
                register_school_to_payment_url = url_for('school_payment.register_school_to_payment')
                logger.info(f"[OK] URL pour register_school_to_payment: {register_school_to_payment_url}")
            except Exception as e:
                logger.error(f"[ERREUR] La route register_school_to_payment n'est pas définie: {str(e)}")

def main():
    """
    Fonction principale du script de test.
    """
    logger.info("=== DÉBUT DU TEST D'INTÉGRATION DU BOUTON ÉCOLE ===")
    
    # Création de l'application de test
    app = create_test_app()
    if not app:
        logger.error("Impossible de créer l'application de test.")
        sys.exit(1)
    
    # Test des routes
    test_routes(app)
    
    # Vérification du template login.html
    try:
        with open('templates/login.html', 'r', encoding='utf-8') as file:
            content = file.read()
            if 'url_for(\'register_school\')' in content:
                logger.info("[OK] Le template login.html contient une référence à register_school")
            else:
                logger.error("[ERREUR] Le template login.html ne contient pas de référence à register_school")
    except Exception as e:
        logger.error(f"[ERREUR] Impossible de lire le template login.html: {str(e)}")
    
    logger.info("=== FIN DU TEST D'INTÉGRATION DU BOUTON ÉCOLE ===")

if __name__ == '__main__':
    main()
