"""
Script de diagnostic pour vérifier les chemins d'images dans les exercices de paires
Version directe sans dépendance à la base de données
"""

import os
import json
from normalize_pairs_exercise_paths import normalize_pairs_exercise_content

def check_file_exists(path, root_path):
    """Vérifie si un fichier existe physiquement"""
    if not path:
        return False
        
    if path.startswith('/'):
        path = path[1:]  # Enlever le / initial
        
    full_path = os.path.join(root_path, path)
    exists = os.path.exists(full_path)
    if exists:
        size = os.path.getsize(full_path)
        return size > 0  # Retourne True seulement si le fichier n'est pas vide
    return False

def test_normalize_path(path, root_path):
    """Teste la normalisation d'un chemin d'image"""
    print(f"\nTest de normalisation pour: {path}")
    
    # Vérifier si le fichier existe avec ce chemin
    file_exists = check_file_exists(path, root_path)
    print(f"  -> Fichier existe: {file_exists}")
    
    # Vérifier le chemin alternatif
    alt_path = None
    if '/static/uploads/' in path:
        alt_path = path.replace('/static/uploads/', '/static/exercises/')
    elif '/static/exercises/' in path:
        alt_path = path.replace('/static/exercises/', '/static/uploads/')
        
    if alt_path:
        alt_exists = check_file_exists(alt_path, root_path)
        print(f"  -> Chemin alternatif: {alt_path}")
        print(f"  -> Fichier alternatif existe: {alt_exists}")
    
    # Tester la normalisation avec un contenu factice
    test_content = {
        'pairs': [
            {
                'id': '1',
                'left': {'content': path, 'type': 'image'},
                'right': {'content': 'Test', 'type': 'text'}
            }
        ]
    }
    
    normalized_content = normalize_pairs_exercise_content(test_content)
    
    # Vérifier si la normalisation a changé quelque chose
    if normalized_content != test_content:
        print("  -> La normalisation a modifié le contenu")
        
        # Vérifier les changements dans les paires
        for i, (orig_pair, norm_pair) in enumerate(zip(test_content['pairs'], normalized_content['pairs'])):
            if orig_pair != norm_pair:
                print(f"  -> Paire {i+1} modifiée:")
                
                # Vérifier les changements dans l'élément gauche
                if orig_pair.get('left') != norm_pair.get('left'):
                    print(f"    -> Gauche original: {orig_pair.get('left', {}).get('content')}")
                    print(f"    -> Gauche normalisé: {norm_pair.get('left', {}).get('content')}")
                    
                    # Vérifier si le fichier normalisé existe
                    if norm_pair.get('left', {}).get('type') == 'image':
                        norm_path = norm_pair.get('left', {}).get('content')
                        norm_exists = check_file_exists(norm_path, root_path)
                        print(f"    -> Fichier gauche normalisé existe: {norm_exists}")
    else:
        print("  -> La normalisation n'a pas modifié le contenu")

def main():
    """Fonction principale"""
    # Chemin racine de l'application
    root_path = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Chemin racine: {root_path}")
    
    # Tester différents formats de chemins
    test_paths = [
        '/static/uploads/pairs/pairs_20250828_195002_aebd5e8e.png',
        '/static/exercises/pairs/pairs_20250828_195002_aebd5e8e.png',
        '/static/uploads/general/general_20250828_195002_aebd5e8e.png',
        '/static/exercises/general/general_20250828_195002_aebd5e8e.png'
    ]
    
    for path in test_paths:
        test_normalize_path(path, root_path)
    
    # Vérifier les dossiers d'images
    print("\nVérification des dossiers d'images:")
    
    uploads_dir = os.path.join(root_path, 'static', 'uploads')
    exercises_dir = os.path.join(root_path, 'static', 'exercises')
    
    if os.path.exists(uploads_dir):
        print(f"Dossier uploads existe: {uploads_dir}")
        # Lister les sous-dossiers
        subdirs = [d for d in os.listdir(uploads_dir) if os.path.isdir(os.path.join(uploads_dir, d))]
        print(f"  Sous-dossiers: {subdirs}")
    else:
        print(f"Dossier uploads n'existe pas: {uploads_dir}")
    
    if os.path.exists(exercises_dir):
        print(f"Dossier exercises existe: {exercises_dir}")
        # Lister les sous-dossiers
        subdirs = [d for d in os.listdir(exercises_dir) if os.path.isdir(os.path.join(exercises_dir, d))]
        print(f"  Sous-dossiers: {subdirs}")
    else:
        print(f"Dossier exercises n'existe pas: {exercises_dir}")

if __name__ == "__main__":
    main()
