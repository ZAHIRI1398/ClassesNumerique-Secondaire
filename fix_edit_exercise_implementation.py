"""
Script pour remplacer la fonction edit_exercise dans app.py
Ce script contient une version améliorée de la fonction edit_exercise
qui utilise les utilitaires de gestion d'images et cloud_storage.
"""

import os
import json
from flask import current_app, flash, request, redirect, url_for, render_template
from flask_login import login_required, current_user
from utils.image_handler import handle_exercise_image
from utils.exercise_editor import process_exercise_edit
import cloud_storage

def new_edit_exercise(exercise_id):
    """
    Version améliorée de la fonction edit_exercise qui utilise les utilitaires
    de gestion d'images et cloud_storage.
    
    Args:
        exercise_id: ID de l'exercice à éditer
        
    Returns:
        La réponse Flask (template ou redirection)
    """
    from models import Exercise, db
    
    exercise = Exercise.query.get_or_404(exercise_id)
    
    # Vérifier que l'utilisateur est autorisé à éditer cet exercice
    if not current_user.is_admin and exercise.teacher_id != current_user.id:
        flash("Vous n'êtes pas autorisé à éditer cet exercice.", "danger")
        return redirect(url_for('index'))
    
    if request.method == 'GET':
        # Charger le contenu de l'exercice
        content = exercise.get_content() if hasattr(exercise, 'get_content') else {}
        if not content and exercise.content:
            try:
                content = json.loads(exercise.content)
            except:
                content = {}
        
        # Pour les exercices image_labeling, s'assurer que les structures de données sont correctes
        if exercise.exercise_type == 'image_labeling':
            # S'assurer que content.labels existe
            if 'labels' not in content:
                content['labels'] = []
            
            # S'assurer que content.zones existe
            if 'zones' not in content:
                content['zones'] = []
            
            # Vérifier que les zones ont le bon format
            for i, zone in enumerate(content.get('zones', [])):
                # S'assurer que chaque zone a les propriétés x, y et label
                if not isinstance(zone, dict):
                    content['zones'][i] = {'x': 0, 'y': 0, 'label': ''}
                    continue
                
                if 'x' not in zone:
                    zone['x'] = 0
                if 'y' not in zone:
                    zone['y'] = 0
                if 'label' not in zone:
                    zone['label'] = ''
            
            # Log pour le débogage
            current_app.logger.info(f"[IMAGE_LABELING_EDIT] Contenu chargé: {content}")
            current_app.logger.info(f"[IMAGE_LABELING_EDIT] Étiquettes: {content.get('labels', [])}")
            current_app.logger.info(f"[IMAGE_LABELING_EDIT] Zones: {content.get('zones', [])}")
        
        # Utiliser le template spécifique selon le type d'exercice
        template_name = f'exercise_types/{exercise.exercise_type}_edit.html'
        return render_template(template_name, exercise=exercise, content=content)
    
    elif request.method == 'POST':
        try:
            # Mettre à jour les champs de base
            exercise.title = request.form.get('title', exercise.title)
            exercise.description = request.form.get('description', exercise.description)
            exercise.subject = request.form.get('subject', exercise.subject)
            
            # Gestion de la suppression d'image si demandée
            if 'remove_exercise_image' in request.form and request.form['remove_exercise_image'] == 'true':
                if exercise.image_path:
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
            
            # Traitement spécifique selon le type d'exercice
            if exercise.exercise_type == 'image_labeling':
                # Gestion de l'image principale pour image_labeling
                if 'main_image' in request.files:
                    main_image_file = request.files['main_image']
                    if main_image_file and main_image_file.filename != '':
                        # Utiliser notre fonction utilitaire pour gérer l'image
                        if not handle_exercise_image(main_image_file, exercise, exercise.exercise_type, field_name='main_image'):
                            current_app.logger.error(f'[EDIT_FIX] Échec de traitement de l\'image principale pour {exercise.id}')
                            flash('Erreur lors de l\'upload de l\'image principale', 'error')
                            return redirect(url_for('edit_exercise', exercise_id=exercise_id))
                
                # Traitement des zones et étiquettes
                try:
                    content = json.loads(exercise.content) if exercise.content else {}
                    
                    # Récupérer les zones et étiquettes
                    zones = []
                    zone_count = int(request.form.get('zone_count', 0))
                    for i in range(1, zone_count + 1):
                        label = request.form.get(f'label_{i}', '')
                        x = request.form.get(f'x_{i}', 0)
                        y = request.form.get(f'y_{i}', 0)
                        
                        if label:
                            zones.append({
                                'label': label,
                                'x': int(x) if x else 0,
                                'y': int(y) if y else 0
                            })
                    
                    content['zones'] = zones
                    exercise.content = json.dumps(content)
                except Exception as e:
                    current_app.logger.error(f'[EDIT_FIX] Erreur lors du traitement des zones: {str(e)}')
                    flash('Erreur lors du traitement des zones', 'error')
            else:
                # Pour les autres types d'exercices, utiliser la fonction process_exercise_edit
                if not process_exercise_edit(exercise, request.form, request.files):
                    flash('Erreur lors de la mise à jour de l\'exercice', 'error')
                    return redirect(url_for('edit_exercise', exercise_id=exercise_id))
            
            # Sauvegarder les modifications
            db.session.commit()
            
            # Ajouter un message de succès
            flash('Exercice mis à jour avec succès', 'success')
            
            # Rediriger vers la page de l'exercice
            return redirect(url_for('view_exercise', exercise_id=exercise_id))
        
        except Exception as e:
            # En cas d'erreur, annuler les modifications
            db.session.rollback()
            
            # Logger l'erreur
            current_app.logger.error(f'[EDIT_FIX] Erreur lors de la mise à jour de l\'exercice {exercise_id}: {str(e)}')
            
            # Afficher un message d'erreur
            flash(f'Erreur lors de la mise à jour de l\'exercice: {str(e)}', 'error')
            
            # Rediriger vers la page d'édition
            return redirect(url_for('edit_exercise', exercise_id=exercise_id))

def apply_edit_exercise_fix(app):
    """
    Applique la correction à la fonction edit_exercise de l'application Flask.
    
    Args:
        app: L'application Flask
    """
    # Sauvegarder l'ancienne fonction pour référence
    app.view_functions['edit_exercise_old'] = app.view_functions['edit_exercise']
    
    # Remplacer par la nouvelle fonction
    app.view_functions['edit_exercise'] = login_required(new_edit_exercise)
    
    # Logger l'application de la correction
    app.logger.info("[FIX_APPLIED] La fonction edit_exercise a été remplacée par la version corrigée")
    
    return "Correction appliquée avec succès à la fonction edit_exercise"
