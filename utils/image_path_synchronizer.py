import os
import json
from flask import current_app
from utils.image_path_handler import normalize_image_path, clean_duplicated_path_segments

def synchronize_image_paths(exercise):
    """
    Synchronise les chemins d'images entre exercise.image_path et content['image']
    pour garantir la cohérence des références d'images.
    
    Args:
        exercise: L'objet Exercise à synchroniser
        
    Returns:
        bool: True si des modifications ont été apportées, False sinon
    """
    try:
        modified = False
        
        # Charger le contenu JSON
        content = json.loads(exercise.content) if exercise.content else {}
        
        # Récupérer les chemins d'images actuels
        exercise_path = exercise.image_path
        content_path = content.get('image')
        
        current_app.logger.info(f'[IMAGE_SYNC] Exercice {exercise.id} - Chemin exercise: {exercise_path}')
        current_app.logger.info(f'[IMAGE_SYNC] Exercice {exercise.id} - Chemin content: {content_path}')
        
        # Si les deux chemins sont None ou vides, rien à faire
        if not exercise_path and not content_path:
            current_app.logger.info(f'[IMAGE_SYNC] Exercice {exercise.id} - Pas d\'image à synchroniser')
            return False
            
        # Déterminer le chemin à utiliser (priorité à exercise_path s'il existe)
        primary_path = exercise_path if exercise_path else content_path
        
        # Normaliser et nettoyer le chemin
        normalized_path = normalize_image_path(primary_path)
        cleaned_path = clean_duplicated_path_segments(normalized_path)
        
        # La fonction normalize_image_path s'occupe déjà de s'assurer que le chemin commence par /static/
        # et préserve la structure des dossiers intermédiaires, donc cette partie est redondante
        # et pourrait causer des problèmes avec les chemins déjà normalisés
        
        current_app.logger.info(f'[IMAGE_SYNC] Exercice {exercise.id} - Chemin normalisé: {cleaned_path}')
        
        # Mettre à jour exercise.image_path si nécessaire
        if exercise_path != cleaned_path:
            exercise.image_path = cleaned_path
            modified = True
            current_app.logger.info(f'[IMAGE_SYNC] Exercice {exercise.id} - Mise à jour exercise.image_path: {cleaned_path}')
        
        # Mettre à jour content['image'] si nécessaire
        if content_path != cleaned_path:
            content['image'] = cleaned_path
            exercise.content = json.dumps(content)
            modified = True
            current_app.logger.info(f'[IMAGE_SYNC] Exercice {exercise.id} - Mise à jour content[\'image\']: {cleaned_path}')
        
        return modified
    except Exception as e:
        current_app.logger.error(f'[IMAGE_SYNC] Erreur lors de la synchronisation des chemins d\'images pour l\'exercice {exercise.id}: {str(e)}')
        return False

def synchronize_all_exercises(db, Exercise):
    """
    Synchronise les chemins d'images pour tous les exercices dans la base de données.
    
    Args:
        db: L'objet SQLAlchemy database
        Exercise: Le modèle Exercise
        
    Returns:
        dict: Statistiques sur les modifications effectuées
    """
    stats = {
        'total': 0,
        'modified': 0,
        'errors': 0,
        'details': []
    }
    
    try:
        # Récupérer tous les exercices
        exercises = Exercise.query.all()
        stats['total'] = len(exercises)
        
        for exercise in exercises:
            try:
                if synchronize_image_paths(exercise):
                    stats['modified'] += 1
                    stats['details'].append({
                        'id': exercise.id,
                        'title': exercise.title,
                        'image_path': exercise.image_path
                    })
            except Exception as e:
                stats['errors'] += 1
                current_app.logger.error(f'[IMAGE_SYNC] Erreur lors de la synchronisation de l\'exercice {exercise.id}: {str(e)}')
        
        # Sauvegarder les modifications en base de données
        if stats['modified'] > 0:
            db.session.commit()
            current_app.logger.info(f'[IMAGE_SYNC] {stats["modified"]} exercices mis à jour avec succès')
        
        return stats
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'[IMAGE_SYNC] Erreur lors de la synchronisation des exercices: {str(e)}')
        stats['errors'] += 1
        return stats
