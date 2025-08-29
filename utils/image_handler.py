import os
import json
from flask import current_app
import cloud_storage
from utils.image_path_handler import normalize_image_path, clean_duplicated_path_segments

def handle_exercise_image(file, exercise, exercise_type):
    """
    Fonction utilitaire pour gérer l'upload et la sauvegarde d'images d'exercices
    de manière cohérente pour tous les types d'exercices.
    
    Cette fonction assure que les chemins d'images sont normalisés et synchronisés
    entre exercise.image_path et content['image'].
    
    Args:
        file: L'objet fichier de l'image à sauvegarder
        exercise: L'objet Exercise à mettre à jour
        exercise_type: Le type d'exercice (pour le dossier de destination)
        
    Returns:
        bool: True si l'opération a réussi, False sinon
    """
    try:
        # Supprimer l'ancienne image si elle existe
        if exercise.image_path:
            try:
                # Utiliser cloud_storage pour supprimer l'ancienne image
                cloud_storage.delete_file(exercise.image_path)
                current_app.logger.info(f'[IMAGE_HANDLER] Ancienne image supprimée via cloud_storage: {exercise.image_path}')
            except Exception as e:
                current_app.logger.error(f'[IMAGE_HANDLER] Erreur suppression ancienne image: {str(e)}')
        
        # Sauvegarder la nouvelle image avec cloud_storage
        image_path = cloud_storage.upload_file(file, 'exercises', exercise_type)
        if image_path:
            # Normaliser et nettoyer le chemin d'image
            normalized_path = normalize_image_path(image_path)
            cleaned_path = clean_duplicated_path_segments(normalized_path)
            
            # S'assurer que le chemin commence par /static/
            if cleaned_path and not cleaned_path.startswith('/static/'):
                cleaned_path = f'/static/{cleaned_path}' if not cleaned_path.startswith('static/') else f'/{cleaned_path}'
            
            current_app.logger.info(f'[IMAGE_HANDLER] Chemin original: {image_path}')
            current_app.logger.info(f'[IMAGE_HANDLER] Chemin normalisé: {normalized_path}')
            current_app.logger.info(f'[IMAGE_HANDLER] Chemin final nettoyé: {cleaned_path}')
            
            # Mettre à jour exercise.image_path avec le chemin normalisé et nettoyé
            exercise.image_path = cleaned_path
            
            # Ajouter l'image au contenu JSON également pour double source
            content = json.loads(exercise.content) if exercise.content else {}
            content['image'] = cleaned_path  # Utiliser le même chemin normalisé et nettoyé
            exercise.content = json.dumps(content)
            
            current_app.logger.info(f'[IMAGE_HANDLER] Nouvelle image sauvegardée via cloud_storage: {image_path}')
            return True
        else:
            current_app.logger.error(f'[IMAGE_HANDLER] Échec de sauvegarde avec cloud_storage')
            return False
    except Exception as e:
        current_app.logger.error(f'[IMAGE_HANDLER] Erreur lors de l\'upload via cloud_storage: {str(e)}')
        return False
