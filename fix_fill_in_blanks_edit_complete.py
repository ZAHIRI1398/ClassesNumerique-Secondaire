"""
Correction complète pour la route d'édition des exercices de type "fill_in_blanks"

Ce script contient la correction à apporter à la route edit_exercise dans app.py
pour gérer correctement la soumission POST des exercices de type "fill_in_blanks",
y compris la gestion des images.
"""

from flask import request, flash, render_template, current_app, redirect, url_for
import json
import os
from werkzeug.utils import secure_filename
import time
import random
import string

def allowed_file(filename):
    """Vérifie si le fichier a une extension autorisée"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(original_filename):
    """Génère un nom de fichier unique basé sur le timestamp et des caractères aléatoires"""
    name, ext = os.path.splitext(original_filename)
    timestamp = str(int(time.time()))
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{timestamp}_{random_str}{ext}"

def fix_fill_in_blanks_edit(exercise, db, app):
    """
    Fonction de correction pour le traitement POST des exercices fill_in_blanks
    avec gestion complète des images
    
    Args:
        exercise: L'objet Exercise à modifier
        db: L'objet SQLAlchemy pour les opérations de base de données
        app: L'application Flask
        
    Returns:
        tuple: (success, template_or_redirect)
            - success: booléen indiquant si le traitement a réussi
            - template_or_redirect: template à rendre ou redirection à effectuer
    """
    current_app.logger.info(f'[FILL_IN_BLANKS_EDIT] Traitement spécifique pour fill_in_blanks')
    
    # Récupérer les phrases et les mots du formulaire
    sentences = request.form.getlist('sentences[]')
    words = request.form.getlist('words[]')
    
    # Validation des données
    if not sentences:
        flash('Veuillez ajouter au moins une phrase.', 'error')
        content = json.loads(exercise.content) if exercise.content else {}
        return False, render_template('exercise_types/fill_in_blanks_edit.html', exercise=exercise, content=content)
    
    if not words:
        flash('Veuillez ajouter au moins un mot.', 'error')
        content = json.loads(exercise.content) if exercise.content else {}
        return False, render_template('exercise_types/fill_in_blanks_edit.html', exercise=exercise, content=content)
    
    # Vérifier que chaque phrase contient au moins un trou
    for i, sentence in enumerate(sentences):
        if '___' not in sentence:
            flash(f'La phrase {i+1} ne contient pas de trous (utilisez ___ pour marquer les trous).', 'error')
            content = json.loads(exercise.content) if exercise.content else {}
            return False, render_template('exercise_types/fill_in_blanks_edit.html', exercise=exercise, content=content)
    
    # Vérifier qu'il y a assez de mots pour tous les trous
    total_blanks = sum(sentence.count('___') for sentence in sentences)
    if len(words) < total_blanks:
        flash(f'Il n\'y a pas assez de mots ({len(words)}) pour remplir tous les trous ({total_blanks}).', 'error')
        content = json.loads(exercise.content) if exercise.content else {}
        return False, render_template('exercise_types/fill_in_blanks_edit.html', exercise=exercise, content=content)
    
    # Gestion de l'image
    # 1. Vérifier si l'utilisateur veut supprimer l'image existante
    if request.form.get('remove_exercise_image') == 'true' and exercise.image_path:
        try:
            # Supprimer l'ancienne image du système de fichiers
            old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(exercise.image_path))
            if os.path.exists(old_image_path):
                os.remove(old_image_path)
                current_app.logger.info(f'[FILL_IN_BLANKS_EDIT] Image supprimée: {old_image_path}')
            
            # Mettre à jour le chemin de l'image dans l'exercice
            exercise.image_path = None
            current_app.logger.info('[FILL_IN_BLANKS_EDIT] Chemin d\'image réinitialisé')
        except Exception as e:
            current_app.logger.error(f'[FILL_IN_BLANKS_EDIT] Erreur lors de la suppression de l\'image: {str(e)}')
            flash('Erreur lors de la suppression de l\'image', 'error')
    
    # 2. Vérifier si l'utilisateur a téléversé une nouvelle image
    if 'exercise_image' in request.files:
        file = request.files['exercise_image']
        if file and file.filename != '' and allowed_file(file.filename):
            try:
                # Supprimer l'ancienne image si elle existe
                if exercise.image_path:
                    try:
                        old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(exercise.image_path))
                        if os.path.exists(old_image_path):
                            os.remove(old_image_path)
                            current_app.logger.info(f'[FILL_IN_BLANKS_EDIT] Ancienne image supprimée: {old_image_path}')
                    except Exception as e:
                        current_app.logger.error(f'[FILL_IN_BLANKS_EDIT] Erreur suppression ancienne image: {str(e)}')
                
                # Sauvegarder la nouvelle image
                filename = generate_unique_filename(file.filename)
                # Créer le dossier de destination s'il n'existe pas
                dest_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'exercises')
                os.makedirs(dest_folder, exist_ok=True)
                file_path = os.path.join(dest_folder, filename)
                file.save(file_path)
                exercise.image_path = f'/static/uploads/exercises/{filename}'
                current_app.logger.info(f'[FILL_IN_BLANKS_EDIT] Nouvelle image sauvegardée: {exercise.image_path}')
            except Exception as e:
                current_app.logger.error(f'[FILL_IN_BLANKS_EDIT] Erreur lors de l\'upload de l\'image: {str(e)}')
                flash('Erreur lors de l\'upload de l\'image', 'error')
    
    # Mettre à jour le contenu JSON
    content = json.loads(exercise.content) if exercise.content else {}
    content['sentences'] = sentences
    content['words'] = words
    
    # Sauvegarder le contenu JSON dans l'exercice
    exercise.content = json.dumps(content)
    current_app.logger.info(f'[FILL_IN_BLANKS_EDIT] Contenu mis à jour: {exercise.content}')
    
    # Sauvegarder les modifications en base de données
    try:
        db.session.commit()
        flash(f'Exercice "{exercise.title}" modifié avec succès!', 'success')
        return True, redirect(url_for('view_exercise', exercise_id=exercise.id))
    except Exception as e:
        current_app.logger.error(f'[FILL_IN_BLANKS_EDIT] Erreur lors de la sauvegarde: {str(e)}')
        db.session.rollback()
        flash(f'Erreur lors de la modification de l\'exercice: {str(e)}', 'error')
        content = json.loads(exercise.content) if exercise.content else {}
        return False, render_template('exercise_types/fill_in_blanks_edit.html', exercise=exercise, content=content)

def integrate_fix_in_app_py():
    """
    Instructions pour intégrer la correction dans app.py
    """
    instructions = """
    Dans app.py, recherchez le bloc de code qui traite la méthode POST dans la route edit_exercise.
    
    Localisez la section qui commence par:
    ```python
    else:
        # Gestion générique pour tous les autres types d'exercices
        # (fill_in_blanks, word_placement, drag_and_drop, etc.)
        current_app.logger.info(f'[EDIT_DEBUG] Traitement générique pour le type: {exercise.exercise_type}')
    ```
    
    Juste avant cette section, ajoutez un nouveau bloc elif pour traiter spécifiquement les exercices de type fill_in_blanks:
    
    ```python
    elif exercise.exercise_type == 'fill_in_blanks':
        current_app.logger.info(f'[EDIT_DEBUG] Traitement spécifique pour fill_in_blanks')
        
        # Récupérer les phrases et les mots du formulaire
        sentences = request.form.getlist('sentences[]')
        words = request.form.getlist('words[]')
        
        # Validation des données
        if not sentences:
            flash('Veuillez ajouter au moins une phrase.', 'error')
            content = json.loads(exercise.content) if exercise.content else {}
            return render_template('exercise_types/fill_in_blanks_edit.html', exercise=exercise, content=content)
        
        if not words:
            flash('Veuillez ajouter au moins un mot.', 'error')
            content = json.loads(exercise.content) if exercise.content else {}
            return render_template('exercise_types/fill_in_blanks_edit.html', exercise=exercise, content=content)
        
        # Vérifier que chaque phrase contient au moins un trou
        for i, sentence in enumerate(sentences):
            if '___' not in sentence:
                flash(f'La phrase {i+1} ne contient pas de trous (utilisez ___ pour marquer les trous).', 'error')
                content = json.loads(exercise.content) if exercise.content else {}
                return render_template('exercise_types/fill_in_blanks_edit.html', exercise=exercise, content=content)
        
        # Vérifier qu'il y a assez de mots pour tous les trous
        total_blanks = sum(sentence.count('___') for sentence in sentences)
        if len(words) < total_blanks:
            flash(f'Il n\'y a pas assez de mots ({len(words)}) pour remplir tous les trous ({total_blanks}).', 'error')
            content = json.loads(exercise.content) if exercise.content else {}
            return render_template('exercise_types/fill_in_blanks_edit.html', exercise=exercise, content=content)
        
        # Gestion de l'image
        # 1. Vérifier si l'utilisateur veut supprimer l'image existante
        if request.form.get('remove_exercise_image') == 'true' and exercise.image_path:
            try:
                # Supprimer l'ancienne image du système de fichiers
                old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(exercise.image_path))
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
                    current_app.logger.info(f'[EDIT_DEBUG] Image supprimée: {old_image_path}')
                
                # Mettre à jour le chemin de l'image dans l'exercice
                exercise.image_path = None
                current_app.logger.info('[EDIT_DEBUG] Chemin d\'image réinitialisé')
            except Exception as e:
                current_app.logger.error(f'[EDIT_DEBUG] Erreur lors de la suppression de l\'image: {str(e)}')
                flash('Erreur lors de la suppression de l\'image', 'error')
        
        # 2. Vérifier si l'utilisateur a téléversé une nouvelle image
        if 'exercise_image' in request.files:
            file = request.files['exercise_image']
            if file and file.filename != '' and allowed_file(file.filename):
                try:
                    # Supprimer l'ancienne image si elle existe
                    if exercise.image_path:
                        try:
                            old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(exercise.image_path))
                            if os.path.exists(old_image_path):
                                os.remove(old_image_path)
                                current_app.logger.info(f'[EDIT_DEBUG] Ancienne image supprimée: {old_image_path}')
                        except Exception as e:
                            current_app.logger.error(f'[EDIT_DEBUG] Erreur suppression ancienne image: {str(e)}')
                    
                    # Sauvegarder la nouvelle image
                    filename = generate_unique_filename(file.filename)
                    # Créer le dossier de destination s'il n'existe pas
                    dest_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'exercises')
                    os.makedirs(dest_folder, exist_ok=True)
                    file_path = os.path.join(dest_folder, filename)
                    file.save(file_path)
                    exercise.image_path = f'/static/uploads/exercises/{filename}'
                    current_app.logger.info(f'[EDIT_DEBUG] Nouvelle image sauvegardée: {exercise.image_path}')
                except Exception as e:
                    current_app.logger.error(f'[EDIT_DEBUG] Erreur lors de l\'upload de l\'image: {str(e)}')
                    flash('Erreur lors de l\'upload de l\'image', 'error')
        
        # Mettre à jour le contenu JSON
        content = json.loads(exercise.content) if exercise.content else {}
        content['sentences'] = sentences
        content['words'] = words
        
        # Sauvegarder le contenu JSON dans l'exercice
        exercise.content = json.dumps(content)
        current_app.logger.info(f'[EDIT_DEBUG] Contenu fill_in_blanks mis à jour: {exercise.content}')
        
        try:
            db.session.commit()
            flash(f'Exercice "{exercise.title}" modifié avec succès!', 'success')
            return redirect(url_for('view_exercise', exercise_id=exercise.id))
        except Exception as e:
            current_app.logger.error(f'[EDIT_DEBUG] Erreur lors de la sauvegarde: {str(e)}')
            db.session.rollback()
            flash(f'Erreur lors de la modification de l\'exercice: {str(e)}', 'error')
            content = json.loads(exercise.content) if exercise.content else {}
            return render_template('exercise_types/fill_in_blanks_edit.html', exercise=exercise, content=content)
    ```
    """
    return instructions
