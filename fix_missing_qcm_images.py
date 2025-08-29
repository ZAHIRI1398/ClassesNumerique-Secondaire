import os
import shutil
import json
import sqlite3
from flask import Flask
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Chemin de la base de données
DB_PATH = 'instance/app.db'

# Répertoires d'images
SOURCE_DIRS = [
    'static/uploads',
    'static/exercises',
    'static/exercise-images',
    'static/exercise_images',
]

# Répertoire cible pour les images QCM
TARGET_DIR = 'static/uploads/exercises/qcm'

def ensure_directory_exists(directory):
    """Crée le répertoire s'il n'existe pas."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Répertoire créé: {directory}")

def find_image_in_directories(filename):
    """Recherche l'image dans les répertoires sources."""
    for source_dir in SOURCE_DIRS:
        # Recherche directe
        direct_path = os.path.join(source_dir, filename)
        if os.path.exists(direct_path):
            return direct_path
        
        # Recherche dans les sous-répertoires
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if file == filename:
                    return os.path.join(root, file)
    
    return None

def copy_image_to_target(source_path, filename):
    """Copie l'image vers le répertoire cible."""
    ensure_directory_exists(TARGET_DIR)
    target_path = os.path.join(TARGET_DIR, filename)
    
    try:
        shutil.copy2(source_path, target_path)
        logger.info(f"Image copiée: {source_path} -> {target_path}")
        return target_path
    except Exception as e:
        logger.error(f"Erreur lors de la copie de l'image: {e}")
        return None

def update_exercise_image_path(exercise_id, new_path):
    """Met à jour le chemin d'image dans la base de données."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Récupérer le contenu actuel
        cursor.execute("SELECT content FROM exercise WHERE id = ?", (exercise_id,))
        result = cursor.fetchone()
        if not result:
            logger.error(f"Exercice {exercise_id} non trouvé")
            return False
        
        content = json.loads(result[0])
        
        # Mettre à jour le chemin d'image dans le contenu
        if 'image' in content:
            old_path = content['image']
            content['image'] = f"/static/uploads/exercises/qcm/{os.path.basename(new_path)}"
            logger.info(f"Chemin d'image mis à jour: {old_path} -> {content['image']}")
        
        # Sauvegarder le contenu mis à jour
        cursor.execute("UPDATE exercise SET content = ? WHERE id = ?", 
                      (json.dumps(content), exercise_id))
        conn.commit()
        logger.info(f"Base de données mise à jour pour l'exercice {exercise_id}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de la base de données: {e}")
        return False
    finally:
        if conn:
            conn.close()

def fix_qcm_images():
    """Corrige les images manquantes pour les exercices QCM."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Récupérer tous les exercices QCM
        cursor.execute("SELECT id, content FROM exercise WHERE exercise_type = 'qcm'")
        exercises = cursor.fetchall()
        
        for exercise_id, content_json in exercises:
            try:
                content = json.loads(content_json)
                if 'image' in content:
                    image_path = content['image']
                    filename = os.path.basename(image_path)
                    
                    # Vérifier si l'image existe déjà dans le répertoire cible
                    target_file = os.path.join(TARGET_DIR, filename)
                    if os.path.exists(target_file):
                        logger.info(f"L'image existe déjà: {target_file}")
                        continue
                    
                    # Rechercher l'image dans les répertoires sources
                    source_path = find_image_in_directories(filename)
                    if source_path:
                        # Copier l'image vers le répertoire cible
                        new_path = copy_image_to_target(source_path, filename)
                        if new_path:
                            # Mettre à jour le chemin d'image dans la base de données
                            update_exercise_image_path(exercise_id, new_path)
                    else:
                        logger.warning(f"Image non trouvée: {filename} pour l'exercice {exercise_id}")
            except json.JSONDecodeError:
                logger.error(f"Contenu JSON invalide pour l'exercice {exercise_id}")
                continue
    except Exception as e:
        logger.error(f"Erreur lors de la correction des images QCM: {e}")
    finally:
        if conn:
            conn.close()

def create_placeholder_image(filename):
    """Crée une image placeholder si l'image originale n'est pas trouvée."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Créer une image placeholder
        width, height = 800, 400
        image = Image.new('RGB', (width, height), color=(173, 216, 230))  # Bleu clair
        draw = ImageDraw.Draw(image)
        
        # Ajouter du texte
        text = f"Image placeholder: {filename}"
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except IOError:
            font = ImageFont.load_default()
        
        text_width, text_height = draw.textsize(text, font=font) if hasattr(draw, 'textsize') else (300, 36)
        position = ((width - text_width) // 2, (height - text_height) // 2)
        draw.text(position, text, fill=(0, 0, 0), font=font)
        
        # Sauvegarder l'image
        ensure_directory_exists(TARGET_DIR)
        target_path = os.path.join(TARGET_DIR, filename)
        image.save(target_path)
        logger.info(f"Image placeholder créée: {target_path}")
        return target_path
    except Exception as e:
        logger.error(f"Erreur lors de la création de l'image placeholder: {e}")
        return None

def main():
    """Fonction principale."""
    logger.info("Début de la correction des images QCM")
    ensure_directory_exists(TARGET_DIR)
    fix_qcm_images()
    logger.info("Fin de la correction des images QCM")

if __name__ == "__main__":
    main()
