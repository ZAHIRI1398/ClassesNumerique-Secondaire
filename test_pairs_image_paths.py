"""
Script de diagnostic pour vérifier les chemins d'images dans les exercices de paires
"""

import os
import json
import sys
from flask import Flask, current_app
from models import db, Exercise
from normalize_pairs_exercise_paths import normalize_pairs_exercise_content

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def check_file_exists(path):
    """Vérifie si un fichier existe physiquement"""
    if not path:
        return False
        
    if path.startswith('/'):
        path = path[1:]  # Enlever le / initial
        
    full_path = os.path.join(app.root_path, path)
    exists = os.path.exists(full_path)
    if exists:
        size = os.path.getsize(full_path)
        return size > 0  # Retourne True seulement si le fichier n'est pas vide
    return False

def check_pairs_exercise_images():
    """Vérifie les chemins d'images dans les exercices de paires"""
    with app.app_context():
        # Récupérer tous les exercices de type 'pairs'
        pairs_exercises = Exercise.query.filter_by(exercise_type='pairs').all()
        
        print(f"Nombre d'exercices de paires trouvés: {len(pairs_exercises)}")
        
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
                
                # Vérifier chaque paire
                for i, pair in enumerate(content['pairs']):
                    print(f"\n  Paire {i+1}:")
                    
                    # Vérifier l'élément gauche
                    if 'left' in pair and isinstance(pair['left'], dict):
                        left_type = pair['left'].get('type')
                        left_content = pair['left'].get('content')
                        
                        print(f"    Gauche (type: {left_type}): {left_content}")
                        
                        if left_type == 'image' and left_content:
                            # Vérifier si le fichier existe
                            file_exists = check_file_exists(left_content)
                            print(f"    -> Fichier gauche existe: {file_exists}")
                            
                            # Vérifier le chemin alternatif
                            alt_path = None
                            if '/static/uploads/' in left_content:
                                alt_path = left_content.replace('/static/uploads/', '/static/exercises/')
                            elif '/static/exercises/' in left_content:
                                alt_path = left_content.replace('/static/exercises/', '/static/uploads/')
                                
                            if alt_path:
                                alt_exists = check_file_exists(alt_path)
                                print(f"    -> Chemin alternatif: {alt_path}")
                                print(f"    -> Fichier alternatif existe: {alt_exists}")
                    
                    # Vérifier l'élément droit
                    if 'right' in pair and isinstance(pair['right'], dict):
                        right_type = pair['right'].get('type')
                        right_content = pair['right'].get('content')
                        
                        print(f"    Droite (type: {right_type}): {right_content}")
                        
                        if right_type == 'image' and right_content:
                            # Vérifier si le fichier existe
                            file_exists = check_file_exists(right_content)
                            print(f"    -> Fichier droite existe: {file_exists}")
                            
                            # Vérifier le chemin alternatif
                            alt_path = None
                            if '/static/uploads/' in right_content:
                                alt_path = right_content.replace('/static/uploads/', '/static/exercises/')
                            elif '/static/exercises/' in right_content:
                                alt_path = right_content.replace('/static/exercises/', '/static/uploads/')
                                
                            if alt_path:
                                alt_exists = check_file_exists(alt_path)
                                print(f"    -> Chemin alternatif: {alt_path}")
                                print(f"    -> Fichier alternatif existe: {alt_exists}")
                
                # Tester la normalisation
                print("\n  Test de normalisation:")
                normalized_content = normalize_pairs_exercise_content(content)
                
                # Vérifier si la normalisation a changé quelque chose
                if normalized_content != content:
                    print("  -> La normalisation a modifié le contenu")
                    
                    # Vérifier les changements dans les paires
                    for i, (orig_pair, norm_pair) in enumerate(zip(content['pairs'], normalized_content['pairs'])):
                        if orig_pair != norm_pair:
                            print(f"  -> Paire {i+1} modifiée:")
                            
                            # Vérifier les changements dans l'élément gauche
                            if orig_pair.get('left') != norm_pair.get('left'):
                                print(f"    -> Gauche original: {orig_pair.get('left', {}).get('content')}")
                                print(f"    -> Gauche normalisé: {norm_pair.get('left', {}).get('content')}")
                                
                                # Vérifier si le fichier normalisé existe
                                if norm_pair.get('left', {}).get('type') == 'image':
                                    norm_path = norm_pair.get('left', {}).get('content')
                                    norm_exists = check_file_exists(norm_path)
                                    print(f"    -> Fichier gauche normalisé existe: {norm_exists}")
                            
                            # Vérifier les changements dans l'élément droit
                            if orig_pair.get('right') != norm_pair.get('right'):
                                print(f"    -> Droite original: {orig_pair.get('right', {}).get('content')}")
                                print(f"    -> Droite normalisé: {norm_pair.get('right', {}).get('content')}")
                                
                                # Vérifier si le fichier normalisé existe
                                if norm_pair.get('right', {}).get('type') == 'image':
                                    norm_path = norm_pair.get('right', {}).get('content')
                                    norm_exists = check_file_exists(norm_path)
                                    print(f"    -> Fichier droite normalisé existe: {norm_exists}")
                else:
                    print("  -> La normalisation n'a pas modifié le contenu")
                    
            except Exception as e:
                print(f"  Erreur lors de l'analyse du contenu: {str(e)}")

if __name__ == "__main__":
    check_pairs_exercise_images()
