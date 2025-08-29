"""
Correction pour la route d'édition des exercices de type "fill_in_blanks"

Ce script contient la correction à apporter à la route edit_exercise dans app.py
pour gérer correctement la soumission POST des exercices de type "fill_in_blanks".
"""

from flask import request, flash, render_template, current_app
import json
import os

def fix_fill_in_blanks_edit(exercise, content):
    """
    Fonction de correction pour le traitement POST des exercices fill_in_blanks
    
    Args:
        exercise: L'objet Exercise à modifier
        content: Le dictionnaire de contenu actuel de l'exercice
        
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
        return False, render_template('exercise_types/fill_in_blanks_edit.html', 
                                     exercise=exercise, 
                                     content=exercise.get_content())
    
    if not words:
        flash('Veuillez ajouter au moins un mot.', 'error')
        return False, render_template('exercise_types/fill_in_blanks_edit.html', 
                                     exercise=exercise, 
                                     content=exercise.get_content())
    
    # Vérifier que chaque phrase contient au moins un trou
    for i, sentence in enumerate(sentences):
        if '___' not in sentence:
            flash(f'La phrase {i+1} ne contient pas de trous (utilisez ___ pour marquer les trous).', 'error')
            return False, render_template('exercise_types/fill_in_blanks_edit.html', 
                                         exercise=exercise, 
                                         content=exercise.get_content())
    
    # Vérifier qu'il y a assez de mots pour tous les trous
    total_blanks = sum(sentence.count('___') for sentence in sentences)
    if len(words) < total_blanks:
        flash(f'Il n\'y a pas assez de mots ({len(words)}) pour remplir tous les trous ({total_blanks}).', 'error')
        return False, render_template('exercise_types/fill_in_blanks_edit.html', 
                                     exercise=exercise, 
                                     content=exercise.get_content())
    
    # Mettre à jour le contenu JSON
    content['sentences'] = sentences
    content['words'] = words
    
    # Sauvegarder le contenu JSON dans l'exercice
    exercise.content = json.dumps(content)
    current_app.logger.info(f'[FILL_IN_BLANKS_EDIT] Contenu mis à jour: {exercise.content}')
    
    return True, None

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
