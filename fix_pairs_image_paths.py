"""
Script de correction pour les chemins d'images dans les exercices de paires
Ce script assure la cohérence entre les chemins physiques et les chemins référencés dans la base de données
"""

import os
import json
import sys
from flask import Flask
from models import db, Exercise
from normalize_pairs_exercise_paths import normalize_pairs_exercise_content

# Configuration de l'application Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def check_file_exists(path):
    """Vérifie si un fichier existe physiquement"""
    if not path or not isinstance(path, str):
        return False
        
    if path.startswith('/'):
        path = path[1:]  # Enlever le / initial
        
    full_path = os.path.join(app.root_path, path)
    exists = os.path.exists(full_path)
    if exists:
        size = os.path.getsize(full_path)
        return size > 0  # Retourne True seulement si le fichier n'est pas vide
    return False

def get_correct_path(path):
    """
    Détermine le chemin correct pour une image en vérifiant son existence
    dans les dossiers uploads et exercises
    """
    if not path or not isinstance(path, str):
        return path
        
    # Vérifier le chemin actuel
    if check_file_exists(path):
        print(f"[PATH_FIX] Le fichier existe avec le chemin actuel: {path}")
        return path
        
    # Vérifier le chemin alternatif
    alt_path = None
    if '/static/uploads/' in path:
        alt_path = path.replace('/static/uploads/', '/static/exercises/')
    elif '/static/exercises/' in path:
        alt_path = path.replace('/static/exercises/', '/static/uploads/')
        
    if alt_path and check_file_exists(alt_path):
        print(f"[PATH_FIX] Le fichier existe avec le chemin alternatif: {alt_path}")
        return alt_path
        
    # Si aucun des deux chemins n'existe, retourner le chemin original
    print(f"[PATH_FIX] Aucun fichier trouvé pour: {path}")
    return path

def fix_pair_image_path(pair_item):
    """
    Corrige le chemin d'image d'un élément de paire
    
    Args:
        pair_item (dict): L'élément de paire (left ou right)
        
    Returns:
        bool: True si des modifications ont été apportées, False sinon
    """
    if not pair_item or not isinstance(pair_item, dict):
        return False
        
    if pair_item.get('type') != 'image' or not pair_item.get('content'):
        return False
        
    old_path = pair_item['content']
    new_path = get_correct_path(old_path)
    
    if new_path != old_path:
        pair_item['content'] = new_path
        return True
        
    return False

def fix_pairs_exercise_content(content):
    """
    Corrige les chemins d'images dans un exercice de paires
    
    Args:
        content (dict): Le contenu JSON de l'exercice
        
    Returns:
        tuple: (content modifié, booléen indiquant si des modifications ont été apportées)
    """
    if not isinstance(content, dict):
        return content, False
        
    modified = False
    
    # Corriger les chemins dans les paires
    if 'pairs' in content and isinstance(content['pairs'], list):
        for pair in content['pairs']:
            # Corriger l'élément gauche s'il s'agit d'une image
            if 'left' in pair and isinstance(pair['left'], dict):
                if fix_pair_image_path(pair['left']):
                    modified = True
            
            # Corriger l'élément droit s'il s'agit d'une image
            if 'right' in pair and isinstance(pair['right'], dict):
                if fix_pair_image_path(pair['right']):
                    modified = True
    
    # Corriger les chemins dans les éléments gauches et droits (ancien format)
    for item_list in ['left_items', 'right_items']:
        if item_list in content and isinstance(content[item_list], list):
            for i, item in enumerate(content[item_list]):
                # Si l'élément est un dictionnaire avec type='image'
                if isinstance(item, dict) and item.get('type') == 'image':
                    if fix_pair_image_path(item):
                        modified = True
    
    return content, modified

def fix_pairs_exercises():
    """Corrige les chemins d'images dans tous les exercices de paires"""
    with app.app_context():
        # Récupérer tous les exercices de type 'pairs'
        pairs_exercises = Exercise.query.filter_by(exercise_type='pairs').all()
        
        print(f"Nombre d'exercices de paires trouvés: {len(pairs_exercises)}")
        
        fixed_count = 0
        
        for exercise in pairs_exercises:
            print(f"\n--- Exercice ID: {exercise.id}, Titre: {exercise.title} ---")
            
            if not exercise.content:
                print("  Pas de contenu JSON")
                continue
                
            try:
                content = json.loads(exercise.content)
                
                # Vérifier si le contenu a des paires
                if 'pairs' not in content or not isinstance(content['pairs'], list):
                    print("  Pas de paires dans le contenu")
                    continue
                    
                print(f"  Nombre de paires: {len(content['pairs'])}")
                
                # Corriger les chemins d'images
                fixed_content, modified = fix_pairs_exercise_content(content)
                
                if modified:
                    # Mettre à jour le contenu dans la base de données
                    exercise.content = json.dumps(fixed_content)
                    db.session.commit()
                    fixed_count += 1
                    print(f"  [OK] Chemins d'images corrigés pour l'exercice {exercise.id}")
                else:
                    print(f"  [INFO] Aucune correction nécessaire pour l'exercice {exercise.id}")
                    
            except Exception as e:
                print(f"  [ERREUR] Erreur lors de la correction de l'exercice {exercise.id}: {str(e)}")
        
        print(f"\nRésumé: {fixed_count}/{len(pairs_exercises)} exercices corrigés")

def main():
    """Fonction principale"""
    try:
        fix_pairs_exercises()
        print("\nCorrection des chemins d'images terminée avec succès!")
    except Exception as e:
        print(f"\nErreur lors de la correction des chemins d'images: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
