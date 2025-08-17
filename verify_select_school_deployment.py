import os
import logging
import requests
from datetime import datetime
import time

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"verify_deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger(__name__)

# URL de l'application en production
PRODUCTION_URL = "https://classesnumerique.up.railway.app"

def verify_deployment():
    """Vérifier que le déploiement de la correction est effectif en production"""
    logger.info("=== Vérification du déploiement de la correction ===")
    
    # Attendre un peu pour que le déploiement soit effectif
    logger.info("Attente de 30 secondes pour que le déploiement soit effectif...")
    time.sleep(30)
    
    # Vérifier que l'application est accessible
    try:
        response = requests.get(f"{PRODUCTION_URL}")
        if response.status_code == 200:
            logger.info(f"L'application est accessible en production (code {response.status_code})")
        else:
            logger.warning(f"L'application retourne un code {response.status_code}")
    except Exception as e:
        logger.error(f"Erreur lors de l'accès à l'application: {str(e)}")
        return False
    
    # Vérifier la route de diagnostic
    try:
        logger.info("Vérification de la route de diagnostic...")
        response = requests.get(f"{PRODUCTION_URL}/diagnose/select-school")
        
        if response.status_code == 200:
            logger.info(f"La route de diagnostic est accessible (code {response.status_code})")
            logger.info("Contenu de la page de diagnostic:")
            
            # Analyser la réponse pour vérifier si elle contient des informations sur les écoles
            if "Ecole Sainte Bernadette" in response.text or "Collége Notre Dame" in response.text:
                logger.info("Les écoles sont correctement détectées dans la page de diagnostic")
            else:
                logger.warning("Les écoles ne semblent pas être détectées dans la page de diagnostic")
        elif response.status_code == 401 or response.status_code == 403:
            logger.info(f"La route de diagnostic nécessite une authentification (code {response.status_code})")
            logger.info("C'est normal, la route est protégée par authentification")
        else:
            logger.warning(f"La route de diagnostic retourne un code {response.status_code}")
    except Exception as e:
        logger.error(f"Erreur lors de l'accès à la route de diagnostic: {str(e)}")
    
    # Vérifier la route de sélection d'école
    try:
        logger.info("Vérification de la route de sélection d'école...")
        response = requests.get(f"{PRODUCTION_URL}/payment/select-school")
        
        if response.status_code == 200:
            logger.info(f"La route de sélection d'école est accessible (code {response.status_code})")
            logger.info("La correction a été déployée avec succès!")
            
            # Vérifier si la page contient le formulaire de sélection d'école
            if "Sélectionnez votre école" in response.text or "form" in response.text.lower():
                logger.info("Le formulaire de sélection d'école est présent dans la page")
            else:
                logger.warning("Le formulaire de sélection d'école ne semble pas être présent dans la page")
        elif response.status_code == 302:
            logger.info(f"La route de sélection d'école redirige (code {response.status_code})")
            logger.info("C'est normal si l'utilisateur n'est pas authentifié")
        else:
            logger.warning(f"La route de sélection d'école retourne un code {response.status_code}")
            
            if response.status_code == 500:
                logger.error("ERREUR 500: La correction n'a pas résolu le problème!")
                logger.error("Vérifiez les logs de production pour plus de détails")
                return False
    except Exception as e:
        logger.error(f"Erreur lors de l'accès à la route de sélection d'école: {str(e)}")
    
    logger.info("=== Vérification terminée ===")
    logger.info("Pour vérifier manuellement:")
    logger.info(f"1. Accédez à {PRODUCTION_URL}/payment/select-school après vous être connecté en tant qu'enseignant")
    logger.info("2. Vérifiez que la page affiche correctement les écoles avec abonnement")
    logger.info("3. Vérifiez que vous pouvez sélectionner une école et continuer le processus")
    
    return True

if __name__ == "__main__":
    verify_deployment()
