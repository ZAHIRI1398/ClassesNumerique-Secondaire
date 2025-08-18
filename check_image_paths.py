"""
Script pour vérifier les chemins d'images dans la base de données
"""

import os
import sys
from flask import Flask
from models import db, Exercise
from config import config

def check_image_paths():
    """Vérifie les chemins d'images dans la base de données"""
    # Créer une application Flask minimale
    app = Flask(__name__)
    app.config.from_object(config['development'])
    db.init_app(app)
    
    with app.app_context():
        # Compter les exercices avec des images
        total_with_images = Exercise.query.filter(Exercise.image_path.isnot(None)).count()
        print(f"Nombre total d'exercices avec image: {total_with_images}")
        
        # Récupérer quelques exemples
        exercises = Exercise.query.filter(Exercise.image_path.isnot(None)).limit(10).all()
        
        if not exercises:
            print("Aucun exercice avec image trouvé dans la base de données.")
            return
        
        print("\nExemples de chemins d'images:")
        for ex in exercises:
            print(f"ID: {ex.id}, Titre: {ex.title[:30]}..., Image: {ex.image_path}")
        
        # Analyser les chemins d'images
        local_paths = []
        cloudinary_paths = []
        other_paths = []
        
        all_exercises = Exercise.query.filter(Exercise.image_path.isnot(None)).all()
        for ex in all_exercises:
            if not ex.image_path:
                continue
                
            if 'cloudinary.com' in ex.image_path:
                cloudinary_paths.append(ex.image_path)
            elif ex.image_path.startswith('http'):
                other_paths.append(ex.image_path)
            else:
                local_paths.append(ex.image_path)
        
        print(f"\nAnalyse des {len(all_exercises)} chemins d'images:")
        print(f"- Images Cloudinary: {len(cloudinary_paths)}")
        print(f"- Images externes (non-Cloudinary): {len(other_paths)}")
        print(f"- Images locales: {len(local_paths)}")
        
        if local_paths:
            print("\nExemples de chemins d'images locales:")
            for path in local_paths[:5]:
                print(f"- {path}")
            
            # Vérifier si les fichiers existent
            static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
            print(f"\nVérification des fichiers dans {static_folder}:")
            
            for path in local_paths[:5]:
                # Extraire le nom du fichier
                filename = path.split('/')[-1]
                full_path = os.path.join(static_folder, 'uploads', filename)
                exists = os.path.isfile(full_path)
                print(f"- {filename}: {'Existe' if exists else 'Manquant'} ({full_path})")

if __name__ == "__main__":
    check_image_paths()
