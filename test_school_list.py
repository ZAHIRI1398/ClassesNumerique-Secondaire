"""
Script de test pour vérifier que les écoles apparaissent correctement dans la liste des écoles pour les paiements
"""
from flask import Flask
from models import db, User
from sqlalchemy import func
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='test_school_list.log',
    filemode='w'
)
logger = logging.getLogger(__name__)

# Créer une application Flask minimale pour le test
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def test_school_list():
    """
    Teste la requête SQL qui récupère les écoles avec un abonnement actif
    """
    with app.app_context():
        try:
            # Exécuter la requête SQL
            schools_with_subscription = db.session.query(User.school_name, func.count(User.id).label('user_count')).\
                filter(User.school_name != None).\
                filter(User.school_name != '').\
                filter(User.subscription_type == 'school').\
                filter(User.subscription_status == 'approved').\
                group_by(User.school_name).all()
            
            # Afficher les résultats
            logger.info(f"Nombre d'écoles trouvées: {len(schools_with_subscription)}")
            
            if schools_with_subscription:
                logger.info("Liste des écoles avec abonnement actif:")
                for school, count in schools_with_subscription:
                    logger.info(f"École: {school}, Utilisateurs: {count}")
                
                # Vérifier si l'école "Ecole Bruxelles ll" est dans la liste
                bruxelles_school = next((school for school, count in schools_with_subscription if school == "Ecole Bruxelles ll"), None)
                if bruxelles_school:
                    logger.info("L'école 'Ecole Bruxelles ll' est présente dans la liste.")
                else:
                    logger.warning("L'école 'Ecole Bruxelles ll' n'est PAS présente dans la liste.")
                    
                # Vérifier si l'école "École Bruxelles II" est dans la liste (avec accent)
                bruxelles_school_accent = next((school for school, count in schools_with_subscription if school == "École Bruxelles II"), None)
                if bruxelles_school_accent:
                    logger.info("L'école 'École Bruxelles II' est présente dans la liste.")
                else:
                    logger.warning("L'école 'École Bruxelles II' n'est PAS présente dans la liste.")
                
                # Vérifier les types d'abonnement et statuts des écoles
                for school_name, _ in schools_with_subscription:
                    school_users = User.query.filter_by(school_name=school_name).all()
                    for user in school_users:
                        logger.info(f"École: {school_name}, Utilisateur: {user.email}, Type d'abonnement: {user.subscription_type}, Statut: {user.subscription_status}")
            else:
                logger.warning("Aucune école avec abonnement actif n'a été trouvée.")
                
            # Vérifier les écoles qui pourraient avoir un problème de configuration
            problematic_schools = db.session.query(User.school_name, User.subscription_type, User.subscription_status).\
                filter(User.school_name != None).\
                filter(User.school_name != '').\
                filter(User.subscription_type != 'school').\
                all()
            
            if problematic_schools:
                logger.warning("Écoles avec un type d'abonnement différent de 'school':")
                for school_name, sub_type, sub_status in problematic_schools:
                    logger.warning(f"École: {school_name}, Type d'abonnement: {sub_type}, Statut: {sub_status}")
            
            # Vérifier les écoles avec un statut non approuvé
            non_approved_schools = db.session.query(User.school_name, User.subscription_type, User.subscription_status).\
                filter(User.school_name != None).\
                filter(User.school_name != '').\
                filter(User.subscription_type == 'school').\
                filter(User.subscription_status != 'approved').\
                all()
            
            if non_approved_schools:
                logger.warning("Écoles avec un statut non approuvé:")
                for school_name, sub_type, sub_status in non_approved_schools:
                    logger.warning(f"École: {school_name}, Type d'abonnement: {sub_type}, Statut: {sub_status}")
                    
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de la requête: {str(e)}")

if __name__ == "__main__":
    test_school_list()
    print("Test terminé. Consultez le fichier test_school_list.log pour les résultats.")
