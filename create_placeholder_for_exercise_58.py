import os
import json
import sqlite3
from PIL import Image, ImageDraw, ImageFont
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Chemin de la base de données
DB_PATH = 'instance/app.db'

# Répertoire cible pour les images QCM
TARGET_DIR = 'static/uploads/exercises/qcm'

def ensure_directory_exists(directory):
    """Crée le répertoire s'il n'existe pas."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Répertoire créé: {directory}")

def create_placeholder_image(filename, title="Système solaire"):
    """Crée une image placeholder pour le système solaire."""
    try:
        # Créer une image placeholder
        width, height = 800, 400
        image = Image.new('RGB', (width, height), color=(0, 0, 50))  # Bleu foncé (comme l'espace)
        draw = ImageDraw.Draw(image)
        
        # Ajouter du texte
        text = f"Le système solaire"
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except IOError:
            font = ImageFont.load_default()
        
        # Dessiner un soleil et quelques planètes
        # Soleil (cercle jaune)
        draw.ellipse((50, 150, 150, 250), fill=(255, 255, 0))
        
        # Planètes (cercles de différentes tailles et couleurs)
        # Mercure
        draw.ellipse((200, 180, 220, 200), fill=(200, 200, 200))
        # Vénus
        draw.ellipse((280, 175, 310, 205), fill=(255, 200, 100))
        # Terre
        draw.ellipse((370, 170, 410, 210), fill=(0, 100, 255))
        # Mars
        draw.ellipse((470, 175, 500, 205), fill=(255, 100, 0))
        # Jupiter
        draw.ellipse((550, 160, 610, 220), fill=(255, 220, 150))
        # Saturne
        draw.ellipse((670, 170, 720, 210), fill=(255, 240, 200))
        # Anneaux de Saturne
        draw.arc((660, 165, 730, 215), 0, 360, fill=(255, 255, 200))
        
        # Ajouter le texte en haut
        draw.text((300, 50), text, fill=(255, 255, 255), font=font)
        
        # Sauvegarder l'image
        ensure_directory_exists(TARGET_DIR)
        target_path = os.path.join(TARGET_DIR, filename)
        image.save(target_path)
        logger.info(f"Image placeholder créée: {target_path}")
        return target_path
    except Exception as e:
        logger.error(f"Erreur lors de la création de l'image placeholder: {e}")
        return None

def update_exercise_image_path(exercise_id, filename):
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
            content['image'] = f"/static/uploads/exercises/qcm/{filename}"
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

def main():
    """Fonction principale."""
    logger.info("Création d'une image placeholder pour l'exercice 58")
    
    # Nom du fichier manquant
    filename = "Capture_d_ecran_2025-08-14_151156_20250828_154105_KZGCo1.png"
    
    # Créer l'image placeholder
    ensure_directory_exists(TARGET_DIR)
    target_path = create_placeholder_image(filename)
    
    if target_path:
        # Mettre à jour le chemin d'image dans la base de données
        update_exercise_image_path(58, filename)
    
    logger.info("Fin de la création de l'image placeholder")

if __name__ == "__main__":
    main()
