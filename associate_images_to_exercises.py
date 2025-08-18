"""
Script pour associer des images aux exercices existants
et préparer la migration vers Cloudinary
"""

import os
import sys
import random
import argparse
from flask import Flask
from models import db, Exercise
from config import config

def create_app():
    """Crée une instance minimale de l'application Flask"""
    app = Flask(__name__)
    
    # Charger la configuration depuis config.py
    try:
        app.config.from_object(config['development'])
        print("[OK] Configuration chargée avec succès")
    except Exception as e:
        print(f"[ERREUR] Impossible de charger la configuration: {str(e)}")
        sys.exit(1)
    
    # Initialiser la base de données
    db.init_app(app)
    
    return app

def get_available_images(app):
    """
    Récupère la liste des images disponibles dans static/uploads
    
    Returns:
        list: Liste des chemins relatifs des images
    """
    uploads_dir = os.path.join(app.static_folder, 'uploads')
    
    if not os.path.exists(uploads_dir):
        print(f"[ERREUR] Le répertoire {uploads_dir} n'existe pas")
        return []
    
    # Récupérer la liste des fichiers
    images = []
    for root, _, filenames in os.walk(uploads_dir):
        for filename in filenames:
            # Ignorer les fichiers cachés et .gitkeep
            if filename.startswith('.') or filename == '.gitkeep':
                continue
            
            # Ignorer les répertoires
            file_path = os.path.join(root, filename)
            if os.path.isdir(file_path):
                continue
            
            # Ignorer les fichiers vides
            if os.path.getsize(file_path) == 0:
                continue
            
            # Vérifier l'extension pour s'assurer que c'est une image
            _, ext = os.path.splitext(filename)
            if ext.lower() not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                continue
            
            # Calculer le chemin relatif par rapport à static
            rel_path = os.path.relpath(file_path, app.static_folder)
            
            # Ajouter à la liste
            images.append(rel_path)
    
    return images

def associate_images_to_exercises(dry_run=True):
    """
    Associe des images aux exercices existants
    
    Args:
        dry_run: Si True, n'effectue pas réellement les modifications
    """
    app = create_app()
    
    with app.app_context():
        # Récupérer la liste des images disponibles
        available_images = get_available_images(app)
        
        if not available_images:
            print("[ERREUR] Aucune image disponible dans static/uploads")
            return
        
        print(f"Trouvé {len(available_images)} images disponibles")
        
        # Récupérer les exercices sans image
        exercises = Exercise.query.filter(Exercise.image_path.is_(None)).all()
        
        if not exercises:
            print("Aucun exercice sans image trouvé")
            return
        
        print(f"Trouvé {len(exercises)} exercices sans image")
        
        # Associer des images aux exercices
        updated_exercises = []
        
        for exercise in exercises:
            # Sélectionner une image aléatoire
            image_path = random.choice(available_images)
            
            print(f"Exercice #{exercise.id} ({exercise.title}): {image_path}")
            
            if not dry_run:
                exercise.image_path = image_path
                updated_exercises.append(exercise)
        
        if not dry_run and updated_exercises:
            try:
                db.session.commit()
                print(f"[OK] {len(updated_exercises)} exercices mis à jour avec succès")
            except Exception as e:
                db.session.rollback()
                print(f"[ERREUR] Impossible de mettre à jour les exercices: {str(e)}")
        elif dry_run:
            print("\n[SIMULATION] Mode simulation activé, aucune modification n'a été effectuée")
            print("Pour effectuer les modifications réelles, exécutez avec --no-dry-run")

def create_sample_exercise_with_image(dry_run=True):
    """
    Crée un exercice d'exemple avec une image
    
    Args:
        dry_run: Si True, n'effectue pas réellement les modifications
    """
    app = create_app()
    
    with app.app_context():
        # Récupérer la liste des images disponibles
        available_images = get_available_images(app)
        
        if not available_images:
            print("[ERREUR] Aucune image disponible dans static/uploads")
            return
        
        # Sélectionner une image aléatoire
        image_path = random.choice(available_images)
        
        # Créer un exercice d'exemple
        exercise = Exercise(
            title="Exercice d'exemple avec image",
            description="Cet exercice a été créé pour tester la migration d'images vers Cloudinary",
            exercise_type="qcm",
            content={
                "question": "Quelle est la capitale de la France?",
                "options": ["Paris", "Londres", "Berlin", "Madrid"],
                "correct_answer": 0
            },
            subject="Géographie",
            teacher_id=1,
            max_attempts=3,
            image_path=image_path
        )
        
        print(f"Création d'un exercice d'exemple avec l'image: {image_path}")
        
        if not dry_run:
            try:
                db.session.add(exercise)
                db.session.commit()
                print(f"[OK] Exercice créé avec succès (ID: {exercise.id})")
            except Exception as e:
                db.session.rollback()
                print(f"[ERREUR] Impossible de créer l'exercice: {str(e)}")
        else:
            print("\n[SIMULATION] Mode simulation activé, aucune modification n'a été effectuée")
            print("Pour effectuer les modifications réelles, exécutez avec --no-dry-run")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Associer des images aux exercices")
    parser.add_argument("--no-dry-run", action="store_true", help="Effectuer réellement les modifications")
    parser.add_argument("--create-sample", action="store_true", help="Créer un exercice d'exemple avec une image")
    args = parser.parse_args()
    
    if args.create_sample:
        create_sample_exercise_with_image(dry_run=not args.no_dry_run)
    else:
        associate_images_to_exercises(dry_run=not args.no_dry_run)
