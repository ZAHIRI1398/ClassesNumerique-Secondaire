import os
import json
import sqlite3
import logging
from flask import Flask

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Créer une application Flask pour avoir accès au root_path
app = Flask(__name__)

def verify_exercise_images():
    """
    Vérifie si toutes les images référencées dans les exercices existent réellement
    dans le système de fichiers.
    """
    try:
        # Connexion à la base de données
        db_path = 'instance/app.db'
        if not os.path.exists(db_path):
            logger.error(f"Base de données non trouvée: {db_path}")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Récupérer tous les exercices avec leurs chemins d'images
        cursor.execute("SELECT id, title, exercise_type, image_path, content FROM exercise")
        exercises = cursor.fetchall()
        
        if not exercises:
            logger.warning("Aucun exercice trouvé dans la base de données.")
            return False
        
        logger.info(f"Nombre total d'exercices: {len(exercises)}")
        
        # Statistiques
        total_exercises = len(exercises)
        exercises_with_images = 0
        missing_images = 0
        exercises_with_content_images = 0
        missing_content_images = 0
        
        # Vérifier chaque exercice
        for exercise_id, title, exercise_type, image_path, content_str in exercises:
            logger.info(f"\n=== Exercice #{exercise_id}: {title} ({exercise_type}) ===")
            
            # Vérifier l'image principale
            if image_path:
                # Normaliser le chemin d'image
                if image_path.startswith('/static/'):
                    file_path = os.path.join(app.root_path, image_path[1:])  # Enlever le premier '/'
                else:
                    file_path = os.path.join(app.root_path, 'static', image_path)
                
                if os.path.exists(file_path):
                    logger.info(f"Image principale: {image_path} ✓")
                    exercises_with_images += 1
                    
                    # Vérifier la taille du fichier
                    file_size = os.path.getsize(file_path)
                    if file_size == 0:
                        logger.warning(f"L'image {image_path} existe mais est vide (0 bytes)!")
                else:
                    logger.error(f"Image principale: {image_path} ✗ (fichier manquant)")
                    missing_images += 1
                    
                    # Suggérer un chemin alternatif
                    alt_path = os.path.join(app.root_path, 'static', 'uploads', exercise_type, os.path.basename(image_path))
                    if os.path.exists(alt_path):
                        logger.info(f"Suggestion: L'image existe peut-être à {alt_path}")
            else:
                logger.warning(f"Pas d'image principale définie pour cet exercice")
            
            # Vérifier les images dans le contenu JSON
            try:
                content = json.loads(content_str)
                
                # Vérifier si le contenu a une image
                if 'image' in content and content['image']:
                    content_image = content['image']
                    exercises_with_content_images += 1
                    
                    # Normaliser le chemin d'image du contenu
                    if content_image.startswith('/static/'):
                        content_file_path = os.path.join(app.root_path, content_image[1:])
                    else:
                        content_file_path = os.path.join(app.root_path, 'static', content_image)
                    
                    if os.path.exists(content_file_path):
                        logger.info(f"Image dans le contenu: {content_image} ✓")
                        
                        # Vérifier la taille du fichier
                        file_size = os.path.getsize(content_file_path)
                        if file_size == 0:
                            logger.warning(f"L'image {content_image} existe mais est vide (0 bytes)!")
                    else:
                        logger.error(f"Image dans le contenu: {content_image} ✗ (fichier manquant)")
                        missing_content_images += 1
                        
                        # Suggérer un chemin alternatif
                        alt_content_path = os.path.join(app.root_path, 'static', 'uploads', exercise_type, os.path.basename(content_image))
                        if os.path.exists(alt_content_path):
                            logger.info(f"Suggestion: L'image existe peut-être à {alt_content_path}")
            except json.JSONDecodeError:
                logger.error(f"Contenu JSON invalide pour l'exercice #{exercise_id}")
            except Exception as e:
                logger.error(f"Erreur lors de l'analyse du contenu de l'exercice #{exercise_id}: {str(e)}")
        
        # Afficher les statistiques
        logger.info(f"\n=== STATISTIQUES ===")
        logger.info(f"Nombre total d'exercices: {total_exercises}")
        logger.info(f"Exercices avec image principale: {exercises_with_images}/{total_exercises}")
        logger.info(f"Images principales manquantes: {missing_images}")
        logger.info(f"Exercices avec image dans le contenu: {exercises_with_content_images}/{total_exercises}")
        logger.info(f"Images dans le contenu manquantes: {missing_content_images}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des images: {str(e)}")
        return False

def main():
    """
    Fonction principale
    """
    logger.info("=== VÉRIFICATION DES IMAGES DES EXERCICES ===")
    
    # Vérifier les images
    success = verify_exercise_images()
    
    if success:
        logger.info("""
=== VÉRIFICATION TERMINÉE ===

La vérification des images des exercices est terminée.
Consultez les messages ci-dessus pour voir les résultats.

Si des images sont manquantes, vous pouvez:
1. Créer les dossiers nécessaires dans static/uploads/[type_exercice]/
2. Ajouter les images manquantes
3. Ou corriger les chemins d'images dans la base de données
""")
    else:
        logger.error("""
=== ÉCHEC DE LA VÉRIFICATION ===

La vérification des images des exercices a échoué.
Vérifiez les messages d'erreur ci-dessus.
""")

if __name__ == "__main__":
    main()
