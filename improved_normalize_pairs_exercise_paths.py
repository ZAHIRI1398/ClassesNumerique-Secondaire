"""
Module amélioré pour normaliser les chemins d'images dans les exercices de paires
Cette version corrige les problèmes d'affichage des images dans les exercices de paires
"""

import os
import json
import logging
from flask import current_app

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def normalize_pairs_exercise_content(content):
    """
    Normalise les chemins d'images dans un exercice de paires pour assurer la cohérence
    et l'affichage correct des images
    
    Args:
        content (dict): Le contenu JSON de l'exercice
        
    Returns:
        dict: Le contenu normalisé
    """
    if not isinstance(content, dict):
        return content
    
    # Fonction utilitaire pour normaliser un chemin d'image
    def normalize_path(path):
        if not path or not isinstance(path, str):
            return path
        return normalize_image_path(path)
        
    # Normaliser les chemins dans les paires
    if 'pairs' in content and isinstance(content['pairs'], list):
        for pair in content['pairs']:
            # Normaliser l'élément gauche s'il s'agit d'une image
            if 'left' in pair and isinstance(pair['left'], dict) and pair['left'].get('type') == 'image':
                pair['left']['content'] = normalize_image_path(pair['left']['content'])
            
            # Normaliser l'élément droit s'il s'agit d'une image
            if 'right' in pair and isinstance(pair['right'], dict) and pair['right'].get('type') == 'image':
                pair['right']['content'] = normalize_image_path(pair['right']['content'])
    
    # Normaliser les chemins dans les éléments gauches et droits (format utilisé dans le template)
    for item_list in ['left_items', 'right_items', 'shuffled_right_items']:
        if item_list in content and isinstance(content[item_list], list):
            for i, item in enumerate(content[item_list]):
                # Si l'élément est un dictionnaire avec type='image'
                if isinstance(item, dict) and item.get('type') == 'image':
                    item['content'] = normalize_image_path(item['content'])
                # Si l'élément est une chaîne et semble être un chemin d'image
                elif isinstance(item, str) and (
                    item.startswith('/static/') or 
                    item.startswith('static/') or
                    any(item.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif'])
                ):
                    # Convertir en format objet
                    content[item_list][i] = {
                        'type': 'image',
                        'content': normalize_image_path(item)
                    }
    
    # Normaliser l'image principale si elle existe
    if 'image' in content and isinstance(content['image'], str):
        content['image'] = normalize_image_path(content['image'])
    
    return content

def normalize_image_path(path, check_existence=True):
    """
    Normalise un chemin d'image pour assurer la cohérence
    
    Args:
        path (str): Chemin d'image à normaliser
        check_existence (bool): Vérifier si le fichier existe
        
    Returns:
        str: Chemin normalisé
    """
    if not path or not isinstance(path, str):
        return path
        
    # Cas 1: URL externe (http://, https://, etc.)
    if path.startswith(('http://', 'https://', 'data:')):
        return path
        
    # Cas 2: Chemin absolu avec /static/
    if path.startswith('/static/'):
        # Déjà normalisé, conserver la structure de répertoires existante
        return path
        
    # Cas 3: Chemin relatif commençant par static/
    if path.startswith('static/'):
        return '/' + path
        
    # Cas 4: Chemin avec sous-répertoire spécifique (comme general/)
    if '/' in path and not path.startswith('/'):
        # Vérifier si c'est un chemin d'image avec sous-répertoire
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        is_image = any(path.lower().endswith(ext) for ext in image_extensions)
        
        if is_image:
            # Conserver la structure de sous-répertoire
            return f'/static/{path}'
    
    # Cas 5: Chemin relatif sans préfixe ni sous-répertoire
    # Vérifier si c'est un chemin d'image (extensions communes)
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    is_image = any(path.lower().endswith(ext) for ext in image_extensions)
    
    if is_image:
        # Ajouter le préfixe /static/uploads/ par défaut
        return f'/static/uploads/{path}'
    
    # Cas par défaut: retourner le chemin tel quel
    return path

def check_image_path_validity(path):
    """
    Vérifie si un chemin d'image est valide (existe et n'est pas vide)
    
    Args:
        path (str): Chemin d'image à vérifier
        
    Returns:
        bool: True si le chemin est valide, False sinon
    """
    if not path or not isinstance(path, str):
        return False
        
    # Cas 1: URL externe
    if path.startswith(('http://', 'https://', 'data:')):
        # On ne peut pas vérifier facilement, on suppose que c'est valide
        return True
        
    try:
        # Convertir le chemin relatif en chemin absolu
        if path.startswith('/static/'):
            # Enlever le préfixe /static/
            relative_path = path[8:]
            # Construire le chemin absolu
            absolute_path = os.path.join(current_app.static_folder, relative_path)
        else:
            # Chemin déjà absolu ou relatif au répertoire courant
            absolute_path = path
            
        # Vérifier si le fichier existe et n'est pas vide
        if os.path.exists(absolute_path) and os.path.getsize(absolute_path) > 0:
            return True
        else:
            # Essayer des chemins alternatifs si le fichier n'existe pas
            # Par exemple, si le chemin est /static/uploads/general/image.png mais que le fichier est en réalité dans /static/uploads/image.png
            if path.startswith('/static/'):
                # Extraire le nom du fichier sans le chemin
                filename = os.path.basename(path)
                alternative_paths = [
                    os.path.join(current_app.static_folder, 'uploads', filename),
                    os.path.join(current_app.static_folder, 'exercises', filename),
                    os.path.join(current_app.static_folder, filename)
                ]
                
                for alt_path in alternative_paths:
                    if os.path.exists(alt_path) and os.path.getsize(alt_path) > 0:
                        print(f"Image trouvée dans un chemin alternatif: {alt_path} (original: {path})")
                        return True
            
            print(f"Image invalide ou vide: {path} (chemin absolu: {absolute_path})")
            return False
    except Exception as e:
        print(f"Erreur lors de la vérification du chemin d'image {path}: {str(e)}")
        return False

def check_image_paths(content):
    """
    Vérifie si les chemins d'images dans le contenu sont valides
    
    Args:
        content (dict): Le contenu JSON de l'exercice
        
    Returns:
        dict: Rapport sur les chemins d'images
    """
    report = {
        'total_images': 0,
        'valid_paths': 0,
        'invalid_paths': 0,
        'details': []
    }
    
    if not isinstance(content, dict):
        return report
    
    # Vérifier les chemins dans les paires
    if 'pairs' in content and isinstance(content['pairs'], list):
        for pair in content['pairs']:
            # Vérifier l'élément gauche s'il s'agit d'une image
            if 'left' in pair and isinstance(pair['left'], dict) and pair['left'].get('type') == 'image':
                path = pair['left'].get('content')
                report['total_images'] += 1
                is_valid = check_image_path_validity(path)
                if is_valid:
                    report['valid_paths'] += 1
                else:
                    report['invalid_paths'] += 1
                report['details'].append({
                    'path': path,
                    'valid': is_valid,
                    'location': 'pair.left'
                })
            
            # Vérifier l'élément droit s'il s'agit d'une image
            if 'right' in pair and isinstance(pair['right'], dict) and pair['right'].get('type') == 'image':
                path = pair['right'].get('content')
                report['total_images'] += 1
                is_valid = check_image_path_validity(path)
                if is_valid:
                    report['valid_paths'] += 1
                else:
                    report['invalid_paths'] += 1
                report['details'].append({
                    'path': path,
                    'valid': is_valid,
                    'location': 'pair.right'
                })
    
    # Vérifier les chemins dans les éléments gauches et droits
    for item_list_name in ['left_items', 'right_items', 'shuffled_right_items']:
        if item_list_name in content and isinstance(content[item_list_name], list):
            for i, item in enumerate(content[item_list_name]):
                if isinstance(item, dict) and item.get('type') == 'image':
                    path = item.get('content')
                    report['total_images'] += 1
                    is_valid = check_image_path_validity(path)
                    if is_valid:
                        report['valid_paths'] += 1
                    else:
                        report['invalid_paths'] += 1
                    report['details'].append({
                        'path': path,
                        'valid': is_valid,
                        'location': f'{item_list_name}[{i}]'
                    })
    
    return report

# Test de la fonction
if __name__ == "__main__":
    # Exemple de contenu d'exercice
    test_content = {
        "pairs": [
            {
                "id": "1",
                "left": {
                    "content": "/static/exercises/test_image.png",
                    "type": "image"
                },
                "right": {
                    "content": "Texte test",
                    "type": "text"
                }
            },
            {
                "id": "2",
                "left": {
                    "content": "Autre texte",
                    "type": "text"
                },
                "right": {
                    "content": "uploads/image2.jpg",
                    "type": "image"
                }
            }
        ],
        "left_items": [
            {
                "content": "/static/exercises/test_image.png",
                "type": "image"
            },
            {
                "content": "Autre texte",
                "type": "text"
            }
        ],
        "right_items": [
            {
                "content": "Texte test",
                "type": "text"
            },
            {
                "content": "uploads/image2.jpg",
                "type": "image"
            }
        ]
    }
    
    # Normaliser le contenu
    normalized_content = normalize_pairs_exercise_content(test_content)
    
    # Afficher le résultat
    print(json.dumps(normalized_content, indent=2))
