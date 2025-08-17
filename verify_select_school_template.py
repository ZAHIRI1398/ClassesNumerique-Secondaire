import requests
import logging
import os
from datetime import datetime

# Configuration du logging
log_filename = f"verify_select_school_template_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def verify_template_deployment():
    """
    Vérifie si le template select_school.html est correctement déployé sur Railway
    en testant l'accès à la route /payment/select_school
    """
    try:
        # URL de l'application sur Railway
        url = "https://web-production-9a047.up.railway.app/payment/select_school"
        
        # Effectuer la requête
        logger.info(f"Tentative d'acces a {url}")
        response = requests.get(url)
        
        # Vérifier le code de statut
        logger.info(f"Code de statut: {response.status_code}")
        
        if response.status_code == 200:
            logger.info("[SUCCES] La route /payment/select_school fonctionne correctement!")
            logger.debug(f"Contenu de la page (premiers 500 caracteres): {response.text[:500]}")
            print("[SUCCES] La route /payment/select_school fonctionne correctement!")
            return True
        else:
            logger.error(f"[ERREUR] La route renvoie un code d'erreur: {response.status_code}")
            logger.debug(f"Contenu de l'erreur: {response.text[:500]}")
            print(f"[ERREUR] La route renvoie un code d'erreur: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"[ERREUR] Erreur lors de la verification: {str(e)}")
        print(f"[ERREUR] Erreur lors de la verification: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== VERIFICATION DU DEPLOIEMENT DU TEMPLATE SELECT_SCHOOL ===")
    success = verify_template_deployment()
    
    if success:
        print("\nLe template a ete correctement deploye et la route fonctionne!")
    else:
        print("\nLe deploiement a echoue ou la route ne fonctionne pas correctement.")
        print(f"Consultez le fichier de log {log_filename} pour plus de details.")
