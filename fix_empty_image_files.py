"""
Script pour corriger les fichiers images vides (0 octet) dans les dossiers d'upload.
Ce script identifie les fichiers vides et les remplace par une image par défaut.
"""

import os
import sys
import shutil
import json
from datetime import datetime
from flask import Flask
from models import Exercise, db

# Créer une application Flask minimale pour le contexte
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Image par défaut à utiliser pour remplacer les fichiers vides
DEFAULT_IMAGE_PATH = 'static/img/default_exercise_image.png'

def create_default_image_if_needed():
    """Crée une image par défaut si elle n'existe pas"""
    if not os.path.exists(DEFAULT_IMAGE_PATH):
        os.makedirs(os.path.dirname(DEFAULT_IMAGE_PATH), exist_ok=True)
        
        # Créer une image par défaut simple avec un message
        try:
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (800, 400), color=(245, 245, 245))
            d = ImageDraw.Draw(img)
            
            # Texte à afficher
            text = "Image temporaire - Veuillez télécharger une nouvelle image"
            
            # Utiliser une police par défaut
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()
                
            # Calculer la position du texte
            text_width, text_height = d.textsize(text, font=font)
            position = ((800 - text_width) // 2, (400 - text_height) // 2)
            
            # Dessiner le texte
            d.text(position, text, fill=(0, 0, 0), font=font)
            
            # Sauvegarder l'image
            img.save(DEFAULT_IMAGE_PATH)
            print(f"Image par défaut créée: {DEFAULT_IMAGE_PATH}")
        except Exception as e:
            print(f"Erreur lors de la création de l'image par défaut: {e}")
            
            # Méthode alternative si PIL n'est pas disponible
            with open(DEFAULT_IMAGE_PATH, 'wb') as f:
                # En-tête minimal pour un fichier PNG
                f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82')
            print(f"Image par défaut minimale créée: {DEFAULT_IMAGE_PATH}")

def scan_upload_directories():
    """Scanne les répertoires d'upload pour trouver les fichiers vides"""
    print("Scan des répertoires d'upload...")
    
    # Répertoires à scanner
    upload_dirs = [
        'static/uploads',
        'static/uploads/exercises',
        'static/uploads/exercises/qcm',
        'static/uploads/exercises/fill_in_blanks',
        'static/uploads/exercises/flashcards',
        'static/uploads/exercises/pairs',
        'static/uploads/exercises/image_labeling',
        'static/uploads/exercises/legend',
        'static/uploads/exercises/word_placement',
        'static/uploads/exercises/drag_and_drop',
        'static/exercises',
        'static/exercises/qcm',
        'static/exercises/fill_in_blanks',
        'static/exercises/flashcards',
        'static/exercises/pairs',
        'static/exercises/image_labeling',
        'static/exercises/legend',
        'static/exercises/word_placement',
        'static/exercises/drag_and_drop'
    ]
    
    empty_files = []
    
    for directory in upload_dirs:
        if not os.path.exists(directory):
            print(f"Répertoire non trouvé, création: {directory}")
            os.makedirs(directory, exist_ok=True)
            continue
            
        print(f"Scan du répertoire: {directory}")
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            
            # Ignorer les répertoires et les fichiers cachés
            if os.path.isdir(filepath) or filename.startswith('.'):
                continue
                
            # Vérifier si le fichier est vide
            if os.path.getsize(filepath) == 0:
                empty_files.append(filepath)
                print(f"Fichier vide trouvé: {filepath}")
    
    return empty_files

def fix_empty_files(empty_files):
    """Remplace les fichiers vides par l'image par défaut"""
    if not empty_files:
        print("Aucun fichier vide trouvé.")
        return
        
    print(f"\nCorrection de {len(empty_files)} fichiers vides...")
    
    # S'assurer que l'image par défaut existe
    create_default_image_if_needed()
    
    if not os.path.exists(DEFAULT_IMAGE_PATH):
        print(f"ERREUR: Image par défaut non trouvée: {DEFAULT_IMAGE_PATH}")
        return
        
    # Remplacer chaque fichier vide
    for filepath in empty_files:
        try:
            # Sauvegarder le fichier vide original avec un suffixe .empty
            empty_backup = f"{filepath}.empty"
            shutil.move(filepath, empty_backup)
            
            # Copier l'image par défaut
            shutil.copy2(DEFAULT_IMAGE_PATH, filepath)
            
            # Vérifier que la copie a réussi
            if os.path.getsize(filepath) > 0:
                print(f"Fichier corrigé: {filepath}")
            else:
                print(f"ERREUR: Échec de la correction pour {filepath}")
                # Restaurer le fichier original
                shutil.move(empty_backup, filepath)
        except Exception as e:
            print(f"ERREUR lors de la correction de {filepath}: {e}")

def update_exercise_database():
    """Met à jour la base de données pour synchroniser les chemins d'images"""
    print("\nMise à jour de la base de données...")
    
    try:
        exercises = Exercise.query.all()
        updated_count = 0
        
        for exercise in exercises:
            # Vérifier si l'image existe et n'est pas vide
            if exercise.image_path:
                # Nettoyer le chemin pour obtenir le chemin physique
                if exercise.image_path.startswith('/static/'):
                    file_path = exercise.image_path[1:]  # Enlever le / initial
                else:
                    file_path = f"static/{exercise.image_path.lstrip('/')}"
                    
                # Vérifier si le fichier existe et n'est pas vide
                if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                    print(f"Problème avec l'image de l'exercice {exercise.id}: {exercise.image_path}")
                    
                    # Mettre à jour le chemin d'image vers l'image par défaut
                    exercise.image_path = f"/{DEFAULT_IMAGE_PATH}"
                    
                    # Mettre à jour le contenu JSON également
                    try:
                        content = json.loads(exercise.content) if exercise.content else {}
                        if isinstance(content, dict):
                            content['image'] = f"/{DEFAULT_IMAGE_PATH}"
                            exercise.content = json.dumps(content)
                    except Exception as e:
                        print(f"Erreur lors de la mise à jour du contenu JSON: {e}")
                    
                    updated_count += 1
        
        # Sauvegarder les modifications
        if updated_count > 0:
            db.session.commit()
            print(f"{updated_count} exercices mis à jour dans la base de données.")
        else:
            print("Aucun exercice n'a nécessité de mise à jour.")
            
    except Exception as e:
        print(f"Erreur lors de la mise à jour de la base de données: {e}")
        db.session.rollback()

def main():
    """Fonction principale"""
    print("=== CORRECTION DES FICHIERS IMAGES VIDES ===")
    print(f"Date et heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Créer l'image par défaut si nécessaire
    create_default_image_if_needed()
    
    # Scanner les répertoires d'upload
    empty_files = scan_upload_directories()
    
    # Corriger les fichiers vides
    fix_empty_files(empty_files)
    
    # Mettre à jour la base de données
    with app.app_context():
        update_exercise_database()
    
    print("\n=== CORRECTION TERMINÉE ===")
    print(f"Nombre de fichiers corrigés: {len(empty_files)}")
    print("Veuillez vérifier les résultats et recharger l'application.")

if __name__ == "__main__":
    main()
