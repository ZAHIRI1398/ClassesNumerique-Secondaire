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
                        # Extraire les chemins d'images des paires
                        if 'pairs' in content:
                            for pair in content['pairs']:
                                if 'image1' in pair and pair['image1']:
                                    image_paths['pairs'].append(pair['image1'])
                                if 'image2' in pair and pair['image2']:
                                    image_paths['pairs'].append(pair['image2'])
                    
                    elif exercise_type == 'qcm' or exercise_type == 'qcm_multichoix':
                        # Extraire les chemins d'images des questions et réponses
                        if 'questions' in content:
                            for question in content['questions']:
                                if 'image' in question and question['image']:
                                    image_paths[exercise_type].append(question['image'])
                    
                    elif exercise_type == 'image_labeling':
                        # Extraire l'image principale
                        if 'image' in content and content['image']:
                            image_paths['image_labeling'].append(content['image'])
                    
                    # Ajouter d'autres types d'exercices selon les besoins
                    
                except Exception as e:
                    print(f"[ERREUR] Impossible de parser le contenu JSON de l'exercice {exercise.id}: {str(e)}")
    
    # Nettoyer les chemins d'images (enlever les doublons et les valeurs None)
    for exercise_type in image_paths:
        # Filtrer les valeurs None
        image_paths[exercise_type] = [path for path in image_paths[exercise_type] if path is not None]
        # Enlever les doublons tout en préservant l'ordre
        image_paths[exercise_type] = list(dict.fromkeys(image_paths[exercise_type]))
    
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
            
            # Chemin cible dans le répertoire organisé
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
                        # Mettre à jour les chemins d'images des paires
                        if 'pairs' in content:
                            for pair in content['pairs']:
                                if 'image1' in pair and pair['image1'] in updated_paths:
                                    pair['image1'] = updated_paths[pair['image1']]
                                    content_updated = True
                                if 'image2' in pair and pair['image2'] in updated_paths:
                                    pair['image2'] = updated_paths[pair['image2']]
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
                    
                    # Ajouter d'autres types d'exercices selon les besoins
                    
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

def organize_image_files(image_paths):
    """
    Organise les fichiers d'images dans les répertoires appropriés
    
    Args:
        image_paths (dict): Dictionnaire des chemins d'images par type d'exercice
        
    Returns:
        dict: Statistiques sur les fichiers organisés
    """
    stats = {
        'total_paths': 0,
        'organized_files': 0,
        'missing_files': 0,
        'already_organized': 0
    }
    
    # Compter le nombre total de chemins
    for paths in image_paths.values():
        stats['total_paths'] += len(paths)
    
    with app.app_context():
        static_folder = current_app.static_folder
        
        # Traiter chaque type d'exercice
        for exercise_type, paths in image_paths.items():
            target_dir = os.path.join(static_folder, 'uploads', exercise_type)
            
            # S'assurer que le répertoire cible existe
            os.makedirs(target_dir, exist_ok=True)
            
            for path in paths:
                # Ignorer les URLs externes
                if path.startswith(('http://', 'https://', 'data:')):
                    continue
                
                # Normaliser le chemin
                if path.startswith('/static/'):
                    relative_path = path[8:]  # Enlever le préfixe /static/
                    source_path = os.path.join(static_folder, '..', relative_path)
                else:
                    # Chemin relatif ou absolu
                    source_path = path
                
                # Extraire le nom du fichier
                filename = os.path.basename(path)
                
                # Chemin cible dans le répertoire organisé
                target_path = os.path.join(target_dir, filename)
                
                # Vérifier si le fichier source existe
                if os.path.exists(source_path) and os.path.isfile(source_path):
                    # Vérifier si le fichier est déjà au bon endroit
                    if os.path.normpath(source_path) == os.path.normpath(target_path):
                        stats['already_organized'] += 1
                        continue
                    
                    # Copier le fichier vers le répertoire cible
                    try:
                        shutil.copy2(source_path, target_path)
                        print(f"[INFO] Fichier copié: {source_path} -> {target_path}")
                        stats['organized_files'] += 1
                    except Exception as e:
                        print(f"[ERREUR] Impossible de copier le fichier {source_path}: {str(e)}")
                else:
                    print(f"[AVERTISSEMENT] Fichier introuvable: {source_path}")
                    stats['missing_files'] += 1
    
    return stats

def update_exercise_image_paths():
    """
    Met à jour les chemins d'images dans les exercices pour utiliser la nouvelle structure de répertoires
    
    Returns:
        int: Nombre d'exercices mis à jour
    """
    updated_count = 0
    
    with app.app_context():
        # Récupérer tous les exercices
        exercises = Exercise.query.all()
        
        for exercise in exercises:
            modified = False
            
            # Mettre à jour le chemin d'image principal
            if exercise.image_path:
                old_path = exercise.image_path
                filename = os.path.basename(old_path)
                new_path = f'/static/uploads/{exercise.exercise_type}/{filename}'
                
                if old_path != new_path:
                    exercise.image_path = new_path
                    modified = True
            
            # Mettre à jour les chemins d'images dans le contenu JSON
            if exercise.content:
                try:
                    content = json.loads(exercise.content)
                    content_modified = False
                    
                    # Traitement spécifique selon le type d'exercice
                    if exercise.exercise_type == 'pairs':
                        # Mettre à jour les chemins d'images des paires
                        if 'pairs' in content and isinstance(content['pairs'], list):
                            for pair in content['pairs']:
                                # Élément gauche
                                if 'left' in pair and isinstance(pair['left'], dict) and pair['left'].get('type') == 'image':
                                    path = pair['left'].get('content')
                                    if path and isinstance(path, str) and not path.startswith(('http://', 'https://', 'data:')):
                                        filename = os.path.basename(path)
                                        new_path = f'/static/uploads/pairs/{filename}'
                                        if path != new_path:
                                            pair['left']['content'] = new_path
                                            content_modified = True
                                
                                # Élément droit
                                if 'right' in pair and isinstance(pair['right'], dict) and pair['right'].get('type') == 'image':
                                    path = pair['right'].get('content')
                                    if path and isinstance(path, str) and not path.startswith(('http://', 'https://', 'data:')):
                                        filename = os.path.basename(path)
                                        new_path = f'/static/uploads/pairs/{filename}'
                                        if path != new_path:
                                            pair['right']['content'] = new_path
                                            content_modified = True
                    
                    # Mettre à jour l'image principale du contenu
                    if 'image' in content and isinstance(content['image'], str):
                        path = content['image']
                        if not path.startswith(('http://', 'https://', 'data:')):
                            filename = os.path.basename(path)
                            new_path = f'/static/uploads/{exercise.exercise_type}/{filename}'
                            if path != new_path:
                                content['image'] = new_path
                                content_modified = True
                    
                    # Sauvegarder le contenu modifié
                    if content_modified:
                        exercise.content = json.dumps(content)
                        modified = True
                    
                except Exception as e:
                    print(f"[ERREUR] Impossible de mettre à jour le contenu de l'exercice {exercise.id}: {str(e)}")
            
            # Sauvegarder l'exercice si modifié
            if modified:
                try:
                    db.session.commit()
                    updated_count += 1
                    print(f"[INFO] Exercice {exercise.id} mis à jour")
                except Exception as e:
                    db.session.rollback()
                    print(f"[ERREUR] Impossible de sauvegarder l'exercice {exercise.id}: {str(e)}")
    
    return updated_count

def main():
    """Fonction principale"""
    try:
        print("\n=== ORGANISATION DES RÉPERTOIRES STATIC ===")
        
        # 1. Créer les répertoires nécessaires
        print("\n1. Création des répertoires...")
        created_dirs = ensure_static_directories()
        
        # 2. Extraire les chemins d'images des exercices
        print("\n2. Extraction des chemins d'images...")
        image_paths = extract_image_paths_from_exercises()
        
        # 3. Organiser les fichiers d'images
        print("\n3. Organisation des fichiers d'images...")
        stats = organize_image_files(image_paths)
        
        # 4. Mettre à jour les chemins d'images dans les exercices
        print("\n4. Mise à jour des chemins d'images dans les exercices...")
        updated_count = update_exercise_image_paths()
        
        # Afficher le résumé
        print("\n=== RÉSUMÉ ===")
        print(f"Répertoires créés: {len(created_dirs)}")
        print(f"Chemins d'images trouvés: {stats['total_paths']}")
        print(f"Fichiers organisés: {stats['organized_files']}")
        print(f"Fichiers déjà organisés: {stats['already_organized']}")
        print(f"Fichiers manquants: {stats['missing_files']}")
        print(f"Exercices mis à jour: {updated_count}")
        
        print("\nOrganisation des répertoires static terminée avec succès!")
        
    except Exception as e:
        print(f"\n[ERREUR] Une erreur est survenue: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
