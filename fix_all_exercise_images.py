"""
Route Flask pour corriger la gestion des images dans tous les exercices.
Cette route permet d'appliquer automatiquement les corrections nécessaires
pour assurer que tous les exercices utilisent correctement cloud_storage.
"""

from flask import Blueprint, current_app, render_template, flash, redirect, url_for
from flask_login import login_required
import json
import os
from utils.image_handler import handle_exercise_image
import cloud_storage

# Créer un blueprint pour les routes de correction
fix_exercise_images_bp = Blueprint('fix_exercise_images', __name__)

@fix_exercise_images_bp.route('/fix-all-exercise-images')
@login_required
def fix_all_exercise_images():
    """
    Route pour corriger tous les exercices avec des problèmes d'images.
    Cette route est accessible uniquement aux utilisateurs connectés.
    """
    from models import Exercise, User, db
    
    # Vérifier si l'utilisateur est admin
    from flask_login import current_user
    if not current_user.is_admin:
        flash('Accès non autorisé. Vous devez être administrateur.', 'error')
        return redirect(url_for('index'))
    
    try:
        # Récupérer tous les exercices
        exercises = Exercise.query.all()
        
        # Statistiques
        stats = {
            'total': len(exercises),
            'with_image': 0,
            'fixed_content': 0,
            'errors': 0
        }
        
        # Liste des exercices corrigés pour affichage
        fixed_exercises = []
        error_exercises = []
        
        for exercise in exercises:
            try:
                # Vérifier si l'exercice a une image
                if exercise.image_path:
                    stats['with_image'] += 1
                    
                    # Vérifier si l'image est dans le contenu JSON
                    content = json.loads(exercise.content) if exercise.content else {}
                    
                    # Si l'image n'est pas dans le contenu, l'ajouter
                    if 'image' not in content or content['image'] != exercise.image_path:
                        content['image'] = exercise.image_path
                        exercise.content = json.dumps(content)
                        stats['fixed_content'] += 1
                        fixed_exercises.append({
                            'id': exercise.id,
                            'title': exercise.title,
                            'type': exercise.exercise_type,
                            'image_path': exercise.image_path
                        })
                        current_app.logger.info(f"[FIX_IMAGES] Exercice {exercise.id} corrigé: image ajoutée au contenu JSON")
            except Exception as e:
                stats['errors'] += 1
                error_exercises.append({
                    'id': exercise.id,
                    'title': exercise.title,
                    'error': str(e)
                })
                current_app.logger.error(f"[FIX_IMAGES] Erreur lors de la correction de l'exercice {exercise.id}: {str(e)}")
        
        # Sauvegarder les modifications
        db.session.commit()
        
        # Afficher un résumé
        flash(f"Correction terminée: {stats['fixed_content']} exercices corrigés sur {stats['with_image']} exercices avec images.", 'success')
        
        # Rendre un template avec les statistiques
        return render_template('admin/fix_exercise_images.html', 
                              stats=stats, 
                              fixed_exercises=fixed_exercises,
                              error_exercises=error_exercises)
    
    except Exception as e:
        current_app.logger.error(f"[FIX_IMAGES] Erreur générale: {str(e)}")
        flash(f"Erreur lors de la correction des exercices: {str(e)}", 'error')
        db.session.rollback()
        return redirect(url_for('index'))

def register_fix_exercise_images_routes(app):
    """
    Enregistre les routes de correction des images d'exercices dans l'application Flask.
    """
    app.register_blueprint(fix_exercise_images_bp)
    app.logger.info("Routes de correction des images d'exercices enregistrées")
