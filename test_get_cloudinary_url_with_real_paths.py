import requests
import json
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_get_cloudinary_url_with_real_paths():
    """
    Test la route /get_cloudinary_url avec les chemins d'images réels trouvés dans la base de données
    """
    # URL de base de l'application
    base_url = "http://127.0.0.1:5000"
    
    # Liste de chemins d'images réels trouvés dans la base de données
    real_paths = [
        "uploads/1756247392_3opwru.png",  # Exercice 70, Carte 1
        "uploads/1756247392_o1p7u4.png",  # Exercice 70, Carte 2
        "uploads/1756247392_sfnq84.png",  # Exercice 70, Carte 3
        "uploads/1756307741_mox2ot.png",  # Exercice 71, Carte 1
        "uploads/1756307741_fpxlrz.png",  # Exercice 71, Carte 2
        "uploads/1756307741_gl8wuh.png",  # Exercice 71, Carte 3
    ]
    
    # Tester chaque chemin
    for path in real_paths:
        logger.info(f"Test avec le chemin réel: {path}")
        
        # Construire l'URL complète
        url = f"{base_url}/get_cloudinary_url?image_path={path}"
        
        try:
            # Faire la requête
            response = requests.get(url)
            
            # Afficher le code de statut
            logger.info(f"Code de statut: {response.status_code}")
            
            # Afficher le contenu de la réponse
            if response.status_code == 200:
                try:
                    # Essayer de parser comme JSON
                    json_response = response.json()
                    logger.info(f"Réponse JSON: {json.dumps(json_response, indent=2)}")
                    
                    # Vérifier si l'URL est présente et si elle commence par /static/
                    if 'url' in json_response:
                        url_value = json_response['url']
                        logger.info(f"URL trouvée: {url_value}")
                        
                        # Vérifier si l'URL commence par /static/
                        if not url_value.startswith('/static/'):
                            logger.warning(f"L'URL ne commence pas par /static/: {url_value}")
                    else:
                        logger.warning("Pas d'URL dans la réponse JSON")
                except json.JSONDecodeError:
                    logger.error(f"La réponse n'est pas du JSON valide: {response.text}")
            else:
                logger.error(f"Réponse non-200: {response.text}")
        
        except Exception as e:
            logger.error(f"Erreur lors de la requête: {str(e)}")
    
    logger.info("Tests terminés")

if __name__ == "__main__":
    test_get_cloudinary_url_with_real_paths()
