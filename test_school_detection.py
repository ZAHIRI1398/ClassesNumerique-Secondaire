from flask import Flask
from extensions import db
from models import User
from sqlalchemy import func
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    # Configuration de la base de données
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialisation des extensions
    db.init_app(app)
    
    return app

def test_school_detection():
    """
    Teste la détection des écoles avec abonnement actif
    en simulant la requête SQL utilisée dans payment_routes.py
    """
    try:
        logger.info("=== TEST DE DÉTECTION DES ÉCOLES AVEC ABONNEMENT ===")
        
        # Vérifier toutes les écoles dans la base de données
        all_schools = db.session.query(User.school_name, User.subscription_status).\
            filter(User.school_name != None).\
            filter(User.school_name != '').distinct().all()
        
        logger.info(f"Toutes les écoles dans la base: {all_schools}")
        
        # Trouver toutes les écoles avec au moins un utilisateur ayant un abonnement actif
        schools_with_subscription = db.session.query(User.school_name, func.count(User.id).label('user_count')).\
            filter(User.school_name != None).\
            filter(User.school_name != '').\
            filter(User.subscription_type == 'school').\
            filter(User.subscription_status == 'approved').\
            group_by(User.school_name).all()
        
        logger.info(f"Écoles avec abonnement trouvées: {schools_with_subscription}")
        
        # Si aucune école n'est trouvée
        if not schools_with_subscription:
            logger.warning("Aucune école avec abonnement actif n'a été trouvée")
        else:
            logger.info(f"Écoles avec abonnement trouvées: {[school.school_name for school in schools_with_subscription]}")
        
        # Vérifier spécifiquement l'école Bruxelles II
        ecole_bruxelles = User.query.filter_by(school_name="École Bruxelles II").all()
        logger.info(f"Utilisateurs de l'École Bruxelles II: {len(ecole_bruxelles)}")
        for user in ecole_bruxelles:
            logger.info(f"ID: {user.id}, Email: {user.email}, Rôle: {user.role}, Statut: {user.subscription_status}")
        
        logger.info("=== FIN DU TEST ===")
        
        return True
    
    except Exception as e:
        logger.error(f"Erreur lors du test de détection des écoles: {str(e)}")
        return False

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        test_school_detection()
