import os
import sys
import psycopg2
import logging
from dotenv import load_dotenv
from tabulate import tabulate
from datetime import datetime

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

# Charger les variables d'environnement
load_dotenv()

# URL de la base de données de production (extraite du fichier run_fix_trial_subscriptions.bat)
db_url = "postgresql://postgres:SJqjLlGjIzLYjOuaKRcTmDqrgkMpcGJO@postgres.railway.internal:5432/railway"

# Vérifier si l'URL est fournie en ligne de commande
if len(sys.argv) > 1 and sys.argv[1].startswith("postgresql://"):
    db_url = sys.argv[1]
    logger.info(f"Utilisation de l'URL de base de données fournie en ligne de commande")

logger.info(f"Connexion à la base de données: {db_url[:20]}...")


def verify_subscriptions():
    """Vérifier les abonnements en production"""
    try:
        # Connexion à la base de données
        logger.info("Connexion à la base de données de production...")
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # 1. Vérifier les écoles avec abonnements actifs
        logger.info("=== ÉCOLES AVEC ABONNEMENTS ACTIFS ===")
        cursor.execute("""
            SELECT DISTINCT school_name, COUNT(*) as user_count
            FROM users
            WHERE school_name IS NOT NULL 
            AND school_name != ''
            AND subscription_type = 'school'
            AND subscription_status = 'approved'
            GROUP BY school_name
            ORDER BY school_name
        """)
        active_schools = cursor.fetchall()
        
        if not active_schools:
            logger.warning("Aucune école avec abonnement actif trouvée.")
        else:
            logger.info(tabulate(active_schools, headers=["Nom de l'école", "Nombre d'utilisateurs"]))
            logger.info(f"Nombre total d'écoles avec abonnement actif: {len(active_schools)}")
        
        # 2. Vérifier les types d'abonnement
        logger.info("\n=== TYPES D'ABONNEMENT ===")
        cursor.execute("""
            SELECT subscription_type, COUNT(*) as count
            FROM users
            WHERE subscription_type IS NOT NULL
            GROUP BY subscription_type
            ORDER BY count DESC
        """)
        subscription_types = cursor.fetchall()
        
        if not subscription_types:
            logger.warning("Aucun type d'abonnement trouvé.")
        else:
            logger.info(tabulate(subscription_types, headers=["Type d'abonnement", "Nombre d'utilisateurs"]))
        
        # 3. Vérifier les statuts d'abonnement
        logger.info("\n=== STATUTS D'ABONNEMENT ===")
        cursor.execute("""
            SELECT subscription_status, COUNT(*) as count
            FROM users
            WHERE subscription_status IS NOT NULL
            GROUP BY subscription_status
            ORDER BY count DESC
        """)
        subscription_statuses = cursor.fetchall()
        
        if not subscription_statuses:
            logger.warning("Aucun statut d'abonnement trouvé.")
        else:
            logger.info(tabulate(subscription_statuses, headers=["Statut d'abonnement", "Nombre d'utilisateurs"]))
        
        # 4. Vérifier les écoles qui seraient détectées par la route select-school
        logger.info("\n=== ÉCOLES DÉTECTÉES PAR LA ROUTE SELECT-SCHOOL ===")
        cursor.execute("""
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
        """)
        detected_schools = cursor.fetchall()
        
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
        cursor.execute("""
            SELECT id, email, school_name, subscription_type, subscription_status
            FROM users
            WHERE subscription_type IN ('Trial', 'trial')
            ORDER BY school_name
        """)
        trial_users = cursor.fetchall()
        
        if not trial_users:
            logger.info("Aucun utilisateur avec abonnement de type 'Trial' ou 'trial' trouvé.")
        else:
            logger.warning(tabulate(trial_users, headers=["ID", "Email", "École", "Type d'abonnement", "Statut"]))
            logger.warning(f"Nombre total d'utilisateurs avec abonnement 'Trial': {len(trial_users)}")
            logger.warning("Ces abonnements devraient être convertis en 'school'.")
        
        logger.info("\n=== VÉRIFICATION TERMINÉE ===")
        logger.info("Pour corriger les abonnements de type 'Trial', exécutez:")
        logger.info("python fix_trial_subscriptions.py --fix")
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des abonnements: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    verify_subscriptions()
