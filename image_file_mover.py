"""
Module pour déplacer/copier les fichiers images vers les chemins normalisés
Ce module résout le problème des images 404 après normalisation des chemins
en s'assurant que les fichiers physiques existent aux emplacements attendus.
"""

import os
import shutil
import logging
from flask import current_app
import json

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ensure_directory_exists(directory_path):
    """
    S'assure qu'un répertoire existe, le crée si nécessaire
    
    Args:
        directory_path (str): Chemin du répertoire à créer
        
    Returns:
        bool: True si le répertoire existe ou a été créé, False sinon
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la création du répertoire {directory_path}: {str(e)}")
        return False

def copy_image_to_normalized_path(original_path, normalized_path, root_path=None):
    """
    Copie un fichier image de son chemin original vers son chemin normalisé
    
    Args:
        original_path (str): Chemin original de l'image (relatif ou absolu)
        normalized_path (str): Chemin normalisé de l'image (relatif ou absolu)
        root_path (str, optional): Chemin racine de l'application
        
    Returns:
        bool: True si la copie a réussi, False sinon
    """
    if not original_path or not normalized_path:
        logger.warning("Chemins d'origine ou normalisé manquants")
        return False
        
    # Si les chemins sont identiques, rien à faire
    if original_path == normalized_path:
        logger.info(f"Les chemins sont identiques, aucune action nécessaire: {original_path}")
        return True
        
    # Déterminer le chemin racine
    if root_path is None:
        try:
            root_path = current_app.root_path
        except Exception:
            root_path = os.getcwd()
            
    # Convertir les chemins relatifs en chemins absolus
    def get_absolute_path(path):
        if path.startswith('/static/'):
            return os.path.join(root_path, path[1:])  # Enlever le / initial
        elif path.startswith('static/'):
            return os.path.join(root_path, path)
        else:
            return path
            
    abs_original_path = get_absolute_path(original_path)
    abs_normalized_path = get_absolute_path(normalized_path)
    
    # Vérifier si le fichier source existe
    if not os.path.exists(abs_original_path):
        logger.warning(f"Le fichier source n'existe pas: {abs_original_path}")
        # Essayer de trouver le fichier dans d'autres répertoires courants
        potential_locations = [
            os.path.join(root_path, 'static', 'uploads', os.path.basename(original_path)),
            os.path.join(root_path, 'static', 'exercises', os.path.basename(original_path)),
            os.path.join(root_path, 'static', 'uploads', 'general', os.path.basename(original_path)),
            os.path.join(root_path, 'static', 'uploads', 'pairs', os.path.basename(original_path))
        ]
        
        for location in potential_locations:
            if os.path.exists(location):
                logger.info(f"Fichier trouvé dans un emplacement alternatif: {location}")
                abs_original_path = location
                break
        else:
            logger.error(f"Impossible de trouver le fichier source: {original_path}")
            return False
    
    # Créer le répertoire de destination si nécessaire
    dest_dir = os.path.dirname(abs_normalized_path)
    if not ensure_directory_exists(dest_dir):
        logger.error(f"Impossible de créer le répertoire de destination: {dest_dir}")
        return False
    
    # Copier le fichier
    try:
        shutil.copy2(abs_original_path, abs_normalized_path)
        logger.info(f"Fichier copié avec succès: {abs_original_path} -> {abs_normalized_path}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la copie du fichier: {str(e)}")
        return False

def process_pairs_exercise_images(exercise_content, root_path=None):
    """
    Traite toutes les images d'un exercice de paires pour s'assurer qu'elles
    existent physiquement aux emplacements normalisés
    
    Args:
        exercise_content (dict): Contenu JSON de l'exercice
        root_path (str, optional): Chemin racine de l'application
        
    Returns:
        tuple: (bool, dict) - Succès de l'opération et contenu mis à jour
    """
    if not isinstance(exercise_content, dict):
        try:
            exercise_content = json.loads(exercise_content)
        except Exception as e:
            logger.error(f"Impossible de parser le contenu de l'exercice: {str(e)}")
            return False, exercise_content
    
    # Traiter les paires
    if 'pairs' in exercise_content and isinstance(exercise_content['pairs'], list):
        for pair in exercise_content['pairs']:
            # Traiter l'élément gauche s'il s'agit d'une image
            if 'left' in pair and isinstance(pair['left'], dict) and pair['left'].get('type') == 'image':
                original_path = pair['left'].get('content')
                if original_path and '/static/uploads/general/general_' in original_path:
                    # Normaliser le chemin
                    normalized_path = original_path.replace('/static/uploads/general/general_', '/static/uploads/pairs/pairs_')
                    # Copier le fichier
                    if copy_image_to_normalized_path(original_path, normalized_path, root_path):
                        # Mettre à jour le chemin dans le contenu
                        pair['left']['content'] = normalized_path
            
            # Traiter l'élément droit s'il s'agit d'une image
            if 'right' in pair and isinstance(pair['right'], dict) and pair['right'].get('type') == 'image':
                original_path = pair['right'].get('content')
                if original_path and '/static/uploads/general/general_' in original_path:
                    # Normaliser le chemin
                    normalized_path = original_path.replace('/static/uploads/general/general_', '/static/uploads/pairs/pairs_')
                    # Copier le fichier
                    if copy_image_to_normalized_path(original_path, normalized_path, root_path):
                        # Mettre à jour le chemin dans le contenu
                        pair['right']['content'] = normalized_path
    
    # Traiter les listes d'éléments (format utilisé dans le template)
    for item_list in ['left_items', 'right_items', 'shuffled_right_items']:
        if item_list in exercise_content and isinstance(exercise_content[item_list], list):
            for i, item in enumerate(exercise_content[item_list]):
                # Si l'élément est un dictionnaire avec type='image'
                if isinstance(item, dict) and item.get('type') == 'image':
                    original_path = item.get('content')
                    if original_path and '/static/uploads/general/general_' in original_path:
                        # Normaliser le chemin
                        normalized_path = original_path.replace('/static/uploads/general/general_', '/static/uploads/pairs/pairs_')
                        # Copier le fichier
                        if copy_image_to_normalized_path(original_path, normalized_path, root_path):
                            # Mettre à jour le chemin dans le contenu
                            exercise_content[item_list][i]['content'] = normalized_path
    
    return True, exercise_content

def fix_exercise_images(exercise, exercise_type='pairs'):
    """
    Fonction principale pour corriger les chemins d'images d'un exercice
    et s'assurer que les fichiers existent physiquement
    
    Args:
        exercise: Objet exercice avec contenu JSON
        exercise_type (str): Type d'exercice ('pairs', 'qcm', etc.)
        
    Returns:
        bool: True si les corrections ont été appliquées avec succès
    """
    try:
        # Vérifier si l'exercice a un contenu
        if not hasattr(exercise, 'content') or not exercise.content:
            logger.warning(f"L'exercice {exercise.id} n'a pas de contenu")
            return False
        
        # Parser le contenu JSON
        content = json.loads(exercise.content)
        
        # Traiter les images selon le type d'exercice
        if exercise_type == 'pairs':
            success, updated_content = process_pairs_exercise_images(content)
            if success:
                # Mettre à jour le contenu de l'exercice
                exercise.content = json.dumps(updated_content)
                logger.info(f"Contenu de l'exercice {exercise.id} mis à jour avec succès")
                return True
        
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la correction des images de l'exercice {exercise.id}: {str(e)}")
        return False

# Test de la fonction
if __name__ == "__main__":
    # Exemple de contenu d'exercice avec le cas problématique
    test_content = {
        "pairs": [
            {
                "id": "1",
                "left": {
                    "content": "/static/uploads/general/general_20250828_21abc.png",
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
                    "content": "/static/uploads/general/general_20250828_22xyz.png",
                    "type": "image"
                }
            }
        ]
    }
    
    # Créer des fichiers factices pour le test
    os.makedirs('static/uploads/general', exist_ok=True)
    with open('static/uploads/general/general_20250828_21abc.png', 'w') as f:
        f.write('test image content')
    with open('static/uploads/general/general_20250828_22xyz.png', 'w') as f:
        f.write('test image content')
    
    # Traiter les images
    success, updated_content = process_pairs_exercise_images(test_content)
    
    # Afficher le résultat
    print(f"Succès: {success}")
    print(json.dumps(updated_content, indent=2))
