import requests
import json
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_get_cloudinary_url():
    """
    Test la route /get_cloudinary_url avec différents chemins d'images
    pour vérifier les réponses et détecter les problèmes potentiels
    """
    # URL de base de l'application
    base_url = "http://127.0.0.1:5000"
    
    # Liste de chemins d'images à tester
    test_paths = [
        "static/exercise_images/1738345030_image5.jpeg",
        "static/exercise_images/test_image.png",
        "static/uploads/flashcards/test_image.jpg",
        # Ajoutez d'autres chemins selon votre structure
    ]
    
    # Tester chaque chemin
    for path in test_paths:
        logger.info(f"Test avec le chemin: {path}")
        
        # Construire l'URL complète
        url = f"{base_url}/get_cloudinary_url?image_path={path}"
        
        try:
            # Faire la requête
            response = requests.get(url)
            
            # Afficher le code de statut
            logger.info(f"Code de statut: {response.status_code}")
            
            # Afficher les en-têtes de réponse
            logger.info(f"En-têtes: {response.headers}")
            
            # Afficher le contenu de la réponse
            if response.status_code == 200:
                try:
                    # Essayer de parser comme JSON
                    json_response = response.json()
                    logger.info(f"Réponse JSON: {json.dumps(json_response, indent=2)}")
                    
                    # Vérifier si l'URL est présente
                    if 'url' in json_response:
                        logger.info(f"URL trouvée: {json_response['url']}")
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
    test_get_cloudinary_url()
