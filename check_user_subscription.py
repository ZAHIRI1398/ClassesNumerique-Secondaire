from flask import Flask
from extensions import db
from models import User
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

def check_user_subscription():
    """
    Vérifie les détails de l'abonnement de l'utilisateur de l'École Bruxelles II
    et corrige le type d'abonnement si nécessaire.
    """
    try:
        # Rechercher l'utilisateur de l'École Bruxelles II
        school_name = "École Bruxelles II"
        user = User.query.filter_by(school_name=school_name).first()
        
        if not user:
            logger.warning(f"Aucun utilisateur trouvé pour l'école '{school_name}'")
            return False
        
        # Afficher les détails de l'abonnement
        logger.info(f"Détails de l'utilisateur:")
        logger.info(f"ID: {user.id}, Email: {user.email}, Rôle: {user.role}")
        logger.info(f"École: {user.school_name}")
        logger.info(f"Type d'abonnement: {user.subscription_type}")
        logger.info(f"Statut d'abonnement: {user.subscription_status}")
        logger.info(f"Montant d'abonnement: {user.subscription_amount}")
        
        # Vérifier si le type d'abonnement est correct
        if user.subscription_type != 'school':
            logger.warning(f"Le type d'abonnement est incorrect: '{user.subscription_type}'. Correction en cours...")
            
            # Corriger le type d'abonnement
            user.subscription_type = 'school'
            user.subscription_amount = 80.0  # Montant pour les écoles
            db.session.commit()
            
            logger.info("Type d'abonnement corrigé à 'school' et montant à 80.0")
            
            # Vérifier que la correction a été appliquée
            updated_user = User.query.get(user.id)
            logger.info(f"Type d'abonnement après correction: {updated_user.subscription_type}")
            logger.info(f"Montant d'abonnement après correction: {updated_user.subscription_amount}")
        else:
            logger.info("Le type d'abonnement est déjà correct ('school')")
        
        return True
    
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de l'abonnement: {str(e)}")
        db.session.rollback()
        return False

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        check_user_subscription()
