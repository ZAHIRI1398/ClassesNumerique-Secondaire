from flask import Flask
from models import db, User
from config import config
import logging
import sys

# Configuration du logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])

logger = logging.getLogger('list_users')

def create_app():
    # Création de l'application Flask
    app = Flask(__name__)
    
    # Utiliser la configuration de développement par défaut
    app.config.from_object(config['development'])
    
    # Initialisation de la base de données
    db.init_app(app)
    
    return app

def list_all_users():
    """Lister tous les utilisateurs dans la base de données"""
    app = create_app()
    
    with app.app_context():
        users = User.query.all()
        
        logger.info(f"=== LISTE DES UTILISATEURS ({len(users)}) ===")
        
        for user in users:
            logger.info(f"ID: {user.id}, Email: {user.email}, Rôle: {user.role}, École: {user.school_name}")
            logger.info(f"  Type d'abonnement: {user.subscription_type}, Statut: {user.subscription_status}")
            logger.info("---")

if __name__ == '__main__':
    list_all_users()
