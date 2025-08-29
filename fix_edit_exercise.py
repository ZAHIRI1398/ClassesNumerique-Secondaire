"""
Script pour remplacer la gestion des images dans la fonction edit_exercise
par l'utilisation de cloud_storage et des utilitaires de gestion d'images.
"""

import os
import json
from flask import current_app, flash, request, redirect, url_for, render_template
from utils.image_handler import handle_exercise_image
import cloud_storage

def fix_edit_exercise_image_handling(exercise, request, db):
    """
    Fonction de remplacement pour la gestion des images dans edit_exercise
    
    Args:
        exercise: L'objet Exercise à mettre à jour
        request: L'objet request Flask
        db: L'objet db SQLAlchemy
        
    Returns:
        bool: True si l'opération a réussi, False sinon
    """
    try:
        # 1. Vérifier si l'utilisateur veut supprimer l'image existante
        if request.form.get('remove_exercise_image') == 'true' and exercise.image_path:
            try:
                # Utiliser cloud_storage pour supprimer l'image
                cloud_storage.delete_file(exercise.image_path)
                current_app.logger.info(f'[EDIT_FIX] Image supprimée via cloud_storage: {exercise.image_path}')
                
                # Mettre à jour le chemin de l'image dans l'exercice
                exercise.image_path = None
                
                # Mettre à jour le contenu JSON également
                content = json.loads(exercise.content) if exercise.content else {}
                if 'image' in content:
                    del content['image']
                    exercise.content = json.dumps(content)
                
                current_app.logger.info('[EDIT_FIX] Chemin d\'image réinitialisé')
            except Exception as e:
                current_app.logger.error(f'[EDIT_FIX] Erreur lors de la suppression de l\'image: {str(e)}')
                flash('Erreur lors de la suppression de l\'image', 'error')
                return False

        # 2. Vérifier si l'utilisateur a téléversé une nouvelle image
        image_field_name = 'exercise_image'
        if exercise.exercise_type == 'image_labeling':
            image_field_name = 'image'  # Certains types d'exercices utilisent un nom différent
            
        if image_field_name in request.files:
            file = request.files[image_field_name]
            if file and file.filename != '':
                # Utiliser notre fonction utilitaire pour gérer l'image
                if not handle_exercise_image(file, exercise, exercise.exercise_type):
                    current_app.logger.error(f'[EDIT_FIX] Échec de traitement de l\'image pour {exercise.id}')
                    flash('Erreur lors de l\'upload de l\'image', 'error')
                    return False
                current_app.logger.info(f'[EDIT_FIX] Image traitée avec succès via handle_exercise_image')
        
        return True
    except Exception as e:
        current_app.logger.error(f'[EDIT_FIX] Erreur générale: {str(e)}')
        return False

# Fonction pour appliquer la correction à tous les types d'exercices
def apply_fix_to_all_exercise_types():
    """
    Applique la correction de gestion d'images à tous les types d'exercices.
    Cette fonction est appelée depuis une route admin.
    """
    from models import Exercise
    
    try:
        exercises = Exercise.query.all()
        fixed_count = 0
        
        for exercise in exercises:
            # Vérifier si l'exercice a une image
            if exercise.image_path:
                # Vérifier si l'image existe dans le contenu JSON
                content = json.loads(exercise.content) if exercise.content else {}
                if 'image' not in content:
                    content['image'] = exercise.image_path
                    exercise.content = json.dumps(content)
                    fixed_count += 1
        
        db.session.commit()
        return f"Correction appliquée à {fixed_count} exercices"
    except Exception as e:
        db.session.rollback()
        return f"Erreur lors de l'application de la correction: {str(e)}"
