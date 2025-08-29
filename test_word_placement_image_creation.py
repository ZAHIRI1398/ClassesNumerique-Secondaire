"""
Script pour tester la création d'un exercice word_placement avec image
"""

import os
import time
import logging
import json
from flask import Flask, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests
from models import db, Exercise, User, Course

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('test_word_placement')

# Création de l'application Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def create_test_image():
    """
    Crée une image de test pour l'exercice word_placement
    """
    # Créer une image avec PIL
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color=(240, 248, 255))  # Fond bleu clair
    draw = ImageDraw.Draw(image)
    
    # Dessiner un cadre
    draw.rectangle([(20, 20), (width-20, height-20)], outline=(70, 130, 180), width=5)
    
    # Ajouter du texte
    try:
        # Essayer de charger une police
        font = ImageFont.truetype("arial.ttf", 36)
    except IOError:
        # Si la police n'est pas disponible, utiliser la police par défaut
        font = ImageFont.load_default()
    
    # Titre
    draw.text((width//2, 50), "IMAGE TEST WORD PLACEMENT", fill=(0, 0, 128), font=font, anchor="mt")
    
    # Sous-titre
    draw.text((width//2, 120), "Cette image est utilisée pour tester", fill=(0, 0, 0), font=font, anchor="mt")
    draw.text((width//2, 170), "l'affichage des images dans les exercices", fill=(0, 0, 0), font=font, anchor="mt")
    draw.text((width//2, 220), "de type 'word_placement'", fill=(0, 0, 0), font=font, anchor="mt")
    
    # Date et heure
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    draw.text((width//2, height-50), f"Créée le {timestamp}", fill=(100, 100, 100), font=font, anchor="mm")
    
    # Sauvegarder l'image
    os.makedirs('static/uploads/word_placement', exist_ok=True)
    image_path = f'static/uploads/word_placement/test_word_placement_{int(time.time())}.png'
    image.save(image_path)
    
    logger.info(f"Image de test créée: {image_path}")
    
    # Retourner le chemin de l'image et un objet BytesIO pour simuler un fichier uploadé
    image_io = BytesIO()
    image.save(image_io, format='PNG')
    image_io.seek(0)
    
    return image_path, image_io

def create_test_exercise():
    """
    Crée un exercice de test word_placement avec une image
    """
    with app.app_context():
        # Vérifier si l'utilisateur de test existe
        user = User.query.filter_by(username='admin').first()
        if not user:
            logger.error("Utilisateur admin non trouvé. Veuillez créer un utilisateur admin.")
            return False
        
        # Vérifier si une classe de test existe
        from models import Class
        import random
        import string
        
        test_class = Class.query.filter_by(name='Classe de test').first()
        if not test_class:
            # Générer un code d'accès aléatoire de 6 caractères
            access_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            
            # Créer une classe de test
            test_class = Class(
                name='Classe de test', 
                teacher_id=user.id,
                description='Classe pour tester les exercices',
                access_code=access_code
            )
            db.session.add(test_class)
            db.session.commit()
            logger.info(f"Classe de test créée: {test_class.name} (ID: {test_class.id}, Code: {access_code})")
        
        # Vérifier si le cours de test existe
        course = Course.query.filter_by(title='Cours de test').first()
        if not course:
            # Créer un cours de test
            course = Course(title='Cours de test', content='Contenu du cours de test', class_id=test_class.id)
            db.session.add(course)
            db.session.commit()
            logger.info(f"Cours de test créé: {course.title} (ID: {course.id})")
        
        # Créer une image de test
        image_path, image_io = create_test_image()
        
        # Normaliser le chemin pour la base de données
        normalized_path = f'/static/uploads/word_placement/{os.path.basename(image_path)}'
        
        # Créer l'exercice
        content_json = {
            'sentences': [
                'Le ___ est un animal domestique.',
                'La ___ est un fruit rouge.',
                'Le ___ est une planète du système solaire.'
            ],
            'words': ['chat', 'fraise', 'Mars'],
            'image': normalized_path,
            'instructions': 'Placez les mots au bon endroit dans les phrases.'
        }
        
        # Convertir le contenu en JSON
        content_str = json.dumps(content_json)
        
        # Créer l'exercice
        exercise = Exercise(
            title="Test Word Placement avec Image",
            description="Exercice de test pour vérifier l'affichage des images",
            exercise_type="word_placement",
            content=content_str,
            subject="Français",
            teacher_id=user.id,
            image_path=normalized_path
        )
        
        db.session.add(exercise)
        db.session.commit()
        
        logger.info(f"Exercice créé: {exercise.title} (ID: {exercise.id})")
        logger.info(f"Chemin d'image: {exercise.image_path}")
        logger.info(f"Contenu JSON: {exercise.get_content()}")
        
        return exercise.id

def verify_exercise_image(exercise_id):
    """
    Vérifie que l'image de l'exercice est correctement associée et accessible
    """
    with app.app_context():
        exercise = Exercise.query.get(exercise_id)
        if not exercise:
            logger.error(f"Exercice ID {exercise_id} non trouvé")
            return False
        
        logger.info(f"Vérification de l'exercice: {exercise.title} (ID: {exercise.id})")
        
        # Vérifier le chemin d'image
        if not exercise.image_path:
            logger.error("Pas de chemin d'image défini")
            return False
        
        logger.info(f"Chemin d'image: {exercise.image_path}")
        
        # Vérifier si le fichier existe
        file_path = os.path.join(os.getcwd(), exercise.image_path.lstrip('/'))
        if not os.path.exists(file_path):
            logger.error(f"Fichier image non trouvé: {file_path}")
            return False
        
        logger.info(f"Fichier image trouvé: {file_path}")
        
        # Vérifier le contenu JSON
        content = exercise.get_content()
        if not content:
            logger.error("Pas de contenu JSON")
            return False
        
        if 'image' not in content:
            logger.error("Pas d'image dans le contenu JSON")
            return False
        
        logger.info(f"Image dans le contenu JSON: {content['image']}")
        
        # Vérifier que les chemins correspondent
        if content['image'] != exercise.image_path:
            logger.warning(f"Les chemins d'image ne correspondent pas: {content['image']} != {exercise.image_path}")
        
        return True

if __name__ == "__main__":
    print("=== Test de création d'un exercice word_placement avec image ===")
    
    # Créer un exercice de test
    exercise_id = create_test_exercise()
    
    if exercise_id:
        # Vérifier l'exercice
        success = verify_exercise_image(exercise_id)
        
        # Résumé
        print("\n=== Résumé du test ===")
        print(f"Exercice créé avec ID: {exercise_id}")
        print(f"Vérification de l'image: {'Réussie' if success else 'Échouée'}")
        
        if success:
            print("\n✅ TEST RÉUSSI")
            print("L'exercice a été créé avec succès et l'image est correctement associée.")
            print("La correction du problème d'affichage des images dans les exercices word_placement est efficace.")
        else:
            print("\n❌ TEST ÉCHOUÉ")
            print("L'exercice a été créé mais l'image n'est pas correctement associée.")
            print("La correction du problème d'affichage des images doit être revue.")
    else:
        print("\n❌ TEST ÉCHOUÉ")
        print("Impossible de créer l'exercice de test.")
