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

def update_school_name():
    """
    Met à jour le nom de l'école de "Ecole Bruxelles ll" à "École Bruxelles II"
    dans la table User pour corriger le problème de détection d'abonnement.
    """
    try:
        # Rechercher les utilisateurs avec l'ancien nom d'école
        old_name = "Ecole Bruxelles ll"
        new_name = "École Bruxelles II"
        
        users = User.query.filter_by(school_name=old_name).all()
        
        if not users:
            logger.warning(f"Aucun utilisateur trouvé avec le nom d'école '{old_name}'")
            return False
        
        # Afficher les utilisateurs trouvés
        logger.info(f"Utilisateurs trouvés avec le nom d'école '{old_name}':")
        for user in users:
            logger.info(f"ID: {user.id}, Email: {user.email}, Rôle: {user.role}, Statut: {user.subscription_status}")
        
        # Mettre à jour le nom de l'école
        count = 0
        for user in users:
            user.school_name = new_name
            count += 1
        
        # Sauvegarder les modifications
        db.session.commit()
        
        logger.info(f"Mise à jour réussie! {count} utilisateur(s) modifié(s).")
        logger.info(f"Le nom de l'école a été changé de '{old_name}' à '{new_name}'.")
        
        # Vérifier que la mise à jour a bien été effectuée
        updated_users = User.query.filter_by(school_name=new_name).all()
        logger.info(f"Utilisateurs avec le nouveau nom d'école '{new_name}':")
        for user in updated_users:
            logger.info(f"ID: {user.id}, Email: {user.email}, Rôle: {user.role}, Statut: {user.subscription_status}")
        
        return True
    
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du nom d'école: {str(e)}")
        db.session.rollback()
        return False

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        update_school_name()
