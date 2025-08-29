import os
import json
from flask import current_app, flash
from utils.image_handler import handle_exercise_image

def process_exercise_edit(exercise, form, files):
    """
    Fonction utilitaire pour traiter l'édition d'un exercice, incluant la gestion des images
    et la mise à jour du contenu JSON.
    
    Args:
        exercise: L'objet Exercise à mettre à jour
        form: L'objet form contenant les données du formulaire
        files: Les fichiers uploadés (request.files)
        
    Returns:
        bool: True si l'édition a réussi, False sinon
    """
    try:
        # Mettre à jour les champs de base
        exercise.title = form.get('title', '')
        exercise.description = form.get('description', '')
        exercise.difficulty = form.get('difficulty', 1)
        
        # Traiter l'image si elle est présente
        file = files.get('image')
        if file and file.filename != '':
            # Utiliser notre fonction utilitaire pour gérer l'image
            if not handle_exercise_image(file, exercise, exercise.exercise_type):
                current_app.logger.error(f'[EXERCISE_EDITOR] Échec de traitement de l\'image pour {exercise.id}')
                flash('Erreur lors de l\'upload de l\'image', 'error')
                return False
        
        # Traitement spécifique selon le type d'exercice
        if exercise.exercise_type == 'fill_in_blanks':
            return process_fill_in_blanks_edit(exercise, form)
        elif exercise.exercise_type == 'qcm':
            return process_qcm_edit(exercise, form)
        elif exercise.exercise_type == 'image_labeling':
            return process_image_labeling_edit(exercise, form, files)
        # Ajouter d'autres types d'exercices au besoin
        else:
            # Pour les types non spécifiés, on garde le contenu tel quel
            current_app.logger.warning(f'[EXERCISE_EDITOR] Type d\'exercice non géré spécifiquement: {exercise.exercise_type}')
            return True
            
    except Exception as e:
        current_app.logger.error(f'[EXERCISE_EDITOR] Erreur lors de l\'édition: {str(e)}')
        return False

def process_fill_in_blanks_edit(exercise, form):
    """Traite l'édition d'un exercice de type fill_in_blanks"""
    try:
        content = json.loads(exercise.content) if exercise.content else {}
        content['text'] = form.get('text', '')
        content['answers'] = form.getlist('answers[]')
        exercise.content = json.dumps(content)
        return True
    except Exception as e:
        current_app.logger.error(f'[EXERCISE_EDITOR] Erreur fill_in_blanks: {str(e)}')
        return False

def process_qcm_edit(exercise, form):
    """Traite l'édition d'un exercice de type qcm"""
    try:
        content = json.loads(exercise.content) if exercise.content else {}
        
        # Récupérer les questions, options et réponses correctes
        questions = []
        for i in range(1, int(form.get('question_count', 0)) + 1):
            question_text = form.get(f'question_{i}', '')
            options = []
            for j in range(1, 5):  # Supposons 4 options max par question
                option = form.get(f'option_{i}_{j}', '')
                if option:
                    options.append(option)
            
            correct_option = int(form.get(f'correct_option_{i}', 0))
            
            if question_text and options:
                questions.append({
                    'question': question_text,
                    'options': options,
                    'correct_option': correct_option
                })
        
        content['questions'] = questions
        exercise.content = json.dumps(content)
        return True
    except Exception as e:
        current_app.logger.error(f'[EXERCISE_EDITOR] Erreur qcm: {str(e)}')
        return False

def process_image_labeling_edit(exercise, form, files):
    """Traite l'édition d'un exercice de type image_labeling"""
    try:
        content = json.loads(exercise.content) if exercise.content else {}
        
        # Traiter l'image principale si elle est présente
        main_image_file = files.get('main_image')
        if main_image_file and main_image_file.filename != '':
            from cloud_storage import upload_file
            main_image_path = upload_file(main_image_file, 'exercises', 'image_labeling')
            if main_image_path:
                content['main_image'] = main_image_path
        
        # Récupérer les zones et étiquettes
        zones = []
        zone_count = int(form.get('zone_count', 0))
        for i in range(1, zone_count + 1):
            label = form.get(f'label_{i}', '')
            x = form.get(f'x_{i}', 0)
            y = form.get(f'y_{i}', 0)
            
            if label:
                zones.append({
                    'label': label,
                    'x': int(x) if x else 0,
                    'y': int(y) if y else 0
                })
        
        content['zones'] = zones
        exercise.content = json.dumps(content)
        return True
    except Exception as e:
        current_app.logger.error(f'[EXERCISE_EDITOR] Erreur image_labeling: {str(e)}')
        return False
