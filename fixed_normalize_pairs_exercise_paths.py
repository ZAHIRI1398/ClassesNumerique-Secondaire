"""
Module amélioré pour normaliser les chemins d'images dans les exercices de paires
Cette version corrige les problèmes d'affichage des images dans les exercices de paires,
y compris le cas spécifique des chemins avec /static/uploads/general/general_
"""

import os
import json
import logging
from flask import current_app

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def normalize_pairs_exercise_content(content, exercise_type='pairs'):
    """
    Normalise les chemins d'images dans un exercice de paires pour assurer la cohérence
    et l'affichage correct des images
    
    Args:
        content (dict): Le contenu JSON de l'exercice
        exercise_type (str): Le type d'exercice (par défaut 'pairs')
        
    Returns:
        dict: Le contenu normalisé
    """
    if not isinstance(content, dict):
        return content
    
    # Normaliser les chemins dans les paires
    if 'pairs' in content and isinstance(content['pairs'], list):
        for pair in content['pairs']:
            # Normaliser l'élément gauche s'il s'agit d'une image
            if 'left' in pair and isinstance(pair['left'], dict) and pair['left'].get('type') == 'image':
                pair['left']['content'] = normalize_image_path(pair['left']['content'], exercise_type=exercise_type)
            
            # Normaliser l'élément droit s'il s'agit d'une image
            if 'right' in pair and isinstance(pair['right'], dict) and pair['right'].get('type') == 'image':
                pair['right']['content'] = normalize_image_path(pair['right']['content'], exercise_type=exercise_type)
    
    # Normaliser les chemins dans les éléments gauches et droits (format utilisé dans le template)
    for item_list in ['left_items', 'right_items', 'shuffled_right_items']:
        if item_list in content and isinstance(content[item_list], list):
            for i, item in enumerate(content[item_list]):
                # Si l'élément est un dictionnaire avec type='image'
                if isinstance(item, dict) and item.get('type') == 'image':
                    item['content'] = normalize_image_path(item['content'], exercise_type=exercise_type)
                # Si l'élément est une chaîne et semble être un chemin d'image
                elif isinstance(item, str) and (
                    item.startswith('/static/') or 
                    item.startswith('static/') or
                    any(item.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif'])
                ):
                    # Convertir en format objet
                    content[item_list][i] = {
                        'type': 'image',
                        'content': normalize_image_path(item, exercise_type=exercise_type)
                    }
    
    # Normaliser l'image principale si elle existe
    if 'image' in content and isinstance(content['image'], str):
        content['image'] = normalize_image_path(content['image'], exercise_type=exercise_type)
    
    return content

def normalize_image_path(path, exercise_type=None):
    """
    Normalise un chemin d'image pour assurer la cohérence
    
    Args:
        path (str): Chemin d'image à normaliser
        exercise_type (str, optional): Le type d'exercice pour organiser les images dans des sous-dossiers
        
    Returns:
        str: Chemin normalisé
    """
    logger.info(f"[IMAGE_PATH_DEBUG] Normalisation du chemin: {path} (type: {exercise_type})")
    if not path or not isinstance(path, str):
        return path
        
    # Cas 1: URL externe (http://, https://, etc.)
    if path.startswith(('http://', 'https://', 'data:')):
        return path
    
    # Normaliser le nom du fichier (remplacer les espaces par des underscores, supprimer les apostrophes)
    path = path.replace(' ', '_').replace("'", '')
    
    # Cas spécifique: /static/uploads/general/general_TIMESTAMP_...
    if '/static/uploads/general/general_' in path:
        logger.info(f"[IMAGE_PATH_DEBUG] Détection du cas spécifique /static/uploads/general/general_")
        # Extraire le nom du fichier
        filename = path.split('/')[-1]
        
        # Si le nom commence par 'general_' et qu'on a un type d'exercice spécifique,
        # remplacer 'general_' par le type d'exercice
        if exercise_type and exercise_type != 'general' and filename.startswith('general_'):
            # Enlever le préfixe 'general_' pour éviter la duplication
            clean_filename = filename[8:]  # Longueur de 'general_'
            normalized_path = f'/static/uploads/{exercise_type}/{exercise_type}_{clean_filename}'
            logger.info(f"[IMAGE_PATH_DEBUG] Chemin normalisé (cas 1): {normalized_path}")
            return normalized_path
        elif exercise_type and exercise_type != 'general':
            # Garder le nom tel quel mais changer le dossier
            normalized_path = f'/static/uploads/{exercise_type}/{filename}'
            logger.info(f"[IMAGE_PATH_DEBUG] Chemin normalisé (cas 2): {normalized_path}")
            return normalized_path
        else:
            # Garder le chemin générique si pas de type spécifique
            normalized_path = f'/static/uploads/{filename}'
            logger.info(f"[IMAGE_PATH_DEBUG] Chemin normalisé (cas 3): {normalized_path}")
            return normalized_path
    
    # Cas 2: Chemin avec /static/uploads/general/ mais sans double 'general_'
    if '/static/uploads/general/' in path and exercise_type and exercise_type != 'general':
        # Extraire le nom du fichier
        filename = path.split('/')[-1]
        return f'/static/uploads/{exercise_type}/{filename}'
    
    # Cas 3: Chemin absolu avec /static/
    if path.startswith('/static/'):
        # Si le chemin n'a pas de sous-dossier spécifique et qu'on a un type d'exercice
        if '/uploads/' in path and exercise_type and exercise_type != 'general':
            parts = path.split('/')
            if len(parts) >= 3:
                filename = parts[-1]
                # Vérifier si le chemin contient déjà le type d'exercice
                if exercise_type not in path:
                    return f'/static/uploads/{exercise_type}/{filename}'
        return path
        
    # Cas 4: Chemin relatif commençant par static/
    if path.startswith('static/'):
        normalized = '/' + path
        if '/uploads/' in normalized and exercise_type and exercise_type != 'general':
            parts = normalized.split('/')
            if len(parts) >= 3:
                filename = parts[-1]
                # Vérifier si le chemin contient déjà le type d'exercice
                if exercise_type not in normalized:
                    return f'/static/uploads/{exercise_type}/{filename}'
        return normalized
        
    # Cas 5: Chemin avec sous-répertoire spécifique (comme general/)
    if '/' in path and not path.startswith('/'):
        # Vérifier si c'est un chemin d'image avec sous-répertoire
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        is_image = any(path.lower().endswith(ext) for ext in image_extensions)
        
        if is_image:
            # Conserver la structure de sous-répertoire
            if exercise_type and exercise_type != 'general':
                filename = path.split('/')[-1]
                return f'/static/uploads/{exercise_type}/{filename}'
            return f'/static/{path}'
    
    # Cas 6: Chemin relatif sans préfixe ni sous-répertoire
    # Vérifier si c'est un chemin d'image (extensions communes)
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    is_image = any(path.lower().endswith(ext) for ext in image_extensions)
    
    if is_image:
        # Construire le chemin normalisé avec le type d'exercice si spécifié
        if exercise_type and exercise_type != 'general':
            normalized_path = f'/static/uploads/{exercise_type}/{path}'
            logger.info(f"[IMAGE_PATH_DEBUG] Chemin normalisé (cas 4): {normalized_path}")
            return normalized_path
        else:
            normalized_path = f'/static/uploads/{path}'
            logger.info(f"[IMAGE_PATH_DEBUG] Chemin normalisé (cas 5): {normalized_path}")
            return normalized_path
    
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
                        logger.info(f"Image trouvée dans un chemin alternatif: {alt_path} (original: {path})")
                        return True
            
            logger.warning(f"Image invalide ou vide: {path} (chemin absolu: {absolute_path})")
            return False
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du chemin d'image {path}: {str(e)}")
        return False

# Test de la fonction
if __name__ == "__main__":
    # Exemple de contenu d'exercice avec le cas problématique
    test_content = {
        "pairs": [
            {
                "id": "1",
                "left": {
                    "content": "/static/uploads/general/general_20250828_21",
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
                    "content": "/static/uploads/general/general_20250828_22",
                    "type": "image"
                }
            }
        ]
    }
    
    # Normaliser le contenu
    normalized_content = normalize_pairs_exercise_content(test_content, exercise_type='pairs')
    
    # Afficher le résultat
    print(json.dumps(normalized_content, indent=2))
