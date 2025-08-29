"""
Script pour organiser les répertoires static et assurer la cohérence des chemins d'images
Ce script crée la structure de répertoires nécessaire, vérifie l'existence des fichiers,
nettoie les fichiers vides et organise les fichiers PDF
"""

import os
import sys
import shutil
import json
import pathlib
import sqlite3
from datetime import datetime
from flask import Flask, current_app
from models import db, Exercise

# Configuration de l'application Flask
app = Flask(__name__)

# Fonction pour trouver dynamiquement le chemin de la base de données
def find_database_path():
    # Vérifier d'abord dans le répertoire instance
    instance_db_path = os.path.abspath('instance/app.db')
    root_db_path = os.path.abspath('app.db')
    
    if os.path.exists(instance_db_path):
        print(f"[INFO] Base de données trouvée à {instance_db_path}")
        return f'sqlite:///{instance_db_path}'
    elif os.path.exists(root_db_path):
        print(f"[INFO] Base de données trouvée à {root_db_path}")
        return f'sqlite:///{root_db_path}'
    else:
        # Recherche récursive
        for db_file in pathlib.Path('.').glob('**/app.db'):
            db_path = os.path.abspath(db_file)
            print(f"[INFO] Base de données trouvée à {db_path}")
            return f'sqlite:///{db_path}'
    
    print("[ERREUR] Aucune base de données trouvée")
    return None

# Configurer la base de données
db_uri = find_database_path()
if not db_uri:
    print("Impossible de trouver la base de données. Vérifiez qu'elle existe.")
    sys.exit(1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Fonction pour créer une sauvegarde de la base de données
def backup_database():
    # Extraire le chemin de fichier de l'URI SQLAlchemy
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    
    # Vérifier si le fichier existe
    if not os.path.exists(db_path):
        print(f"[ERREUR] Le fichier de base de données n'existe pas: {db_path}")
        return None
    
    # Créer le nom du fichier de sauvegarde avec timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"app_backup_{timestamp}.db"
    backup_path = os.path.join(os.path.dirname(db_path), backup_filename)
    
    try:
        # Copier le fichier
        shutil.copy2(db_path, backup_path)
        print(f"[INFO] Sauvegarde créée : {backup_path}")
        return backup_path
    except Exception as e:
        print(f"[ERREUR] Impossible de créer une sauvegarde : {str(e)}")
        return None

def ensure_static_directories():
    """
    S'assure que tous les répertoires nécessaires existent dans le dossier static
    """
    # Liste des répertoires à créer
    directories = [
        # Répertoires principaux
        'static/uploads',
        'static/exercises',
        
        # Répertoires par type d'exercice
        'static/uploads/pairs',
        'static/uploads/qcm',
        'static/uploads/qcm_multichoix',
        'static/uploads/fill_in_blanks',
        'static/uploads/word_placement',
        'static/uploads/image_labeling',
        'static/uploads/legend',
        'static/uploads/drag_and_drop',
        'static/uploads/drag_drop',
        'static/uploads/underline_words',
        'static/uploads/flashcards',
        
        # Répertoires spéciaux
        'static/uploads/general',
        'static/uploads/audio',
        'static/uploads/pdf',  # Nouveau répertoire pour les fichiers PDF
        
        # Répertoires legacy pour compatibilité
        'static/exercises/pairs',
        'static/exercises/qcm',
        'static/exercises/fill_in_blanks',
        'static/exercises/word_placement',
        'static/exercises/image_labeling',
        'static/exercises/legend'
    ]
    
    created_dirs = []
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            created_dirs.append(directory)
            print(f"[INFO] Répertoire créé: {directory}")
        else:
            print(f"[INFO] Répertoire existant: {directory}")
    
    return created_dirs

def clean_empty_files():
    """
    Nettoie les fichiers vides et les fichiers .empty dans le répertoire static
    """
    empty_files_removed = 0
    empty_extensions_removed = 0
    
    # Parcourir tous les fichiers dans static et ses sous-répertoires
    for root, dirs, files in os.walk('static'):
        for file in files:
            file_path = os.path.join(root, file)
            
            # Vérifier si le fichier est vide
            if os.path.getsize(file_path) == 0:
                print(f"[INFO] Suppression du fichier vide: {file_path}")
                os.remove(file_path)
                empty_files_removed += 1
                continue
                
            # Vérifier si le fichier a l'extension .empty
            if file.endswith('.empty'):
                print(f"[INFO] Suppression du fichier .empty: {file_path}")
                os.remove(file_path)
                empty_extensions_removed += 1
    
    print(f"[INFO] Total des fichiers vides supprimés: {empty_files_removed}")
    print(f"[INFO] Total des fichiers .empty supprimés: {empty_extensions_removed}")
    
    return empty_files_removed + empty_extensions_removed

def organize_pdf_files():
    """
    Déplace tous les fichiers PDF dans le répertoire static/uploads/pdf
    """
    pdf_files_moved = 0
    pdf_dir = 'static/uploads/pdf'
    
    # S'assurer que le répertoire PDF existe
    os.makedirs(pdf_dir, exist_ok=True)
    
    # Parcourir tous les fichiers dans static et ses sous-répertoires
    for root, dirs, files in os.walk('static'):
        # Ignorer le répertoire pdf lui-même
        if root == pdf_dir:
            continue
            
        for file in files:
            if file.lower().endswith('.pdf'):
                source_path = os.path.join(root, file)
                target_path = os.path.join(pdf_dir, file)
                
                # Vérifier si le fichier existe déjà dans le répertoire cible
                if os.path.exists(target_path):
                    # Ajouter un timestamp pour éviter les conflits
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename, ext = os.path.splitext(file)
                    target_path = os.path.join(pdf_dir, f"{filename}_{timestamp}{ext}")
                
                try:
                    shutil.move(source_path, target_path)
                    print(f"[INFO] Fichier PDF déplacé: {source_path} -> {target_path}")
                    pdf_files_moved += 1
                except Exception as e:
                    print(f"[ERREUR] Impossible de déplacer {source_path}: {str(e)}")
    
    print(f"[INFO] Total des fichiers PDF organisés: {pdf_files_moved}")
    return pdf_files_moved

def extract_image_paths_from_exercises():
    """
    Extrait tous les chemins d'images des exercices dans la base de données
    
    Returns:
        dict: Dictionnaire des chemins d'images par type d'exercice
    """
    image_paths = {
        'pairs': [],
        'qcm': [],
        'qcm_multichoix': [],
        'fill_in_blanks': [],
        'word_placement': [],
        'image_labeling': [],
        'legend': [],
        'drag_and_drop': [],
        'flashcards': [],
        'underline_words': [],
        'general': []  # Pour les images qui ne correspondent à aucun type spécifique
    }
    
    with app.app_context():
        # Récupérer tous les exercices
        exercises = Exercise.query.all()
        
        for exercise in exercises:
            # Vérifier si l'exercice a un type valide
            exercise_type = exercise.exercise_type
            if exercise_type not in image_paths and exercise_type is not None:
                # Ajouter un nouveau type si nécessaire
                image_paths[exercise_type] = []
            
            # Traiter l'image principale de l'exercice
            if exercise.image_path:
                if exercise_type in image_paths:
                    image_paths[exercise_type].append(exercise.image_path)
                else:
                    image_paths['general'].append(exercise.image_path)
            
            # Traiter les images dans le contenu JSON
            if exercise.content:
                try:
                    content = json.loads(exercise.content)
                    
                    # Traitement spécifique selon le type d'exercice
                    if exercise_type == 'pairs':
                        # Format 1: Paires avec image1/image2
                        if 'pairs' in content:
                            for pair in content['pairs']:
                                if 'image1' in pair and pair['image1']:
                                    image_paths['pairs'].append(pair['image1'])
                                if 'image2' in pair and pair['image2']:
                                    image_paths['pairs'].append(pair['image2'])
                        
                        # Format 2: Paires avec left/right
                        if 'pairs' in content and isinstance(content['pairs'], list):
                            for pair in content['pairs']:
                                # Élément gauche
                                if 'left' in pair and isinstance(pair['left'], dict) and pair['left'].get('type') == 'image':
                                    path = pair['left'].get('content')
                                    if path and isinstance(path, str):
                                        image_paths['pairs'].append(path)
                                
                                # Élément droit
                                if 'right' in pair and isinstance(pair['right'], dict) and pair['right'].get('type') == 'image':
                                    path = pair['right'].get('content')
                                    if path and isinstance(path, str):
                                        image_paths['pairs'].append(path)
                    
                    elif exercise_type in ['qcm', 'qcm_multichoix']:
                        # Extraire les chemins d'images des questions et réponses
                        if 'questions' in content:
                            for question in content['questions']:
                                if 'image' in question and question['image']:
                                    image_paths[exercise_type].append(question['image'])
                    
                    elif exercise_type == 'image_labeling':
                        # Extraire l'image principale
                        if 'image' in content and content['image']:
                            image_paths['image_labeling'].append(content['image'])
                    
                    # Image principale dans le contenu
                    if 'image' in content and isinstance(content['image'], str):
                        if exercise_type in image_paths:
                            image_paths[exercise_type].append(content['image'])
                        else:
                            image_paths['general'].append(content['image'])
                    
                except Exception as e:
                    print(f"[ERREUR] Impossible de parser le contenu JSON de l'exercice {exercise.id}: {str(e)}")
    
    # Nettoyer les chemins d'images (enlever les doublons et les valeurs None)
    for exercise_type in image_paths:
        # Filtrer les valeurs None
        image_paths[exercise_type] = [path for path in image_paths[exercise_type] if path is not None]
        # Enlever les doublons tout en préservant l'ordre
        image_paths[exercise_type] = list(dict.fromkeys(image_paths[exercise_type]))
    
    # Afficher les statistiques
    for exercise_type, paths in image_paths.items():
        print(f"[INFO] {len(paths)} chemins d'images trouvés pour le type '{exercise_type}'")
    
    return image_paths

def organize_images(image_paths):
    """
    Organise les images dans les répertoires appropriés selon leur type d'exercice
    
    Args:
        image_paths (dict): Dictionnaire des chemins d'images par type d'exercice
    
    Returns:
        dict: Dictionnaire des chemins d'images mis à jour
    """
    # Dictionnaire pour stocker les nouveaux chemins d'images
    updated_paths = {}
    images_moved = 0
    images_not_found = 0
    
    # Base du chemin static
    base_path = os.path.abspath('static')
    
    # Traiter chaque type d'exercice
    for exercise_type, paths in image_paths.items():
        for original_path in paths:
            # Ignorer les chemins vides ou None
            if not original_path:
                continue
                
            # Normaliser le chemin (enlever les / au début)
            if original_path.startswith('/'):
                original_path = original_path[1:]
                
            # Construire le chemin complet du fichier source
            source_path = os.path.join(os.getcwd(), original_path)
            
            # Vérifier si le fichier existe
            if not os.path.exists(source_path):
                print(f"[AVERTISSEMENT] Fichier non trouvé: {source_path}")
                images_not_found += 1
                # Conserver le chemin original
                updated_paths[original_path] = original_path
                continue
                
            # Déterminer le nouveau répertoire cible
            if exercise_type == 'drag_and_drop':
                # Gérer le cas spécial de drag_and_drop qui peut être dans drag_drop
                target_dir = os.path.join('static', 'uploads', 'drag_drop')
            else:
                target_dir = os.path.join('static', 'uploads', exercise_type)
                
            # S'assurer que le répertoire cible existe
            os.makedirs(target_dir, exist_ok=True)
            
            # Extraire le nom du fichier
            filename = os.path.basename(source_path)
            
            # Construire le chemin cible
            target_path = os.path.join(target_dir, filename)
            
            # Vérifier si le fichier existe déjà dans le répertoire cible
            if os.path.exists(target_path) and os.path.samefile(source_path, target_path):
                # Le fichier est déjà au bon endroit
                print(f"[INFO] Fichier déjà au bon endroit: {source_path}")
                # Mettre à jour le chemin dans le dictionnaire
                new_path = f"/static/uploads/{exercise_type}/{filename}"
                updated_paths[original_path] = new_path
                continue
                
            # Si le fichier existe déjà à la destination mais n'est pas le même
            if os.path.exists(target_path):
                # Ajouter un timestamp pour éviter les conflits
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                name, ext = os.path.splitext(filename)
                new_filename = f"{name}_{timestamp}{ext}"
                target_path = os.path.join(target_dir, new_filename)
                new_path = f"/static/uploads/{exercise_type}/{new_filename}"
            else:
                new_path = f"/static/uploads/{exercise_type}/{filename}"
                
            try:
                # Copier le fichier plutôt que de le déplacer pour éviter les problèmes
                shutil.copy2(source_path, target_path)
                print(f"[INFO] Fichier copié: {source_path} -> {target_path}")
                images_moved += 1
                # Mettre à jour le chemin dans le dictionnaire
                updated_paths[original_path] = new_path
            except Exception as e:
                print(f"[ERREUR] Impossible de copier {source_path}: {str(e)}")
                # Conserver le chemin original en cas d'erreur
                updated_paths[original_path] = original_path
    
    print(f"[INFO] Total des images organisées: {images_moved}")
    print(f"[INFO] Total des images non trouvées: {images_not_found}")
    
    return updated_paths

def update_database_paths(updated_paths):
    """
    Met à jour les chemins d'images dans la base de données
    
    Args:
        updated_paths (dict): Dictionnaire des chemins d'images mis à jour
    
    Returns:
        int: Nombre d'exercices mis à jour
    """
    exercises_updated = 0
    
    with app.app_context():
        # Récupérer tous les exercices
        exercises = Exercise.query.all()
        
        print(f"[INFO] Mise à jour des chemins d'images pour {len(exercises)} exercices...")
        
        for exercise in exercises:
            updated = False
            
            # Mettre à jour l'image principale de l'exercice
            if exercise.image_path and exercise.image_path in updated_paths:
                exercise.image_path = updated_paths[exercise.image_path]
                updated = True
            
            # Mettre à jour les images dans le contenu JSON
            if exercise.content:
                try:
                    content = json.loads(exercise.content)
                    content_updated = False
                    
                    # Traitement spécifique selon le type d'exercice
                    if exercise.exercise_type == 'pairs':
                        # Format 1: Paires avec image1/image2
                        if 'pairs' in content:
                            for pair in content['pairs']:
                                if 'image1' in pair and pair['image1'] in updated_paths:
                                    pair['image1'] = updated_paths[pair['image1']]
                                    content_updated = True
                                if 'image2' in pair and pair['image2'] in updated_paths:
                                    pair['image2'] = updated_paths[pair['image2']]
                                    content_updated = True
                        
                        # Format 2: Paires avec left/right
                        if 'pairs' in content and isinstance(content['pairs'], list):
                            for pair in content['pairs']:
                                # Élément gauche
                                if 'left' in pair and isinstance(pair['left'], dict) and pair['left'].get('type') == 'image':
                                    path = pair['left'].get('content')
                                    if path and isinstance(path, str) and path in updated_paths:
                                        pair['left']['content'] = updated_paths[path]
                                        content_updated = True
                                
                                # Élément droit
                                if 'right' in pair and isinstance(pair['right'], dict) and pair['right'].get('type') == 'image':
                                    path = pair['right'].get('content')
                                    if path and isinstance(path, str) and path in updated_paths:
                                        pair['right']['content'] = updated_paths[path]
                                        content_updated = True
                    
                    elif exercise.exercise_type in ['qcm', 'qcm_multichoix']:
                        # Mettre à jour les chemins d'images des questions
                        if 'questions' in content:
                            for question in content['questions']:
                                if 'image' in question and question['image'] in updated_paths:
                                    question['image'] = updated_paths[question['image']]
                                    content_updated = True
                    
                    elif exercise.exercise_type == 'image_labeling':
                        # Mettre à jour l'image principale
                        if 'image' in content and content['image'] in updated_paths:
                            content['image'] = updated_paths[content['image']]
                            content_updated = True
                    
                    # Mettre à jour l'image principale du contenu
                    if 'image' in content and isinstance(content['image'], str) and content['image'] in updated_paths:
                        content['image'] = updated_paths[content['image']]
                        content_updated = True
                    
                    # Sauvegarder le contenu mis à jour
                    if content_updated:
                        exercise.content = json.dumps(content)
                        updated = True
                        
                except Exception as e:
                    print(f"[ERREUR] Impossible de mettre à jour le contenu JSON de l'exercice {exercise.id}: {str(e)}")
            
            # Compter les exercices mis à jour
            if updated:
                exercises_updated += 1
        
        # Sauvegarder les modifications dans la base de données
        if exercises_updated > 0:
            try:
                db.session.commit()
                print(f"[INFO] {exercises_updated} exercices mis à jour dans la base de données")
            except Exception as e:
                db.session.rollback()
                print(f"[ERREUR] Impossible de sauvegarder les modifications: {str(e)}")
    
    return exercises_updated

def main():
    """Fonction principale"""
    try:
        print("\n=== ORGANISATION DES RÉPERTOIRES STATIC ===")
        
        # 0. Créer une sauvegarde de la base de données
        print("\n0. Création d'une sauvegarde de la base de données...")
        backup_path = backup_database()
        if not backup_path:
            print("[AVERTISSEMENT] Impossible de créer une sauvegarde. Voulez-vous continuer ? (y/n)")
            response = input().lower()
            if response != 'y':
                print("Opération annulée.")
                return
        
        # 1. Créer les répertoires nécessaires
        print("\n1. Création des répertoires...")
        created_dirs = ensure_static_directories()
        
        # 2. Nettoyer les fichiers vides et .empty
        print("\n2. Nettoyage des fichiers vides et .empty...")
        cleaned_files = clean_empty_files()
        
        # 3. Organiser les fichiers PDF
        print("\n3. Organisation des fichiers PDF...")
        pdf_files = organize_pdf_files()
        
        # 4. Extraire les chemins d'images des exercices
        print("\n4. Extraction des chemins d'images...")
        image_paths = extract_image_paths_from_exercises()
        
        # 5. Organiser les fichiers d'images
        print("\n5. Organisation des fichiers d'images...")
        updated_paths = organize_images(image_paths)
        
        # 6. Mettre à jour les chemins d'images dans la base de données
        print("\n6. Mise à jour des chemins d'images dans la base de données...")
        updated_count = update_database_paths(updated_paths)
        
        # Afficher le résumé
        print("\n=== RÉSUMÉ ===")
        print(f"Sauvegarde de la base de données: {backup_path}")
        print(f"Répertoires créés: {len(created_dirs)}")
        print(f"Fichiers vides et .empty supprimés: {cleaned_files}")
        print(f"Fichiers PDF organisés: {pdf_files}")
        print(f"Exercices mis à jour: {updated_count}")
        
        print("\nOrganisation des répertoires static terminée avec succès!")
        
    except Exception as e:
        print(f"\n[ERREUR] Une erreur est survenue: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
