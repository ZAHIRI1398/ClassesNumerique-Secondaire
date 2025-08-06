from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app, session
from traceback import format_exc as exc_info
from flask_login import login_required, current_user
from models import db, Exercise, ExerciseAttempt, User
from sqlalchemy import desc
from decorators import teacher_required
from forms import ExerciseForm
from werkzeug.utils import secure_filename
import json
import random
import os

bp = Blueprint('exercise', __name__)

# Fonctions helper pour l'upload de fichiers
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(original_filename):
    import string
    import time
    name, ext = os.path.splitext(original_filename)
    timestamp = str(int(time.time()))
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{timestamp}_{random_str}{ext}"

@bp.route('/create', methods=['GET', 'POST'])
# @login_required  # Temporarily disabled for testing
# @teacher_required  # Temporarily disabled for testing
def create_exercise():
    form = ExerciseForm()
    if request.method == 'GET':
        return render_template('exercise_types/create_exercise_simple.html', form=form, exercise_types=Exercise.EXERCISE_TYPES)
    
    if request.method == 'POST':
        form = ExerciseForm(request.form)
        if not form.validate():
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'Erreur dans le champ {field}: {error}', 'error')
            return render_template('exercise_types/create_exercise_simple.html', form=form, exercise_types=Exercise.EXERCISE_TYPES)
        
        try:
            # Log sécurisé sans caractères Unicode problématiques
            current_app.logger.info('Donnees recues pour creation exercice')
            title = form.title.data
            description = form.description.data
            exercise_type = form.exercise_type.data
            max_attempts = request.form.get('max_attempts', type=int, default=3)
            
            # Nouveaux champs ajoutés
            course_id = request.form.get('course_id')
            subject = request.form.get('subject', '').strip()

            current_app.logger.info(f'Titre: {title}')
            current_app.logger.info(f'Type: {exercise_type}')
            current_app.logger.info(f'Tentatives: {max_attempts}')
            current_app.logger.info(f'Cours ID: {course_id}')
            current_app.logger.info(f'Matiere: {subject}')

            if not all([title, exercise_type]):
                flash('Le titre et le type d\'exercice sont obligatoires.', 'error')
                return redirect(request.url)

            # Vérifier si le type d'exercice est supporté
            supported_types = [t[0] for t in Exercise.EXERCISE_TYPES]
            if exercise_type not in supported_types:
                flash(f'Le type d\'exercice {exercise_type} n\'est pas pris en charge.', 'error')
                return redirect(request.url)

            if max_attempts < 1:
                flash('Le nombre de tentatives doit être au moins égal à 1.', 'error')
                return redirect(request.url)

            # Initialiser le contenu et le chemin d'image
            content = {}
            exercise_image_path = None
            
            if exercise_type == 'qcm':
                current_app.logger.debug('Traitement d\'un exercice QCM')
                current_app.logger.debug(f'Données du formulaire: {dict(request.form)}')
                
                # Récupérer les questions et leurs options
                questions_data = []
                question_index = 0
                
                while f'question_{question_index}' in request.form:
                    question_text = request.form.get(f'question_{question_index}')
                    
                    # Récupérer les options individuelles (option_0_0, option_0_1, option_0_2)
                    options = []
                    option_index = 0
                    while f'option_{question_index}_{option_index}' in request.form:
                        option_text = request.form.get(f'option_{question_index}_{option_index}')
                        if option_text and option_text.strip():
                            options.append(option_text.strip())
                        option_index += 1
                    
                    correct_answer = request.form.get(f'correct_{question_index}')
                    
                    current_app.logger.debug(f'Question {question_index}: {question_text}')
                    current_app.logger.debug(f'Options {question_index}: {options}')
                    current_app.logger.debug(f'Correct {question_index}: {correct_answer}')
                    
                    if question_text and question_text.strip() and options and len(options) >= 2:
                        questions_data.append({
                            'text': question_text.strip(),
                            'choices': options,  # Utiliser 'choices' pour correspondre au template
                            'correct_answer': int(correct_answer) if correct_answer is not None else 0
                        })
                    
                    question_index += 1
                
                if not questions_data:
                    flash('Veuillez ajouter au moins une question avec des options.', 'error')
                    return redirect(request.url)
                
                content['questions'] = questions_data
                
                # Gestion de l'image optionnelle pour QCM
                if 'qcm_image' in request.files:
                    image_file = request.files['qcm_image']
                    if image_file and image_file.filename != '' and allowed_file(image_file.filename):
                        filename = secure_filename(image_file.filename)
                        unique_filename = generate_unique_filename(filename)
                        
                        # Créer le dossier uploads s'il n'existe pas
                        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                        os.makedirs(upload_folder, exist_ok=True)
                        
                        # Sauvegarder l'image
                        image_path = os.path.join(upload_folder, unique_filename)
                        image_file.save(image_path)
                        
                        # Ajouter le chemin de l'image au contenu
                        content['image'] = f'static/uploads/{unique_filename}'
                        current_app.logger.debug(f'Image QCM sauvegardée: {content["image"]}')

            elif exercise_type == 'word_search':
                print(f'[WORD_SEARCH_CREATE_DEBUG] Form data: {dict(request.form)}')
                
                # Récupérer les mots depuis les champs word_search_words[]
                words_from_fields = request.form.getlist('word_search_words[]')
                print(f'[WORD_SEARCH_CREATE_DEBUG] Words from fields: {words_from_fields}')
                
                # Traiter chaque champ (peut contenir des mots séparés par des virgules)
                all_words = []
                for field_value in words_from_fields:
                    if field_value and field_value.strip():
                        # Si le champ contient des virgules, séparer les mots
                        if ',' in field_value:
                            words_in_field = [w.strip().upper() for w in field_value.split(',') if w.strip()]
                            all_words.extend(words_in_field)
                        else:
                            # Sinon, ajouter le mot unique
                            all_words.append(field_value.strip().upper())
                
                print(f'[WORD_SEARCH_CREATE_DEBUG] All words processed: {all_words}')
                
                # Supprimer les doublons tout en préservant l'ordre
                unique_words = []
                for word in all_words:
                    if word not in unique_words:
                        unique_words.append(word)
                
                print(f'[WORD_SEARCH_CREATE_DEBUG] Final unique words: {unique_words}')
                words = unique_words
                
                if not words:
                    flash('Veuillez entrer au moins un mot.', 'error')
                    return redirect(request.url)
                
                # Récupérer les dimensions de la grille
                grid_width = int(request.form.get('grid_width', 15))
                grid_height = int(request.form.get('grid_height', 15))
                
                content['words'] = words
                content['grid_width'] = grid_width
                content['grid_height'] = grid_height
                
            elif exercise_type == 'dictation':
                print(f'[DICTATION_CREATE_DEBUG] Form data: {dict(request.form)}')
                
                # Récupérer les phrases de dictée
                sentences = request.form.getlist('dictation_sentences[]')
                sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
                
                print(f'[DICTATION_CREATE_DEBUG] Sentences: {sentences}')
                
                if not sentences:
                    flash('Veuillez entrer au moins une phrase pour la dictée.', 'error')
                    return redirect(request.url)
                
                # Traitement des fichiers audio (si uploadés)
                audio_files = []
                for i, sentence in enumerate(sentences):
                    audio_file = request.files.get(f'dictation_audio_{i}')
                    if audio_file and audio_file.filename:
                        # Sauvegarder le fichier audio
                        filename = secure_filename(f'dictation_{exercise_id}_{i}_{audio_file.filename}')
                        audio_path = os.path.join('static/uploads/audio', filename)
                        
                        # Créer le dossier s'il n'existe pas
                        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
                        
                        audio_file.save(audio_path)
                        audio_files.append(f'/static/uploads/audio/{filename}')
                        print(f'[DICTATION_CREATE_DEBUG] Audio saved: {audio_path}')
                    else:
                        audio_files.append(None)  # Pas de fichier audio pour cette phrase
                
                content['sentences'] = sentences
                content['audio_files'] = audio_files
                content['instructions'] = request.form.get('dictation_instructions', 'Écoute et écris sans faute. Ne mets pas de majuscule.')
                
                print(f'[DICTATION_CREATE_DEBUG] Final content: {content}')
                
            elif exercise_type == 'fill_in_blanks':
                sentences = request.form.getlist('fill_in_blanks_sentences[]')
                words = request.form.getlist('fill_in_blanks_words[]')
                
                if not sentences:
                    flash('Veuillez ajouter au moins une phrase.', 'error')
                    return redirect(request.url)
                
                if not words:
                    flash('Veuillez ajouter au moins un mot.', 'error')
                    return redirect(request.url)
                
                # Vérifier que chaque phrase contient au moins un trou
                for i, sentence in enumerate(sentences):
                    if '___' not in sentence:
                        flash(f'La phrase {i+1} ne contient pas de trous (utilisez ___ pour marquer les trous).', 'error')
                        return redirect(request.url)
                
                # Nettoyer les phrases et les mots
                sentences = [s.strip() for s in sentences if s.strip()]
                words = [w.strip() for w in words if w.strip()]
                
                # Stocker le contenu dans un format standard
                content = {
                    'sentences': sentences,
                    'words': words
                }
                
                # Gestion de l'image optionnelle pour Texte à trous
                if 'fill_in_blanks_image' in request.files:
                    image_file = request.files['fill_in_blanks_image']
                    if image_file and image_file.filename != '' and allowed_file(image_file.filename):
                        filename = secure_filename(image_file.filename)
                        unique_filename = generate_unique_filename(filename)
                        
                        # Créer le dossier uploads s'il n'existe pas
                        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                        os.makedirs(upload_folder, exist_ok=True)
                        
                        # Sauvegarder l'image
                        image_path = os.path.join(upload_folder, unique_filename)
                        image_file.save(image_path)
                        
                        # Ajouter le chemin de l'image au contenu
                        content['image'] = f'static/uploads/{unique_filename}'
                        current_app.logger.debug(f'Image Texte à trous sauvegardée: {content["image"]}')
                
            elif exercise_type == 'drag_and_drop':
                # Traitement pour glisser-déposer
                drag_items = request.form.getlist('drag_items[]')
                drop_zones = request.form.getlist('drop_zones[]')
                correct_order_str = request.form.get('correct_order', '')
                
                # Filtrer les éléments vides
                filtered_drag_items = [item.strip() for item in drag_items if item.strip()]
                filtered_drop_zones = [zone.strip() for zone in drop_zones if zone.strip()]
                
                # Validation
                if not filtered_drag_items:
                    flash('Au moins un élément à glisser est requis pour un exercice "Glisser-déposer".', 'error')
                    return redirect(request.url)
                
                if not filtered_drop_zones:
                    flash('Au moins une zone de dépôt est requise pour un exercice "Glisser-déposer".', 'error')
                    return redirect(request.url)
                
                if len(filtered_drag_items) != len(filtered_drop_zones):
                    flash('Le nombre d\'éléments à glisser doit être égal au nombre de zones de dépôt.', 'error')
                    return redirect(request.url)
                
                # Parser l'ordre correct
                try:
                    correct_order = [int(x.strip()) for x in correct_order_str.split(',') if x.strip()]
                    if len(correct_order) != len(filtered_drag_items):
                        flash('L\'ordre correct doit contenir autant d\'éléments que d\'éléments à glisser.', 'error')
                        return redirect(request.url)
                except (ValueError, AttributeError):
                    flash('L\'ordre correct doit être une liste de nombres séparés par des virgules (ex: 1,0,2,3).', 'error')
                    return redirect(request.url)
                
                content = {
                    'draggable_items': filtered_drag_items,
                    'drop_zones': filtered_drop_zones,
                    'correct_order': correct_order
                }
                
            elif exercise_type == 'pairs':
                pairs = []
                pair_ids = set()
                
                # Récupérer tous les IDs de paires
                for key in request.form:
                    if key.startswith('pair_left_') and not key.endswith('_type'):
                        pair_id = key.split('_')[-1]
                        pair_ids.add(pair_id)
                
                # Construire les paires
                for pair_id in pair_ids:
                    left_content = ''
                    right_content = ''
                    left_type = request.form.get(f'pair_left_type_{pair_id}', 'text')
                    right_type = request.form.get(f'pair_right_type_{pair_id}', 'text')
                    
                    # Traiter l'élément de gauche
                    if left_type == 'image':
                        # Vérifier s'il y a un fichier uploadé
                        left_file_key = f'pair_left_image_{pair_id}'
                        if left_file_key in request.files:
                            file = request.files[left_file_key]
                            if file and file.filename and allowed_file(file.filename):
                                filename = secure_filename(file.filename)
                                unique_filename = generate_unique_filename(filename)
                                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                                file.save(file_path)
                                left_content = f'/static/uploads/{unique_filename}'
                        
                        # Si pas de fichier, utiliser l'URL
                        if not left_content:
                            left_content = request.form.get(f'pair_left_{pair_id}', '').strip()
                    else:
                        left_content = request.form.get(f'pair_left_{pair_id}', '').strip()
                    
                    # Traiter l'élément de droite
                    if right_type == 'image':
                        # Vérifier s'il y a un fichier uploadé
                        right_file_key = f'pair_right_image_{pair_id}'
                        if right_file_key in request.files:
                            file = request.files[right_file_key]
                            if file and file.filename and allowed_file(file.filename):
                                filename = secure_filename(file.filename)
                                unique_filename = generate_unique_filename(filename)
                                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                                file.save(file_path)
                                right_content = f'/static/uploads/{unique_filename}'
                        
                        # Si pas de fichier, utiliser l'URL
                        if not right_content:
                            right_content = request.form.get(f'pair_right_{pair_id}', '').strip()
                    else:
                        right_content = request.form.get(f'pair_right_{pair_id}', '').strip()
                    
                    if left_content and right_content:  # Ne garder que les paires complètes
                        pairs.append({
                            'id': pair_id,
                            'left': {'content': left_content, 'type': left_type},
                            'right': {'content': right_content, 'type': right_type}
                        })
                
                if not pairs:
                    flash('Veuillez ajouter au moins une paire.', 'error')
                    return redirect(request.url)
                
                content['pairs'] = pairs

            elif exercise_type == 'drag_and_drop':
                # Récupérer les éléments à glisser
                draggable_items = request.form.getlist('draggable_items[]')
                draggable_items = [item.strip() for item in draggable_items if item.strip()]
                
                # Récupérer les zones de dépôt
                drop_zones = request.form.getlist('drop_zones[]')
                drop_zones = [zone.strip() for zone in drop_zones if zone.strip()]
                
                if not draggable_items:
                    flash('Veuillez ajouter au moins un élément à glisser.', 'error')
                    return redirect(request.url)
                
                if not drop_zones:
                    flash('Veuillez ajouter au moins une zone de dépôt.', 'error')
                    return redirect(request.url)
                
                if len(draggable_items) != len(drop_zones):
                    flash('Le nombre d\'\u00e9léments à glisser doit égaler le nombre de zones de dépôt.', 'error')
                    return redirect(request.url)
                
                # L'ordre correct correspond à l'ordre de saisie (0, 1, 2, ...)
                correct_order = list(range(len(draggable_items)))
                
                content['draggable_items'] = draggable_items
                content['drop_zones'] = drop_zones
                content['correct_order'] = correct_order

            elif exercise_type == 'underline_words':
                # Récupérer les instructions
                instructions = request.form.get('underline_instructions', '').strip()
                if not instructions:
                    instructions = 'Soulignez tous les mots demandés dans chaque phrase.'
                
                # Récupérer les phrases et les mots à souligner
                sentences = request.form.getlist('underline_sentences[]')
                words_lists = request.form.getlist('underline_words[]')
                
                if not sentences:
                    flash('Veuillez ajouter au moins une phrase.', 'error')
                    return redirect(request.url)
                
                if not words_lists:
                    flash('Veuillez spécifier les mots à souligner pour chaque phrase.', 'error')
                    return redirect(request.url)
                
                if len(sentences) != len(words_lists):
                    flash('Chaque phrase doit avoir ses mots à souligner spécifiés.', 'error')
                    return redirect(request.url)
                
                # Construire les données des phrases
                words_data = []
                for i, (sentence, words_str) in enumerate(zip(sentences, words_lists)):
                    sentence = sentence.strip()
                    words_str = words_str.strip()
                    
                    if not sentence:
                        flash(f'La phrase {i+1} ne peut pas être vide.', 'error')
                        return redirect(request.url)
                    
                    if not words_str:
                        flash(f'Veuillez spécifier les mots à souligner pour la phrase {i+1}.', 'error')
                        return redirect(request.url)
                    
                    # Diviser les mots par virgules et nettoyer
                    words_to_underline = [word.strip() for word in words_str.split(',') if word.strip()]
                    
                    if not words_to_underline:
                        flash(f'Veuillez spécifier au moins un mot à souligner pour la phrase {i+1}.', 'error')
                        return redirect(request.url)
                    
                    words_data.append({
                        'text': sentence,
                        'words_to_underline': words_to_underline
                    })
                
                content['instructions'] = instructions
                content['words'] = words_data
                
                # Gestion de l'image optionnelle pour Souligner les mots
                if 'underline_words_image' in request.files:
                    image_file = request.files['underline_words_image']
                    if image_file and image_file.filename != '' and allowed_file(image_file.filename):
                        filename = secure_filename(image_file.filename)
                        unique_filename = generate_unique_filename(filename)
                        
                        # Créer le dossier uploads s'il n'existe pas
                        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                        os.makedirs(upload_folder, exist_ok=True)
                        
                        # Sauvegarder l'image
                        image_path = os.path.join(upload_folder, unique_filename)
                        image_file.save(image_path)
                        
                        # CORRECTION: Sauvegarder dans exercise_image_path pour que le template puisse l'afficher
                        if not exercise_image_path:  # Ne pas écraser si déjà défini
                            exercise_image_path = unique_filename
                        
                        # Ajouter le chemin de l'image au contenu (pour compatibilité)
                        content['image'] = f'static/uploads/{unique_filename}'
                        current_app.logger.debug(f'Image Souligner les mots sauvegardée: {unique_filename}')

            # Gestion de l'image de l'exercice (pour tous les types d'exercices)
            # exercise_image_path déjà initialisé plus haut pour underline_words
            if 'exercise_image' in request.files:
                image_file = request.files['exercise_image']
                if image_file and image_file.filename != '' and allowed_file(image_file.filename):
                    filename = secure_filename(image_file.filename)
                    unique_filename = generate_unique_filename(filename)
                    
                    # Créer le dossier uploads s'il n'existe pas
                    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                    os.makedirs(upload_folder, exist_ok=True)
                    
                    # Sauvegarder l'image
                    image_path = os.path.join(upload_folder, unique_filename)
                    image_file.save(image_path)
                    
                    # Stocker le chemin relatif pour la base de données
                    exercise_image_path = unique_filename
                    current_app.logger.info(f'Image exercice sauvegardée: {exercise_image_path}')

            # Créer l'exercice
            exercise = Exercise(
                title=title,
                description=description,
                exercise_type=exercise_type,
                content=json.dumps(content),
                subject=subject if subject else None,
                max_attempts=max_attempts,
                teacher_id=current_user.id,
                image_path=exercise_image_path
            )

            db.session.add(exercise)
            db.session.commit()
            
            # Associer l'exercice au cours sélectionné si spécifié
            if course_id:
                try:
                    from models import Course
                    course = Course.query.get(int(course_id))
                    if course and course.class_obj.teacher_id == current_user.id:
                        # Vérifier que l'enseignant possède bien ce cours
                        # Vérifier si l'association existe déjà
                        if exercise not in course.exercises:
                            course.exercises.append(exercise)
                            db.session.commit()
                            print(f'Exercice associé au cours: {course.title}')
                        else:
                            print(f'Exercice déjà associé au cours: {course.title}')
                    else:
                        print('Cours non trouvé ou accès non autorisé')
                except (ValueError, TypeError) as e:
                    print(f'Erreur lors de l\'association au cours: {e}')
                except Exception as e:
                    print(f'Erreur d\'association (contrainte unique): {e}')
                    # L'exercice est créé, l'association échoue mais ce n'est pas grave

            flash('Exercice créé avec succès !', 'success')
            return redirect(url_for('exercise.exercise_library'))

        except Exception as e:
            # Logs sécurisés sans caractères Unicode problématiques
            current_app.logger.error("=== ERREUR CREATION EXERCICE ===")
            current_app.logger.error(f"Type d'erreur: {type(e).__name__}")
            current_app.logger.error(f"Message: {str(e)}")
            current_app.logger.error(f"Traceback complet: {exc_info()}")
            try:
                current_app.logger.error(f"Form data recue: {dict(request.form)}")
            except UnicodeEncodeError:
                current_app.logger.error("Form data recue: [Unicode encoding error]")
            current_app.logger.error(f"Files recus: {list(request.files.keys())}")
            current_app.logger.error("=== FIN ERREUR ===")
            db.session.rollback()
            flash(f'Une erreur est survenue lors de la creation de l\'exercice: {str(e)}', 'error')
            return redirect(request.url)


@bp.route('/edit_exercise/<int:exercise_id>', methods=['GET', 'POST'])
@login_required
def edit_exercise(exercise_id):
    try:
        exercise = Exercise.query.get_or_404(exercise_id)
        
        # Vérifier que l'utilisateur est le propriétaire de l'exercice
        if not current_user.is_teacher or current_user.id != exercise.teacher_id:
            flash('Vous n\'avez pas la permission de modifier cet exercice.', 'error')
            return redirect(url_for('exercise.exercise_library'))
        
        # Vérifier si le template existe
        template = f'exercise_types/{exercise.exercise_type}_edit.html'
        try:
            current_app.jinja_env.get_template(template)
        except Exception:
            flash('Une erreur est survenue : le template de modification pour ce type d\'exercice est manquant.', 'error')
            return redirect(url_for('exercise.exercise_library'))

        if request.method == 'POST':
            print(f"[EDIT_POST_DEBUG] POST request received for exercise {exercise_id}")
            print(f"[EDIT_POST_DEBUG] Form data keys: {list(request.form.keys())}")
            print(f"[EDIT_POST_DEBUG] Form data: {dict(request.form)}")
            
            # Vérifier les champs requis
            title = request.form.get('title', '').strip()
            subject = request.form.get('subject', '').strip()
            description = request.form.get('description', '').strip()
            
            print(f"[EDIT_POST_DEBUG] Title: '{title}'")
            print(f"[EDIT_POST_DEBUG] Subject: '{subject}'")
            print(f"[EDIT_POST_DEBUG] Description: '{description}'")
            
            if not title:
                flash('Le titre est requis.', 'error')
                return render_template(f'exercise_types/{exercise.exercise_type}_edit.html', exercise=exercise, content=exercise.get_content())
            
            # Mettre à jour les champs de base
            exercise.title = title
            # Note: subject field removed as it doesn't exist in Exercise model
            exercise.description = description
            
            # Traiter le contenu selon le type d'exercice
            content = {}
            if exercise.exercise_type == 'qcm':
                print(f"[QCM_EDIT_DEBUG] Processing QCM edit...")
                
                # Utiliser la convention harmonisée : question_0, option_0_0, correct_0
                questions = []
                question_index = 0
                
                # Parcourir toutes les questions possibles
                while f'question_{question_index}' in request.form:
                    question_text = request.form.get(f'question_{question_index}', '').strip()
                    print(f"[QCM_EDIT_DEBUG] Question {question_index}: '{question_text}'")
                    
                    if question_text:  # Si la question n'est pas vide
                        # Récupérer les options pour cette question
                        options = []
                        option_index = 0
                        
                        while f'option_{question_index}_{option_index}' in request.form:
                            option_text = request.form.get(f'option_{question_index}_{option_index}', '').strip()
                            if option_text:
                                options.append(option_text)
                            option_index += 1
                        
                        print(f"[QCM_EDIT_DEBUG] Options for Q{question_index}: {options}")
                        
                        # Récupérer la réponse correcte
                        correct = request.form.get(f'correct_{question_index}')
                        print(f"[QCM_EDIT_DEBUG] Correct answer for Q{question_index}: '{correct}'")
                        
                        if options:  # Si au moins une option existe
                            questions.append({
                                'question': question_text,
                                'choices': options,  # Utiliser 'choices' pour compatibilité affichage
                                'correct_answer': int(correct) if correct is not None else 0
                            })
                    
                    question_index += 1
                
                print(f"[QCM_EDIT_DEBUG] Total questions found: {len(questions)}")
                
                if not questions:
                    flash('Veuillez ajouter au moins une question.', 'error')
                    return render_template('exercise_types/qcm_edit.html', exercise=exercise, content=exercise.get_content())
                
                content['questions'] = questions
            
            elif exercise.exercise_type == 'fill_in_blanks':
                sentences = request.form.getlist('sentences[]')
                words = request.form.getlist('words[]')
                
                if not sentences:
                    flash('Veuillez ajouter au moins une phrase.', 'error')
                    return render_template('exercise_types/fill_in_blanks_edit.html', exercise=exercise, content=exercise.get_content())
                
                if not words:
                    flash('Veuillez ajouter au moins un mot.', 'error')
                    return render_template('exercise_types/fill_in_blanks_edit.html', exercise=exercise, content=exercise.get_content())
                
                # Vérifier que chaque phrase contient au moins un trou
                for i, sentence in enumerate(sentences):
                    if '___' not in sentence:
                        flash(f'La phrase {i+1} ne contient pas de trous (utilisez ___ pour marquer les trous).', 'error')
                        return render_template('exercise_types/fill_in_blanks_edit.html', exercise=exercise, content=exercise.get_content())
                    
                    # Compter le nombre de trous dans la phrase
                    nb_blanks = sentence.count('___')
                
                # Vérifier qu'il y a assez de mots pour tous les trous
                total_blanks = sum(sentence.count('___') for sentence in sentences)
                if len(words) < total_blanks:
                    flash(f'Il n\'y a pas assez de mots ({len(words)}) pour remplir tous les trous ({total_blanks}).', 'error')
                    return render_template('exercise_types/fill_in_blanks_edit.html', exercise=exercise, content=exercise.get_content())
                
                content['sentences'] = sentences
                content['words'] = words
                
            elif exercise.exercise_type == 'word_search':
                # Traitement pour mots mêlés (édition)
                print(f"[WORD_SEARCH_EDIT_DEBUG] Processing word_search edit...")
                
                # Récupérer les mots à trouver
                words = request.form.getlist('words[]')
                # Filtrer les mots vides
                filtered_words = [word.strip().upper() for word in words if word.strip()]
                
                print(f"[WORD_SEARCH_EDIT_DEBUG] Words received: {words}")
                print(f"[WORD_SEARCH_EDIT_DEBUG] Filtered words: {filtered_words}")
                
                # Récupérer la taille de grille
                grid_size_value = request.form.get('grid_size', '8')
                try:
                    grid_size = int(grid_size_value)
                    if grid_size < 8 or grid_size > 20:
                        grid_size = 12  # Valeur par défaut
                except (ValueError, TypeError):
                    grid_size = 12  # Valeur par défaut
                
                print(f"[WORD_SEARCH_EDIT_DEBUG] Grid size: {grid_size}")
                
                # Validation
                if not filtered_words:
                    flash('Veuillez ajouter au moins un mot.', 'error')
                    return render_template('exercise_types/word_search_edit.html', exercise=exercise, content=exercise.get_content())
                
                # Vérifier que les mots ne sont pas trop longs pour la grille
                max_word_length = max(len(word) for word in filtered_words)
                if max_word_length > grid_size:
                    flash(f'Le mot le plus long ({max_word_length} lettres) est trop grand pour une grille {grid_size}x{grid_size}.', 'error')
                    return render_template('exercise_types/word_search_edit.html', exercise=exercise, content=exercise.get_content())
                
                # Construire le contenu
                content['words'] = filtered_words
                content['grid_size'] = {'width': grid_size, 'height': grid_size}
                content['instructions'] = 'Trouvez tous les mots cachés dans la grille ci-dessous.'
                
                print(f"[WORD_SEARCH_EDIT_DEBUG] Final content: {content}")
                
            elif exercise.exercise_type == 'drag_and_drop':
                # Traitement pour glisser-déposer (édition)
                drag_items = request.form.getlist('drag_items[]')
                drop_zones = request.form.getlist('drop_zones[]')
                correct_order_str = request.form.get('correct_order', '')
                
                # Filtrer les éléments vides
                filtered_drag_items = [item.strip() for item in drag_items if item.strip()]
                filtered_drop_zones = [zone.strip() for zone in drop_zones if zone.strip()]
                
                # Validation
                if not filtered_drag_items:
                    flash('Au moins un élément à glisser est requis.', 'error')
                    return render_template('exercise_types/drag_and_drop_edit.html', exercise=exercise, content=exercise.get_content())
                
                if not filtered_drop_zones:
                    flash('Au moins une zone de dépôt est requise.', 'error')
                    return render_template('exercise_types/drag_and_drop_edit.html', exercise=exercise, content=exercise.get_content())
                
                if len(filtered_drag_items) != len(filtered_drop_zones):
                    flash('Le nombre d\'éléments à glisser doit être égal au nombre de zones de dépôt.', 'error')
                    return render_template('exercise_types/drag_and_drop_edit.html', exercise=exercise, content=exercise.get_content())
                
                # Parser l'ordre correct
                try:
                    if correct_order_str.strip():
                        correct_order = [int(x.strip()) for x in correct_order_str.split(',') if x.strip()]
                        if len(correct_order) != len(filtered_drag_items):
                            flash('L\'ordre correct doit contenir autant d\'éléments que d\'éléments à glisser.', 'error')
                            return render_template('exercise_types/drag_and_drop_edit.html', exercise=exercise, content=exercise.get_content())
                    else:
                        # Générer un ordre par défaut si vide
                        correct_order = list(range(len(filtered_drag_items)))
                except (ValueError, AttributeError):
                    flash('L\'ordre correct doit être une liste de nombres séparés par des virgules (ex: 1,0,2,3).', 'error')
                    return render_template('exercise_types/drag_and_drop_edit.html', exercise=exercise, content=exercise.get_content())
                
                content['draggable_items'] = filtered_drag_items
                content['drop_zones'] = filtered_drop_zones
                content['correct_order'] = correct_order
                
            elif exercise.exercise_type == 'pairs':
                pairs = []
                pair_ids = set()
                
                # Récupérer tous les IDs de paires
                for key in request.form:
                    if key.startswith('pair_left_') and not key.endswith('_type'):
                        pair_id = key.split('_')[-1]
                        pair_ids.add(pair_id)
                
                # Construire les paires avec support des images
                for pair_id in pair_ids:
                    left_content = ''
                    right_content = ''
                    left_type = request.form.get(f'pair_left_type_{pair_id}', 'text')
                    right_type = request.form.get(f'pair_right_type_{pair_id}', 'text')
                    
                    # Gestion du contenu gauche (left)
                    if left_type == 'image':
                        if f'pair_left_image_{pair_id}' in request.files:
                            file = request.files[f'pair_left_image_{pair_id}']
                            if file and file.filename and allowed_file(file.filename):
                                filename = secure_filename(file.filename)
                                unique_filename = generate_unique_filename(filename)
                                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                                file.save(file_path)
                                left_content = f'/static/uploads/{unique_filename}'
                        if not left_content:
                            left_content = request.form.get(f'pair_left_{pair_id}', '').strip()
                    else:
                        left_content = request.form.get(f'pair_left_{pair_id}', '').strip()
                    
                    # Gestion du contenu droit (right)
                    if right_type == 'image':
                        if f'pair_right_image_{pair_id}' in request.files:
                            file = request.files[f'pair_right_image_{pair_id}']
                            if file and file.filename and allowed_file(file.filename):
                                filename = secure_filename(file.filename)
                                unique_filename = generate_unique_filename(filename)
                                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                                file.save(file_path)
                                right_content = f'/static/uploads/{unique_filename}'
                        if not right_content:
                            right_content = request.form.get(f'pair_right_{pair_id}', '').strip()
                    else:
                        right_content = request.form.get(f'pair_right_{pair_id}', '').strip()
                    
                    if left_content and right_content:  # Ne garder que les paires complètes
                        pairs.append({
                            'id': pair_id,
                            'left': {'content': left_content, 'type': left_type},
                            'right': {'content': right_content, 'type': right_type}
                        })
                
                if not pairs:
                    flash('Veuillez ajouter au moins une paire.', 'error')
                    return render_template('exercise_types/pairs_edit.html', exercise=exercise, content=exercise.get_content())
                
                content['pairs'] = pairs
            
            elif exercise.exercise_type == 'dictation':
                # Traitement pour les exercices de dictée (édition)
                print(f"[DICTATION_EDIT_DEBUG] Processing dictation edit...")
                
                # Récupérer les instructions
                instructions = request.form.get('dictation_instructions', '').strip()
                if not instructions:
                    instructions = 'Écoutez attentivement chaque phrase et écrivez ce que vous entendez.'
                
                # Récupérer les phrases
                sentences = request.form.getlist('dictation_sentences[]')
                sentences = [s.strip() for s in sentences if s.strip()]
                
                print(f"[DICTATION_EDIT_DEBUG] Instructions: {instructions}")
                print(f"[DICTATION_EDIT_DEBUG] Sentences: {sentences}")
                
                # Validation
                if not sentences:
                    flash('Veuillez ajouter au moins une phrase.', 'error')
                    return render_template('exercise_types/dictation_edit.html', exercise=exercise, content=exercise.get_content())
                
                # Gestion des fichiers audio
                audio_files = []
                for i in range(len(sentences)):
                    audio_file = None
                    
                    # Vérifier s'il y a un nouveau fichier audio
                    if f'dictation_audio_{i}' in request.files:
                        file = request.files[f'dictation_audio_{i}']
                        if file and file.filename:
                            # Vérifier l'extension du fichier
                            if file.filename.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a')):
                                filename = secure_filename(file.filename)
                                unique_filename = generate_unique_filename(filename)
                                
                                # Créer le dossier audio s'il n'existe pas
                                audio_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'audio')
                                os.makedirs(audio_folder, exist_ok=True)
                                
                                file_path = os.path.join(audio_folder, unique_filename)
                                file.save(file_path)
                                audio_file = f'/static/uploads/audio/{unique_filename}'
                                print(f"[DICTATION_EDIT_DEBUG] Audio file {i} saved: {audio_file}")
                            else:
                                flash(f'Le fichier audio {i+1} doit être au format MP3, WAV, OGG ou M4A.', 'error')
                                return render_template('exercise_types/dictation_edit.html', exercise=exercise, content=exercise.get_content())
                    
                    # Si pas de nouveau fichier, garder l'ancien s'il existe
                    if not audio_file:
                        existing_content = exercise.get_content()
                        existing_audio_files = existing_content.get('audio_files', [])
                        if i < len(existing_audio_files):
                            audio_file = existing_audio_files[i]
                    
                    audio_files.append(audio_file)
                
                print(f"[DICTATION_EDIT_DEBUG] Audio files: {audio_files}")
                
                # Construire le contenu
                content = {
                    'instructions': instructions,
                    'sentences': sentences,
                    'audio_files': audio_files
                }
                
                print(f"[DICTATION_EDIT_DEBUG] Final content: {content}")
            
            # Sauvegarder les modifications
            exercise.content = json.dumps(content)
            db.session.commit()
            
            flash('L\'exercice a été modifié avec succès.', 'success')
            return redirect(url_for('exercise.exercise_library'))
        
        # Méthode GET : afficher le formulaire d'édition
        print(f"[EDIT_DEBUG] Exercise ID: {exercise_id}")
        print(f"[EDIT_DEBUG] Exercise type: '{exercise.exercise_type}'")
        print(f"[EDIT_DEBUG] Exercise title: '{exercise.title}'")
        
        template_path = f'exercise_types/{exercise.exercise_type}_edit.html'
        print(f"[EDIT_DEBUG] Template path: '{template_path}'")
        
        content = exercise.get_content()
        print(f"[EDIT_DEBUG] Content type: {type(content)}")
        print(f"[EDIT_DEBUG] Content keys: {list(content.keys()) if isinstance(content, dict) else 'Not a dict'}")
        
        attempts_count = ExerciseAttempt.query.filter_by(exercise_id=exercise_id).count()
        print(f"[EDIT_DEBUG] Attempts count: {attempts_count}")
        
        try:
            return render_template(template_path, exercise=exercise, content=content, attempts_count=attempts_count)
        except Exception as template_error:
            print(f"[EDIT_DEBUG] Template error: {str(template_error)}")
            flash(f'Une erreur est survenue : le template de modification pour ce type d\'exercice est manquant.', 'error')
            return redirect(url_for('exercise.exercise_library'))
        
    except Exception as e:
        db.session.rollback()
        print(f'Erreur lors de la modification de l\'exercice {exercise_id}: {str(e)}')
        flash('Une erreur est survenue lors de la modification de l\'exercice.', 'error')
        
        # Essayer de récupérer le contenu même en cas d'erreur
        try:
            content = exercise.get_content()
        except:
            content = {'questions': []}  # Contenu par défaut si impossible de récupérer
        
        attempts_count = 0  # Valeur par défaut
        return render_template(f'exercise_types/{exercise.exercise_type}_edit.html', 
                             exercise=exercise, content=content, attempts_count=attempts_count)

@bp.route('/test_exercise_library')
@login_required
def test_exercise_library():
    # Route de test pour isoler le problème de routage
    exercises = Exercise.query.order_by(desc(Exercise.created_at)).all()
    return render_template('test_exercise_library.html', exercises=exercises)

@bp.route('/exercise_library')
@login_required
def exercise_library():
    # Récupérer les paramètres de filtrage
    search_query = request.args.get('search', '').strip()
    selected_type = request.args.get('type', '')
    selected_subject = request.args.get('subject', '')
    
    # Construire la requête de base
    query = Exercise.query
    
    # Appliquer les filtres
    if search_query:
        query = query.filter(Exercise.title.ilike(f'%{search_query}%'))
    if selected_type:
        query = query.filter(Exercise.exercise_type == selected_type)
    if selected_subject:
        query = query.filter(Exercise.subject == selected_subject)
    
    # Trier par date de création décroissante
    exercises = query.order_by(desc(Exercise.created_at)).all()
    
    # Définir les types d'exercices disponibles
    exercise_types = [
        ('qcm', 'QCM'),
        ('word_search', 'Mots mêlés'),
        ('pairs', 'Paires'),
        ('fill_in_blanks', 'Texte à trous'),
        ('underline_words', 'Souligner les mots'),
        ('dictation', 'Dictée')
    ]
    
    return render_template('exercise_library.html',
                           exercises=exercises,
                           exercise_types=exercise_types,
                           search_query=search_query,
                           selected_type=selected_type,
                           selected_subject=selected_subject)



@bp.route('/exercise/<int:exercise_id>/submit', methods=['POST'])
@login_required
def submit_answer(exercise_id):
    try:
        exercise = db.get_or_404(Exercise, exercise_id)
        content = exercise.get_content()
        
        # Vérifier si le type d'exercice est supporté
        supported_types = [t[0] for t in Exercise.EXERCISE_TYPES]  # Utilise la liste des types du modèle Exercise
        if exercise.exercise_type not in supported_types:
            print(f'Type d\'exercice non supporté: {exercise.exercise_type}')
            flash(f'Le type d\'exercice {exercise.exercise_type} n\'est pas pris en charge.', 'error')
            return render_template('exercise_not_found.html'), 404
            
        # Vérifier la structure du contenu
        if not content:
            print('Contenu invalide: contenu vide ou None')
            flash('Erreur: Le contenu de l\'exercice est invalide.', 'error')
            return render_template('exercise_not_found.html'), 404
            
        if exercise.exercise_type == 'qcm':
            # Vérifier la structure du contenu
            if not content or 'questions' not in content:
                print('Contenu QCM invalide: clé "questions" manquante')
                flash('Erreur: Le contenu de l\'exercice est invalide.', 'error')
                return render_template('exercise_not_found.html'), 404
            
            # Récupérer les réponses de l'utilisateur
            user_answers = []
            for i in range(len(content['questions'])):
                answer = request.form.get(f'answer_{i}')
                if answer is not None:
                    try:
                        user_answers.append(int(answer))
                    except ValueError:
                        user_answers.append(-1)  # -1 pour une réponse invalide
                else:
                    user_answers.append(-1)  # -1 pour une absence de réponse
            
            # Vérifier que toutes les questions ont une réponse
            if -1 in user_answers:
                flash('Veuillez répondre à toutes les questions.', 'error')
                return redirect(url_for('view_exercise', exercise_id=exercise_id))
            
            # Calculer le score
            correct_count = 0
            total_questions = len(content['questions'])
            feedback = []
            
            for i, (question, user_answer) in enumerate(zip(content['questions'], user_answers)):
                is_correct = user_answer == question['correct_answer']
                if is_correct:
                    correct_count += 1
                
                feedback.append({
                    'question': question['text'],
                    'student_answer': question['options'][user_answer] if user_answer >= 0 else 'Pas de réponse',
                    'correct_answer': question['options'][question['correct_answer']],
                    'is_correct': is_correct
                })
            
            score = (correct_count / total_questions) * 100 if total_questions > 0 else 0
            
        elif exercise.exercise_type == 'pairs':
            # Vérifier la structure du contenu
            if not content or 'pairs' not in content:
                print('Contenu Paires invalide: clé "pairs" manquante')
                flash('Erreur: Le contenu de l\'exercice est invalide.', 'error')
                return render_template('exercise_not_found.html'), 404
            
            # Récupérer les paires soumises par l'utilisateur
            submitted_pairs = []
            for key, value in request.form.items():
                if key.startswith('pair_'):
                    try:
                        pair_index = int(key.split('_')[1])
                        right_index = int(value)
                        submitted_pairs.append((pair_index, right_index))
                    except (ValueError, TypeError):
                        continue
            
            # Vérifier que toutes les paires ont été associées
            if len(submitted_pairs) != len(content['pairs']):
                flash('Veuillez associer toutes les paires.', 'error')
                return redirect(url_for('view_exercise', exercise_id=exercise_id))
            
            # Trier les paires par index
            submitted_pairs.sort()
            
            # Vérifier les correspondances
            correct_count = 0
            total_pairs = len(content['pairs'])
            feedback = []
            
            for left_idx, right_idx in submitted_pairs:
                is_correct = left_idx == right_idx
                if is_correct:
                    correct_count += 1
                
                feedback.append({
                    'left': content['pairs'][left_idx]['left'],
                    'right': content['pairs'][right_idx]['right'],
                    'correct_right': content['pairs'][left_idx]['right'],
                    'is_correct': is_correct
                })
            
            score = (correct_count / total_pairs) * 100 if total_pairs > 0 else 0
            
        elif exercise.exercise_type == 'word_search':
            print(f'[WORD_SEARCH_SUBMIT_DEBUG] Processing word_search exercise {exercise_id}')
            print(f'[WORD_SEARCH_SUBMIT_DEBUG] Form data: {dict(request.form)}')
            
            # Récupérer les mots trouvés par l'utilisateur depuis les champs word_0, word_1, etc.
            found_words = []
            for key, value in request.form.items():
                if key.startswith('word_') and value:
                    word = value.strip().upper()
                    if word and word != 'UNDEFINED':  # Éviter les valeurs vides ou non définies
                        found_words.append(word)
            
            print(f'[WORD_SEARCH_SUBMIT_DEBUG] Found words by user: {found_words}')
            
            target_words = content.get('words', [])
            print(f'[WORD_SEARCH_SUBMIT_DEBUG] Target words: {target_words}')
            
            if not target_words:
                print('Contenu Mots mêlés invalide: liste de mots vide')
                flash('Erreur: Le contenu de l\'exercice est invalide.', 'error')
                return render_template('exercise_not_found.html'), 404
            
            # Calculer le score
            correct_words = [word for word in found_words if word in target_words]
            incorrect_words = [word for word in found_words if word not in target_words]
            missed_words = [word for word in target_words if word not in found_words]
            
            correct_count = len(correct_words)
            total_words = len(target_words)
            score = (correct_count / total_words) * 100 if total_words > 0 else 0
            
            print(f'[WORD_SEARCH_SUBMIT_DEBUG] Correct words: {correct_words}')
            print(f'[WORD_SEARCH_SUBMIT_DEBUG] Incorrect words: {incorrect_words}')
            print(f'[WORD_SEARCH_SUBMIT_DEBUG] Missed words: {missed_words}')
            print(f'[WORD_SEARCH_SUBMIT_DEBUG] Score: {correct_count}/{total_words} = {score}%')
            
            feedback = {
                'correct_words': correct_words,
                'incorrect_words': incorrect_words,
                'missed_words': missed_words,
                'total_found': len(found_words),
                'total_correct': correct_count,
                'total_words': total_words
            }
            
        elif exercise.exercise_type == 'fill_in_blanks':
            # Log du contenu de l'exercice
            current_app.logger.info(f'Contenu de l\'exercice: {json.dumps(content, indent=2)}')
            current_app.logger.info(f'Données du formulaire: {json.dumps(dict(request.form), indent=2)}')
            
            # Récupérer les réponses
            answers = {}
            for key, value in request.form.items():
                if key.startswith('answer_'):
                    try:
                        blank_index = int(key.split('_')[1])
                        answers[blank_index] = value.strip()
                        current_app.logger.info(f'Réponse trouvée: index={blank_index}, valeur={value}')
                    except (ValueError, TypeError) as e:
                        current_app.logger.error(f'Erreur de parsing pour {key}: {str(e)}')
                        continue
            
            if not content.get('sentences') or not content.get('words'):
                current_app.logger.error('Contenu Texte à trous invalide: clés "sentences" ou "words" manquantes')
                current_app.logger.error(f'Contenu disponible: {json.dumps(content, indent=2)}')
                flash('Erreur: Le contenu de l\'exercice est invalide.', 'error')
                return render_template('exercise_not_found.html'), 404
            
            correct_count = 0
            total_blanks = 0
            feedback = []
            
            # Pour chaque phrase
            for i, sentence in enumerate(content['sentences']):
                current_app.logger.info(f'Traitement de la phrase {i}: {sentence}')
                
                # Extraire le texte de la phrase selon sa structure
                if isinstance(sentence, dict) and 'text' in sentence:
                    sentence_text = sentence['text']
                else:
                    sentence_text = sentence
                current_app.logger.info(f'Texte de la phrase: {sentence_text}')
                
                # Trouver tous les trous dans la phrase
                blanks = sentence_text.count('___')
                total_blanks += blanks
                current_app.logger.info(f'Nombre de trous trouvés: {blanks}')

                # Séparer la phrase en parties
                parts = sentence_text.split('___')
                current_app.logger.info(f'Parties de la phrase: {parts}')
                
                # Vérifier si la réponse est correcte pour cette position
                student_answer = answers.get(i, '')
                current_app.logger.info(f'Réponse de l\'étudiant: {student_answer}')
                
                if student_answer in content['words']:
                    current_app.logger.info(f'Réponse {student_answer} trouvée dans les mots disponibles')
                    # Reconstruire la phrase avec la réponse
                    reconstructed = parts[0]
                    for j in range(1, len(parts)):
                        reconstructed += student_answer + parts[j]
                    
                    current_app.logger.info(f'Phrase reconstruite: {reconstructed}')
                    current_app.logger.info(f'Phrase attendue: {sentence_text.replace("___", student_answer)}')
                    
                    # Vérifier si la réponse est correcte à cette position
                    if reconstructed.strip() == sentence_text.replace('___', student_answer).strip():
                        correct_count += 1
                        current_app.logger.info('Réponse correcte !')
                    else:
                        current_app.logger.info('Réponse incorrecte')
                else:
                    current_app.logger.info(f'Réponse {student_answer} non trouvée dans les mots disponibles: {content["words"]}')

                feedback.append({
                    'sentence': sentence_text,
                    'student_answer': student_answer,
                    'is_correct': student_answer in content['words'] and \
                                 reconstructed.strip() == sentence_text.replace('___', student_answer).strip()
                })
            
            score = (correct_count / total_blanks) * 100 if total_blanks > 0 else 0
        else:
            flash(f'Le type d\'exercice {exercise.exercise_type} n\'est pas pris en charge.', 'error')
            return redirect(url_for('view_exercise', exercise_id=exercise_id))
        
        # Récupérer le course_id s'il est présent dans la requête
        course_id = request.args.get('course_id', type=int)
        
        # Créer une nouvelle tentative
        attempt = ExerciseAttempt(
            exercise_id=exercise_id,
            student_id=current_user.id,
            course_id=course_id,  # Peut être None si pas de cours associé
            score=score,
            feedback=json.dumps(feedback),
            completed=True
        )
        db.session.add(attempt)
        db.session.commit()
        
        flash(f'Score: {score:.1f}%', 'success' if score >= 50 else 'warning')
        return redirect(url_for('view_exercise', exercise_id=exercise_id))
            
    except Exception as e:
        # Log détaillé de l'erreur
        current_app.logger.error('='*50)
        current_app.logger.error('ERREUR DE SOUMISSION')
        current_app.logger.error(f'Exercise ID: {exercise_id}')
        current_app.logger.error(f'Type d\'erreur: {type(e).__name__}')
        current_app.logger.error(f'Message d\'erreur: {str(e)}')
        current_app.logger.error('Traceback complet:')
        current_app.logger.error(exc_info())
        
        # Log des données de la requête
        current_app.logger.error('\nDonnées de la requête:')
        current_app.logger.error(f'Method: {request.method}')
        current_app.logger.error(f'Form data: {dict(request.form)}')
        current_app.logger.error(f'Args: {dict(request.args)}')
        
        # Log du contenu de l'exercice
        try:
            exercise = db.get_or_404(Exercise, exercise_id)
            current_app.logger.error('\nDonnées de l\'exercice:')
            current_app.logger.error(f'Type: {exercise.exercise_type}')
            current_app.logger.error(f'Content: {exercise.content}')
        except Exception as ex:
            current_app.logger.error(f'\nErreur lors de la récupération de l\'exercice: {str(ex)}')
        
        current_app.logger.error('='*50)
        
        flash('Une erreur est survenue lors de la soumission de l\'exercice.', 'error')
        return redirect(url_for('view_exercise', exercise_id=exercise_id))

# Route supprimée car dupliquée avec app.py - utiliser la route principale dans app.py

@bp.route('/delete_exercise/<int:exercise_id>', methods=['POST'])
@login_required
def delete_exercise(exercise_id):
    try:
        # Verify CSRF token
        csrf_token = request.form.get('csrf_token')
        if not csrf_token:
            flash('Token de sécurité invalide.', 'error')
            return redirect(url_for('exercise.exercise_library'))

        exercise = Exercise.query.get_or_404(exercise_id)
        
        # Vérifier que l'utilisateur est l'enseignant qui a créé l'exercice
        if not current_user.is_teacher or (current_user.id != exercise.teacher_id):
            flash('Vous n\'avez pas la permission de supprimer cet exercice.', 'error')
            return redirect(url_for('exercise.exercise_library'))
        
        # Supprimer toutes les tentatives liées à cet exercice
        ExerciseAttempt.query.filter_by(exercise_id=exercise.id).delete()
        
        # Supprimer l'exercice
        db.session.delete(exercise)
        db.session.commit()
        
        flash('Exercice supprimé avec succès !', 'success')
        return redirect(url_for('exercise.exercise_library'))
        
    except Exception as e:
        db.session.rollback()
        print(f'Erreur lors de la suppression de l\'exercice {exercise_id}: {str(e)}\n{exc_info()}')
        flash('Une erreur est survenue lors de la suppression de l\'exercice.', 'error')
        return redirect(url_for('exercise.exercise_library'))


@bp.route('/preview/<int:exercise_id>')
@login_required
@teacher_required
def preview_exercise(exercise_id):
    try:
        exercise = Exercise.query.get_or_404(exercise_id)
        
        # Vérifier que l'utilisateur est le propriétaire de l'exercice
        if not current_user.is_teacher or current_user.id != exercise.teacher_id:
            flash('Vous n\'avez pas la permission de prévisualiser cet exercice.', 'error')
            return redirect(url_for('exercise.exercise_library'))
        
        # Vérifier si le type d'exercice est supporté
        supported_types = [t[0] for t in Exercise.EXERCISE_TYPES]
        if exercise.exercise_type not in supported_types:
            flash(f'Le type d\'exercice {exercise.exercise_type} n\'est pas pris en charge.', 'error')
            return redirect(url_for('exercise.exercise_library'))

        # Vérifier si le template existe
        template = f'exercise_types/{exercise.exercise_type}.html'
        try:
            current_app.jinja_env.get_template(template)
        except Exception:
            flash('Une erreur est survenue : le template de prévisualisation pour ce type d\'exercice est manquant.', 'error')
            return redirect(url_for('exercise.exercise_library'))

        # Charger le contenu de l'exercice
        content = exercise.get_content()
        
        # Rendre le template approprié selon le type d'exercice
        if exercise.exercise_type == 'qcm':
            return render_template('exercise_types/qcm_preview.html', exercise=exercise, content=content)
        elif exercise.exercise_type == 'word_search':
            return render_template('exercise_types/word_search_preview.html', exercise=exercise, content=content)
        elif exercise.exercise_type == 'pairs':
            return render_template('exercise_types/pairs_preview.html', exercise=exercise, content=content)
        else:
            flash('Type d\'exercice non pris en charge pour la prévisualisation.', 'error')
            return redirect(url_for('exercise.exercise_library'))
            
    except Exception as e:
        current_app.logger.error(f'Erreur lors de la prévisualisation de l\'exercice: {str(e)}\n{exc_info()}')
        flash('Une erreur est survenue lors de la prévisualisation de l\'exercice.', 'error')
        return redirect(url_for('exercise.exercise_library'))


        return redirect(url_for('exercise.exercise_library'))

@bp.route('/feedback/<int:exercise_id>/<int:attempt_id>')
@login_required
def view_feedback(exercise_id, attempt_id):
    try:
        exercise = Exercise.query.get_or_404(exercise_id)
        attempt = ExerciseAttempt.query.get_or_404(attempt_id)
        
        # Vérifier que l'utilisateur est soit le propriétaire de l'exercice, soit l'étudiant qui a fait la tentative
        if not (current_user.is_teacher and current_user.id == exercise.teacher_id) and \
           not (current_user.id == attempt.student_id):
            flash('Vous n\'avez pas la permission de voir ce feedback.', 'error')
            return redirect(url_for('exercise.exercise_library'))
        
        # Vérifier que la tentative correspond bien à l'exercice
        if attempt.exercise_id != exercise.id:
            flash('La tentative ne correspond pas à l\'exercice spécifié.', 'error')
            return redirect(url_for('exercise.exercise_library'))
        
        # Vérifier si le type d'exercice est supporté
        supported_types = [t[0] for t in Exercise.EXERCISE_TYPES]
        if exercise.exercise_type not in supported_types:
            flash(f'Le type d\'exercice {exercise.exercise_type} n\'est pas pris en charge.', 'error')
            return redirect(url_for('exercise.exercise_library'))

        # Charger le feedback
        feedback = json.loads(attempt.feedback) if attempt.feedback else None
        
        # Utiliser le template de feedback générique
        return render_template(
            'feedback.html',
            exercise=exercise,
            attempt=attempt,
            feedback=feedback,
            answers=json.loads(attempt.answers) if attempt.answers else None
        )
        
    except Exception as e:
        current_app.logger.error(f'Erreur lors de l\'affichage du feedback: {str(e)}\n{exc_info()}')
        flash('Une erreur est survenue lors de l\'affichage du feedback.', 'error')
        return redirect(url_for('exercise.exercise_library'))

@bp.route('/stats/<int:exercise_id>')
@login_required
def exercise_stats(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    course_id = request.args.get('course_id', type=int)
    
    # Vérifier que l'enseignant a le droit d'accéder à ces statistiques
    has_access = False
    
    # Vérifier si l'enseignant est le créateur de l'exercice
    if exercise.teacher_id == current_user.id:
        has_access = True
    else:
        # Vérifier si l'exercice est utilisé dans l'une des classes de l'enseignant
        teacher_classes = Class.query.filter_by(teacher_id=current_user.id).all()
        for class_obj in teacher_classes:
            for course in class_obj.courses:
                if exercise in course.exercises:
                    has_access = True
                    break
            if has_access:
                break
    
    if not has_access:
        flash("Vous n'avez pas l'autorisation de voir ces statistiques.", "error")
        return redirect(url_for('index'))
    
    # Récupérer les statistiques
    stats = exercise.get_stats(course_id)
    
    # Récupérer les informations du cours si spécifié
    course = Course.query.get(course_id) if course_id else None
    
    # Ajouter les informations de progression pour chaque étudiant
    student_progress = []
    
    if course:
        # Pour un cours spécifique, ne montrer que les étudiants de la classe associée
        students_to_show = course.class_obj.students
    else:
        # Sans cours spécifié, montrer tous les étudiants qui ont déjà fait l'exercice
        attempts = ExerciseAttempt.query.filter_by(exercise_id=exercise.id).all()
        student_ids = list(set([a.student_id for a in attempts]))  # Utiliser set() pour éliminer les doublons
        students_to_show = User.query.filter(User.id.in_(student_ids), User.role=='student').all()
    
    for student in students_to_show:
        progress = exercise.get_student_progress(student.id)
        if progress:
            student_progress.append({
                'student': student,
                'progress': progress
            })
    
    return render_template('exercise_stats.html',
                         exercise=exercise,
                         course=course,
                         stats=stats,
                         student_progress=student_progress)

def init_app(app):
    app.register_blueprint(bp)
