import os
import sys
import logging
from datetime import datetime
from tabulate import tabulate
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"verify_subscriptions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger(__name__)

# Initialisation de l'application Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def verify_subscriptions():
    """Vérifier les abonnements en production"""
    try:
        with app.app_context():
            # 1. Vérifier les écoles avec abonnements actifs
            logger.info("=== ÉCOLES AVEC ABONNEMENTS ACTIFS ===")
            result = db.session.execute(text("""
                SELECT DISTINCT school_name, COUNT(*) as user_count
                FROM users
                WHERE school_name IS NOT NULL 
                AND school_name != ''
                AND subscription_type = 'school'
                AND subscription_status = 'approved'
                GROUP BY school_name
                ORDER BY school_name
            """))
            active_schools = result.fetchall()
            
            if not active_schools:
                logger.warning("Aucune école avec abonnement actif trouvée.")
            else:
                logger.info(tabulate(active_schools, headers=["Nom de l'école", "Nombre d'utilisateurs"]))
                logger.info(f"Nombre total d'écoles avec abonnement actif: {len(active_schools)}")
            
            # 2. Vérifier les types d'abonnement
            logger.info("\n=== TYPES D'ABONNEMENT ===")
            result = db.session.execute(text("""
                SELECT subscription_type, COUNT(*) as count
                FROM users
                WHERE subscription_type IS NOT NULL
                GROUP BY subscription_type
                ORDER BY count DESC
            """))
            subscription_types = result.fetchall()
            
            if not subscription_types:
                logger.warning("Aucun type d'abonnement trouvé.")
            else:
                logger.info(tabulate(subscription_types, headers=["Type d'abonnement", "Nombre d'utilisateurs"]))
            
            # 3. Vérifier les statuts d'abonnement
            logger.info("\n=== STATUTS D'ABONNEMENT ===")
            result = db.session.execute(text("""
                SELECT subscription_status, COUNT(*) as count
                FROM users
                WHERE subscription_status IS NOT NULL
                GROUP BY subscription_status
                ORDER BY count DESC
            """))
            subscription_statuses = result.fetchall()
            
            if not subscription_statuses:
                logger.warning("Aucun statut d'abonnement trouvé.")
            else:
                logger.info(tabulate(subscription_statuses, headers=["Statut d'abonnement", "Nombre d'utilisateurs"]))
            
            # 4. Vérifier les écoles qui seraient détectées par la route select-school
            logger.info("\n=== ÉCOLES DÉTECTÉES PAR LA ROUTE SELECT-SCHOOL ===")
            result = db.session.execute(text("""
                SELECT DISTINCT u.school_name
                FROM users u
                WHERE u.school_name IS NOT NULL
                AND u.school_name != ''
                AND EXISTS (
                    SELECT 1 FROM users s
                    WHERE s.school_name = u.school_name
                    AND s.subscription_type = 'school'
                    AND s.subscription_status = 'approved'
                )
                ORDER BY u.school_name
            """))
            detected_schools = result.fetchall()
            
            if not detected_schools:
                logger.warning("Aucune école ne serait détectée par la route select-school.")
            else:
                logger.info(tabulate(detected_schools, headers=["Nom de l'école"]))
                logger.info(f"Nombre total d'écoles détectées: {len(detected_schools)}")
                
                # Afficher les écoles détectées
                schools_list = [school[0] for school in detected_schools]
                logger.info(f"Écoles qui seraient détectées: {', '.join(schools_list)}")
            
            # 5. Vérifier les abonnements de type 'Trial' ou 'trial'
            logger.info("\n=== ABONNEMENTS DE TYPE 'TRIAL' ===")
            result = db.session.execute(text("""
                SELECT id, email, school_name, subscription_type, subscription_status
                FROM users
                WHERE subscription_type IN ('Trial', 'trial')
                ORDER BY school_name
            """))
            trial_users = result.fetchall()
            
            if not trial_users:
                logger.info("Aucun utilisateur avec abonnement de type 'Trial' ou 'trial' trouvé.")
            else:
                logger.warning(tabulate(trial_users, headers=["ID", "Email", "École", "Type d'abonnement", "Statut"]))
                logger.warning(f"Nombre total d'utilisateurs avec abonnement 'Trial': {len(trial_users)}")
                logger.warning("Ces abonnements devraient être convertis en 'school'.")
            
            logger.info("\n=== VÉRIFICATION TERMINÉE ===")
            
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des abonnements: {str(e)}")

if __name__ == "__main__":
    verify_subscriptions()
