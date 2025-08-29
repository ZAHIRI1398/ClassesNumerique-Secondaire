"""
Module pour corriger la création des exercices de type légende
et assurer la synchronisation des chemins d'images.
"""

import os
import json
import time
from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from models import Exercise, db
from utils.image_utils import allowed_file, generate_unique_filename
from utils.image_path_manager import normalize_image_path, ImagePathManager
from cloud_storage import get_cloudinary_url

# Créer un blueprint pour la gestion des exercices de type légende
legend_bp = Blueprint('legend', __name__)

@legend_bp.route('/create-legend', methods=['GET', 'POST'])
def create_legend_exercise():
    """
    Route pour créer un nouvel exercice de type légende.
    Assure la synchronisation entre exercise.image_path et content['main_image'].
    """
    if request.method == 'GET':
        return render_template('exercise_types/create_legend.html')
    
    if request.method == 'POST':
        # Récupérer les données de base de l'exercice
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        subject = request.form.get('subject', '').strip()
        max_attempts = request.form.get('max_attempts', type=int, default=3)
        
        # Validation des données
        if not title:
            flash('Le titre de l\'exercice est obligatoire.', 'error')
            return redirect(request.url)
        
        # Créer un nouvel exercice de type légende
        exercise = Exercise(
            title=title,
            description=description,
            exercise_type='legend',
            max_attempts=max_attempts,
            subject=subject,
            teacher_id=1  # À remplacer par l'ID de l'enseignant connecté
        )
        
        # Récupérer les instructions
        instructions = request.form.get('legend_instructions', '').strip()
        
        # Récupérer le mode de légende (classic, grid, spatial)
        legend_mode = request.form.get('legend_mode', 'classic')
        
        # Initialiser le contenu
        content = {
            'mode': legend_mode,
            'instructions': instructions,
            'zones': [],
            'elements': []
        }
        
        # Gestion de l'image principale
        main_image_path = None
        if 'legend_main_image' in request.files:
            image_file = request.files['legend_main_image']
            if image_file and image_file.filename != '' and allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                unique_filename = generate_unique_filename(filename)
                
                # Créer le dossier uploads s'il n'existe pas
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                
                # Sauvegarder l'image
                image_path = os.path.join(upload_folder, unique_filename)
                image_file.save(image_path)
                
                # CORRECTION: Normaliser le chemin avec préfixe /static/
                main_image_path = f'/static/uploads/{unique_filename}'
                current_app.logger.info(f'[LEGEND_CREATE_DEBUG] Image principale sauvegardée: {main_image_path}')
        
        # Si une image a été uploadée, l'ajouter au contenu et à l'exercice
        if main_image_path:
            # Normaliser le chemin avec le préfixe /static/
            if not main_image_path.startswith('/static/'):
                main_image_path = f'/static/uploads/{os.path.basename(main_image_path)}'
                
            # S'assurer que le chemin est correctement formaté pour l'affichage
            normalized_path = ImagePathManager.clean_duplicate_paths(main_image_path)
            
            # Synchroniser les deux chemins avec la version normalisée
            content['main_image'] = normalized_path
            exercise.image_path = normalized_path
            
            current_app.logger.info(f'[LEGEND_CREATE_DEBUG] Chemin d\'image normalisé: {normalized_path}')
        
        # Traitement spécifique selon le mode de légende
        if legend_mode == 'classic':
            # Mode classique - pas de traitement supplémentaire à la création
            pass
        
        elif legend_mode == 'grid':
            # Mode grille - initialiser avec une grille vide
            grid_rows = request.form.get('grid_rows', '3')
            grid_cols = request.form.get('grid_cols', '3')
            
            try:
                grid_rows = int(grid_rows)
                grid_cols = int(grid_cols)
            except ValueError:
                grid_rows, grid_cols = 3, 3
            
            content['grid_rows'] = grid_rows
            content['grid_cols'] = grid_cols
        
        elif legend_mode == 'spatial':
            # Mode spatial - initialiser avec des zones vides
            content['zones'] = []
        
        # Sauvegarder le contenu JSON
        exercise.content = json.dumps(content)
        
        try:
            # Ajouter et sauvegarder l'exercice
            db.session.add(exercise)
            db.session.commit()
            flash(f'Exercice "{exercise.title}" créé avec succès!', 'success')
            
            # Rediriger vers l'édition pour compléter l'exercice
            # Ajouter un paramètre pour forcer le rafraîchissement du cache
            timestamp = int(time.time())
            return redirect(url_for('edit_exercise', exercise_id=exercise.id, refresh=timestamp))
        except Exception as e:
            current_app.logger.error(f'Erreur lors de la création de l\'exercice de légende: {e}')
            db.session.rollback()
            flash(f'Erreur lors de la création de l\'exercice: {str(e)}', 'error')
            return redirect(request.url)
        finally:
            db.session.close()

def register_legend_blueprint(app):
    """
    Enregistre le blueprint legend dans l'application Flask.
    """
    app.register_blueprint(legend_bp)
    return app
