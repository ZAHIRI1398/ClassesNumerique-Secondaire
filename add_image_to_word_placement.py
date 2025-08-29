"""
Script pour ajouter une image à l'exercice "Test mots à placerComplet"
"""

import os
import json
import logging
from flask import Flask
from models import db, Exercise
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('add_image_to_word_placement')

# Création de l'application Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def create_triangle_image():
    """
    Crée une image de triangle pour l'exercice de géométrie
    """
    # Créer un répertoire pour les images si nécessaire
    os.makedirs('static/uploads/word_placement', exist_ok=True)
    
    # Chemin de l'image
    image_path = 'static/uploads/word_placement/triangles_types.png'
    
    # Vérifier si l'image existe déjà
    if os.path.exists(image_path):
        logger.info(f"L'image existe déjà: {image_path}")
        return image_path
    
    # Créer une nouvelle image
    width, height = 800, 400
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Dessiner un triangle rectangle
    draw.polygon([(50, 300), (250, 300), (50, 100)], outline=(0, 0, 0), width=3)
    draw.rectangle([(45, 295), (55, 305)], outline=(0, 0, 0), width=2)  # Angle droit
    
    # Dessiner un triangle obtusangle
    draw.polygon([(350, 300), (550, 300), (400, 100)], outline=(0, 0, 0), width=3)
    
    # Dessiner un triangle rectangle isocèle
    draw.polygon([(600, 300), (800, 300), (700, 150)], outline=(0, 0, 0), width=3)
    draw.rectangle([(595, 295), (605, 305)], outline=(0, 0, 0), width=2)  # Angle droit
    
    # Ajouter des étiquettes
    try:
        # Essayer de charger une police
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        # Utiliser la police par défaut si arial n'est pas disponible
        font = ImageFont.load_default()
    
    draw.text((100, 320), "Triangle Rectangle", fill=(0, 0, 0), font=font)
    draw.text((400, 320), "Triangle Obtusangle", fill=(0, 0, 0), font=font)
    draw.text((650, 320), "Triangle Rectangle Isocèle", fill=(0, 0, 0), font=font)
    
    # Sauvegarder l'image
    image.save(image_path)
    logger.info(f"Image créée: {image_path}")
    
    return image_path

def add_image_to_exercise(exercise_id, image_path):
    """
    Ajoute une image à un exercice
    
    Args:
        exercise_id: ID de l'exercice
        image_path: Chemin de l'image à ajouter
    """
    with app.app_context():
        exercise = Exercise.query.get(exercise_id)
        if not exercise:
            logger.error(f"Exercice non trouvé (ID: {exercise_id})")
            return False
        
        # Mettre à jour le chemin d'image de l'exercice
        exercise.image_path = f"/{image_path}"
        
        # Mettre à jour le contenu de l'exercice si nécessaire
        content = exercise.get_content()
        if content and isinstance(content, dict):
            # Ajouter l'image au contenu
            content['image'] = f"/{image_path}"
            exercise.content = json.dumps(content)
        
        db.session.commit()
        logger.info(f"✅ Image ajoutée à l'exercice {exercise.title} (ID: {exercise_id})")
        return True

def find_exercise_by_title(title):
    """
    Trouve un exercice par son titre
    
    Args:
        title: Titre ou partie du titre de l'exercice
    
    Returns:
        L'exercice trouvé ou None
    """
    with app.app_context():
        exercise = Exercise.query.filter(Exercise.title.like(f"%{title}%")).first()
        if exercise:
            logger.info(f"Exercice trouvé: {exercise.title} (ID: {exercise.id})")
        else:
            logger.error(f"Aucun exercice trouvé avec le titre contenant '{title}'")
        return exercise

if __name__ == "__main__":
    # Créer l'image
    image_path = create_triangle_image()
    
    # Trouver l'exercice "Test mots à placerComplet"
    exercise = find_exercise_by_title("Test mots")
    
    if exercise:
        # Ajouter l'image à l'exercice
        success = add_image_to_exercise(exercise.id, image_path)
        
        if success:
            print(f"✅ Image ajoutée avec succès à l'exercice '{exercise.title}'")
            print(f"   Chemin de l'image: /{image_path}")
        else:
            print(f"❌ Échec de l'ajout de l'image à l'exercice '{exercise.title}'")
    else:
        print("❌ Exercice non trouvé")
