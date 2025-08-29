"""
Script de test pour vérifier la solution de gestion des chemins d'images
avec caractères spéciaux
"""

import os
import logging
import shutil
from flask import Flask
from image_url_service import ImageUrlService, get_cloudinary_url
from utils.image_path_handler import normalize_image_path, normalize_filename, get_image_url as handler_get_image_url

# Configuration du logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('test_image_path_solution.log'), 
                              logging.StreamHandler()])
logger = logging.getLogger(__name__)

# Créer une application Flask pour le test
app = Flask(__name__)

def create_test_files():
    """
    Crée des fichiers de test avec différents noms pour tester la solution
    """
    # Créer les répertoires nécessaires s'ils n'existent pas
    os.makedirs("static/uploads/exercises/qcm", exist_ok=True)
    os.makedirs("static/exercises/qcm", exist_ok=True)
    
    # Créer des fichiers de test avec différents noms
    test_files = [
        "static/uploads/exercises/qcm/Capture d'écran 2025-08-12 180016.png",
        "static/uploads/exercises/qcm/Image avec espaces.jpg",
        "static/exercises/qcm/Image-avec-tirets.png",
        "static/exercises/qcm/Image_avec_underscores.jpg",
        "static/uploads/exercises/qcm/Image avec caractères spéciaux éèàç.png"
    ]
    
    for file_path in test_files:
        # Créer un fichier vide
        with open(file_path, 'w') as f:
            f.write("Test file")
        logger.info(f"Fichier de test créé: {file_path}")

def test_image_url_service():
    """
    Teste le service ImageUrlService avec différents chemins d'images
    """
    logger.info("=== Test du service ImageUrlService ===")
    
    # Liste des chemins à tester
    test_paths = [
        "/static/uploads/exercises/qcm/Capture d'écran 2025-08-12 180016.png",
        "static/uploads/exercises/qcm/Image avec espaces.jpg",
        "/static/exercises/qcm/Image-avec-tirets.png",
        "static/exercises/qcm/Image_avec_underscores.jpg",
        "/static/uploads/exercises/qcm/Image avec caractères spéciaux éèàç.png",
        # Chemins avec noms normalisés
        "/static/uploads/exercises/qcm/Capture_d_ecran_2025-08-12_180016.png",
        "static/uploads/exercises/qcm/Image_avec_espaces.jpg",
        "/static/uploads/exercises/qcm/Image_avec_caracteres_speciaux_eeac.png"
    ]
    
    with app.app_context():
        for path in test_paths:
            # Tester le service ImageUrlService
            result = ImageUrlService.get_image_url(path)
            logger.info(f"ImageUrlService.get_image_url({path}) => {result}")
            
            # Tester la fonction de compatibilité get_cloudinary_url
            compat_result = get_cloudinary_url(path)
            logger.info(f"get_cloudinary_url({path}) => {compat_result}")

def test_image_path_handler():
    """
    Teste les fonctions du module image_path_handler
    """
    logger.info("=== Test du module image_path_handler ===")
    
    # Liste des noms de fichiers à tester
    test_filenames = [
        "Capture d'écran 2025-08-12 180016.png",
        "Image avec espaces.jpg",
        "Image-avec-tirets.png",
        "Image_avec_underscores.jpg",
        "Image avec caractères spéciaux éèàç.png"
    ]
    
    # Tester la fonction normalize_filename
    for filename in test_filenames:
        normalized = normalize_filename(filename)
        logger.info(f"normalize_filename({filename}) => {normalized}")
    
    # Liste des chemins à tester
    test_paths = [
        "/static/uploads/exercises/qcm/Capture d'écran 2025-08-12 180016.png",
        "static/uploads/exercises/qcm/Image avec espaces.jpg",
        "/static/exercises/qcm/Image-avec-tirets.png",
        "static/exercises/qcm/Image_avec_underscores.jpg",
        "/static/uploads/exercises/qcm/Image avec caractères spéciaux éèàç.png"
    ]
    
    # Tester la fonction normalize_image_path
    for path in test_paths:
        normalized = normalize_image_path(path)
        logger.info(f"normalize_image_path({path}) => {normalized}")
    
    with app.app_context():
        # Tester la fonction get_image_url du module image_path_handler
        for path in test_paths:
            result = handler_get_image_url(path)
            logger.info(f"handler_get_image_url({path}) => {result}")

def cleanup_test_files():
    """
    Nettoie les fichiers de test créés
    """
    try:
        # Supprimer les fichiers de test
        if os.path.exists("static/uploads/exercises/qcm"):
            shutil.rmtree("static/uploads/exercises/qcm")
        if os.path.exists("static/exercises/qcm"):
            shutil.rmtree("static/exercises/qcm")
        logger.info("Fichiers de test supprimés")
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage des fichiers de test: {str(e)}")

def run_tests():
    """
    Exécute tous les tests
    """
    try:
        # Créer les fichiers de test
        create_test_files()
        
        # Tester le service ImageUrlService
        test_image_url_service()
        
        # Tester le module image_path_handler
        test_image_path_handler()
        
        logger.info("Tous les tests ont été exécutés avec succès")
        
    finally:
        # Nettoyer les fichiers de test
        cleanup_test_files()

if __name__ == "__main__":
    run_tests()
