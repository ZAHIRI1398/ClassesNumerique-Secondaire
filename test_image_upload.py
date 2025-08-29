"""
Script de test pour l'upload d'images sur les exercices de type Legend et Image Labeling.
Ce script crée un exercice de type Legend et teste l'upload d'image sur les deux types d'exercices.
"""

import os
import sys
import json
import datetime
from app import app, db
from models import Exercise, User
from flask import url_for

def create_legend_exercise():
    """Crée un exercice de type Legend pour tester l'upload d'image"""
    print("Création d'un exercice de type Legend...")
    
    # Vérifier si un exercice de type Legend existe déjà
    legend_exercise = Exercise.query.filter_by(exercise_type='legend').first()
    if legend_exercise:
        print(f"Un exercice de type Legend existe déjà avec l'ID {legend_exercise.id}")
        return legend_exercise.id
    
    # Créer un nouvel exercice de type Legend
    try:
        new_exercise = Exercise(
            title="Test Legend Exercise",
            description="Exercice de test pour l'upload d'image sur les exercices de type Legend",
            exercise_type="legend",
            subject="test",
            teacher_id=1,  # ID de l'utilisateur admin
            content=json.dumps({
                "legend_mode": "classic",
                "zones": []
            })
        )
        db.session.add(new_exercise)
        db.session.commit()
        print(f"Exercice de type Legend créé avec l'ID {new_exercise.id}")
        return new_exercise.id
    except Exception as e:
        print(f"Erreur lors de la création de l'exercice Legend: {e}")
        db.session.rollback()
        return None

def test_image_paths():
    """Teste les chemins d'images pour les exercices existants"""
    print("\nTest des chemins d'images pour les exercices existants...")
    
    exercises = Exercise.query.all()
    for exercise in exercises:
        print(f"ID: {exercise.id}, Type: {exercise.exercise_type}, Titre: {exercise.title}")
        print(f"  Image path: {exercise.image_path}")
        
        # Vérifier si l'image existe physiquement
        if exercise.image_path:
            if exercise.image_path.startswith('/static/'):
                file_path = os.path.join(app.root_path, exercise.image_path.lstrip('/'))
                print(f"  Chemin physique: {file_path}")
                print(f"  Fichier existe: {os.path.exists(file_path)}")
            else:
                print(f"  Chemin non standard: {exercise.image_path}")
        
        # Vérifier l'image dans le contenu JSON
        try:
            content = json.loads(exercise.content) if exercise.content else {}
            if isinstance(content, dict):
                if 'main_image' in content:
                    print(f"  Image principale dans content: {content['main_image']}")
                    if content['main_image'].startswith('/static/'):
                        file_path = os.path.join(app.root_path, content['main_image'].lstrip('/'))
                        print(f"  Chemin physique: {file_path}")
                        print(f"  Fichier existe: {os.path.exists(file_path)}")
                elif 'image' in content:
                    print(f"  Image dans content: {content['image']}")
                    if content['image'].startswith('/static/'):
                        file_path = os.path.join(app.root_path, content['image'].lstrip('/'))
                        print(f"  Chemin physique: {file_path}")
                        print(f"  Fichier existe: {os.path.exists(file_path)}")
        except Exception as e:
            print(f"  Erreur lors de la lecture du contenu JSON: {e}")
        
        print("---")

def test_upload_folders():
    """Vérifie la structure des dossiers d'upload"""
    print("\nVérification de la structure des dossiers d'upload...")
    
    # Dossiers à vérifier
    folders = [
        'static/uploads',
        'static/uploads/exercises',
        'static/uploads/exercises/image_labeling',
        'static/uploads/legend'
    ]
    
    for folder in folders:
        folder_path = os.path.join(app.root_path, folder)
        exists = os.path.exists(folder_path)
        print(f"Dossier {folder}: {'Existe' if exists else 'N\'existe pas'}")
        
        if exists:
            # Lister les fichiers dans le dossier
            files = os.listdir(folder_path)
            print(f"  Nombre de fichiers: {len(files)}")
            if len(files) > 0:
                print(f"  Exemples de fichiers: {', '.join(files[:5])}")

def test_fix_image_paths_route():
    """Teste la route de correction automatique des chemins d'images"""
    print("\nTest de la route de correction automatique des chemins d'images...")
    
    with app.test_client() as client:
        # Tester la route /fix-all-image-paths
        response = client.get('/fix-all-image-paths')
        print(f"Statut de la réponse: {response.status_code}")
        if response.status_code == 200:
            print("Contenu de la réponse:")
            print(response.data.decode('utf-8')[:500] + "..." if len(response.data) > 500 else response.data.decode('utf-8'))

def main():
    """Fonction principale"""
    with app.app_context():
        print("=== TEST DE L'UPLOAD D'IMAGES SUR LES EXERCICES LEGEND ET IMAGE LABELING ===\n")
        
        # Vérifier la structure des dossiers d'upload
        test_upload_folders()
        
        # Tester les chemins d'images pour les exercices existants
        test_image_paths()
        
        # Créer un exercice de type Legend si nécessaire
        legend_exercise_id = create_legend_exercise()
        
        # Tester la route de correction automatique des chemins d'images
        test_fix_image_paths_route()
        
        print("\n=== TEST TERMINÉ ===")
        print(f"Pour tester l'upload d'image sur l'exercice d'Image Labeling, accédez à: http://127.0.0.1:5000/exercise/10/edit")
        if legend_exercise_id:
            print(f"Pour tester l'upload d'image sur l'exercice Legend, accédez à: http://127.0.0.1:5000/exercise/edit_exercise/{legend_exercise_id}")

if __name__ == "__main__":
    main()
