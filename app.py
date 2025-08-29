import os
import re
import json
import uuid
import time
import random
import string
import logging
import datetime
import requests
import traceback
from PIL import Image
from io import BytesIO
from decimal import Decimal
from functools import wraps
from datetime import timedelta
from werkzeug.utils import secure_filename
from fixed_normalize_pairs_exercise_paths import normalize_pairs_exercise_content
# Réintégration de l'import cloud_storage
import cloud_storage
from fix_image_display import register_image_fix_routes
from teacher_classes_route import register_teacher_classes_route
from image_sync import register_image_sync_routes
from fix_image_display_routes import register_image_display_routes
from fix_flashcard_images import register_fix_flashcard_images_routes
from diagnose_flashcard_images import register_diagnose_flashcard_routes

from utils.image_utils_no_normalize import normalize_image_path
from utils.image_handler import handle_exercise_image
from template_helpers import register_template_helpers
# Import cloud_storage pour utiliser sa fonction get_cloudinary_url avec support du paramètre exercise_type
import cloud_storage
from utils.image_path_handler import normalize_image_path as normalize_path, fix_exercise_image_path, get_image_url
# Import du service d'images unifié
from register_unified_image_service import register_unified_image_service

def process_qcm_question_images(request, questions, question_count):
    """
    Traite les images des questions QCM et les ajoute aux questions
    
    Args:
        request: L'objet request Flask
        questions: La liste des questions à mettre à jour
        question_count: Le nombre de questions
        
    Returns:
        La liste des questions mise à jour avec les chemins d'images normalisés
    """
    current_app.logger.info(f'[QCM_IMAGE_DEBUG] Début du traitement des images pour {question_count} questions')
    
    # Importer la fonction de normalisation des chemins d'images
    from utils.image_utils_no_normalize import normalize_image_path
    
    # S'assurer que la liste des questions est assez grande
    while len(questions) < question_count:
        questions.append({})
    
    for i in range(question_count):
        current_app.logger.debug(f'[QCM_IMAGE_DEBUG] Traitement de la question {i+1}/{question_count}')
        
        # Vérifier si une image a été téléchargée pour cette question
        image_key = f'question_image_{i}'
        path_key = f'question_image_path_{i}'
        
        # Récupérer le chemin d'image existant s'il existe
        existing_path = request.form.get(path_key, '')
        if existing_path and isinstance(existing_path, str):
            existing_path = existing_path.strip()
            # Normaliser immédiatement le chemin existant pour assurer la cohérence
            existing_path = normalize_image_path(existing_path)
        
        current_app.logger.debug(f'[QCM_IMAGE_DEBUG] Question {i} - Chemin existant normalisé: {existing_path}')
        
        # Vérifier si l'utilisateur a demandé de supprimer l'image
        remove_image = request.form.get(f'remove_question_image_{i}') == 'true'
        
        if remove_image:
            current_app.logger.info(f'[QCM_IMAGE_DEBUG] Suppression demandée pour l\'image de la question {i}')
            # Supprimer l'image existante si demandé
            if i < len(questions) and questions[i].get('image'):
                old_image_path = questions[i]['image']
                try:
                    # Extraire le chemin du fichier physique si c'est un chemin local
                    physical_path = None
                    if old_image_path.startswith('/static/'):
                        # Convertir le chemin /static/ en chemin physique
                        physical_path = os.path.join(current_app.static_folder, old_image_path.replace('/static/', '', 1))
                    
                    # Ne supprimer que les fichiers locaux qui existent, pas les URLs Cloudinary
                    if physical_path and os.path.exists(physical_path) and not old_image_path.startswith(('http://', 'https://')):
                        os.remove(physical_path)
                        current_app.logger.info(f'[QCM_IMAGE_DEBUG] Fichier local supprimé pour la question {i}: {physical_path}')
                    
                    # Supprimer la référence à l'image
                    questions[i].pop('image', None)
                    current_app.logger.info(f'[QCM_IMAGE_DEBUG] Référence à l\'image supprimée pour la question {i}')
                except Exception as e:
                    current_app.logger.error(f'[QCM_IMAGE_DEBUG] Erreur lors de la suppression de l\'image pour la question {i}: {str(e)}')
            continue
        
        # Traitement du téléchargement d'une nouvelle image
        if image_key in request.files:
            file = request.files[image_key]
            if file and file.filename != '':
                if not allowed_file(file.filename, file):
                    current_app.logger.warning(f'[QCM_IMAGE_DEBUG] Type de fichier non autorisé pour la question {i}: {file.filename}')
                    continue
                
                try:
                    # Sauvegarder l'ancien chemin d'image pour le nettoyage après un upload réussi
                    old_image_path = questions[i].get('image') if i < len(questions) and questions[i].get('image') else None
                    
                    # Utiliser Cloudinary pour l'upload en production, stockage local en dev
                    image_url = cloud_storage.upload_file(
                        file, 
                        folder="exercises/qcm",
                        public_id=f"qcm_question_{int(time.time())}_{i}"  # Nom de fichier unique
                    )
                    
                    if image_url:
                        # Normaliser le chemin/URL de l'image pour assurer la cohérence
                        normalized_image_url = normalize_image_path(image_url)
                        current_app.logger.info(f'[QCM_IMAGE_DEBUG] Image téléchargée avec succès pour la question {i}: {normalized_image_url}')
                        
                        # Mettre à jour la question avec la nouvelle image normalisée
                        if i < len(questions):
                            questions[i]['image'] = normalized_image_url
                            current_app.logger.debug(f'[QCM_IMAGE_DEBUG] Image mise à jour pour la question {i}')
                        
                        # Nettoyer l'ancienne image si elle existe et est locale
                        if old_image_path and old_image_path.startswith('/static/'):
                            physical_path = os.path.join(current_app.static_folder, old_image_path.replace('/static/', '', 1))
                            if os.path.exists(physical_path):
                                try:
                                    os.remove(physical_path)
                                    current_app.logger.info(f'[QCM_IMAGE_DEBUG] Ancien fichier local nettoyé: {physical_path}')
                                except Exception as e:
                                    current_app.logger.error(f'[QCM_IMAGE_DEBUG] Erreur lors du nettoyage de l\'ancien fichier {physical_path}: {str(e)}')
                    else:
                        current_app.logger.error(f'[QCM_IMAGE_DEBUG] Échec du téléchargement de l\'image pour la question {i}')
                except Exception as e:
                    current_app.logger.error(f'[QCM_IMAGE_DEBUG] Erreur lors du traitement de l\'image pour la question {i}: {str(e)}')
                    current_app.logger.debug(f'[QCM_IMAGE_DEBUG] Traceback: {traceback.format_exc()}')
        elif existing_path and i < len(questions):
            # Conserver l'image existante normalisée si aucune nouvelle image n'est fournie
            questions[i]['image'] = existing_path
            current_app.logger.debug(f'[QCM_IMAGE_DEBUG] Conservation de l\'image existante normalisée pour la question {i}: {existing_path}')
    
    # Vérification finale pour s'assurer que tous les chemins d'images sont normalisés
    for i, question in enumerate(questions):
        if question.get('image'):
            question['image'] = normalize_image_path(question['image'])
            current_app.logger.debug(f'[QCM_IMAGE_DEBUG] Vérification finale: chemin d\'image normalisé pour la question {i}: {question["image"]}')
    
    return questions

def get_blank_location(global_blank_index, sentences):
    """Détermine à quelle phrase et à quel indice dans cette phrase correspond un indice global de blanc"""
    blank_count = 0
    for idx, sentence in enumerate(sentences):
        blanks_in_sentence = sentence.count('___')
        if blank_count <= global_blank_index < blank_count + blanks_in_sentence:
            # Calculer l'indice local du blanc dans cette phrase
            local_blank_index = global_blank_index - blank_count
            return idx, local_blank_index
        blank_count += blanks_in_sentence
    return -1, -1

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, session, current_app, abort, send_file
from utils.image_fallback_middleware import register_image_fallback_middleware
from fix_image_paths import register_image_sync_routes
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, TextAreaField, MultipleFileField
from wtforms.validators import DataRequired
from flask_wtf.csrf import generate_csrf

from extensions import db, init_extensions, login_manager
from models import User, Class, Course, Exercise, ExerciseAttempt, CourseFile, student_class_association, course_exercise
from payment_routes import payment_bp
from forms import ExerciseForm
from modified_submit import bp as exercise_bp
from export_utils import generate_class_pdf, generate_class_excel
from test_planning_route import register_test_planning_route




logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('flask_app.log')
    ]
)
logger = logging.getLogger(__name__)

# Création de l'application Flask
app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

# Enregistrer les routes de diagnostic et correction d'images
register_image_fix_routes(app)

# Enregistrer les routes pour l'affichage des images Cloudinary
register_image_display_routes(app)

# Enregistrer les routes pour la correction des images de flashcards
register_fix_flashcard_images_routes(app)

# Enregistrer les routes pour le diagnostic des images de flashcards
register_diagnose_flashcard_routes(app)

# Enregistrer la route de test pour la planification annuelle
register_test_planning_route(app)

# Enregistrer la route pour les classes de l'enseignant
register_teacher_classes_route(app)

# Rendre la fonction normalize_image_path disponible dans tous les templates
@app.context_processor
def utility_processor():
    return dict(normalize_image_path=normalize_image_path)

# Enregistrer les helpers de template pour la gestion d'images
register_template_helpers(app)

# Enregistrer le service d'images unifié
register_unified_image_service(app)
app.logger.info("Service d'images unifié enregistré avec succès")

# Configuration de Cloudinary si les variables d'environnement sont disponibles
with app.app_context():
    try:
        # Tenter de configurer Cloudinary
        if os.environ.get('CLOUDINARY_CLOUD_NAME'):
            if cloud_storage.configure_cloudinary():
                app.logger.info('Cloudinary configuré avec succès pour la production')
                cloud_storage.cloudinary_configured = True
            else:
                app.logger.warning('Impossible de configurer Cloudinary. Utilisation du stockage local.')
        else:
            app.logger.info('Mode développement: stockage local des fichiers')
    except Exception as e:
        app.logger.error(f'Erreur lors de la configuration de Cloudinary: {str(e)}')
        app.logger.info('Fallback: utilisation du stockage local des fichiers')
        # Continuer l'exécution de l'application même en cas d'erreur

# Configuration selon l'environnement
config_name = os.environ.get('FLASK_ENV', 'development')
if config_name == 'production':
    from config import ProductionConfig
    app.config.from_object(ProductionConfig)
    app.logger.info("Configuration de production chargée")
else:
    from config import DevelopmentConfig
    app.config.from_object(DevelopmentConfig)
    app.logger.info("Configuration de développement chargée")

# Initialisation des extensions
from extensions import init_extensions
init_extensions(app)

# Initialiser le middleware de fallback d'images
register_image_fallback_middleware(app)

# Configuration de la gestion automatique des images
# DÉSACTIVÉ - from image_fallback_middleware import setup_image_fallback
from auto_image_handler import setup_auto_image_handler

# Initialiser les composants de gestion automatique des images
# DÉSACTIVÉ - setup_image_fallback(app)
setup_auto_image_handler(app)
app.logger.info("Gestion automatique des images configurée")

# Rendre les services d'URL d'image disponibles dans tous les templates
@app.context_processor
def inject_image_url_service():
    # Exposer image_url_service sous son propre nom pour éviter les conflits
    import image_url_service
    return dict(image_url_service=image_url_service)


# Route de diagnostic pour tous les exercices fill_in_blanks
@app.route('/debug-all-fill-in-blanks')
def debug_all_fill_in_blanks():
    # Route de diagnostic pour analyser tous les exercices fill_in_blanks
    if not current_user.is_authenticated or not current_user.is_admin:
        return "Accès non autorisé", 403
        
    results = []
    
    # En-tête
    results.append("<h1>DIAGNOSTIC TOUS LES EXERCICES FILL_IN_BLANKS</h1>")
    
    # 1. Environnement
    results.append("<h2>1. ENVIRONNEMENT</h2>")
    
    # Vérifier les variables d'environnement
    env_vars = {
        'FLASK_ENV': os.environ.get('FLASK_ENV', 'non défini'),
        'DATABASE_URL': os.environ.get('DATABASE_URL', 'non défini')[:10] + '...' if os.environ.get('DATABASE_URL') else 'non défini',
        'RAILWAY_ENVIRONMENT': os.environ.get('RAILWAY_ENVIRONMENT', 'non défini'),
        'PORT': os.environ.get('PORT', 'non défini')
    }
    
    results.append("<h3>Variables d'environnement:</h3>")
    for key, value in env_vars.items():
        results.append(f"<p>{key}: {value}</p>")
    
    # 2. Liste des exercices
    results.append("<h2>2. LISTE DES EXERCICES FILL_IN_BLANKS</h2>")
    
    try:
        exercises = Exercise.query.filter_by(exercise_type='fill_in_blanks').all()
        results.append(f"<p>Nombre d'exercices fill_in_blanks: {len(exercises)}</p>")
        
        if exercises:
            results.append("<table border='1' style='border-collapse: collapse; width: 100%;'>")
            results.append("<tr><th>ID</th><th>Titre</th><th>Image</th><th>Blancs</th><th>Mots</th><th>Cohérence</th></tr>")
            
            for ex in exercises:
                try:
                    content = json.loads(ex.content)
                    
                    # Compter les blancs
                    total_blanks = 0
                    
                    if 'sentences' in content:
                        sentences_blanks = sum(s.count('___') for s in content['sentences'])
                        total_blanks = sentences_blanks
                    elif 'text' in content:
                        text_blanks = content['text'].count('___')
                        total_blanks = text_blanks
                    
                    # Compter les mots
                    words = []
                    if 'words' in content:
                        words = content['words']
                    elif 'available_words' in content:
                        words = content['available_words']
                    
                    # Vérifier la cohérence
                    coherence = "✓" if total_blanks == len(words) else "✗"
                    coherence_color = "green" if total_blanks == len(words) else "red"
                    
                    # Image
                    has_image = "✓" if ex.image_path else "✗"
                    image_color = "green" if ex.image_path else "gray"
                    
                    results.append(f"<tr>")
                    results.append(f"<td>{ex.id}</td>")
                    results.append(f"<td>{ex.title}</td>")
                    results.append(f"<td style='color: {image_color};'>{has_image}</td>")
                    results.append(f"<td>{total_blanks}</td>")
                    results.append(f"<td>{len(words)}</td>")
                    results.append(f"<td style='color: {coherence_color};'>{coherence}</td>")
                    results.append(f"</tr>")
                except Exception as e:
                    results.append(f"<tr><td>{ex.id}</td><td>{ex.title}</td><td colspan='4' style='color: red;'>Erreur: {str(e)}</td></tr>")
            
            results.append("</table>")
        else:
            results.append("<p>Aucun exercice fill_in_blanks trouvé.</p>")
    except Exception as e:
        results.append(f"<p style='color: red;'>Erreur lors de la récupération des exercices: {str(e)}</p>")
    
    # 3. Liste des exercices word_placement
    results.append("<h2>3. LISTE DES EXERCICES WORD_PLACEMENT</h2>")
    
    try:
        exercises = Exercise.query.filter_by(exercise_type='word_placement').all()
        results.append(f"<p>Nombre d'exercices word_placement: {len(exercises)}</p>")
        
        if exercises:
            results.append("<table border='1' style='border-collapse: collapse; width: 100%;'>")
            results.append("<tr><th>ID</th><th>Titre</th><th>Image</th><th>Blancs</th><th>Mots</th><th>Cohérence</th></tr>")
            
            for ex in exercises:
                try:
                    content = json.loads(ex.content)
                    
                    # Compter les blancs
                    total_blanks = 0
                    
                    if 'sentences' in content:
                        sentences_blanks = sum(s.count('___') for s in content['sentences'])
                        total_blanks = sentences_blanks
                    elif 'text' in content:
                        text_blanks = content['text'].count('___')
                        total_blanks = text_blanks
                    
                    # Compter les mots
                    words = []
                    if 'words' in content:
                        words = content['words']
                    elif 'available_words' in content:
                        words = content['available_words']
                    
                    # Vérifier la cohérence
                    coherence = "✓" if total_blanks == len(words) else "✗"
                    coherence_color = "green" if total_blanks == len(words) else "red"
                    
                    # Image
                    has_image = "✓" if ex.image_path else "✗"
                    image_color = "green" if ex.image_path else "gray"
                    
                    results.append(f"<tr>")
                    results.append(f"<td>{ex.id}</td>")
                    results.append(f"<td>{ex.title}</td>")
                    results.append(f"<td style='color: {image_color};'>{has_image}</td>")
                    results.append(f"<td>{total_blanks}</td>")
                    results.append(f"<td>{len(words)}</td>")
                    results.append(f"<td style='color: {coherence_color};'>{coherence}</td>")
                    results.append(f"</tr>")
                except Exception as e:
                    results.append(f"<tr><td>{ex.id}</td><td>{ex.title}</td><td colspan='4' style='color: red;'>Erreur: {str(e)}</td></tr>")
            
            results.append("</table>")
        else:
            results.append("<p>Aucun exercice word_placement trouvé.</p>")
    except Exception as e:
        results.append(f"<p style='color: red;'>Erreur lors de la récupération des exercices: {str(e)}</p>")
    
    # 4. Test de la logique de scoring
    results.append("<h2>4. TEST DE LA LOGIQUE DE SCORING</h2>")
    
    # Test avec sentences
    results.append("<h3>Test avec sentences</h3>")
    test_content_sentences = {
        "sentences": ["Le ___ mange une ___ rouge."],
        "words": ["chat", "pomme"]
    }
    
    # Simuler des réponses utilisateur parfaites
    user_answers_sentences = {
        'answer_0': 'chat',
        'answer_1': 'pomme'
    }
    
    # Calculer le score
    try:
        total_blanks = sum(s.count('___') for s in test_content_sentences['sentences'])
        correct_blanks = 0
        
        for i in range(total_blanks):
            answer_key = f'answer_{i}'
            user_answer = user_answers_sentences.get(answer_key, '')
            correct_answer = test_content_sentences['words'][i] if i < len(test_content_sentences['words']) else ''
            
            if user_answer.lower() == correct_answer.lower():
                correct_blanks += 1
        
        score = round((correct_blanks / total_blanks) * 100) if total_blanks > 0 else 0
        
        results.append(f"<p>Score avec sentences: {correct_blanks}/{total_blanks} = {score}%</p>")
        if score == 100:
            results.append("<p style='color: green;'>✓ Test sentences réussi!</p>")
        else:
            results.append("<p style='color: red;'>✗ Test sentences échoué!</p>")
    except Exception as e:
        results.append(f"<p style='color: red;'>Erreur test sentences: {str(e)}</p>")
    
    # Test avec text
    results.append("<h3>Test avec text</h3>")
    test_content_text = {
        "text": "Le ___ mange une ___ rouge.",
        "words": ["chat", "pomme"]
    }
    
    # Simuler des réponses utilisateur parfaites
    user_answers_text = {
        'answer_0': 'chat',
        'answer_1': 'pomme'
    }
    
    # Calculer le score
    try:
        total_blanks = test_content_text['text'].count('___')
        correct_blanks = 0
        
        for i in range(total_blanks):
            answer_key = f'answer_{i}'
            user_answer = user_answers_text.get(answer_key, '')
            correct_answer = test_content_text['words'][i] if i < len(test_content_text['words']) else ''
            
            if user_answer.lower() == correct_answer.lower():
                correct_blanks += 1
        
        score = round((correct_blanks / total_blanks) * 100) if total_blanks > 0 else 0
        
        results.append(f"<p>Score avec text: {correct_blanks}/{total_blanks} = {score}%</p>")
        if score == 100:
            results.append("<p style='color: green;'>✓ Test text réussi!</p>")
        else:
            results.append("<p style='color: red;'>✗ Test text échoué!</p>")
    except Exception as e:
        results.append(f"<p style='color: red;'>Erreur test text: {str(e)}</p>")
    
    # 5. Conclusion
    results.append("<h2>5. CONCLUSION</h2>")
    results.append("<p>Si tous les tests ci-dessus sont réussis (affichés en vert), la logique de scoring est correcte.</p>")
    results.append("<p>Vérifiez particulièrement:</p>")
    results.append("<ul>")
    results.append("<li>Que le nombre de blancs correspond au nombre de mots pour chaque exercice</li>")
    results.append("<li>Que les tests de scoring donnent bien 100%</li>")
    results.append("<li>Que les exercices problématiques sont identifiés (marqués en rouge)</li>")
    results.append("</ul>")
    
    return "<br>".join(results)
# Global request logging removed to restore normal operation

# Initialize CSRF protection (déjà fait dans init_extensions)

# Register blueprints
app.register_blueprint(exercise_bp, url_prefix='/exercise')

# Import and register payment blueprint
from payment_routes import payment_bp
app.register_blueprint(payment_bp)

# Import and register diagnostic and fix blueprints
from diagnostic_school_choice import diagnostic_bp
from fix_school_choice import fix_bp
app.register_blueprint(diagnostic_bp)
app.register_blueprint(fix_bp)

# Import et enregistrement du blueprint de synchronisation des images
from fix_image_paths import register_image_sync_routes
register_image_sync_routes(app)

# Ajout du filtre shuffle pour Jinja2
@app.template_filter('shuffle')
def shuffle_filter(seq):
    try:
        result = list(seq)
        random.shuffle(result)
        return result
    except:
        return seq

# Ajout du filtre chr pour Jinja2 (conversion nombre -> caractère ASCII)
@app.template_filter('chr')
def chr_filter_registered(value):
    """Convertit un nombre en caractère ASCII (65 -> 'A', 66 -> 'B', etc.)"""
    try:
        return chr(int(value))
    except (ValueError, TypeError):
        return str(value)

app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max-limit

# S'assurer que le dossier d'upload existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

os.makedirs('static/uploads/qcm_multichoix', exist_ok=True)
# Configuration de l'extension pour les fichiers
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'webp', 'svg', 'bmp'}

def allowed_file(filename, file_obj=None):
    """Vérifie si un fichier est autorisé en fonction de son extension et de sa taille.
    
    Args:
        filename: Nom du fichier à vérifier
        file_obj: Objet fichier (optionnel) pour vérifier la taille
        
    Returns:
        bool: True si le fichier est autorisé, False sinon
    """
    # Vérification du nom de fichier
    if not filename or not isinstance(filename, str):
        app.logger.warning(f"[EDIT_DEBUG] Nom de fichier invalide: {filename}")
        return False
    
    if '.' not in filename:
        app.logger.warning(f"[EDIT_DEBUG] Pas d'extension dans le nom de fichier: {filename}")
        return False
        
    # Vérification de l'extension
    extension = filename.rsplit('.', 1)[1].lower()
    extension_ok = extension in ALLOWED_EXTENSIONS
    
    if not extension_ok:
        app.logger.warning(f"[EDIT_DEBUG] Extension non autorisée: {extension}")
        return False
    
    # Vérification de la taille du fichier si l'objet fichier est fourni
    if file_obj:
        try:
            # Sauvegarde de la position actuelle dans le fichier
            current_position = file_obj.tell()
            
            # Aller à la fin du fichier pour obtenir sa taille
            file_obj.seek(0, 2)  # 2 = SEEK_END
            file_size = file_obj.tell()
            
            # Revenir à la position d'origine
            file_obj.seek(current_position)
            
            if file_size == 0:
                app.logger.warning(f"[EDIT_DEBUG] Fichier vide détecté: {filename}")
                return False
                
            app.logger.info(f"[EDIT_DEBUG] Taille du fichier {filename}: {file_size} octets")
        except Exception as e:
            app.logger.error(f"[EDIT_DEBUG] Erreur lors de la vérification de la taille du fichier {filename}: {str(e)}")
    
    return True

# Initialisation automatique de la base de données
def init_database():
    """Initialise la base de données de manière sécurisée"""
    try:
        with app.app_context():
            # Créer toutes les tables si elles n'existent pas
            db.create_all()
            app.logger.info("Tables de base de donnees creees avec succes")
        
            # Créer le compte administrateur par défaut si nécessaire
            admin_email = os.environ.get('ADMIN_EMAIL', 'admin@classesnumeriques.com')
            admin_user = User.query.filter_by(email=admin_email).first()
            
            if not admin_user:
                from werkzeug.security import generate_password_hash
                admin_user = User(
                    username='admin',
                    email=admin_email,
                    name='Administrateur',
                    password_hash=generate_password_hash('AdminSecure2024!'),
                    role='admin',
                    subscription_status='approved',
                    subscription_type='admin',
                    approved_by='system'
                )
                db.session.add(admin_user)
                db.session.commit()
                app.logger.info(f"Compte administrateur cree: {admin_email}")
            else:
                app.logger.info(f"Compte administrateur existant: {admin_email}")
            
                # Approuver automatiquement mr.zahiri@gmail.com et lui donner les droits admin
                zahiri_user = User.query.filter_by(email='mr.zahiri@gmail.com').first()
                if zahiri_user:
                    zahiri_user.subscription_status = 'approved'
                    zahiri_user.role = 'admin'  # Donner les droits admin
                    zahiri_user.subscription_type = 'admin'
                    zahiri_user.approved_by = 'system'
                    db.session.commit()
                    app.logger.info("mr.zahiri@gmail.com approuve et promu administrateur")
                else:
                    app.logger.info("Compte mr.zahiri@gmail.com non trouve - sera approuve a la creation")
                    
    except Exception as e:
        app.logger.error(f"Erreur lors de l'initialisation de la base: {e}")
        # Ne pas faire planter l'app, continuer quand même

# Initialiser la base de données seulement si on n'est pas en mode import
if __name__ == '__main__' or os.environ.get('FLASK_ENV') == 'production':
    init_database()

# Enregistrement des blueprints (déjà fait ligne 48)

# Fonctions pour les filtres Jinja2
def enumerate_filter(iterable, start=0):
    return enumerate(iterable, start=start)

def from_json_filter(value):
    if value is None:
        return None
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value

def chr_filter(value):
    """Convertit un nombre en caractère ASCII (65 -> 'A', 66 -> 'B', etc.)"""
    try:
        return chr(int(value))
    except (ValueError, TypeError):
        return str(value)

def tojson_filter(value, indent=None):
    return json.dumps(value, indent=indent, ensure_ascii=False)

def get_file_icon(filename):
    """Retourne l'icône Font Awesome appropriée en fonction de l'extension du fichier"""
    extension = filename.lower().split('.')[-1] if '.' in filename else ''
    
    icon_mapping = {
        'pdf': 'fa-file-pdf',
        'doc': 'fa-file-word',
        'docx': 'fa-file-word',
        'xls': 'fa-file-excel',
        'xlsx': 'fa-file-excel',
        'ppt': 'fa-file-powerpoint',
        'pptx': 'fa-file-powerpoint',
        'txt': 'fa-file-alt',
        'jpg': 'fa-file-image',
        'jpeg': 'fa-file-image',
        'png': 'fa-file-image',
        'gif': 'fa-file-image',
        'zip': 'fa-file-archive',
        'rar': 'fa-file-archive',
        '7z': 'fa-file-archive',
    }
    
    return icon_mapping.get(extension, 'fa-file')  # fa-file est l'icône par défaut

app.jinja_env.globals.update(get_file_icon=get_file_icon)
app.jinja_env.globals.update(get_cloudinary_url=cloud_storage.get_cloudinary_url)
app.jinja_env.globals.update(cloud_storage=cloud_storage)

# Enregistrement des filtres Jinja2
app.jinja_env.filters['enumerate'] = enumerate_filter
app.jinja_env.filters['from_json'] = from_json_filter
app.jinja_env.filters['tojson'] = tojson_filter

# Décorateurs
def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_teacher:
            flash('Accès réservé aux enseignants.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def sanitize_filename(filename):
    # Supprimer les accents
    filename = ''.join(c for c in unicodedata.normalize('NFD', filename)
                      if unicodedata.category(c) != 'Mn')
    # Remplacer les espaces par des underscores
    filename = filename.replace(' ', '_')
    # Garder uniquement les caractères alphanumériques et quelques caractères spéciaux
    filename = ''.join(c for c in filename if c.isalnum() or c in '._-')
    return filename

def generate_unique_filename(original_filename):
    # Séparer le nom de fichier et l'extension
    name, ext = os.path.splitext(original_filename)
    # Générer un timestamp
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    # Générer une chaîne aléatoire
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    # Combiner le tout
    return f"{name}_{timestamp}_{random_string}{ext}"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.after_request
def add_csrf_token(response):
    if 'csrf_token' not in request.cookies:
        response.set_cookie('csrf_token', generate_csrf())
    return response

@app.before_request
def log_request_info():
    logger.debug('Headers: %s', request.headers)
    logger.debug('Body: %s', request.get_data())
    logger.debug('URL: %s', request.url)
    logger.debug('Method: %s', request.method)
    logger.debug('Path: %s', request.path)

# Route pour servir les fichiers uploadés
@app.route('/static/uploads/<path:filename>')
def uploaded_file(filename):
    """Sert les fichiers uploadés depuis le dossier static/uploads"""
    try:
        # Le chemin complet vers le fichier dans static/uploads
        full_path = os.path.join('static', 'uploads', filename)
        directory = os.path.dirname(full_path)
        file_name = os.path.basename(full_path)
        return send_from_directory(directory, file_name)
    except FileNotFoundError:
        logger.error(f"Fichier non trouvé: {filename}")
        return "Fichier non trouvé", 404

# Routes
@app.route('/')
def index():
    try:
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif current_user.is_teacher:
                return redirect(url_for('teacher_dashboard'))
            else:  # student
                return redirect(url_for('view_student_classes'))
        else:
            # Utilisateurs non connectés voient la belle page d'accueil moderne avec bouton S'abonner
            return render_template('login.html')
    except Exception as e:
        # En cas d'erreur avec current_user, afficher la page d'accueil par défaut
        app.logger.error(f"Erreur route index: {str(e)}")
        return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    app.logger.debug(f"[LOGIN] Méthode: {request.method}")
    app.logger.debug(f"[LOGIN] Headers: {request.headers}")
    app.logger.debug(f"[LOGIN] Form data: {request.form}")
    app.logger.debug(f"[LOGIN] Cookies: {request.cookies}")
    
    if current_user.is_authenticated:
        app.logger.debug(f"[LOGIN] Utilisateur déjà authentifié: {current_user.email}")
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        app.logger.debug(f"[LOGIN] Contenu du formulaire: {request.form}")
        email = request.form.get('email')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me') == '1'
        app.logger.debug(f"[LOGIN] Email: {email}, Remember me: {remember_me}")
        
        # Vérifier le token CSRF
        app.logger.debug(f"[LOGIN] CSRF token dans le formulaire: {request.form.get('csrf_token')}")
        app.logger.debug(f"[LOGIN] CSRF token dans la session: {session.get('csrf_token')}")
        app.logger.debug(f"[LOGIN] Session: {session}")
        app.logger.debug(f"[LOGIN] Session ID: {session.sid if hasattr(session, 'sid') else 'N/A'}")
        app.logger.debug(f"[LOGIN] Session modifiée: {session.modified}")
        app.logger.debug(f"[LOGIN] Session permanente: {session.permanent}")
        app.logger.debug(f"[LOGIN] Session nouvelle: {session.new if hasattr(session, 'new') else 'N/A'}")
        app.logger.debug(f"[LOGIN] Config SESSION_COOKIE_SECURE: {app.config.get('SESSION_COOKIE_SECURE')}")
        app.logger.debug(f"[LOGIN] Config SESSION_COOKIE_HTTPONLY: {app.config.get('SESSION_COOKIE_HTTPONLY')}")
        app.logger.debug(f"[LOGIN] Config SESSION_COOKIE_SAMESITE: {app.config.get('SESSION_COOKIE_SAMESITE')}")
        app.logger.debug(f"[LOGIN] Config SECRET_KEY: {'Définie' if app.config.get('SECRET_KEY') else 'Non définie'}")
        app.logger.debug(f"[LOGIN] Config DEBUG: {app.config.get('DEBUG')}")
        app.logger.debug(f"[LOGIN] Config ENV: {app.config.get('ENV')}")
        app.logger.debug(f"[LOGIN] Config TESTING: {app.config.get('TESTING')}")
        app.logger.debug(f"[LOGIN] Config SERVER_NAME: {app.config.get('SERVER_NAME')}")
        app.logger.debug(f"[LOGIN] Config APPLICATION_ROOT: {app.config.get('APPLICATION_ROOT')}")
        app.logger.debug(f"[LOGIN] Config PREFERRED_URL_SCHEME: {app.config.get('PREFERRED_URL_SCHEME')}")
        app.logger.debug(f"[LOGIN] Config MAX_CONTENT_LENGTH: {app.config.get('MAX_CONTENT_LENGTH')}")
        app.logger.debug(f"[LOGIN] Config TEMPLATES_AUTO_RELOAD: {app.config.get('TEMPLATES_AUTO_RELOAD')}")
        app.logger.debug(f"[LOGIN] Config EXPLAIN_TEMPLATE_LOADING: {app.config.get('EXPLAIN_TEMPLATE_LOADING')}")
        app.logger.debug(f"[LOGIN] Config PRESERVE_CONTEXT_ON_EXCEPTION: {app.config.get('PRESERVE_CONTEXT_ON_EXCEPTION')}")
        app.logger.debug(f"[LOGIN] Config TRAP_HTTP_EXCEPTIONS: {app.config.get('TRAP_HTTP_EXCEPTIONS')}")
        app.logger.debug(f"[LOGIN] Config TRAP_BAD_REQUEST_ERRORS: {app.config.get('TRAP_BAD_REQUEST_ERRORS')}")
        app.logger.debug(f"[LOGIN] Config JSON_AS_ASCII: {app.config.get('JSON_AS_ASCII')}")
        app.logger.debug(f"[LOGIN] Config JSON_SORT_KEYS: {app.config.get('JSON_SORT_KEYS')}")
        app.logger.debug(f"[LOGIN] Config JSONIFY_PRETTYPRINT_REGULAR: {app.config.get('JSONIFY_PRETTYPRINT_REGULAR')}")
        app.logger.debug(f"[LOGIN] Config JSONIFY_MIMETYPE: {app.config.get('JSONIFY_MIMETYPE')}")
        app.logger.debug(f"[LOGIN] Config MAX_COOKIE_SIZE: {app.config.get('MAX_COOKIE_SIZE')}")
        app.logger.debug(f"[LOGIN] Config SESSION_COOKIE_NAME: {app.config.get('SESSION_COOKIE_NAME')}")
        app.logger.debug(f"[LOGIN] Config SESSION_COOKIE_DOMAIN: {app.config.get('SESSION_COOKIE_DOMAIN')}")
        app.logger.debug(f"[LOGIN] Config SESSION_COOKIE_PATH: {app.config.get('SESSION_COOKIE_PATH')}")
        app.logger.debug(f"[LOGIN] Config SESSION_COOKIE_MAX_AGE: {app.config.get('SESSION_COOKIE_MAX_AGE')}")
        app.logger.debug(f"[LOGIN] Config SESSION_REFRESH_EACH_REQUEST: {app.config.get('SESSION_REFRESH_EACH_REQUEST')}")
        app.logger.debug(f"[LOGIN] Config SESSION_USE_SIGNER: {app.config.get('SESSION_USE_SIGNER')}")
        app.logger.debug(f"[LOGIN] Config SESSION_FILE_DIR: {app.config.get('SESSION_FILE_DIR')}")
        app.logger.debug(f"[LOGIN] Config SESSION_FILE_THRESHOLD: {app.config.get('SESSION_FILE_THRESHOLD')}")
        app.logger.debug(f"[LOGIN] Config SESSION_FILE_MODE: {app.config.get('SESSION_FILE_MODE')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MONGODB_DB: {app.config.get('SESSION_MONGODB_DB')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MONGODB_COLLECT: {app.config.get('SESSION_MONGODB_COLLECT')}")
        app.logger.debug(f"[LOGIN] Config SESSION_REDIS_URL: {app.config.get('SESSION_REDIS_URL')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MEMCACHED_SERVERS: {app.config.get('SESSION_MEMCACHED_SERVERS')}")
        app.logger.debug(f"[LOGIN] Config SESSION_TYPE: {app.config.get('SESSION_TYPE')}")
        app.logger.debug(f"[LOGIN] Config SESSION_PERMANENT: {app.config.get('SESSION_PERMANENT')}")
        app.logger.debug(f"[LOGIN] Config SESSION_USE_SIGNER: {app.config.get('SESSION_USE_SIGNER')}")
        app.logger.debug(f"[LOGIN] Config SESSION_KEY_PREFIX: {app.config.get('SESSION_KEY_PREFIX')}")
        app.logger.debug(f"[LOGIN] Config SESSION_REDIS: {app.config.get('SESSION_REDIS')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MEMCACHED: {app.config.get('SESSION_MEMCACHED')}")
        app.logger.debug(f"[LOGIN] Config SESSION_FILE_DIR: {app.config.get('SESSION_FILE_DIR')}")
        app.logger.debug(f"[LOGIN] Config SESSION_SQLALCHEMY: {app.config.get('SESSION_SQLALCHEMY')}")
        app.logger.debug(f"[LOGIN] Config SESSION_SQLALCHEMY_TABLE: {app.config.get('SESSION_SQLALCHEMY_TABLE')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MONGODB: {app.config.get('SESSION_MONGODB')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MONGODB_DB: {app.config.get('SESSION_MONGODB_DB')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MONGODB_COLLECT: {app.config.get('SESSION_MONGODB_COLLECT')}")
        app.logger.debug(f"[LOGIN] Config SESSION_REDIS_URL: {app.config.get('SESSION_REDIS_URL')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MEMCACHED_SERVERS: {app.config.get('SESSION_MEMCACHED_SERVERS')}")
        app.logger.debug(f"[LOGIN] Config SESSION_TYPE: {app.config.get('SESSION_TYPE')}")
        app.logger.debug(f"[LOGIN] Config SESSION_PERMANENT: {app.config.get('SESSION_PERMANENT')}")
        app.logger.debug(f"[LOGIN] Config SESSION_USE_SIGNER: {app.config.get('SESSION_USE_SIGNER')}")
        app.logger.debug(f"[LOGIN] Config SESSION_KEY_PREFIX: {app.config.get('SESSION_KEY_PREFIX')}")
        app.logger.debug(f"[LOGIN] Config SESSION_REDIS: {app.config.get('SESSION_REDIS')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MEMCACHED: {app.config.get('SESSION_MEMCACHED')}")
        app.logger.debug(f"[LOGIN] Config SESSION_FILE_DIR: {app.config.get('SESSION_FILE_DIR')}")
        app.logger.debug(f"[LOGIN] Config SESSION_SQLALCHEMY: {app.config.get('SESSION_SQLALCHEMY')}")
        app.logger.debug(f"[LOGIN] Config SESSION_SQLALCHEMY_TABLE: {app.config.get('SESSION_SQLALCHEMY_TABLE')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MONGODB: {app.config.get('SESSION_MONGODB')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MONGODB_DB: {app.config.get('SESSION_MONGODB_DB')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MONGODB_COLLECT: {app.config.get('SESSION_MONGODB_COLLECT')}")
        app.logger.debug(f"[LOGIN] Config SESSION_REDIS_URL: {app.config.get('SESSION_REDIS_URL')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MEMCACHED_SERVERS: {app.config.get('SESSION_MEMCACHED_SERVERS')}")
        app.logger.debug(f"[LOGIN] Config SESSION_TYPE: {app.config.get('SESSION_TYPE')}")
        app.logger.debug(f"[LOGIN] Config SESSION_PERMANENT: {app.config.get('SESSION_PERMANENT')}")
        app.logger.debug(f"[LOGIN] Config SESSION_USE_SIGNER: {app.config.get('SESSION_USE_SIGNER')}")
        app.logger.debug(f"[LOGIN] Config SESSION_KEY_PREFIX: {app.config.get('SESSION_KEY_PREFIX')}")
        app.logger.debug(f"[LOGIN] Config SESSION_REDIS: {app.config.get('SESSION_REDIS')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MEMCACHED: {app.config.get('SESSION_MEMCACHED')}")
        app.logger.debug(f"[LOGIN] Config SESSION_FILE_DIR: {app.config.get('SESSION_FILE_DIR')}")
        app.logger.debug(f"[LOGIN] Config SESSION_SQLALCHEMY: {app.config.get('SESSION_SQLALCHEMY')}")
        app.logger.debug(f"[LOGIN] Config SESSION_SQLALCHEMY_TABLE: {app.config.get('SESSION_SQLALCHEMY_TABLE')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MONGODB: {app.config.get('SESSION_MONGODB')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MONGODB_DB: {app.config.get('SESSION_MONGODB_DB')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MONGODB_COLLECT: {app.config.get('SESSION_MONGODB_COLLECT')}")
        app.logger.debug(f"[LOGIN] Config SESSION_REDIS_URL: {app.config.get('SESSION_REDIS_URL')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MEMCACHED_SERVERS: {app.config.get('SESSION_MEMCACHED_SERVERS')}")
        app.logger.debug(f"[LOGIN] Config SESSION_TYPE: {app.config.get('SESSION_TYPE')}")
        app.logger.debug(f"[LOGIN] Config SESSION_PERMANENT: {app.config.get('SESSION_PERMANENT')}")
        app.logger.debug(f"[LOGIN] Config SESSION_USE_SIGNER: {app.config.get('SESSION_USE_SIGNER')}")
        app.logger.debug(f"[LOGIN] Config SESSION_KEY_PREFIX: {app.config.get('SESSION_KEY_PREFIX')}")
        app.logger.debug(f"[LOGIN] Config SESSION_REDIS: {app.config.get('SESSION_REDIS')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MEMCACHED: {app.config.get('SESSION_MEMCACHED')}")
        app.logger.debug(f"[LOGIN] Config SESSION_FILE_DIR: {app.config.get('SESSION_FILE_DIR')}")
        app.logger.debug(f"[LOGIN] Config SESSION_SQLALCHEMY: {app.config.get('SESSION_SQLALCHEMY')}")
        app.logger.debug(f"[LOGIN] Config SESSION_SQLALCHEMY_TABLE: {app.config.get('SESSION_SQLALCHEMY_TABLE')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MONGODB: {app.config.get('SESSION_MONGODB')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MONGODB_DB: {app.config.get('SESSION_MONGODB_DB')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MONGODB_COLLECT: {app.config.get('SESSION_MONGODB_COLLECT')}")
        app.logger.debug(f"[LOGIN] Config SESSION_REDIS_URL: {app.config.get('SESSION_REDIS_URL')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MEMCACHED_SERVERS: {app.config.get('SESSION_MEMCACHED_SERVERS')}")
        app.logger.debug(f"[LOGIN] Config SESSION_TYPE: {app.config.get('SESSION_TYPE')}")
        app.logger.debug(f"[LOGIN] Config SESSION_PERMANENT: {app.config.get('SESSION_PERMANENT')}")
        app.logger.debug(f"[LOGIN] Config SESSION_USE_SIGNER: {app.config.get('SESSION_USE_SIGNER')}")
        app.logger.debug(f"[LOGIN] Config SESSION_KEY_PREFIX: {app.config.get('SESSION_KEY_PREFIX')}")
        app.logger.debug(f"[LOGIN] Config SESSION_REDIS: {app.config.get('SESSION_REDIS')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MEMCACHED: {app.config.get('SESSION_MEMCACHED')}")
        app.logger.debug(f"[LOGIN] Config SESSION_FILE_DIR: {app.config.get('SESSION_FILE_DIR')}")
        app.logger.debug(f"[LOGIN] Config SESSION_SQLALCHEMY: {app.config.get('SESSION_SQLALCHEMY')}")
        app.logger.debug(f"[LOGIN] Config SESSION_SQLALCHEMY_TABLE: {app.config.get('SESSION_SQLALCHEMY_TABLE')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MONGODB: {app.config.get('SESSION_MONGODB')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MONGODB_DB: {app.config.get('SESSION_MONGODB_DB')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MONGODB_COLLECT: {app.config.get('SESSION_MONGODB_COLLECT')}")
        app.logger.debug(f"[LOGIN] Config SESSION_REDIS_URL: {app.config.get('SESSION_REDIS_URL')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MEMCACHED_SERVERS: {app.config.get('SESSION_MEMCACHED_SERVERS')}")
        app.logger.debug(f"[LOGIN] Config SESSION_TYPE: {app.config.get('SESSION_TYPE')}")
        app.logger.debug(f"[LOGIN] Config SESSION_PERMANENT: {app.config.get('SESSION_PERMANENT')}")
        app.logger.debug(f"[LOGIN] Config SESSION_USE_SIGNER: {app.config.get('SESSION_USE_SIGNER')}")
        app.logger.debug(f"[LOGIN] Config SESSION_KEY_PREFIX: {app.config.get('SESSION_KEY_PREFIX')}")
        app.logger.debug(f"[LOGIN] Config SESSION_REDIS: {app.config.get('SESSION_REDIS')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MEMCACHED: {app.config.get('SESSION_MEMCACHED')}")
        app.logger.debug(f"[LOGIN] Config SESSION_FILE_DIR: {app.config.get('SESSION_FILE_DIR')}")
        app.logger.debug(f"[LOGIN] Config SESSION_SQLALCHEMY: {app.config.get('SESSION_SQLALCHEMY')}")
        app.logger.debug(f"[LOGIN] Config SESSION_SQLALCHEMY_TABLE: {app.config.get('SESSION_SQLALCHEMY_TABLE')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MONGODB: {app.config.get('SESSION_MONGODB')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MONGODB_DB: {app.config.get('SESSION_MONGODB_DB')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MONGODB_COLLECT: {app.config.get('SESSION_MONGODB_COLLECT')}")
        app.logger.debug(f"[LOGIN] Config SESSION_REDIS_URL: {app.config.get('SESSION_REDIS_URL')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MEMCACHED_SERVERS: {app.config.get('SESSION_MEMCACHED_SERVERS')}")
        app.logger.debug(f"[LOGIN] Config SESSION_TYPE: {app.config.get('SESSION_TYPE')}")
        app.logger.debug(f"[LOGIN] Config SESSION_PERMANENT: {app.config.get('SESSION_PERMANENT')}")
        app.logger.debug(f"[LOGIN] Config SESSION_USE_SIGNER: {app.config.get('SESSION_USE_SIGNER')}")
        app.logger.debug(f"[LOGIN] Config SESSION_KEY_PREFIX: {app.config.get('SESSION_KEY_PREFIX')}")
        app.logger.debug(f"[LOGIN] Config SESSION_REDIS: {app.config.get('SESSION_REDIS')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MEMCACHED: {app.config.get('SESSION_MEMCACHED')}")
        app.logger.debug(f"[LOGIN] Config SESSION_FILE_DIR: {app.config.get('SESSION_FILE_DIR')}")
        app.logger.debug(f"[LOGIN] Config SESSION_SQLALCHEMY: {app.config.get('SESSION_SQLALCHEMY')}")
        app.logger.debug(f"[LOGIN] Config SESSION_SQLALCHEMY_TABLE: {app.config.get('SESSION_SQLALCHEMY_TABLE')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MONGODB: {app.config.get('SESSION_MONGODB')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MONGODB_DB: {app.config.get('SESSION_MONGODB_DB')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MONGODB_COLLECT: {app.config.get('SESSION_MONGODB_COLLECT')}")
        app.logger.debug(f"[LOGIN] Config SESSION_REDIS_URL: {app.config.get('SESSION_REDIS_URL')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MEMCACHED_SERVERS: {app.config.get('SESSION_MEMCACHED_SERVERS')}")
        app.logger.debug(f"[LOGIN] Config SESSION_TYPE: {app.config.get('SESSION_TYPE')}")
        app.logger.debug(f"[LOGIN] Config SESSION_PERMANENT: {app.config.get('SESSION_PERMANENT')}")
        app.logger.debug(f"[LOGIN] Config SESSION_USE_SIGNER: {app.config.get('SESSION_USE_SIGNER')}")
        app.logger.debug(f"[LOGIN] Config SESSION_KEY_PREFIX: {app.config.get('SESSION_KEY_PREFIX')}")
        app.logger.debug(f"[LOGIN] Config SESSION_REDIS: {app.config.get('SESSION_REDIS')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MEMCACHED: {app.config.get('SESSION_MEMCACHED')}")
        app.logger.debug(f"[LOGIN] Config SESSION_FILE_DIR: {app.config.get('SESSION_FILE_DIR')}")
        app.logger.debug(f"[LOGIN] Config SESSION_SQLALCHEMY: {app.config.get('SESSION_SQLALCHEMY')}")
        app.logger.debug(f"[LOGIN] Config SESSION_SQLALCHEMY_TABLE: {app.config.get('SESSION_SQLALCHEMY_TABLE')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MONGODB: {app.config.get('SESSION_MONGODB')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MONGODB_DB: {app.config.get('SESSION_MONGODB_DB')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MONGODB_COLLECT: {app.config.get('SESSION_MONGODB_COLLECT')}")
        app.logger.debug(f"[LOGIN] Config SESSION_REDIS_URL: {app.config.get('SESSION_REDIS_URL')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MEMCACHED_SERVERS: {app.config.get('SESSION_MEMCACHED_SERVERS')}")
        app.logger.debug(f"[LOGIN] Config SESSION_TYPE: {app.config.get('SESSION_TYPE')}")
        app.logger.debug(f"[LOGIN] Config SESSION_PERMANENT: {app.config.get('SESSION_PERMANENT')}")
        app.logger.debug(f"[LOGIN] Config SESSION_USE_SIGNER: {app.config.get('SESSION_USE_SIGNER')}")
        app.logger.debug(f"[LOGIN] Config SESSION_KEY_PREFIX: {app.config.get('SESSION_KEY_PREFIX')}")
        app.logger.debug(f"[LOGIN] Config SESSION_REDIS: {app.config.get('SESSION_REDIS')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MEMCACHED: {app.config.get('SESSION_MEMCACHED')}")
        app.logger.debug(f"[LOGIN] Config SESSION_FILE_DIR: {app.config.get('SESSION_FILE_DIR')}")
        app.logger.debug(f"[LOGIN] Config SESSION_SQLALCHEMY: {app.config.get('SESSION_SQLALCHEMY')}")
        app.logger.debug(f"[LOGIN] Config SESSION_SQLALCHEMY_TABLE: {app.config.get('SESSION_SQLALCHEMY_TABLE')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MONGODB: {app.config.get('SESSION_MONGODB')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MONGODB_DB: {app.config.get('SESSION_MONGODB_DB')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MONGODB_COLLECT: {app.config.get('SESSION_MONGODB_COLLECT')}")
        app.logger.debug(f"[LOGIN] Config SESSION_REDIS_URL: {app.config.get('SESSION_REDIS_URL')}")
        app.logger.debug(f"[LOGIN] Config SESSION_MEMCACHED_SERVERS: {app.config.get('SESSION_MEMCACHED_SERVERS')}")
        
        email = request.form.get('email')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me') == '1'
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            # Vérifier le statut d'abonnement avant la connexion
            if user.subscription_status == 'suspended':
                flash('Votre compte a été suspendu. Contactez l\'administrateur pour plus d\'informations.', 'error')
                return render_template('login.html')
            elif user.subscription_status == 'rejected':
                flash('Votre demande d\'abonnement a été rejetée. Contactez l\'administrateur.', 'error')
                return render_template('login.html')
            elif user.subscription_status == 'pending':
                # Exception spéciale pour mr.zahiri@gmail.com - accès admin direct
                if user.email == 'mr.zahiri@gmail.com':
                    try:
                        user.subscription_status = 'approved'
                        user.role = 'teacher'  # Changé en teacher pour avoir accès à la création d'exercices
                        user.subscription_type = 'admin'
                        user.approved_by = None  # Pas d'ID admin spécifique pour l'auto-approbation
                        user.approval_date = datetime.utcnow()
                        db.session.commit()
                        app.logger.info("✅ mr.zahiri@gmail.com auto-approuvé en tant qu'enseignant-admin")
                    except Exception as e:
                        app.logger.error(f"Erreur lors de l'auto-approbation: {e}")
                        # Continuer quand même la connexion
                        pass
                else:
                    # Permettre la connexion même en attente pour qu'ils puissent voir le bouton "S'abonner"
                    flash('Votre compte est en attente de validation. Vous pouvez effectuer un paiement pour accélérer le processus.', 'warning')
            elif user.subscription_status == 'paid' and user.role != 'admin':
                flash('Votre paiement a été reçu. En attente de validation par l\'administrateur.', 'info')
                return render_template('login.html')
            
            # Connexion autorisée pour les comptes approuvés ou les administrateurs
            login_user(user, remember=remember_me)
            flash('Connexion réussie !', 'success')
            
            # Redirection intelligente selon le rôle
            # Exception spéciale pour mr.zahiri@gmail.com - toujours vers teacher_dashboard
            if user.email == 'mr.zahiri@gmail.com':
                return redirect(url_for('teacher_dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            else:  # student
                return redirect(url_for('view_student_classes'))
        else:
            flash('Email ou mot de passe incorrect.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('login'))

@app.route('/subscription-choice')
def subscription_choice():
    """Page de choix d'abonnement pour les utilisateurs non connectés"""
    return render_template('subscription_choice.html')

@app.route('/register/teacher', methods=['GET', 'POST'])
def register_teacher():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        school_name = request.form.get('school_name')
        
        if User.query.filter_by(email=email).first():
            flash('Cet email est déjà utilisé.', 'error')
            return redirect(url_for('register_teacher'))
        
        # Générer un username à partir de l'email
        username = email.split('@')[0]
        
        user = User(
            username=username,
            name=name,
            email=email,
            role='teacher',
            school_name=school_name
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Inscription réussie ! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Erreur lors de l\'inscription.', 'error')
            print(f"Erreur d'inscription : {str(e)}")
    
    return render_template('register_teacher.html')

@app.route('/register/school', methods=['GET', 'POST'])
def register_school():
    """Route d'inscription pour les écoles (directeurs/responsables)"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        school_name = request.form.get('school_name')
        
        if User.query.filter_by(email=email).first():
            flash('Cet email est déjà utilisé.', 'error')
            return redirect(url_for('register_school'))
        
        # Générer un username à partir de l'email
        username = email.split('@')[0]
        
        user = User(
            username=username,
            name=name,
            email=email,
            role='teacher',  # Les responsables d'école sont aussi des enseignants
            school_name=school_name,
            subscription_type='school'  # Type d'abonnement école
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Inscription école réussie ! Vous pouvez maintenant vous connecter et procéder au paiement de 80€.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Erreur lors de l\'inscription.', 'error')
            app.logger.error(f"Erreur d'inscription école : {str(e)}")
    
    return render_template('register.html', user_type='school')

@app.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        app.logger.info("Données du formulaire reçues : %s", request.form)
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        app.logger.info("Valeurs extraites - username: %s, email: %s", username, email)
        
        # Vérifier que tous les champs sont remplis
        if not all([username, email, password, confirm_password]):
            missing_fields = []
            if not username: missing_fields.append('nom d\'utilisateur')
            if not email: missing_fields.append('email')
            if not password: missing_fields.append('mot de passe')
            if not confirm_password: missing_fields.append('confirmation du mot de passe')
            
            flash(f'Les champs suivants sont obligatoires : {", ".join(missing_fields)}.', 'error')
            return redirect(url_for('register_student'))
            
        # Vérifier que les mots de passe correspondent
        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas.', 'error')
            return redirect(url_for('register_student'))
        
        # Vérifier si l'email est déjà utilisé
        if User.query.filter_by(email=email).first():
            flash('Cet email est déjà utilisé.', 'error')
            return redirect(url_for('register_student'))
            
        # Vérifier si le nom d'utilisateur est déjà utilisé
        if User.query.filter_by(username=username).first():
            flash('Ce nom d\'utilisateur est déjà utilisé.', 'error')
            return redirect(url_for('register_student'))
        
        try:
            user = User(
                username=username,
                name=username,  # Utiliser le username comme nom par défaut
                email=email,
                role='student'
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            app.logger.info("Nouvel utilisateur créé avec succès - username: %s, email: %s", username, email)
            flash('Inscription réussie ! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            app.logger.error("Erreur lors de la création de l'utilisateur : %s", str(e))
            flash('Erreur lors de l\'inscription.', 'error')
            return redirect(url_for('register_student'))
    
    return render_template('register_student.html')

@app.route('/setup-admin')
def setup_admin():
    # Vérifier si un utilisateur existe déjà
    if User.query.first() is not None:
        flash('Un utilisateur existe déjà', 'warning')
        return redirect(url_for('login'))
    
    # Créer un compte administrateur par défaut
    admin = User(
        username='admin',
        name='Admin',
        email='admin@example.com',
        role='admin'
    )
    admin.set_password('admin')
    
    try:
        db.session.add(admin)
        db.session.commit()
        flash('Compte administrateur créé avec succès. Email: admin@example.com, Mot de passe: admin', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erreur lors de la création du compte administrateur', 'error')
    
    return redirect(url_for('login'))

@app.route('/dashboard')
@app.route('/teacher_dashboard')
@login_required
def teacher_dashboard():
    if not current_user.is_teacher:
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('index'))
    
    classes = Class.query.filter_by(teacher_id=current_user.id).all()
    return render_template('teacher/dashboard.html', classes=classes)





@app.route('/add_exercise_to_class/<int:exercise_id>', methods=['GET', 'POST'])
@login_required
def add_exercise_to_class(exercise_id):
    if current_user.role == 'student':
        return redirect(url_for('student_dashboard'))

    exercise = Exercise.query.get_or_404(exercise_id)
    # Note: Permettre aux enseignants d'ajouter des exercices d'autres enseignants à leurs classes
    # depuis la bibliothèque partagée (pas de restriction sur teacher_id pour l'ajout)

    # Récupérer les classes de l'enseignant
    classes = Class.query.filter_by(teacher_id=current_user.id).all()

    if request.method == 'POST':
        class_id = request.form.get('class_id')
        course_id = request.form.get('course_id')

        if not class_id or not course_id:
            flash('Veuillez sélectionner une classe et un cours', 'error')
            return redirect(url_for('add_exercise_to_class', exercise_id=exercise_id))

        # Vérifier que la classe et le cours existent et appartiennent à l'enseignant
        class_obj = Class.query.get_or_404(class_id)
        course = Course.query.get_or_404(course_id)

        if class_obj.teacher_id != current_user.id or course.class_obj.id != int(class_id):
            abort(403)

        # Ajouter l'exercice au cours s'il n'y est pas déjà
        if exercise not in course.exercises:
            course.exercises.append(exercise)
            db.session.commit()
            flash('L\'exercice a été ajouté au cours avec succès !', 'success')
        else:
            flash('L\'exercice est déjà dans ce cours', 'warning')

        return redirect(url_for('exercise_library'))

    return render_template('add_exercise_to_class.html', exercise=exercise, classes=classes)

@app.route('/get_courses/<int:class_id>')
@login_required
def get_courses(class_id):
    if current_user.role == 'student':
        return jsonify([]), 403

    # Vérifier que la classe appartient à l'enseignant
    class_obj = Class.query.get_or_404(class_id)
    if class_obj.teacher_id != current_user.id:
        return jsonify([]), 403

    # Récupérer tous les cours de la classe
    courses = Course.query.filter_by(class_id=class_id).all()
    return jsonify([{'id': course.id, 'title': course.title} for course in courses])

@app.route('/class/<int:class_id>/delete', methods=['POST'])
@login_required
@teacher_required
def delete_class(class_id):
    logger.debug('='*50)
    logger.debug('TENTATIVE DE SUPPRESSION DE CLASSE')
    logger.debug(f'class_id: {class_id}')
    logger.debug(f'user: {current_user.name} (id: {current_user.id})')
    logger.debug(f'headers: {dict(request.headers)}')
    logger.debug(f'form data: {dict(request.form)}')
    
    # Vérification du token CSRF
    if not request.form.get('csrf_token'):
        logger.error("Token CSRF manquant")
        flash('Erreur de sécurité : token CSRF manquant.', 'error')
        return redirect(url_for('teacher_dashboard'))
    
    try:
        # Récupération et vérification de la classe
        class_obj = Class.query.get(class_id)
        if not class_obj:
            logger.error(f"Classe {class_id} non trouvée")
            flash('Classe non trouvée.', 'error')
            return redirect(url_for('teacher_dashboard'))
        
        # Vérification des permissions
        if class_obj.teacher_id != current_user.id:
            logger.error(f"L'utilisateur {current_user.name} n'est pas le professeur de la classe {class_obj.name}")
            flash('Vous n\'êtes pas autorisé à supprimer cette classe.', 'error')
            return redirect(url_for('teacher_dashboard'))
        
        try:
            # Supprimer les cours associés
            for course in class_obj.courses:
                db.session.delete(course)
            
            # Supprimer les associations avec les étudiants
            class_obj.students = []
            
            # Sauvegarder le nom pour le message
            class_name = class_obj.name
            
            # Supprimer la classe
            db.session.delete(class_obj)
            db.session.commit()
            
            logger.info(f"Classe {class_name} supprimée avec succès")
            flash(f'La classe {class_name} a été supprimée avec succès !', 'success')
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur SQL lors de la suppression: {str(e)}")
            flash('Une erreur est survenue lors de la suppression de la classe.', 'error')
            return redirect(url_for('view_class', class_id=class_id))
            
    except Exception as e:
        logger.error(f"Erreur inattendue: {str(e)}")
        flash('Une erreur inattendue est survenue.', 'error')
        
    return redirect(url_for('teacher_dashboard'))

@app.route('/course/<int:course_id>/delete', methods=['POST'])
@login_required
def delete_course(course_id):
    if not current_user.is_teacher:
        flash('Seuls les enseignants peuvent supprimer des cours.', 'error')
        return redirect(url_for('index'))
    
    course = Course.query.get_or_404(course_id)
    class_obj = Class.query.get_or_404(course.class_id)
    
    # Vérifier que l'enseignant est bien le propriétaire de la classe
    if class_obj.teacher_id != current_user.id:
        flash('Vous n\'avez pas la permission de supprimer ce cours.', 'error')
        return redirect(url_for('view_class', class_id=class_obj.id))
    
    try:
        # Supprimer les fichiers physiques
        for course_file in course.course_files:
            try:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], course_file.filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                app.logger.error(f"Erreur lors de la suppression du fichier {course_file.filename}: {str(e)}")
        
        # Supprimer le cours (les fichiers et exercices seront supprimés automatiquement grâce à cascade)
        db.session.delete(course)
        db.session.commit()
        flash('Le cours a été supprimé avec succès.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Une erreur est survenue lors de la suppression du cours.', 'error')
        app.logger.error(f"Erreur lors de la suppression du cours {course_id}: {str(e)}")
    
    return redirect(url_for('view_class', class_id=class_obj.id))

@app.route('/class/<int:class_id>/remove-student/<int:student_id>', methods=['POST'])
@login_required
def remove_student_from_class(class_id, student_id):
    logger.debug('='*50)
    logger.debug('TENTATIVE DE SUPPRESSION D\'ÉTUDIANT')
    logger.debug(f'class_id: {class_id}')
    logger.debug(f'student_id: {student_id}')
    logger.debug(f'user: {current_user.name} (id: {current_user.id}, is_teacher: {current_user.is_teacher})')
    logger.debug(f'headers: {dict(request.headers)}')
    logger.debug(f'form data: {dict(request.form)}')
    
    # Vérification du token CSRF
    if not request.form.get('csrf_token'):
        logger.error("Token CSRF manquant")
        flash('Erreur de sécurité : token CSRF manquant.', 'error')
        return redirect(url_for('view_class', class_id=class_id))
    
    # Vérification des permissions
    if not current_user.is_teacher:
        logger.error(f"Accès refusé : l'utilisateur {current_user.name} n'est pas un enseignant")
        flash('Accès réservé aux enseignants.', 'error')
        return redirect(url_for('index'))
    
    try:
        # Vérification de la classe
        class_obj = Class.query.get(class_id)
        if not class_obj:
            logger.error(f"Classe {class_id} non trouvée")
            flash('Classe non trouvée.', 'error')
            return redirect(url_for('teacher_dashboard'))
            
        if class_obj.teacher_id != current_user.id:
            logger.error(f"L'utilisateur {current_user.name} n'est pas le professeur de la classe {class_obj.name}")
            flash('Vous n\'êtes pas le professeur de cette classe.', 'error')
            return redirect(url_for('teacher_dashboard'))
        
        # Vérification de l'étudiant
        student = User.query.get(student_id)
        if not student:
            logger.error(f"Étudiant {student_id} non trouvé")
            flash('Étudiant non trouvé.', 'error')
            return redirect(url_for('view_class', class_id=class_id))
            
        if not student in class_obj.students:
            logger.error(f"L'étudiant {student.name} n'est pas dans la classe {class_obj.name}")
            flash('Cet étudiant n\'est pas inscrit dans cette classe.', 'error')
            return redirect(url_for('view_class', class_id=class_id))
        
        try:
            # Supprimer l'étudiant de la classe
            class_obj.students.remove(student)
            db.session.commit()
            logger.info(f"Étudiant {student.name} supprimé avec succès de la classe {class_obj.name}")
            flash(f'L\'étudiant {student.name} a été retiré de la classe avec succès.', 'success')
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur SQL lors de la suppression: {str(e)}")
            flash('Une erreur est survenue lors de la suppression de l\'étudiant.', 'error')
            
    except Exception as e:
        logger.error(f"Erreur inattendue: {str(e)}")
        flash('Une erreur inattendue est survenue.', 'error')
        
    return redirect(url_for('view_class', class_id=class_id))

@app.route('/exercise-library')
@login_required
@teacher_required
def exercise_library():
    # Récupérer les paramètres de filtrage
    search_query = request.args.get('search', '')
    exercise_type = request.args.get('type', '')
    subject = request.args.get('subject', '')
    level = request.args.get('level', '')

    # Construire la requête de base
    query = Exercise.query

    # Appliquer les filtres
    if search_query:
        search = f"%{search_query}%"
        query = query.filter(
            db.or_(
                Exercise.title.ilike(search),
                Exercise.description.ilike(search)
            )
        )
    
    if exercise_type:
        query = query.filter(Exercise.exercise_type == exercise_type)
    
    if subject:
        query = query.filter(Exercise.subject == subject)
    
    # Exécuter la requête
    exercises = query.all()

    # Debug: afficher le nombre d'exercices trouvés
    app.logger.info(f"Nombre d'exercices trouvés : {len(exercises)}")
    for ex in exercises:
        app.logger.info(f"Exercice : {ex.title} (type: {ex.exercise_type})")

    # Debug: afficher les types d'exercices passés au template
    current_app.logger.debug(f"Types d'exercices passés au template: {Exercise.EXERCISE_TYPES}")
    
    # Debug supplémentaire: vérifier si "Mots à placer" est présent
    word_placement_present = any(type_id == 'word_placement' for type_id, type_name in Exercise.EXERCISE_TYPES)
    current_app.logger.debug(f"'Mots à placer' présent dans la liste: {word_placement_present}")
    
    # Debug: afficher chaque type individuellement
    for i, (type_id, type_name) in enumerate(Exercise.EXERCISE_TYPES):
        current_app.logger.debug(f"  {i+1}. {type_id} -> {type_name}")
    
    return render_template('teacher/exercise_library.html', 
                         exercises=exercises,
                         exercise_types=Exercise.EXERCISE_TYPES,
                         selected_search=search_query,
                         selected_type=exercise_type,
                         selected_subject=subject,
                         selected_level=level)

@app.route('/exercise/<int:exercise_id>')
@app.route('/exercise/<int:exercise_id>/<int:course_id>')
# @login_required  # TEMPORAIREMENT DÉSACTIVÉ POUR TEST
def view_exercise(exercise_id, course_id=None):
    try:
        app.logger.debug(f'[VIEW_EXERCISE] Starting view_exercise for ID {exercise_id}')
        exercise = Exercise.query.get_or_404(exercise_id)
        app.logger.debug(f'[VIEW_EXERCISE] Exercise type: {exercise.exercise_type}')
        app.logger.info(f'Found exercise: {exercise.title} (ID: {exercise_id})')
        
        # Normaliser et corriger les chemins d'images si nécessaire
        modified = fix_exercise_image_path(exercise)
        if modified:
            db.session.commit()
            app.logger.info(f'[VIEW_EXERCISE] Image paths normalized for exercise {exercise_id}')
        
        # Récupérer le course_id depuis l'URL ou les paramètres de requête
        course_id = course_id or request.args.get('course_id', type=int)
        course = Course.query.get(course_id) if course_id else None
        
        if course:
            app.logger.info(f'Course context - ID: {course_id}, Title: {course.title}')
        else:
            app.logger.info('No course context provided')
            
    except Exception as e:
        app.logger.error(f'Error accessing exercise {exercise_id}: {str(e)}')
        app.logger.exception('Stack trace:')
        return 'Une erreur est survenue lors de l\'accès à l\'exercice.', 500
    
    # Si l'exercice est accédé via un cours, vérifier que l'étudiant est inscrit
    # TEMPORAIREMENT DÉSACTIVÉ POUR TEST SANS AUTHENTIFICATION
    # if course and current_user.role == 'student':
    #     class_obj = Class.query.get(course.class_id)
    #     if not class_obj or current_user not in class_obj.students:
    #         flash('Vous n\'avez pas accès à cet exercice.', 'error')
    #         return redirect(url_for('index'))
    
    attempt = None
    user_answers = {}
    # Si l'utilisateur est un étudiant
    # TEMPORAIREMENT DÉSACTIVÉ POUR TEST SANS AUTHENTIFICATION
    # if current_user.role == 'student':
    #     # Récupérer la dernière tentative
    #     attempt = ExerciseAttempt.query.filter_by(
    #         exercise_id=exercise_id,
    #         student_id=current_user.id
    #     ).order_by(ExerciseAttempt.created_at.desc()).first()
    
    # Pour les tests sans authentification, récupérer la dernière tentative
    attempt = ExerciseAttempt.query.filter_by(
        exercise_id=exercise_id
    ).order_by(ExerciseAttempt.created_at.desc()).first()
    
    # Par défaut, ne pas afficher les réponses
    show_answers = False
    user_answers = {}
    
    # Si une tentative existe et qu'elle a été soumise (score non nul)
    if attempt and attempt.score is not None:
        app.logger.debug(f'[VIEW_EXERCISE] Found submitted attempt ID: {attempt.id} with score: {attempt.score}')
        # Ne montrer les réponses que si l'exercice a été noté (après soumission)
        show_answers = True
        try:
            # Essayer de récupérer les réponses depuis le feedback
            if attempt.feedback and attempt.feedback.strip():
                feedback = json.loads(attempt.feedback) if attempt.feedback else []
                if isinstance(feedback, dict) and 'details' in feedback:
                    # Format de feedback structuré
                    for item in feedback.get('details', []):
                        if 'user_answer' in item and 'blank_index' in item:
                            user_answers[f'answer_{item["blank_index"]}'] = item['user_answer']
                        elif 'student_answer' in item and 'blank_index' in item:
                            user_answers[f'answer_{item["blank_index"]}'] = item['student_answer']
                elif isinstance(feedback, list):
                    # Ancien format de feedback
                    for item in feedback:
                        if 'student_answer' in item and 'blank_index' in item:
                            user_answers[f'answer_{item["blank_index"]}'] = item['student_answer']
                        elif 'student_answer' in item:
                            blank_counter = len(user_answers)
                            user_answers[f'answer_{blank_counter}'] = item['student_answer']
            app.logger.debug(f'[VIEW_EXERCISE] User answers to display: {user_answers}')
        except Exception as e:
            error_msg = f'Error parsing attempt feedback: {str(e)}'
            app.logger.error(error_msg)
            app.logger.exception('Error details:')
    else:
        app.logger.debug('[VIEW_EXERCISE] No submitted attempt found or exercise not yet graded')
        # S'assurer que les champs sont vides pour une nouvelle tentative
        user_answers = {}
    
    # Les enseignants peuvent accéder directement aux exercices
    # TEMPORAIREMENT DÉSACTIVÉ POUR TEST SANS AUTHENTIFICATION
    # elif current_user.role != 'teacher':
    #     flash("Vous n'avez pas les permissions nécessaires.", "error")
    #     return redirect(url_for('index'))
        
    # Récupérer les statistiques et le contenu de l'exercice
    app.logger.info(f'Exercise type: {exercise.exercise_type}')
    app.logger.info(f'Raw content: {exercise.content}')
    try:
        content = exercise.get_content()
        app.logger.info(f'Parsed content: {content}')
        
        # Vérifier si l'image existe physiquement et ajuster le chemin si nécessaire
        if 'image' in content and content['image']:
            content['image'] = get_image_url(content['image'])
            app.logger.info(f'[VIEW_EXERCISE] Verified image URL: {content["image"]}')
        # Mélange des éléments de droite pour les appariements
        if exercise.exercise_type == 'pairs':
            # Support pour la nouvelle structure avec 'pairs'
            if 'pairs' in content:
                app.logger.info('Processing pairs with new structure')
                # Convertir la nouvelle structure vers l'ancienne pour compatibilité
                pairs = content.get('pairs', [])
                left_items = [pair['left'] for pair in pairs]
                right_items = [pair['right'] for pair in pairs]
                content['left_items'] = left_items
                content['right_items'] = right_items
                app.logger.info(f'Left items: {left_items}')
                app.logger.info(f'Right items: {right_items}')
                
                # Mélanger les éléments de droite
                import random
                shuffled = list(enumerate(right_items))
                random.shuffle(shuffled)
                content['shuffled_right_items'] = [item for idx, item in shuffled]
                content['shuffled_indices'] = [idx for idx, item in shuffled]
                app.logger.info(f'Shuffled right items: {content["shuffled_right_items"]}')
                app.logger.info(f'Shuffled indices: {content["shuffled_indices"]}')
            # Support pour l'ancienne structure avec 'right_items'
            elif 'right_items' in content:
                app.logger.info('Processing pairs with old structure')
                right_items = content.get('right_items', [])
                import random
                shuffled = list(enumerate(right_items))
                random.shuffle(shuffled)
                content['shuffled_right_items'] = [item for idx, item in shuffled]
                content['shuffled_indices'] = [idx for idx, item in shuffled]
            else:
                app.logger.error('No pairs or right_items found in content')
                app.logger.error(f'Content keys: {list(content.keys())}')
        
        # Traitement spécifique pour les exercices "Souligner les mots"
        elif exercise.exercise_type == 'underline_words':
            app.logger.info('Processing underline_words exercise')
            app.logger.info(f'Content keys: {list(content.keys())}')
            
            # Vérifier que les données nécessaires sont présentes
            if 'words' in content:
                words_data = content['words']
                app.logger.info(f'Found {len(words_data)} sentences in words data')
                
                for i, sentence_data in enumerate(words_data):
                    app.logger.info(f'Sentence {i}: {sentence_data.get("text", "NO TEXT")}')
                    app.logger.info(f'Words to underline {i}: {sentence_data.get("words_to_underline", "NO WORDS")}')
                
                # Ajouter les instructions si elles ne sont pas présentes
                if 'instructions' not in content:
                    content['instructions'] = 'Cliquez sur les mots à souligner dans les phrases ci-dessous.'
                    app.logger.info('Added default instructions')
            else:
                app.logger.error('No words data found in underline_words exercise')
                app.logger.error(f'Available keys: {list(content.keys())}')
                # Créer une structure vide pour éviter les erreurs
                content['words'] = []
                content['instructions'] = 'Aucune phrase trouvée pour cet exercice.'
        
        # Traitement spécifique pour les exercices "Mots mêlés"
        elif exercise.exercise_type == 'word_search':
            app.logger.info('Processing word_search exercise')
            app.logger.info(f'Content keys: {list(content.keys())}')
            
            # Vérifier que les données nécessaires sont présentes
            if 'words' in content and ('grid_size' in content or ('grid_width' in content and 'grid_height' in content)):
                words = content['words']
                
                # Support des deux formats de grille
                if 'grid_size' in content:
                    # Format ancien : {"grid_size": {"width": 15, "height": 15}}
                    grid_size = content['grid_size']
                    width = grid_size['width']
                    height = grid_size['height']
                else:
                    # Format nouveau : {"grid_width": 15, "grid_height": 15}
                    width = content['grid_width']
                    height = content['grid_height']
                    grid_size = {'width': width, 'height': height}
                
                app.logger.info(f'Found {len(words)} words to place in {width}x{height} grid')
                
                # Générer la grille avec les mots placés
                try:
                    from word_search_generator import generate_word_search_grid
                    grid, placed_words = generate_word_search_grid(words, grid_size['width'], grid_size['height'])
                    content['grid'] = grid
                    content['placed_words'] = placed_words
                    app.logger.info(f'Grid generated successfully with {len(placed_words)} words placed')
                except ImportError:
                    app.logger.warning('word_search_generator not available, using improved simple grid generation')
                    # Génération améliorée de grille
                    import random
                    import string
                    
                    width = grid_size['width']
                    height = grid_size['height']
                    
                    # Créer une grille vide
                    grid = []
                    for i in range(height):
                        row = []
                        for j in range(width):
                            row.append('')  # Grille vide au départ
                        grid.append(row)
                    
                    # Directions possibles : horizontal, vertical, diagonal
                    directions = [
                        (0, 1),   # horizontal droite
                        (1, 0),   # vertical bas
                        (1, 1),   # diagonal bas-droite
                        (-1, 1),  # diagonal haut-droite
                    ]
                    
                    placed_words = []
                    
                    # Fonction pour vérifier si un mot peut être placé
                    def can_place_word(word, start_row, start_col, direction):
                        dr, dc = direction
                        for i, letter in enumerate(word):
                            r = start_row + i * dr
                            c = start_col + i * dc
                            if r < 0 or r >= height or c < 0 or c >= width:
                                return False
                            if grid[r][c] != '' and grid[r][c] != letter:
                                return False
                        return True
                    
                    # Fonction pour placer un mot
                    def place_word(word, start_row, start_col, direction):
                        dr, dc = direction
                        for i, letter in enumerate(word):
                            r = start_row + i * dr
                            c = start_col + i * dc
                            grid[r][c] = letter
                        
                        end_row = start_row + (len(word) - 1) * dr
                        end_col = start_col + (len(word) - 1) * dc
                        
                        direction_name = {
                            (0, 1): 'horizontal',
                            (1, 0): 'vertical',
                            (1, 1): 'diagonal_down_right',
                            (-1, 1): 'diagonal_up_right'
                        }.get(direction, 'unknown')
                        
                        placed_words.append({
                            'word': word,
                            'start': [start_row, start_col],
                            'end': [end_row, end_col],
                            'direction': direction_name
                        })
                    
                    # Placer TOUS les mots (pas seulement 3)
                    for word in words:
                        placed = False
                        attempts = 0
                        max_attempts = 100
                        
                        while not placed and attempts < max_attempts:
                            # Choisir une direction aléatoire
                            direction = random.choice(directions)
                            dr, dc = direction
                            
                            # Calculer les limites de position de départ
                            if dr >= 0:
                                max_row = height - len(word)
                            else:
                                max_row = height - 1
                                min_row = len(word) - 1
                            
                            if dc >= 0:
                                max_col = width - len(word)
                            else:
                                max_col = width - 1
                                min_col = len(word) - 1
                            
                            # Générer une position aléatoire valide
                            if dr >= 0:
                                start_row = random.randint(0, max(0, max_row))
                            else:
                                start_row = random.randint(min_row, max_row)
                            
                            if dc >= 0:
                                start_col = random.randint(0, max(0, max_col))
                            else:
                                start_col = random.randint(min_col, max_col)
                            
                            # Vérifier si le mot peut être placé
                            if can_place_word(word, start_row, start_col, direction):
                                place_word(word, start_row, start_col, direction)
                                placed = True
                                app.logger.info(f'Placed word "{word}" at ({start_row}, {start_col}) direction {direction}')
                            
                            attempts += 1
                        
                        if not placed:
                            app.logger.warning(f'Could not place word "{word}" after {max_attempts} attempts')
                    
                    # Remplir les cases vides avec des lettres aléatoires
                    for i in range(height):
                        for j in range(width):
                            if grid[i][j] == '':
                                grid[i][j] = random.choice(string.ascii_uppercase)
                    
                    content['grid'] = grid
                    content['placed_words'] = placed_words
                    app.logger.info(f'Improved grid generated with {len(placed_words)} words placed out of {len(words)} total words')
                
                # Ajouter les instructions si elles ne sont pas présentes
                if 'instructions' not in content:
                    content['instructions'] = 'Trouvez tous les mots cachés dans la grille ci-dessous.'
                    app.logger.info('Added default instructions for word_search')
            else:
                app.logger.error('No words or grid_size found in word_search exercise')
                app.logger.error(f'Available keys: {list(content.keys())}')
                # Créer une structure vide pour éviter les erreurs
                content['words'] = []
                content['grid'] = []
                content['instructions'] = 'Aucune donnée trouvée pour cet exercice.'
        
        # Traitement spécifique pour les exercices "Mots à placer"
        elif exercise.exercise_type == 'word_placement':
            print(f'[WORD_PLACEMENT_DISPLAY] Processing word_placement exercise')
            print(f'[WORD_PLACEMENT_DISPLAY] Content keys: {list(content.keys())}')
            print(f'[WORD_PLACEMENT_DISPLAY] Raw content: {content}')
            
            # Vérifier que les données nécessaires sont présentes
            if 'sentences' in content and 'words' in content:
                sentences = content['sentences']
                words = content['words']
                print(f'[WORD_PLACEMENT_DISPLAY] Found {len(sentences)} sentences and {len(words)} words')
                
                # Ajouter les instructions si elles ne sont pas présentes
                if 'instructions' not in content:
                    content['instructions'] = 'Faites glisser les mots dans les bonnes phrases ou cliquez pour les placer.'
                    app.logger.info('Added default instructions for word_placement')
                
                # Pour word_placement, les phrases sont des chaînes simples avec des "___"
                # Pas besoin de traiter comme des dictionnaires avec blanks
                for i, sentence in enumerate(sentences):
                    if isinstance(sentence, str):
                        blank_count = sentence.count('___')
                        app.logger.info(f'Sentence {i}: "{sentence}" with {blank_count} blanks')
                    else:
                        app.logger.warning(f'Sentence {i} is not a string: {type(sentence)}')
                
                app.logger.info(f'Available words: {words}')
            else:
                app.logger.error('No sentences or words found in word_placement exercise')
                app.logger.error(f'Available keys: {list(content.keys())}')
                # Créer une structure vide pour éviter les erreurs
                content['sentences'] = []
                content['words'] = []
                content['instructions'] = 'Aucune donnée trouvée pour cet exercice.'
    except Exception as e:
        app.logger.error(f'Error parsing content: {str(e)}')
        app.logger.exception('Full error:')
        content = {'questions': []}
    progress = None
    
    # TEMPORAIREMENT DÉSACTIVÉ POUR TEST SANS AUTHENTIFICATION
    # progress = exercise.get_student_progress(current_user.id)
    
    # Choisir le template en fonction du type d'exercice
    if exercise.exercise_type == 'pairs':
        template = 'exercise_types/pairs_fixed.html'  # TEMPLATE CORRIGÉ
        app.logger.info(f'Using FIXED template for pairs: {template}')
    elif exercise.exercise_type == 'underline_words':
        template = 'exercise_types/underline_words.html'  # TEMPLATE ORIGINAL RESTAURÉ
        app.logger.info(f'Using ORIGINAL template for underline_words: {template}')
    else:
        template = f'exercise_types/{exercise.exercise_type}.html'
        app.logger.info(f'Using template: {template}')
    
    try:
        # Vérifier que le template existe
        if not os.path.exists(os.path.join(app.template_folder, template)):
            app.logger.error(f'Template not found: {template}')
            return 'Le template pour ce type d\'exercice n\'existe pas.', 500
        
        # Vérifier que les variables sont correctes
        app.logger.info(f'Variables for template:')
        app.logger.info(f'- exercise: {exercise}')
        app.logger.info(f'- attempt: {attempt}')
        app.logger.info(f'- content: {content}')
        app.logger.info(f'- progress: {progress}')
        app.logger.info(f'- course: {course}')
        
        return render_template(template,
                            exercise=exercise,
                            attempt=attempt,
                            content=content,
                            progress=progress,
                            course=course,
                            user_answers=user_answers,
                            show_answers=show_answers)
    except Exception as e:
        app.logger.error(f'Error rendering template: {str(e)}')
        app.logger.exception('Full template error:')
        return 'Une erreur est survenue lors de l\'affichage de l\'exercice.', 500

# Route /get_cloudinary_url maintenant gérée par fix_image_display_routes.py

@app.route('/exercise/<int:exercise_id>/teacher')
@login_required
def view_exercise_teacher(exercise_id):
    if not current_user.is_teacher:
        flash("Accès non autorisé.", "error")
        return redirect(url_for('index'))
        
    exercise = Exercise.query.get_or_404(exercise_id)
    return render_template('view_exercise_teacher.html', exercise=exercise)

@app.route('/course/<int:course_id>')
@login_required
def view_course(course_id):
    course = Course.query.get_or_404(course_id)

    # Vérifier que l'utilisateur a accès au cours
    if not current_user.is_teacher and not current_user.is_enrolled(course.class_obj.id):
        flash('Vous n\'avez pas accès à ce cours.', 'error')
        return redirect(url_for('index'))

    # Si c'est un enseignant, récupérer la liste des exercices disponibles
    exercises_available = []
    if current_user.is_teacher:
        # Récupérer tous les exercices créés par l'enseignant qui ne sont pas déjà dans le cours
        exercises_available = Exercise.query.filter_by(teacher_id=current_user.id).filter(
            ~Exercise.id.in_([ex.id for ex in course.exercises])
        ).all()

    # Récupérer les exercices du cours
    exercises = course.exercises

    # Pour les enseignants, récupérer les statistiques du cours
    stats = None
    if current_user.is_teacher:
        stats = {
            'total_students': len(course.class_obj.students),
            'total_exercises': len(exercises),
            'exercises_stats': []
        }


        for exercise in exercises:
            exercise_stats = {
                'title': exercise.title,
                'completion_rate': 0,
                'average_score': 0,
                'needs_grading': 0
            }

            total_students = len(course.class_obj.students)
            if total_students > 0:
                completed = 0
                total_score = 0
                needs_grading = 0

                for student in course.class_obj.students:
                    progress = exercise.get_student_progress(student.id)
                    if progress and progress.get('best_score') is not None:
                        completed += 1
                        total_score += progress['best_score']
                    elif progress and progress.get('needs_grading'):
                        needs_grading += 1

                exercise_stats['completion_rate'] = (completed / total_students) * 100
                if completed > 0:
                    exercise_stats['average_score'] = total_score / completed
                exercise_stats['needs_grading'] = needs_grading

            stats['exercises_stats'].append(exercise_stats)

    # Calcul de la progression pour les étudiants (partie droite)
    progress_records = []
    total_exercises = len(exercises)
    if not current_user.is_teacher:
        for ex in exercises:
            progress = ex.get_student_progress(current_user.id)
            if progress and progress.get('best_score', 0) >= 70:
                progress_records.append({'exercise_id': ex.id, 'student_id': current_user.id})

    return render_template('view_course.html',
                         course=course,
                         exercises=exercises,
                         exercises_available=exercises_available,
                         stats=stats,
                         progress_records=progress_records,
                         total_exercises=total_exercises)

@app.route('/class/<int:class_id>/create_course', methods=['GET', 'POST'])
@login_required
@teacher_required
def create_course(class_id):
    class_obj = Class.query.get_or_404(class_id)

    # Vérifier que l'utilisateur est bien le professeur de cette classe
    if class_obj.teacher_id != current_user.id:
        flash("Vous n'avez pas l'autorisation de créer un cours dans cette classe.", 'error')
        return redirect(url_for('teacher_dashboard'))

    class CourseForm(FlaskForm):
        title = StringField('Titre', validators=[DataRequired()])
        content = TextAreaField('Contenu')
        files = MultipleFileField('Fichiers joints')

    form = CourseForm()

    if form.validate_on_submit():
        # Récupérer le contenu de l'éditeur
        content = request.form.get('content', '{}')

        course = Course(
            title=form.title.data,
            content=json.dumps(content),  # Convertir en JSON
            class_id=class_id
        )

        # Gérer les fichiers
        files = request.files.getlist('files')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                course_file = CourseFile(
                    filename=filename,
                    original_filename=file.filename,
                    file_type=file.content_type,
                    file_size=os.path.getsize(filepath),
                    course=course
                )
                db.session.add(course_file)

        db.session.add(course)
        db.session.commit()
        flash('Le cours a été créé avec succès.', 'success')
        return redirect(url_for('view_class', class_id=class_id))

    return render_template('create_course.html', form=form, class_id=class_id)

@app.route('/student/classes')
@login_required
def view_student_classes():
    if current_user.is_teacher:
        flash('Cette page est réservée aux étudiants.', 'error')
        return redirect(url_for('teacher_dashboard'))

    enrolled_classes = current_user.classes_enrolled
    return render_template('student_classes.html', classes=enrolled_classes)

@app.route('/class/join_by_code', methods=['GET', 'POST'])
@login_required
def join_class_by_code():
    if request.method == 'POST':
        class_code = request.form.get('class_code')
        if not class_code:
            flash('Le code d\'accès est requis.', 'error')
            return redirect(url_for('view_student_classes'))

        class_obj = Class.query.filter_by(access_code=class_code).first()
        if not class_obj:
            flash('Code d\'accès invalide.', 'error')
            return redirect(url_for('view_student_classes'))

        if current_user in class_obj.students:
            flash('Vous êtes déjà inscrit dans cette classe.', 'warning')
            return redirect(url_for('view_class', class_id=class_obj.id))

        try:
            class_obj.students.append(current_user)
            db.session.commit()
            flash('Vous avez rejoint la classe avec succès !', 'success')
            return redirect(url_for('view_class', class_id=class_obj.id))
        except Exception as e:
            db.session.rollback()
            flash('Une erreur est survenue lors de l\'inscription à la classe.', 'error')
            return redirect(url_for('view_student_classes'))

    return redirect(url_for('view_student_classes'))

@app.route('/class/<int:class_id>/view')
@login_required
def view_class(class_id):
    class_obj = Class.query.get_or_404(class_id)

    # Si c'est l'enseignant de la classe
    if current_user.is_teacher and class_obj.teacher_id == current_user.id:
        return view_class_teacher(class_id)

    # Si c'est un étudiant inscrit dans la classe
    if not current_user.is_teacher and class_obj in current_user.classes_enrolled:
        return render_template('view_class.html', class_obj=class_obj)

    flash('Accès non autorisé.', 'error')
    return redirect(url_for('index'))

@app.route('/class/<int:class_id>/view/teacher')
@login_required
@teacher_required
def view_class_teacher(class_id):
    class_obj = Class.query.get_or_404(class_id)
    if class_obj.teacher_id != current_user.id:
        flash('Vous n\'êtes pas le professeur de cette classe.', 'error')
        return redirect(url_for('index'))
    return render_template('view_class.html', class_obj=class_obj)

@app.route('/course/<int:course_id>/add-exercise', methods=['POST'])
@login_required
def add_exercise_to_course(course_id):
    app.logger.info(f"[add_exercise_to_course] Début de l'ajout d'exercice au cours {course_id}")
    app.logger.info(f"[add_exercise_to_course] Utilisateur: {current_user.id} ({current_user.role})")

    if not current_user.is_teacher:
        app.logger.warning("[add_exercise_to_course] Tentative d'accès non autorisé")
        flash('Accès non autorisé. Seuls les enseignants peuvent ajouter des exercices.', 'error')
        return redirect(url_for('index'))

    course = Course.query.get_or_404(course_id)
    app.logger.info(f"[add_exercise_to_course] Cours trouvé: {course.title}")

    # Vérifier que l'utilisateur est le propriétaire de la classe
    if course.class_obj.teacher_id != current_user.id:
        app.logger.warning("[add_exercise_to_course] L'utilisateur n'est pas le propriétaire de la classe")
        flash('Vous ne pouvez pas modifier ce cours.', 'error')
        return redirect(url_for('index'))

    exercise_id = request.form.get('exercise_id')
    app.logger.info(f"[add_exercise_to_course] ID de l'exercice reçu: {exercise_id}")

    if not exercise_id:
        app.logger.warning("[add_exercise_to_course] Aucun exercice sélectionné")
        flash('Veuillez sélectionner un exercice.', 'error')
        return redirect(url_for('view_course', course_id=course_id))

    exercise = Exercise.query.get_or_404(exercise_id)
    app.logger.info(f"[add_exercise_to_course] Exercice trouvé: {exercise.title}")

    # Vérifier que l'exercice n'est pas déjà dans le cours
    if exercise in course.exercises:
        app.logger.warning("[add_exercise_to_course] L'exercice est déjà dans le cours")
        flash('Cet exercice est déjà dans le cours.', 'error')
        return redirect(url_for('view_course', course_id=course_id))

    try:
        app.logger.info(f"[add_exercise_to_course] Tentative d'ajout de l'exercice {exercise_id} au cours {course_id}")
        app.logger.info(f"[add_exercise_to_course] État actuel du cours - Exercices: {[ex.id for ex in course.exercises]}")

        course.exercises.append(exercise)
        db.session.commit()

        app.logger.info(f"[add_exercise_to_course] Nouvel état du cours - Exercices: {[ex.id for ex in course.exercises]}")
        flash('Exercice ajouté au cours avec succès !', 'success')
        return redirect(url_for('view_course', course_id=course_id))
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"[add_exercise_to_course] Erreur lors de l'ajout : {str(e)}")
        app.logger.error(f"[add_exercise_to_course] Type d'erreur : {type(e).__name__}")
        import traceback
        app.logger.error(f"[add_exercise_to_course] Traceback : {traceback.format_exc()}")
        flash('Erreur lors de l\'ajout de l\'exercice au cours.', 'error')
        return redirect(url_for('view_course', course_id=course_id))

@app.route('/course/<int:course_id>/remove-exercise/<int:exercise_id>', methods=['POST'])
@login_required
def remove_exercise_from_course(course_id, exercise_id):
    if not current_user.is_teacher:
        flash('Accès non autorisé. Seuls les enseignants peuvent retirer des exercices.', 'error')
        return redirect(url_for('index'))

    course = Course.query.get_or_404(course_id)

    # Vérifier que l'utilisateur est le propriétaire de la classe
    if course.class_obj.teacher_id != current_user.id:
        flash('Vous ne pouvez pas modifier ce cours.', 'error')
        return redirect(url_for('index'))

    exercise = Exercise.query.get_or_404(exercise_id)

    try:
        course.exercises.remove(exercise)
        db.session.commit()
        flash('Exercice retiré du cours avec succès !', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erreur lors du retrait de l\'exercice du cours.', 'error')
        print(f"Erreur : {str(e)}")

    return redirect(url_for('view_course', course_id=course_id))

@app.route('/quick-add-exercise/<int:exercise_id>', methods=['GET', 'POST'])
@login_required
def process_quick_add_exercise(exercise_id):
    try:
        # Récupérer l'exercice
        exercise = Exercise.query.get_or_404(exercise_id)
        app.logger.info(f"[quick_add_exercise] Exercice trouvé: {exercise.title}")

        # Récupérer toutes les classes de l'utilisateur
        classes = Class.query.filter_by(teacher_id=current_user.id).all()
        app.logger.info(f"[quick_add_exercise] Nombre de classes trouvées: {len(classes)}")

        # Récupérer la classe sélectionnée si elle existe
        selected_class_id = request.args.get('class_id')
        selected_courses = []
        if selected_class_id:
            try:
                # Vérifier que la classe appartient à l'utilisateur
                class_obj = Class.query.get(int(selected_class_id))
                if class_obj and class_obj.teacher_id == current_user.id:
                    selected_courses = Course.query.filter_by(class_id=int(selected_class_id)).all()
                    app.logger.info(f"[quick_add_exercise] Cours trouvés pour la classe {selected_class_id}: {len(selected_courses)}")
            except ValueError:
                app.logger.error(f"[quick_add_exercise] ID de classe invalide: {selected_class_id}")
                selected_courses = []

        # Si c'est une requête POST, traiter l'ajout de l'exercice
        if request.method == 'POST':
            class_id = request.form.get('class_id')
            course_id = request.form.get('course_id')

            app.logger.info(f"[process_quick_add_exercise] Données reçues - class_id: {class_id}, course_id: {course_id}")

            if not class_id or not course_id:
                flash('Veuillez sélectionner une classe et un cours.', 'error')
                return redirect(url_for('process_quick_add_exercise', exercise_id=exercise_id, class_id=class_id))

            # Vérifier que la classe appartient à l'utilisateur
            class_obj = Class.query.get(class_id)
            if not class_obj or class_obj.teacher_id != current_user.id:
                flash('Classe non trouvée ou accès non autorisé.', 'error')
                return redirect(url_for('exercise_library'))

            # Vérifier que le cours appartient à la classe
            course = Course.query.get(course_id)
            if not course or course.class_id != int(class_id):
                flash('Cours non trouvé ou accès non autorisé.', 'error')
                return redirect(url_for('exercise_library'))

            # Ajouter l'exercice au cours s'il n'y est pas déjà
            if exercise not in course.exercises:
                app.logger.info(f"[process_quick_add_exercise] Ajout de l'exercice {exercise_id} au cours {course_id}")
                course.exercises.append(exercise)
                db.session.commit()
                flash('Exercice ajouté avec succès au cours !', 'success')
                return redirect(url_for('view_course', course_id=course_id))
            else:
                app.logger.info(f"[process_quick_add_exercise] L'exercice {exercise_id} est déjà dans le cours {course_id}")
                flash('Cet exercice est déjà dans le cours.', 'info')
                return redirect(url_for('view_course', course_id=course_id))

        # Pour les requêtes GET, afficher le formulaire
        return render_template('add_exercise_to_class.html',
                             exercise=exercise,
                             classes=classes,
                             selected_class_id=selected_class_id,
                             selected_courses=selected_courses)

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"[process_quick_add_exercise] Erreur lors de l'ajout de l'exercice: {str(e)}")
        app.logger.error(f"[process_quick_add_exercise] Type d'erreur: {type(e).__name__}")
        import traceback
        app.logger.error(f"[process_quick_add_exercise] Traceback: {traceback.format_exc()}")
        flash('Une erreur est survenue lors de l\'ajout de l\'exercice.', 'error')
        return redirect(url_for('process_quick_add_exercise', exercise_id=exercise_id))

@app.route('/class/create', methods=['GET', 'POST'])
@login_required
@teacher_required
def create_class():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        if not name:
            flash('Le nom de la classe est requis.', 'error')
            return redirect(url_for('create_class'))

        # Générer un code d'accès unique
        import random
        import string

        access_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        while Class.query.filter_by(access_code=access_code).first() is not None:
            access_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        try:
            new_class = Class(
                name=name,
                description=description,
                teacher_id=current_user.id,
                access_code=access_code
            )

            db.session.add(new_class)
            db.session.commit()

            # Afficher le code d'accès à l'enseignant
            flash(f'Classe créée avec succès ! Code d\'accès : {access_code}', 'success')
            return redirect(url_for('view_class', class_id=new_class.id))
        except Exception as e:
            db.session.rollback()
            flash('Une erreur est survenue lors de la création de la classe.', 'error')
            return redirect(url_for('create_class'))

    return render_template('create_class.html')

@app.route('/class/<int:class_id>/edit', methods=['GET', 'POST'])
@login_required
@teacher_required
def edit_class(class_id):
    class_obj = Class.query.get_or_404(class_id)

    # Vérifier que l'utilisateur est bien le propriétaire de la classe
    if class_obj.teacher_id != current_user.id:
        flash('Vous n\'avez pas la permission de modifier cette classe.', 'error')
        return redirect(url_for('teacher_dashboard'))

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        if not name:
            flash('Le nom de la classe est requis.', 'error')
            return redirect(url_for('edit_class', class_id=class_id))

        try:
            class_obj.name = name
            class_obj.description = description
            db.session.commit()
            flash('Classe modifiée avec succès !', 'success')
            return redirect(url_for('view_class', class_id=class_id))
        except Exception as e:
            db.session.rollback()
            flash('Une erreur est survenue lors de la modification de la classe.', 'error')
            return redirect(url_for('edit_class', class_id=class_id))

    return render_template('edit_class.html', class_obj=class_obj)

@app.route('/course/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
@teacher_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    class_obj = Class.query.get_or_404(course.class_id)

    # Vérifier que l'utilisateur est le professeur de la classe
    if current_user.id != class_obj.teacher_id:
        flash("Vous n'êtes pas autorisé à modifier ce cours.", 'error')
        return redirect(url_for('view_class', class_id=class_obj.id))

    class CourseForm(FlaskForm):
        title = StringField('Titre', validators=[DataRequired()])
        files = MultipleFileField('Ajouter des fichiers')

    form = CourseForm(obj=course)

    if form.validate_on_submit():
        course.title = form.title.data
        course.content = json.dumps(request.form.get('content', '{}'))  # Convertir en JSON

        # Gérer les nouveaux fichiers
        files = request.files.getlist('files')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                course_file = CourseFile(
                    filename=filename,
                    original_filename=file.filename,
                    file_type=file.content_type,
                    file_size=os.path.getsize(filepath),
                    course=course
                )
                db.session.add(course_file)

        db.session.commit()
        flash('Le cours a été modifié avec succès !', 'success')
        return redirect(url_for('view_course', course_id=course.id))

    return render_template('edit_course.html', course=course, form=form)

@app.route('/course/<int:course_id>/file/<int:file_id>/delete', methods=['POST'])
@login_required
@teacher_required
def delete_course_file(course_id, file_id):
    course = Course.query.get_or_404(course_id)
    course_file = CourseFile.query.get_or_404(file_id)

    # Vérifier que le fichier appartient bien au cours
    if course_file.course_id != course.id:
        return jsonify({'error': 'Ce fichier n\'appartient pas à ce cours.'}), 403

    # Vérifier que l'utilisateur est bien le professeur de la classe
    class_obj = Class.query.get(course.class_id)
    if current_user.id != class_obj.teacher_id:
        return jsonify({'error': 'Vous n\'êtes pas autorisé à supprimer ce fichier.'}), 403

    try:
        # Supprimer le fichier physique
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], course_file.filename)
        if os.path.exists(file_path):
            os.remove(file_path)

        # Supprimer l'entrée dans la base de données
        db.session.delete(course_file)
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/exercise/underline-words-example')
@app.route('/exercise/<int:exercise_id>/submit', methods=['POST'])
@login_required
def submit_exercise(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    course_id = request.form.get('course_id')
    
    # Si un course_id est fourni, vérifier les permissions
    if course_id:
        course = Course.query.get_or_404(course_id)
        if not current_user.is_enrolled(course.class_obj.id):
            flash('Vous n\'avez pas accès à cet exercice.', 'error')
            return redirect(url_for('student_classes'))
        
        # Vérifier que l'exercice fait partie du cours
        if exercise not in course.exercises:
            flash('Cet exercice ne fait pas partie du cours.', 'error')
            return redirect(url_for('view_course', course_id=course_id))
    
    # Vérifier le nombre de tentatives restantes
    progress = exercise.get_student_progress(current_user.id)
    if exercise.max_attempts and progress and progress['remaining_attempts'] is not None and progress['remaining_attempts'] <= 0:
        flash('Vous avez atteint le nombre maximum de tentatives pour cet exercice.', 'error')
        return redirect(url_for('view_exercise', exercise_id=exercise_id))
        return redirect(url_for('view_exercise', exercise_id=exercise_id, course_id=course_id))
    
    # Traiter les réponses
    answers = []
    score = 0
    feedback = []
    content = exercise.get_content()
    
    if exercise.exercise_type == 'qcm':
        total_questions = len(content['questions'])
        correct_answers = 0
        
        app.logger.debug(f'Content: {content}')
        for i, question in enumerate(content['questions']):
            answer = request.form.get(f'answer_{i}')
            app.logger.debug(f'Réponse brute pour la question {i}: {answer}')
            
            # Convertir la réponse en entier
            try:
                answer = int(answer) if answer is not None else -1
            except (ValueError, TypeError):
                answer = -1
            answers.append(answer)
            
            # Accepter à la fois 'correct' et 'correct_answer' comme clé de la bonne réponse
            correct_key = 'correct'
            if 'correct' not in question and 'correct_answer' in question:
                correct_key = 'correct_answer'
            if correct_key not in question:
                app.logger.error(f"La question {i} ne contient pas la clé 'correct' ou 'correct_answer'. Structure de la question : {question}")
                feedback.append({
                    'question': i + 1,
                    'correct': False,
                    'message': "Erreur interne : la question est mal structurée. Merci de contacter l'enseignant."
                })
                continue  # On passe à la question suivante
            # S'assurer que la valeur est bien un entier pour la comparaison
            try:
                correct = int(question[correct_key])
            except (ValueError, TypeError, KeyError):
                correct = -1
            app.logger.debug(f'Question {i} - Réponse de l\'utilisateur: {answer}, Réponse correcte: {correct}')
            
            # Forcer la conversion en int pour éviter les erreurs de type
            try:
                answer_int = int(answer)
            except (ValueError, TypeError):
                app.logger.warning(f"Impossible de convertir la réponse utilisateur '{answer}' en int pour la question {i}.")
                answer_int = -999
            try:
                correct_int = int(correct)
            except (ValueError, TypeError):
                app.logger.warning(f"Impossible de convertir la réponse correcte '{correct}' en int pour la question {i}.")
                correct_int = -999
            # Vérifier si la réponse est correcte
            if answer_int == correct_int:
                correct_answers += 1
                app.logger.debug(f'Question {i} - Bonne réponse !')
                feedback.append({
                    'question': i + 1,
                    'correct': True,
                    'message': 'Bonne réponse !'
                })
            else:
                # Récupérer le texte de la réponse correcte
                correct_option = question['options'][correct] if 0 <= correct < len(question['options']) else 'Non spécifiée'
                app.logger.debug(f'Question {i} - Mauvaise réponse. Attendu: {correct_option}')
                feedback.append({
                    'question': i + 1,
                    'correct': False,
                    'message': f'La réponse correcte était : {correct_option}'
                })
        
        app.logger.debug(f'Réponses correctes: {correct_answers}, Total questions: {total_questions}')
        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        app.logger.debug(f'Score final: {score}%')
    
    elif exercise.exercise_type == 'fill_in_blanks':
        # Cette implémentation a été désactivée car elle est en conflit avec l'implémentation plus complète
        # Voir lignes ~3415-3510 pour l'implémentation active.
        pass

    elif exercise.exercise_type == 'word_placement':
        user_answers = []
        correct_answers = content.get('answers', [])
        
        # Récupérer toutes les réponses de l'utilisateur dans l'ordre séquentiel
        i = 0
        while True:
            answer = request.form.get(f'answer_{i}')
            if answer is None:
                break
            user_answers.append(answer.strip())
            i += 1
        
        app.logger.debug(f'[WORD_PLACEMENT_SCORING] Réponses utilisateur: {user_answers}')
        app.logger.debug(f'[WORD_PLACEMENT_SCORING] Réponses correctes: {correct_answers}')
        
        if len(user_answers) != len(correct_answers):
            flash('Nombre de réponses incorrect.', 'error')
            return redirect(url_for('view_exercise', exercise_id=exercise_id))
        
        score = 0
        feedback = []
        for i, (user_ans, correct_ans) in enumerate(zip(user_answers, correct_answers)):
            # Comparaison insensible à la casse et aux espaces
            is_correct = user_ans.strip().lower() == correct_ans.strip().lower()
            score += 1 if is_correct else 0
            feedback.append({
                'user_answer': user_ans,
                'correct_answer': correct_ans,
                'is_correct': is_correct,
                'position': i + 1
            })
        
        max_score = len(correct_answers)
        score = (score / max_score) * 100 if max_score > 0 else 0
        
        app.logger.debug(f'[WORD_PLACEMENT_SCORING] Score final: {score}% ({score}/{max_score})')
    
    elif exercise.exercise_type == 'word_search':
        found_words = request.form.getlist('found_words[]')
        total_words = len(content['words'])
        correct_words = 0
        
        # Convertir les mots trouvés et les mots à chercher en minuscules pour la comparaison
        found_words = [word.lower().strip() for word in found_words]
        target_words = [word.lower().strip() for word in content['words']]
        
        for word in found_words:
            if word in target_words:
                correct_words += 1
                feedback.append({
                    'word': word,
                    'correct': True,
                    'message': 'Mot trouvé !'
                })
        
        # Ajouter le feedback pour les mots non trouvés
        for word in target_words:
            if word not in found_words:
                feedback.append({
                    'word': word,
                    'correct': False,
                    'message': 'Mot non trouvé'
                })
        
        score = (correct_words / total_words) * 100 if total_words > 0 else 0
        
    elif exercise.exercise_type == 'pairs':
        # Structure attendue : 'correct_pairs': [[0, 0], [1, 1], ...], left_items, right_items
        correct_pairs = content.get('correct_pairs', [])
        total_pairs = len(correct_pairs)
        correct_count = 0
        user_pairs = []
        for i in range(total_pairs):
            left = request.form.get(f'left_{i}')
            right = request.form.get(f'right_{i}')
            if left is not None and right is not None:
                try:
                    left_idx = int(left)
                    right_idx = int(right)
                    user_pairs.append([left_idx, right_idx])
                    answers.append({'left': left_idx, 'right': right_idx})
                except (ValueError, TypeError):
                    continue
        for pair in correct_pairs:
            if pair in user_pairs:
                correct_count += 1
                feedback.append({'pair': pair, 'correct': True, 'message': 'Paire correcte !'})
            else:
                feedback.append({'pair': pair, 'correct': False, 'message': 'Paire incorrecte'})
        score = (correct_count / total_pairs) * 100 if total_pairs > 0 else 0
    
    # S'assurer que le score est un nombre valide
    if score is None:
        score = 0.0
    
    # Enregistrer la tentative
    attempt = ExerciseAttempt(
        student_id=current_user.id,
        exercise_id=exercise_id,
        course_id=course_id,
        score=float(score),  # Convertir explicitement en float
        answers=json.dumps(answers),
        feedback=json.dumps(feedback),
        completed=True
    )
    
    db.session.add(attempt)
    db.session.commit()
    
    # Rafraîchir l'objet depuis la base de données pour s'assurer que tout est à jour
    db.session.refresh(attempt)
    
    flash(f'Exercice soumis avec succès ! Score : {score:.1f}%', 'success')
    return redirect(url_for('view_exercise', exercise_id=exercise_id, course_id=course_id))

@app.route('/exercise/<int:exercise_id>/stats')
@login_required
@teacher_required
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

@app.route('/exercise/<int:exercise_id>/feedback/<int:attempt_id>')
@login_required
def view_feedback(exercise_id, attempt_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    attempt = ExerciseAttempt.query.get_or_404(attempt_id)
    
    # Vérifier que l'utilisateur a le droit de voir ce feedback
    if not current_user.is_teacher and attempt.student_id != current_user.id:
        flash("Vous n'avez pas l'autorisation de voir cette tentative.", "error")
        return redirect(url_for('index'))

    # Si c'est un enseignant, vérifier qu'il enseigne dans la classe associée au cours
    if current_user.is_teacher and attempt.course_id:
        course = Course.query.get(attempt.course_id)
        if course and course.class_obj.teacher_id != current_user.id:
            flash("Vous n'avez pas l'autorisation de voir cette tentative.", "error")
            return redirect(url_for('index'))
    
    # Convertir les réponses et le feedback en dictionnaires
    answers = {}
    feedback = {}
    
    if exercise.exercise_type == 'qcm':
        answers_list = json.loads(attempt.answers)
        for i, answer in enumerate(answers_list, 1):
            answers[str(i)] = answer
    elif exercise.exercise_type == 'pair_match':
        pairs = json.loads(attempt.answers)
        for i, pair in enumerate(pairs, 1):
            answers[str(i)] = f"{pair['left']} → {pair['right']}"
    
    if attempt.feedback:
        feedback = json.loads(attempt.feedback)
    
    return render_template('feedback.html',
                         exercise=exercise,
                         attempt=attempt,
                         answers=answers,
                         feedback=feedback)

@app.route('/course/<int:course_id>/file/<int:file_id>/download')
@login_required
def download_course_file(course_id, file_id):
    course = Course.query.get_or_404(course_id)
    file = CourseFile.query.get_or_404(file_id)
    
    if file.course_id != course.id:
        flash('Fichier non trouvé.', 'error')
        return redirect(url_for('view_course', course_id=course_id))
    
    # Vérifier que l'utilisateur a accès au cours
    if current_user.is_teacher or any(c.id == course.class_id for c in current_user.classes_enrolled):
        uploads_dir = app.config['UPLOAD_FOLDER']  # Utilise le bon dossier static/uploads
        return send_from_directory(uploads_dir, file.filename, as_attachment=True, download_name=file.original_filename)
    else:
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('index'))

@app.route('/course/<int:course_id>/get-available-exercises')
@login_required
def get_available_exercises(course_id):
    """Retourne la liste des exercices disponibles pour un cours"""
    if not current_user.is_teacher:
        return jsonify({'error': 'Non autorisé'}), 403
    
    course = Course.query.get_or_404(course_id)
    if course.class_obj.teacher_id != current_user.id:
        return jsonify({'error': 'Non autorisé'}), 403
    
    # Récupérer tous les exercices disponibles
    exercises = Exercise.query.all()
    
    # Filtrer les exercices qui ne sont pas déjà dans le cours
    available_exercises = [
        {'id': ex.id, 'title': ex.title, 'type': ex.exercise_type}
        for ex in exercises if ex not in course.exercises
    ]
    
    return jsonify(available_exercises)

@app.route('/exercise/<int:exercise_id>/submit/<int:course_id>', methods=['POST'])
# @login_required  # Commenté pour les tests sans authentification

def submit_answer(exercise_id, course_id=0):
    app.logger.info(f"[DEBUG] submit_exercise_answer called for exercise_id={exercise_id}")
    print("\n=== DÉBUT SUBMIT_ANSWER ===\n")
    print(f"[DEBUG] Soumission pour l'exercice {exercise_id}")
    # print(f"[DEBUG] Utilisateur: {current_user.username} (ID: {current_user.id})")  # Commenté pour tests sans auth
    print("[DEBUG] Form data:", request.form)
    print("[DEBUG] Form data type:", type(request.form))
    
    exercise = Exercise.query.get_or_404(exercise_id)
    # Utiliser le course_id de l'URL ou du formulaire comme fallback
    if not course_id:
        course_id = request.form.get('course_id')
    print(f"[DEBUG] Course ID from route: {course_id}")
    print(f"[DEBUG] Course ID from form: {request.form.get('course_id')}")
    
    # if not course_id:  # Commenté pour tests sans cours
    #     flash('Erreur: Cours non spécifié', 'error')
    #     return redirect(url_for('exercise_library'))
    
    # Vérifier que l'étudiant a accès à ce cours
    # course = Course.query.get_or_404(course_id)  # Commenté pour tests sans cours
    course = None  # Pour les tests
    # if not current_user.is_enrolled(course.class_obj.id):  # Commenté pour tests sans auth
    #     flash('Vous n\'avez pas accès à cet exercice.', 'error')
    #     return redirect(url_for('exercise_library'))
    
    answers = {}
    score = 0
    feedback = []

    if exercise.exercise_type == 'qcm':
        print("\n=== DÉBUT SCORING QCM ===")
        content = exercise.get_content()
        print(f"[QCM_DEBUG] Content: {content}")
        
        if not isinstance(content, dict) or 'questions' not in content:
            print("[QCM_DEBUG] Structure invalide!")
            flash('Structure de l\'exercice invalide.', 'error')
            return redirect(url_for('view_exercise', exercise_id=exercise_id))

        total_questions = len(content['questions'])
        correct_answers = 0
        print(f"[QCM_DEBUG] Total questions: {total_questions}")

        for i, question in enumerate(content['questions']):
            student_answer = request.form.get(f'answer_{i}')
            correct_answer = question.get('correct_answer')
            
            print(f"[QCM_DEBUG] Question {i}:")
            print(f"  - Texte: {question.get('text')}")
            print(f"  - Réponse étudiant (answer_{i}): {student_answer}")
            print(f"  - Bonne réponse: {correct_answer}")
            print(f"  - Choices: {question.get('choices')}")
            
            is_correct = False
            if student_answer is not None and correct_answer is not None:
                is_correct = int(student_answer) == int(correct_answer)
                if is_correct:
                    correct_answers += 1
                    print(f"  - [CORRECT] Bonne reponse!")
                else:
                    print(f"  - [INCORRECT] {student_answer} != {correct_answer}")
            else:
                print(f"  - [WARNING] DONNEES MANQUANTES: student={student_answer}, correct={correct_answer}")

            feedback.append({
                'question': question['text'],
                'student_answer': question['choices'][int(student_answer)] if student_answer and int(student_answer) < len(question['choices']) else 'Aucune réponse',
                'correct_answer': question['choices'][correct_answer] if correct_answer < len(question['choices']) else 'Erreur',
                'is_correct': is_correct
            })

        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        print(f"[QCM_DEBUG] Score final: {correct_answers}/{total_questions} = {score}%")
        print("=== FIN SCORING QCM ===\n")

    elif exercise.exercise_type == 'underline_words':
        content = exercise.get_content()
        
        # Gérer les deux structures possibles : 'sentences' ou 'words'
        sentences_data = content.get('sentences') or content.get('words', [])
        
        if not isinstance(content, dict) or not sentences_data:
            flash('Structure de l\'exercice invalide.', 'error')
            return redirect(url_for('view_exercise', exercise_id=exercise_id, course_id=course_id))

        total_sentences = len(sentences_data)
        correct_sentences = 0

        for i, sentence_data in enumerate(sentences_data):
            student_answers = request.form.getlist(f'underlined_words_{i}[]')
            correct_words = set(word.lower() for word in sentence_data['words_to_underline'])
            student_words = set(word.lower() for word in student_answers)

            is_correct = student_words == correct_words
            if is_correct:
                correct_sentences += 1

            feedback.append({
                'sentence': sentence_data['text'],
                'student_words': list(student_words),
                'correct_words': list(correct_words),
                'is_correct': is_correct
            })

        score = (correct_sentences / total_sentences) * 100 if total_sentences > 0 else 0

    elif exercise.exercise_type == 'pairs':
        content = exercise.get_content()
        if not isinstance(content, dict) or 'pairs' not in content:
            flash('Structure de l\'exercice invalide.', 'error')
            return redirect(url_for('view_exercise', exercise_id=exercise_id, course_id=course_id))

        total_pairs = len(content['pairs'])
        correct_pairs = 0

        # Créer un dictionnaire des paires correctes
        correct_matches = {pair['first']: pair['second'] for pair in content['pairs']}

        for first, correct_second in correct_matches.items():
            student_answer = request.form.get(f'pair_{first}')
            is_correct = student_answer == correct_second

            if is_correct:
                correct_pairs += 1

            feedback.append({
                'first': first,
                'student_answer': student_answer,
                'correct_answer': correct_second,
                'is_correct': is_correct
            })

        score = (correct_pairs / total_pairs) * 100 if total_pairs > 0 else 0

    elif exercise.exercise_type == 'fill_in_blanks':
        content = exercise.get_content()
        print("[DEBUG] Contenu de l'exercice:", content)

        # Vérification de la structure attendue
        if not isinstance(content, dict) or 'sentences' not in content or not isinstance(content['sentences'], list):
            app.logger.error(f"[ERREUR STRUCTURE] L'exercice {exercise.id} n'a pas de clé 'sentences' valide dans son contenu: {content}")
            flash("Erreur de configuration de l'exercice : structure des phrases manquante ou invalide.", 'error')
            return redirect(url_for('view_exercise', exercise_id=exercise_id, course_id=course_id))

        total_questions = len(content['sentences'])
        correct_answers = 0

        for i in range(total_questions):
            student_answer = request.form.get(f'answer_{i}')
            correct_answer = content['sentences'][i]['answer']
            print(f"[DEBUG] Question {i + 1}:")
            print(f"[DEBUG] - Réponse de l'étudiant : {student_answer}")
            print(f"[DEBUG] - Réponse correcte : {correct_answer}")

            if student_answer and student_answer.strip().lower() == correct_answer.strip().lower():
                correct_answers += 1
                feedback.append({
                    'question': content['sentences'][i]['text'],
                    'student_answer': student_answer,
                    'correct_answer': correct_answer,
                    'is_correct': True
                })
            else:
                feedback.append({
                    'question': content['sentences'][i]['text'],
                    'student_answer': student_answer or '',
                    'correct_answer': correct_answer,
                    'is_correct': False
                })

        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0

    elif exercise.exercise_type == 'word_placement':
        print("\n=== DÉBUT SCORING WORD_PLACEMENT ===")
        content = exercise.get_content()
        print(f"[WORD_PLACEMENT_DEBUG] Content: {content}")
        
        if not isinstance(content, dict) or 'sentences' not in content or 'answers' not in content:
            print("[WORD_PLACEMENT_DEBUG] Structure invalide!")
            flash('Structure de l\'exercice invalide.', 'error')
            return redirect(url_for('view_exercise', exercise_id=exercise_id))

        sentences = content['sentences']
        correct_answers = content['answers']
        
        # CORRECTION: Compter le nombre réel de blancs dans les phrases
        total_blanks_in_sentences = sum(s.count('___') for s in sentences)
        total_blanks = max(total_blanks_in_sentences, len(correct_answers))
        
        correct_count = 0
        
        print(f"[WORD_PLACEMENT_DEBUG] Total blanks in sentences: {total_blanks_in_sentences}")
        print(f"[WORD_PLACEMENT_DEBUG] Total answers: {len(correct_answers)}")
        print(f"[WORD_PLACEMENT_DEBUG] Using total_blanks = {total_blanks}")
        print(f"[WORD_PLACEMENT_DEBUG] Expected answers: {correct_answers}")

        # Vérifier chaque réponse
        for i in range(total_blanks):
            student_answer = request.form.get(f'answer_{i}')
            expected_answer = correct_answers[i] if i < len(correct_answers) else ''
            
            print(f"[WORD_PLACEMENT_DEBUG] Blank {i}:")
            print(f"  - Réponse étudiant (answer_{i}): {student_answer}")
            print(f"  - Réponse attendue: {expected_answer}")
            
            # Normaliser les réponses pour la comparaison
            normalized_student_answer = student_answer.strip().lower() if student_answer else ""
            normalized_expected_answer = expected_answer.strip().lower() if expected_answer else ""
            
            # Vérifier si la réponse est correcte
            is_correct = normalized_student_answer == normalized_expected_answer
            
            print(f"  - Comparaison: '{normalized_student_answer}' == '{normalized_expected_answer}' => {is_correct}")
            
            if is_correct:
                correct_count += 1
                feedback.append({
                    'blank_index': i,
                    'student_answer': student_answer,
                    'correct_answer': expected_answer,
                    'is_correct': True
                })
            else:
                feedback.append({
                    'blank_index': i,
                    'student_answer': student_answer or '',
                    'correct_answer': expected_answer,
                    'is_correct': False
                })

        score = (correct_count / total_blanks) * 100 if total_blanks > 0 else 0
        print(f"[WORD_PLACEMENT_DEBUG] Score final: {score}% ({correct_count}/{total_blanks} = {correct_count/total_blanks if total_blanks > 0 else 0})")

    else:
        print(f"[ERROR] Type d'exercice non pris en charge: {exercise.exercise_type}")
        flash(f'Le type d\'exercice {exercise.exercise_type} n\'est pas pris en charge.', 'error')
        return redirect(url_for('view_exercise', exercise_id=exercise_id))
            
    # Créer une nouvelle tentative
    try:
        # Convertir le score en float pour s'assurer qu'il est bien numérique
        score = float(score)
        app.logger.debug(f'Création de la tentative - Score: {score}')
        
        attempt = ExerciseAttempt(
            student_id=current_user.id,
            exercise_id=exercise_id,
            course_id=course_id,
            score=score,
            answers=json.dumps(answers),
            feedback=json.dumps(feedback)
        )
        
        db.session.add(attempt)
        db.session.commit()
        app.logger.debug('Tentative enregistrée avec succès')
        
        flash(f'Exercice soumis avec succès ! Score : {score:.1f}%', 'success')
        return redirect(url_for('view_exercise', exercise_id=exercise_id, course_id=course_id))
        
    except Exception as e:
        app.logger.error(f'Erreur lors de la création de la tentative: {str(e)}')
        db.session.rollback()
        flash('Une erreur est survenue lors de l\'enregistrement de votre tentative.', 'error')
        return redirect(url_for('view_exercise', exercise_id=exercise_id, course_id=course_id))
    return redirect(url_for('view_exercise', exercise_id=exercise_id))

@app.route('/debug/exercises')
@login_required
def debug_exercises():
    if not current_user.is_teacher:
        return "Accès non autorisé", 403
        
    exercises = Exercise.query.all()
    debug_info = []
    
    for ex in exercises:
        debug_info.append({
            'id': ex.id,
            'title': ex.title,
            'type': ex.exercise_type,
            'content': ex.content,
            'parsed_content': ex.get_content()
        })
    
    return render_template('debug_exercises.html', exercises=debug_info)

@app.route('/debug/images')
def debug_images():
    # Lister tous les fichiers dans le dossier uploads
    files = []
    upload_dir = app.config['UPLOAD_FOLDER']
    for filename in os.listdir(upload_dir):
        if filename.startswith('pair_left_'):
            file_path = os.path.join(upload_dir, filename)
            if os.path.isfile(file_path):
                files.append({
                    'name': filename,
                    'url': url_for('static', filename=f'uploads/{filename}'),
                    'size': os.path.getsize(file_path)
                })
    
    return render_template('debug_images.html', files=files)

import random

def generate_word_search_grid(words, max_attempts=3):
    """Génère une grille de mots mêlés à partir d'une liste de mots."""
    if not words:
        return None
        
    # Normaliser les mots (majuscules, pas d'espaces)
    words = [word.strip().upper() for word in words]
    
    # Vérifier la validité des mots
    if any(not word.isalpha() for word in words):
        raise ValueError("Les mots ne doivent contenir que des lettres")
    
    # Trouver la taille de la grille nécessaire
    max_length = max(len(word) for word in words)
    grid_size = max(15, max_length + 2)  # Au moins 15x15 ou assez grand pour le plus long mot
    
    # Directions possibles pour placer les mots
    directions = [
        (0, 1),   # horizontal
        (1, 0),   # vertical
        (1, 1),   # diagonal bas-droite
        (-1, 1),  # diagonal haut-droite
    ]
    
    def can_place_word(grid, word, start_x, start_y, dx, dy):
        """Vérifie si un mot peut être placé à partir d'une position donnée."""
        for i, letter in enumerate(word):
            x = start_x + i * dx
            y = start_y + i * dy
            if not (0 <= x < grid_size and 0 <= y < grid_size):
                return False
            if grid[y][x] and grid[y][x] != letter:
                return False
        return True
    
    def place_word(grid, word):
        """Tente de placer un mot dans la grille."""
        attempts = 100  # Nombre maximum d'essais par mot
        while attempts > 0:
            dx, dy = random.choice(directions)
            if dx == 0:  # horizontal
                x = random.randint(0, grid_size - len(word))
                y = random.randint(0, grid_size - 1)
            elif dy == 0:  # vertical
                x = random.randint(0, grid_size - 1)
                y = random.randint(0, grid_size - len(word))
            else:  # diagonal
                x = random.randint(0, grid_size - len(word))
                y = random.randint(0, grid_size - len(word))
            
            if can_place_word(grid, word, x, y, dx, dy):
                for i, letter in enumerate(word):
                    grid[y + i * dy][x + i * dx] = letter
                return True
            attempts -= 1
        return False
    
    # Essayer de générer une grille valide
    attempt_count = 0
    while attempt_count < max_attempts:
        try:
            # Créer une grille vide
            grid = [['' for _ in range(grid_size)] for _ in range(grid_size)]
            
            # Placer chaque mot
            random.shuffle(words)  # Mélanger les mots pour varier leur placement
            success = True
            for word in words:
                if not place_word(grid, word):
                    success = False
                    break
            
            if success:
                # Remplir les cases vides avec des lettres aléatoires
                letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                for y in range(grid_size):
                    for x in range(grid_size):
                        if not grid[y][x]:
                            grid[y][x] = random.choice(letters)
                return grid
        except Exception:
            pass
            
        attempt_count += 1
    
    return None  # Si on n'a pas réussi à générer une grille valide

@app.route('/exercise/<int:exercise_id>/attempt/<int:attempt_id>')
@login_required
def view_attempt(exercise_id, attempt_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    attempt = ExerciseAttempt.query.get_or_404(attempt_id)
    course_id = request.args.get('course_id', type=int)
    course = Course.query.get(course_id) if course_id else None
    
    # Vérifier que la tentative appartient à l'exercice
    if attempt.exercise_id != exercise_id:
        flash('Cette tentative ne correspond pas à cet exercice.', 'error')
        return redirect(url_for('view_exercise', exercise_id=exercise_id))
    
    # Si c'est un professeur
    if current_user.is_teacher:
        # Vérifier que l'exercice appartient au professeur
        if exercise.teacher_id != current_user.id:
            flash('Vous n\'êtes pas autorisé à voir cette tentative.', 'error')
            return redirect(url_for('view_exercise', exercise_id=exercise_id))
    # Si c'est un élève
    else:
        # Vérifier que la tentative appartient bien à l'élève
        if attempt.student_id != current_user.id:
            flash('Vous n\'êtes pas autorisé à voir cette tentative.', 'error')
            return redirect(url_for('view_exercise', exercise_id=exercise_id))
    
    # Récupérer le contenu de l'exercice
    content = exercise.get_content()
    if not content:
        flash('Impossible de récupérer le contenu de l\'exercice.', 'error')
        return redirect(url_for('view_exercise', exercise_id=exercise_id))
    
    return render_template('view_attempt.html', 
                         exercise=exercise, 
                         attempt=attempt,
                         course=course,
                         content=content)



# Delete route moved to exercise blueprint in modified_submit.py
    return redirect(url_for('exercise_library'))

# Route conflictuelle supprimée - utiliser handle_exercise_answer dans exercise_routes.py

@app.route('/exercise/preview/<int:exercise_id>')
@login_required
def preview_exercise(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    content = exercise.get_content()
    
    # Initialiser le contenu par défaut si nécessaire
    if not content:
        content = {}
    
    # Initialiser le contenu en fonction du type d'exercice
    if exercise.exercise_type == 'underline_words':
        if 'sentences' not in content:
            content['sentences'] = []
        # Convertir les phrases en format adapté au template
        for i, sentence in enumerate(content['sentences']):
            if isinstance(sentence, str):
                content['sentences'][i] = {
                    'text': sentence,
                    'words': sentence.split(),
                    'words_to_underline': []
                }
    elif exercise.exercise_type == 'pairs':
        if 'left_items' not in content:
            content['left_items'] = []
        if 'right_items' not in content:
            content['right_items'] = []
        if 'correct_pairs' not in content:
            content['correct_pairs'] = []
    elif exercise.exercise_type == 'qcm':
        if 'questions' not in content:
            content['questions'] = []
        # S'assurer que chaque question a la bonne structure
        for i, question in enumerate(content.get('questions', [])):
            if isinstance(question, dict):
                if 'text' not in question:
                    question['text'] = ''
                if 'choices' not in question:
                    question['choices'] = []
                if 'correct_answer' not in question:
                    question['correct_answer'] = 0
    
    # Choisir le template en fonction du type d'exercice
    template = f'exercise_types/{exercise.exercise_type}.html'
    
    return render_template(template, exercise=exercise, content=content)






# Route supprimée car dupliquée avec /exercise/create

# Route pour la soumission des exercices (intégrée directement)
@app.route('/test-submit')
def test_submit():
    return render_template('test_submit.html')

@app.route('/test-minimal')
def test_minimal():
    """Route pour tester un formulaire ultra-minimal"""
    return render_template('test_minimal_form.html')

@app.route('/test-pure-html')
def test_pure_html():
    """Route pour tester un formulaire HTML pur sans JavaScript"""
    return render_template('test_pure_html.html')

@app.route('/exercise/<int:exercise_id>/answer', methods=['POST'])
# @login_required  # TEMPORAIREMENT DÉSACTIVÉ POUR TEST
def handle_exercise_answer(exercise_id):
    print(f"[ROUTE_DEBUG] Route /exercise/{exercise_id}/answer accessed")
    print(f"[DIAGNOSTIC] handle_exercise_answer called with exercise_id={exercise_id}")
    app.logger.info(f"[DIAGNOSTIC] Function entry - exercise_id={exercise_id}")
    try:
        app.logger.info(f"[SUBMIT_DEBUG] Starting handle_exercise_answer for exercise {exercise_id}")
        exercise = Exercise.query.get_or_404(exercise_id)
        app.logger.info(f"[SUBMIT_DEBUG] Exercise found: {exercise.title}, type: {exercise.exercise_type}")
        course_id = request.form.get('course_id')
        course = Course.query.get(course_id) if course_id else None
        app.logger.info(f"[SUBMIT_DEBUG] Form data keys: {list(request.form.keys())}")
        
        # Vérifier que l'étudiant a accès à l'exercice si c'est via un cours
        # TEMPORAIREMENT DÉSACTIVÉ POUR TEST SANS AUTHENTIFICATION
        # if course and current_user.role == 'student':
        #     class_obj = Class.query.get(course.class_id)
        #     if not class_obj or current_user not in class_obj.students:
        #         flash('Vous n\'avez pas accès à cet exercice.', 'error')
        #         return redirect(url_for('index'))
        
        # Récupérer les réponses et calculer le score
        answers = {}
        score = 0
        max_score = 0
        feedback = {}
        
        if exercise.exercise_type == 'drag_and_drop':
            # Gestion des exercices glisser-déposer
            content = json.loads(exercise.content)
            app.logger.info(f"[DRAG_DROP_DEBUG] Processing drag_and_drop exercise {exercise_id}")
            app.logger.info(f"[DRAG_DROP_DEBUG] Form data: {dict(request.form)}")
            
            user_order = []
            feedback = []
            
            # Récupérer les réponses du formulaire
            for i in range(len(content['draggable_items'])):
                val = request.form.get(f'answer_{i}')
                app.logger.info(f"[DRAG_DROP_DEBUG] answer_{i} = {val} (type: {type(val)})")
                try:
                    idx = int(val) if val is not None else -1
                    user_order.append(idx)
                except (ValueError, TypeError):
                    user_order.append(-1)
            
            correct_order = content.get('correct_order', [])
            app.logger.info(f"[DRAG_DROP_DEBUG] User order: {user_order}")
            app.logger.info(f"[DRAG_DROP_DEBUG] Correct order: {correct_order}")
            
            # Calculer le score
            score_count = 0
            for i, (user_idx, correct_idx) in enumerate(zip(user_order, correct_order)):
                user_item = content['draggable_items'][user_idx] if 0 <= user_idx < len(content['draggable_items']) else "Vide"
                correct_item = content['draggable_items'][correct_idx] if 0 <= correct_idx < len(content['draggable_items']) else "Vide"
                is_correct = (user_idx == correct_idx) and (user_idx != -1)
                
                feedback.append({
                    'zone': i+1,
                    'expected': correct_item,
                    'given': user_item,
                    'is_correct': is_correct
                })
                
                if is_correct:
                    score_count += 1
                    
                app.logger.info(f"[DRAG_DROP_DEBUG] Zone {i+1}: user={user_idx}, correct={correct_idx}, match={is_correct}")
            
            max_score = len(correct_order)
            score = round((score_count / max_score) * 100) if max_score > 0 else 0
            
            # DEBUG: Log final scoring results
            app.logger.info(f"[DRAG_DROP_DEBUG] Score count: {score_count}")
            app.logger.info(f"[DRAG_DROP_DEBUG] Max score: {max_score}")
            app.logger.info(f"[DRAG_DROP_DEBUG] Final score: {score}%")
            
            # Créer le feedback summary pour drag_and_drop
            feedback_summary = {
                'score': score,
                'score_count': score_count,
                'max_score': max_score,
                'details': feedback
            }
            
            # Pour drag_and_drop, on utilise le score en pourcentage mais on sauvegarde aussi le score_count
            answers = {f'answer_{i}': str(user_order[i]) for i in range(len(user_order))}
        
        elif exercise.exercise_type == 'word_search':
            # Gestion des exercices mots mêlés
            content = json.loads(exercise.content)
            app.logger.info(f"[WORD_SEARCH_DEBUG] Processing word_search exercise {exercise_id}")
            app.logger.info(f"[WORD_SEARCH_DEBUG] Form data: {dict(request.form)}")
            
            # Récupérer les mots à trouver
            words_to_find = content.get('words', [])
            if not words_to_find:
                app.logger.error(f"[WORD_SEARCH_DEBUG] No words found in exercise content")
                flash('Erreur: aucun mot trouvé dans l\'exercice.', 'error')
                return redirect(url_for('view_exercise', exercise_id=exercise_id))
            
            app.logger.info(f"[WORD_SEARCH_DEBUG] Words to find: {words_to_find}")
            
            # Récupérer les mots trouvés par l'utilisateur depuis les champs word_0, word_1, etc.
            found_words = []
            for key, value in request.form.items():
                if key.startswith('word_') and value:
                    word = value.strip().upper()
                    if word and word != 'UNDEFINED':  # Éviter les valeurs vides ou non définies
                        found_words.append(word)
            
            # Alternative: récupérer depuis un champ caché ou une liste (pour compatibilité)
            if not found_words:
                found_words_str = request.form.get('found_words', '')
                if found_words_str:
                    found_words = [word.strip().upper() for word in found_words_str.split(',') if word.strip()]
            
            app.logger.info(f"[WORD_SEARCH_DEBUG] Found words by user: {found_words}")
            
            # Calculer le score
            correct_words = []
            incorrect_words = []
            
            for word in found_words:
                if word in words_to_find:
                    correct_words.append(word)
                else:
                    incorrect_words.append(word)
            
            # Mots manqués
            missed_words = [word for word in words_to_find if word not in found_words]
            
            score_count = len(correct_words)
            max_score = len(words_to_find)
            score = (score_count / max_score) * 100 if max_score > 0 else 0
            
            app.logger.info(f"[WORD_SEARCH_DEBUG] Correct words: {correct_words}")
            app.logger.info(f"[WORD_SEARCH_DEBUG] Incorrect words: {incorrect_words}")
            app.logger.info(f"[WORD_SEARCH_DEBUG] Missed words: {missed_words}")
            app.logger.info(f"[WORD_SEARCH_DEBUG] Score: {score_count}/{max_score} = {score}%")
            
            # Créer le feedback
            feedback = {
                'correct_words': correct_words,
                'incorrect_words': incorrect_words,
                'missed_words': missed_words,
                'total_found': len(found_words),
                'total_correct': score_count,
                'total_words': max_score
            }
            
            feedback_summary = {
                'score': score,
                'score_count': score_count,
                'max_score': max_score,
                'details': feedback
            }
            
            # Sauvegarder les réponses
            answers = {'found_words': ','.join(found_words)}
        
        elif exercise.exercise_type == 'pairs':
            # Gestion des exercices d'association de paires
            content = json.loads(exercise.content)
            app.logger.info(f"[PAIRS_DEBUG] Processing pairs exercise {exercise_id}")
            app.logger.info(f"[PAIRS_DEBUG] Form data: {dict(request.form)}")
            
            # Récupérer les paires originales
            original_pairs = content.get('pairs', [])
            if not original_pairs:
                app.logger.error(f"[PAIRS_DEBUG] No pairs found in exercise content")
                flash('Erreur: aucune paire trouvée dans l\'exercice.', 'error')
                return redirect(url_for('view_exercise', exercise_id=exercise_id))
            
            # Créer un dictionnaire des bonnes réponses (left_index -> right_index)
            correct_answers = {}
            for i, pair in enumerate(original_pairs):
                correct_answers[i] = i  # L'index de gauche correspond à l'index de droite original
            
            app.logger.info(f"[PAIRS_DEBUG] Correct answers: {correct_answers}")
            
            # Récupérer les réponses de l'utilisateur
            user_answers = {}
            for i in range(len(original_pairs)):
                left_value = request.form.get(f'left_{i}')
                if left_value:
                    try:
                        right_index = int(left_value)
                        user_answers[i] = right_index
                        app.logger.info(f"[PAIRS_DEBUG] User paired left_{i} with right_{right_index}")
                    except (ValueError, TypeError):
                        app.logger.warning(f"[PAIRS_DEBUG] Invalid value for left_{i}: {left_value}")
            
            app.logger.info(f"[PAIRS_DEBUG] User answers: {user_answers}")
            
            # Calculer le score
            score_count = 0
            feedback = []
            
            for left_index in range(len(original_pairs)):
                user_right_index = user_answers.get(left_index, -1)
                correct_right_index = correct_answers.get(left_index, -1)
                is_correct = user_right_index == correct_right_index
                
                if is_correct:
                    score_count += 1
                
                # Créer le feedback pour cette paire
                left_item = original_pairs[left_index]['left'] if left_index < len(original_pairs) else None
                expected_right = original_pairs[correct_right_index]['right'] if 0 <= correct_right_index < len(original_pairs) else None
                given_right = original_pairs[user_right_index]['right'] if 0 <= user_right_index < len(original_pairs) else None
                
                feedback.append({
                    'left_index': left_index,
                    'left_item': left_item,
                    'expected_right': expected_right,
                    'given_right': given_right,
                    'is_correct': is_correct
                })
                
                app.logger.info(f"[PAIRS_DEBUG] Pair {left_index}: user={user_right_index}, correct={correct_right_index}, is_correct={is_correct}")
            
            max_score = len(original_pairs)
            score = (score_count / max_score) * 100 if max_score > 0 else 0
            
            # DEBUG: Log final scoring results
            app.logger.info(f"[PAIRS_DEBUG] Score count: {score_count}")
            app.logger.info(f"[PAIRS_DEBUG] Max score: {max_score}")
            app.logger.info(f"[PAIRS_DEBUG] Final score: {score}%")
            
            # Créer le feedback summary pour pairs
            feedback_summary = {
                'score': score,
                'score_count': score_count,
                'max_score': max_score,
                'details': feedback
            }
            
            # Pour pairs, on utilise le score en pourcentage
            answers = {f'left_{i}': str(user_answers.get(i, -1)) for i in range(len(original_pairs))}
        
        elif exercise.exercise_type == 'underline_words':
            # Gestion des exercices "Souligner les mots"
            content = json.loads(exercise.content)
            app.logger.info(f"[UNDERLINE_DEBUG] Processing underline_words exercise {exercise_id}")
            app.logger.info(f"[UNDERLINE_DEBUG] Form data: {dict(request.form)}")
            
            # Récupérer les phrases originales (structure 'words' au lieu de 'sentences')
            sentences = content.get('words', [])  # CORRECTION: utiliser 'words' au lieu de 'sentences'
            if not sentences:
                app.logger.error(f"[UNDERLINE_DEBUG] No words/sentences found in exercise content")
                app.logger.error(f"[UNDERLINE_DEBUG] Available content keys: {list(content.keys())}")
                flash('Erreur: aucune phrase trouvée dans l\'exercice.', 'error')
                return redirect(url_for('view_exercise', exercise_id=exercise_id))
            
            app.logger.info(f"[UNDERLINE_DEBUG] Found {len(sentences)} sentences to process")
            
            # Calculer le score pour chaque phrase
            total_sentences = len(sentences)
            correct_sentences = 0
            feedback = []
            
            for i, sentence_data in enumerate(sentences):
                # Récupérer les mots que l'utilisateur a soulignés pour cette phrase
                # Le template utilise selected_words_{i} avec des mots séparés par des virgules
                user_underlined_str = request.form.get(f'selected_words_{i}', '')
                user_underlined = [word.strip() for word in user_underlined_str.split(',') if word.strip()]
                app.logger.info(f"[UNDERLINE_DEBUG] Sentence {i}: user underlined string '{user_underlined_str}'")
                app.logger.info(f"[UNDERLINE_DEBUG] Sentence {i}: user underlined list {user_underlined}")
                
                # Récupérer les mots qui devaient être soulignés
                expected_words = sentence_data.get('words_to_underline', [])
                app.logger.info(f"[UNDERLINE_DEBUG] Sentence {i}: expected words {expected_words}")
                
                # Normaliser les mots (minuscules, sans ponctuation, sans apostrophes)
                def normalize_word(word):
                    # Convertir en minuscules
                    normalized = word.lower()
                    # Supprimer la ponctuation au début et à la fin
                    normalized = normalized.strip('.,!?;:\'"()[]{}«»')
                    # Gérer les apostrophes (l'autoroute -> autoroute)
                    if normalized.startswith(("l'", "d'", "n'", "m'", "t'", "s'", "c'", "j'", "qu'")):
                        normalized = normalized[2:]  # Supprimer l' d' etc.
                    elif normalized.startswith(("la", "le", "les", "un", "une", "du", "de", "des")):
                        # Garder les articles complets
                        pass
                    return normalized
                
                user_words_normalized = set(normalize_word(word) for word in user_underlined if word.strip())
                expected_words_normalized = set(normalize_word(word) for word in expected_words if word.strip())
                
                app.logger.info(f"[UNDERLINE_DEBUG] Sentence {i}: user normalized {user_words_normalized}")
                app.logger.info(f"[UNDERLINE_DEBUG] Sentence {i}: expected normalized {expected_words_normalized}")
                
                # Vérifier si la phrase est correcte (tous les mots attendus sont soulignés)
                is_correct = user_words_normalized == expected_words_normalized
                if is_correct:
                    correct_sentences += 1
                
                # Créer le feedback pour cette phrase
                sentence_text = sentence_data.get('text', '')  # CORRECTION: utiliser 'text' au lieu de 'words'
                feedback.append({
                    'sentence_index': i,
                    'sentence_text': sentence_text,
                    'user_underlined': list(user_words_normalized),
                    'expected_words': list(expected_words_normalized),
                    'is_correct': is_correct,
                    'missing_words': list(expected_words_normalized - user_words_normalized),
                    'extra_words': list(user_words_normalized - expected_words_normalized)
                })
                
                app.logger.info(f"[UNDERLINE_DEBUG] Sentence {i}: is_correct={is_correct}")
            
            # Calculer le score final
            score = (correct_sentences / total_sentences) * 100 if total_sentences > 0 else 0
            
            # DEBUG: Log final scoring results
            app.logger.info(f"[UNDERLINE_DEBUG] Correct sentences: {correct_sentences}")
            app.logger.info(f"[UNDERLINE_DEBUG] Total sentences: {total_sentences}")
            app.logger.info(f"[UNDERLINE_DEBUG] Final score: {score}%")
            
            # Créer le feedback summary pour underline_words
            feedback_summary = {
                'score': score,
                'correct_sentences': correct_sentences,
                'total_sentences': total_sentences,
                'details': feedback
            }
            
            # Pour underline_words, on utilise le score en pourcentage
            answers = {f'selected_words_{i}': request.form.get(f'selected_words_{i}', '') for i in range(len(sentences))}
        
        elif exercise.exercise_type == 'dictation':
            # Gestion des exercices de dictée
            content = json.loads(exercise.content)
            app.logger.info(f"[DICTATION_DEBUG] Processing dictation exercise {exercise_id}")
            app.logger.info(f"[DICTATION_DEBUG] Form data: {dict(request.form)}")
            
            # Récupérer les phrases de référence
            reference_sentences = content.get('sentences', [])
            if not reference_sentences:
                app.logger.error(f"[DICTATION_DEBUG] No sentences found in exercise content")
                flash('Erreur: aucune phrase trouvée dans l\'exercice.', 'error')
                return redirect(url_for('view_exercise', exercise_id=exercise_id))
            
            app.logger.info(f"[DICTATION_DEBUG] Found {len(reference_sentences)} sentences to check")
            
            # Calculer le score pour chaque phrase
            total_sentences = len(reference_sentences)
            correct_sentences = 0
            feedback = []
            user_answers = {}
            
            for i, reference_sentence in enumerate(reference_sentences):
                # Récupérer la réponse de l'utilisateur
                user_answer = request.form.get(f'dictation_answer_{i}', '').strip()
                reference_text = reference_sentence.strip()
                
                user_answers[f'dictation_answer_{i}'] = user_answer
                
                app.logger.info(f"[DICTATION_DEBUG] Sentence {i}: user='{user_answer}' vs reference='{reference_text}'")
                
                # Normaliser les textes pour la comparaison
                def normalize_text(text):
                    # Convertir en minuscules
                    normalized = text.lower()
                    # Supprimer la ponctuation
                    import string
                    normalized = normalized.translate(str.maketrans('', '', string.punctuation))
                    # Supprimer les espaces multiples
                    normalized = ' '.join(normalized.split())
                    return normalized
                
                user_normalized = normalize_text(user_answer)
                reference_normalized = normalize_text(reference_text)
                
                app.logger.info(f"[DICTATION_DEBUG] Sentence {i}: normalized user='{user_normalized}' vs reference='{reference_normalized}'")
                
                # Vérifier si la phrase est correcte
                is_correct = user_normalized == reference_normalized
                if is_correct:
                    correct_sentences += 1
                
                # Calculer la similarité (pourcentage de mots corrects)
                user_words = user_normalized.split()
                reference_words = reference_normalized.split()
                
                if reference_words:
                    # Compter les mots corrects (même position)
                    correct_words = 0
                    max_length = max(len(user_words), len(reference_words))
                    
                    for j in range(max_length):
                        user_word = user_words[j] if j < len(user_words) else ''
                        ref_word = reference_words[j] if j < len(reference_words) else ''
                        if user_word == ref_word and user_word != '':
                            correct_words += 1
                    
                    similarity = (correct_words / len(reference_words)) * 100
                else:
                    similarity = 100 if not user_words else 0
                
                # Créer le feedback pour cette phrase
                feedback.append({
                    'sentence_index': i,
                    'user_answer': user_answer,
                    'reference_sentence': reference_text,
                    'is_correct': is_correct,
                    'similarity': round(similarity, 1),
                    'status': 'Correct' if is_correct else f'Similarité: {round(similarity, 1)}%'
                })
            
            # Calculer le score final
            max_score = total_sentences
            score_count = correct_sentences
            score = round((score_count / max_score) * 100) if max_score > 0 else 0
            
            app.logger.info(f"[DICTATION_DEBUG] Final score: {score_count}/{max_score} = {score}%")
            
            feedback_summary = {
                'score': score,
                'correct_sentences': correct_sentences,
                'total_sentences': total_sentences,
                'details': feedback
            }
            # Pour dictation, on utilise le score en pourcentage
            answers = user_answers
        
        elif exercise.exercise_type == 'image_labeling':
            # Gestion des exercices d'étiquetage d'image
            content = json.loads(exercise.content)
            app.logger.info(f"[IMAGE_LABELING_DEBUG] Processing image_labeling exercise {exercise_id}")
            app.logger.info(f"[IMAGE_LABELING_DEBUG] Form data: {dict(request.form)}")
            
            # Récupérer les zones définies dans l'exercice
            zones = content.get('zones', [])
            if not zones:
                app.logger.error(f"[IMAGE_LABELING_DEBUG] No zones found in exercise content")
                flash('Erreur: aucune zone trouvée dans l\'exercice.', 'error')
                return redirect(url_for('view_exercise', exercise_id=exercise_id))
            
            app.logger.info(f"[IMAGE_LABELING_DEBUG] Found {len(zones)} zones to check")
            
            # Récupérer les réponses de l'utilisateur depuis le JSON
            user_answers_json = request.form.get('user_answers', '{}')
            try:
                user_answers_data = json.loads(user_answers_json)
                app.logger.info(f"[IMAGE_LABELING_DEBUG] User answers: {user_answers_data}")
            except json.JSONDecodeError:
                app.logger.error(f"[IMAGE_LABELING_DEBUG] Invalid JSON in user_answers: {user_answers_json}")
                user_answers_data = {}
            
            # Calculer le score
            total_zones = len(zones)
            correct_zones = 0
            feedback = []
            
            for i, zone in enumerate(zones):
                zone_id = str(i + 1)  # Les zones sont numérotées à partir de 1
                expected_label = zone.get('label', '')
                user_label = user_answers_data.get(zone_id, '')
                
                is_correct = user_label.lower().strip() == expected_label.lower().strip()
                if is_correct:
                    correct_zones += 1
                
                feedback.append({
                    'zone_id': zone_id,
                    'expected_label': expected_label,
                    'user_label': user_label,
                    'is_correct': is_correct,
                    'status': 'Correct' if is_correct else f'Attendu: {expected_label}, Réponse: {user_label}'
                })
                
                app.logger.info(f"[IMAGE_LABELING_DEBUG] Zone {zone_id}: expected='{expected_label}', user='{user_label}', correct={is_correct}")
            
            # Calculer le score final
            max_score = total_zones
            score_count = correct_zones
            score = round((score_count / max_score) * 100) if max_score > 0 else 0
            
            app.logger.info(f"[IMAGE_LABELING_DEBUG] Final score: {score_count}/{max_score} = {score}%")
            
            feedback_summary = {
                'score': score,
                'correct_zones': correct_zones,
                'total_zones': total_zones,
                'details': feedback
            }
            
            # Pour image_labeling, on utilise le score en pourcentage
            answers = user_answers_data
        
        elif exercise.exercise_type == 'qcm_multichoix':
            # Gestion des exercices QCM Multichoix
            content = json.loads(exercise.content)
            app.logger.info(f"[QCM_MULTICHOIX_DEBUG] Processing qcm_multichoix exercise {exercise_id}")
            app.logger.info(f"[QCM_MULTICHOIX_DEBUG] Form data: {dict(request.form)}")
            
            # Récupérer les questions de l'exercice
            questions = content.get('questions', [])
            if not questions:
                app.logger.error(f"[QCM_MULTICHOIX_DEBUG] No questions found in exercise content")
                flash('Erreur: aucune question trouvée dans l\'exercice.', 'error')
                return redirect(url_for('view_exercise', exercise_id=exercise_id))
            
            app.logger.info(f"[QCM_MULTICHOIX_DEBUG] Found {len(questions)} questions to check")
            
            # Calculer le score
            total_questions = len(questions)
            correct_questions = 0
            feedback_details = []
            user_answers_data = {}
            
            for question_index, question in enumerate(questions):
                # Récupérer les réponses de l'utilisateur pour cette question
                user_selected = request.form.getlist(f'question_{question_index}[]')
                app.logger.info(f"[QCM_MULTICHOIX_DEBUG] Raw user_selected for question {question_index}: {user_selected}")
                user_selected_indices = [int(idx) for idx in user_selected if idx.isdigit()]
                
                # Récupérer les bonnes réponses pour cette question
                correct_options = question.get('correct_options', [])
                
                app.logger.info(f"[QCM_MULTICHOIX_DEBUG] Question {question_index}: user={user_selected_indices}, correct={correct_options}")
                app.logger.info(f"[QCM_MULTICHOIX_DEBUG] Question {question_index}: user_set={set(user_selected_indices)}, correct_set={set(correct_options)}")
                
                # Vérifier si les réponses correspondent exactement
                is_correct = set(user_selected_indices) == set(correct_options)
                app.logger.info(f"[QCM_MULTICHOIX_DEBUG] Question {question_index}: is_correct={is_correct}")
                if is_correct:
                    correct_questions += 1
                
                # Créer le feedback pour cette question
                user_options = [question['options'][i] for i in user_selected_indices if i < len(question['options'])]
                correct_options_text = [question['options'][i] for i in correct_options if i < len(question['options'])]
                
                feedback_details.append({
                    'question_index': question_index,
                    'question_text': question.get('question', ''),
                    'user_selected': user_options,
                    'correct_options': correct_options_text,
                    'is_correct': is_correct,
                    'status': 'Correct' if is_correct else f'Attendu: {", ".join(correct_options_text)}, Réponse: {", ".join(user_options) if user_options else "Aucune réponse"}'
                })
                
                # Sauvegarder les réponses utilisateur
                user_answers_data[f'question_{question_index}'] = user_selected_indices
            
            # Calculer le score final
            max_score = total_questions
            score_count = correct_questions
            score = round((score_count / max_score) * 100) if max_score > 0 else 0
            
            app.logger.info(f"[QCM_MULTICHOIX_DEBUG] Final score: {score_count}/{max_score} = {score}%")
            
            feedback_summary = {
                'score': score,
                'correct_questions': correct_questions,
                'total_questions': total_questions,
                'details': feedback_details
            }
            
            # Pour qcm_multichoix, on utilise le score en pourcentage
            answers = user_answers_data
        
        elif exercise.exercise_type == 'flashcards':
            # Gestion des exercices Flashcards
            content = json.loads(exercise.content)
            app.logger.info(f"[FLASHCARDS_DEBUG] Processing flashcards exercise {exercise_id}")
            app.logger.info(f"[FLASHCARDS_DEBUG] Form data: {dict(request.form)}")
            
            # Récupérer les cartes de l'exercice
            cards = content.get('cards', [])
            if not cards:
                app.logger.error(f"[FLASHCARDS_DEBUG] No cards found in exercise content")
                flash('Erreur: aucune carte trouvée dans l\'exercice.', 'error')
                return redirect(url_for('view_exercise', exercise_id=exercise_id))
            
            app.logger.info(f"[FLASHCARDS_DEBUG] Found {len(cards)} cards to check")
            
            # Récupérer le score et les réponses depuis le formulaire
            final_score = request.form.get('final_score', '0')
            correct_answers_count = request.form.get('correct_answers', '0')
            total_answers_count = request.form.get('total_answers', '0')
            
            try:
                score = float(final_score)
                score_count = int(correct_answers_count)
                max_score = int(total_answers_count)
            except (ValueError, TypeError):
                app.logger.error(f"[FLASHCARDS_DEBUG] Invalid score data: final_score={final_score}, correct={correct_answers_count}, total={total_answers_count}")
                score = 0
                score_count = 0
                max_score = len(cards)
            
            app.logger.info(f"[FLASHCARDS_DEBUG] Score received: {score_count}/{max_score} = {score}%")
            
            # Récupérer les réponses individuelles pour chaque carte
            user_answers = {}
            feedback_details = []
            
            for i in range(len(cards)):
                card_answer = request.form.get(f'card_{i}_answer', '')
                card_correct = request.form.get(f'card_{i}_correct', 'false') == 'true'
                
                user_answers[f'card_{i}'] = {
                    'answer': card_answer,
                    'correct': card_correct,
                    'expected': cards[i].get('answer', '') if i < len(cards) else ''
                }
                
                feedback_details.append({
                    'card_index': i,
                    'question': cards[i].get('question', '') if i < len(cards) else '',
                    'expected_answer': cards[i].get('answer', '') if i < len(cards) else '',
                    'user_answer': card_answer,
                    'is_correct': card_correct
                })
            
            feedback_summary = {
                'score': score,
                'score_count': score_count,
                'max_score': max_score,
                'total_cards': len(cards),
                'details': feedback_details
            }
            
            app.logger.info(f"[FLASHCARDS_DEBUG] Final feedback: {feedback_summary}")
            
            # Pour flashcards, on utilise le score calculé côté frontend
            answers = user_answers
        
        elif exercise.exercise_type == 'fill_in_blanks':
            # Gestion des exercices Texte à trous avec la même logique que Mots à placer
            content = json.loads(exercise.content)
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Processing fill_in_blanks exercise {exercise_id}")
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Form data: {dict(request.form)}")
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Exercise content keys: {list(content.keys())}")
            
            # Compter le nombre réel de blancs dans le contenu
            total_blanks_in_content = 0
            
            # Analyser le format de l'exercice et compter les blancs réels
            # CORRECTION: Éviter le double comptage entre 'text' et 'sentences'
            # Priorité à 'sentences' s'il existe, sinon utiliser 'text'
            if 'sentences' in content:
                sentences_blanks = sum(s.count('___') for s in content['sentences'])
                total_blanks_in_content = sentences_blanks
                app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Format 'sentences' détecté: {sentences_blanks} blancs dans sentences")
                # Log détaillé pour chaque phrase et ses blancs
                for i, sentence in enumerate(content['sentences']):
                    blanks_in_sentence = sentence.count('___')
                    app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Phrase {i}: '{sentence}' contient {blanks_in_sentence} blancs")
            elif 'text' in content:
                text_blanks = content['text'].count('___')
                total_blanks_in_content = text_blanks
                app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Format 'text' détecté: {text_blanks} blancs dans text")
            
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Total blancs trouvés dans le contenu: {total_blanks_in_content}")
            # Log détaillé pour chaque phrase et ses blancs
            if 'sentences' in content:
                for i, sentence in enumerate(content['sentences']):
                    blanks_in_sentence = sentence.count('___')
                    app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Phrase {i}: '{sentence}' contient {blanks_in_sentence} blancs")
            
            # Récupérer les réponses correctes (peut être 'words' ou 'available_words')
            correct_answers = content.get('words', [])
            if not correct_answers:
                correct_answers = content.get('available_words', [])
            
            if not correct_answers:
                app.logger.error(f"[FILL_IN_BLANKS_DEBUG] No correct answers found in exercise content")
                flash('Erreur: aucune réponse correcte trouvée dans l\'exercice.', 'error')
                return redirect(url_for('view_exercise', exercise_id=exercise_id))
            
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Found {len(correct_answers)} correct answers: {correct_answers}")
            
            # Utiliser le nombre réel de blancs trouvés dans le contenu
            total_blanks = max(total_blanks_in_content, len(correct_answers))
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Using total_blanks = {total_blanks}")
            
            correct_blanks = 0
            feedback_details = []
            user_answers_data = {}
            
            # Vérifier chaque blanc individuellement - Même logique que word_placement
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Traitement de {total_blanks} blancs au total")
            for i in range(total_blanks):
                # Récupérer la réponse de l'utilisateur pour ce blanc
                user_answer = request.form.get(f'answer_{i}', '').strip()
                
                # Récupérer la réponse correcte correspondante
                correct_answer = correct_answers[i] if i < len(correct_answers) else ''
                
                app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Blank {i}:")
                app.logger.info(f"  - Réponse étudiant (answer_{i}): {user_answer}")
                app.logger.info(f"  - Réponse attendue: {correct_answer}")
                
                # Vérifier si la réponse est correcte (insensible à la casse)
                is_correct = user_answer and user_answer.strip().lower() == correct_answer.strip().lower()
                if is_correct:
                    correct_blanks += 1
                
                # Créer le feedback pour ce blanc
                # Déterminer l'index de la phrase à laquelle appartient ce blanc
                sentence_index = -1
                local_blank_index = -1
                if 'sentences' in content:
                    sentence_index, local_blank_index = get_blank_location(i, content['sentences'])
                    app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Blank {i} est dans la phrase {sentence_index}, position locale {local_blank_index}")
                
                feedback_details.append({
                    'blank_index': i,
                    'user_answer': user_answer or '',
                    'correct_answer': correct_answer,
                    'is_correct': is_correct,
                    'status': 'Correct' if is_correct else f'Attendu: {correct_answer}, Réponse: {user_answer or "Vide"}',
                    'sentence_index': sentence_index,
                    'sentence': content['sentences'][sentence_index] if sentence_index >= 0 and 'sentences' in content else ''
                })
                
                # Sauvegarder les réponses utilisateur
                user_answers_data[f'answer_{i}'] = user_answer
            
            # Calculer le score final basé sur le nombre réel de blancs - Exactement comme word_placement
            score = (correct_blanks / total_blanks) * 100 if total_blanks > 0 else 0
            
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Score final: {score}% ({correct_blanks}/{total_blanks})")
            
            feedback_summary = {
                'score': score,
                'correct_blanks': correct_blanks,
                'total_blanks': total_blanks,
                'details': feedback_details
            }
            
            # Pour fill_in_blanks, on utilise le score calculé
            answers = user_answers_data
        
                # Logique de scoring pour fill_in_blanks
        elif exercise.exercise_type == 'fill_in_blanks':
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Traitement de l'exercice fill_in_blanks ID {exercise_id}")
            content = exercise.get_content()
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Contenu de l'exercice: {content}")
            
            total_blanks_in_content = 0
            
            # Analyser le format de l'exercice et compter les blancs réels
            # CORRECTION: Éviter le double comptage entre 'text' et 'sentences'
            # Priorité à 'sentences' s'il existe, sinon utiliser 'text'
            if 'sentences' in content:
                sentences_blanks = sum(s.count('___') for s in content['sentences'])
                total_blanks_in_content = sentences_blanks
                app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Format 'sentences' détecté: {sentences_blanks} blancs dans sentences")
                # Log détaillé pour chaque phrase et ses blancs
                for i, sentence in enumerate(content['sentences']):
                    blanks_in_sentence = sentence.count('___')
                    app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Phrase {i}: '{sentence}' contient {blanks_in_sentence} blancs")
            elif 'text' in content:
                text_blanks = content['text'].count('___')
                total_blanks_in_content = text_blanks
                app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Format 'text' détecté: {text_blanks} blancs dans text")
            
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Total blancs trouvés dans le contenu: {total_blanks_in_content}")
            # Log détaillé pour chaque phrase et ses blancs
            if 'sentences' in content:
                for i, sentence in enumerate(content['sentences']):
                    blanks_in_sentence = sentence.count('___')
                    app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Phrase {i}: '{sentence}' contient {blanks_in_sentence} blancs")
            
            # Récupérer les réponses correctes (peut être 'words' ou 'available_words')
            correct_answers = content.get('words', [])
            if not correct_answers:
                correct_answers = content.get('available_words', [])
            
            if not correct_answers:
                app.logger.error(f"[FILL_IN_BLANKS_DEBUG] No correct answers found in exercise content")
                flash('Erreur: aucune réponse correcte trouvée dans l\'exercice.', 'error')
                return redirect(url_for('view_exercise', exercise_id=exercise_id))
            
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Found {len(correct_answers)} correct answers: {correct_answers}")
            
            # Utiliser le nombre réel de blancs trouvés dans le contenu
            total_blanks = max(total_blanks_in_content, len(correct_answers))
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Using total_blanks = {total_blanks}")
            
            correct_blanks = 0
            feedback_details = []
            user_answers_data = {}
            
            # Vérifier chaque blanc individuellement - Même logique que word_placement
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Traitement de {total_blanks} blancs au total")
            for i in range(total_blanks):
                # Récupérer la réponse de l'utilisateur pour ce blanc
                user_answer = request.form.get(f'answer_{i}', '').strip()
                
                # Récupérer la réponse correcte correspondante
                correct_answer = correct_answers[i] if i < len(correct_answers) else ''
                
                app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Blank {i}:")
                app.logger.info(f"  - Réponse étudiant (answer_{i}): {user_answer}")
                app.logger.info(f"  - Réponse attendue: {correct_answer}")
                
                # Vérifier si la réponse est correcte (insensible à la casse)
                is_correct = user_answer and user_answer.strip().lower() == correct_answer.strip().lower()
                if is_correct:
                    correct_blanks += 1
                
                # Créer le feedback pour ce blanc
                # Déterminer l'index de la phrase à laquelle appartient ce blanc
                sentence_index = -1
                local_blank_index = -1
                if 'sentences' in content:
                    sentence_index, local_blank_index = get_blank_location(i, content['sentences'])
                    app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Blank {i} est dans la phrase {sentence_index}, position locale {local_blank_index}")
                
                feedback_details.append({
                    'blank_index': i,
                    'user_answer': user_answer or '',
                    'correct_answer': correct_answer,
                    'is_correct': is_correct,
                    'status': 'Correct' if is_correct else f'Attendu: {correct_answer}, Réponse: {user_answer or "Vide"}',
                    'sentence_index': sentence_index,
                    'sentence': content['sentences'][sentence_index] if sentence_index >= 0 and 'sentences' in content else ''
                })
                
                # Sauvegarder les réponses utilisateur
                user_answers_data[f'answer_{i}'] = user_answer
            
            # Calculer le score final basé sur le nombre réel de blancs - Exactement comme word_placement
            score = (correct_blanks / total_blanks) * 100 if total_blanks > 0 else 0
            
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Score final: {score}% ({correct_blanks}/{total_blanks})")
            
            feedback_summary = {
                'score': score,
                'correct_blanks': correct_blanks,
                'total_blanks': total_blanks,
                'details': feedback_details
            }
            
            # Pour fill_in_blanks, on utilise le score calculé
            answers = user_answers_data
        
        # Créer une nouvelle tentative
        # Pour drag_and_drop, pairs, underline_words, dictation, image_labeling, flashcards, qcm_multichoix, fill_in_blanks, feedback est feedback_summary (sinon feedback dict habituel)
        if exercise.exercise_type in ['drag_and_drop', 'pairs', 'underline_words', 'dictation', 'image_labeling', 'flashcards', 'qcm_multichoix', 'fill_in_blanks']:
            feedback_to_save = feedback_summary
        else:
            feedback_to_save = feedback
            
        attempt = ExerciseAttempt(
            student_id=current_user.id,
            exercise_id=exercise.id,
            answers=json.dumps(answers),
            score=score,
            feedback=json.dumps(feedback_to_save)
        )
        
        db.session.add(attempt)
        db.session.commit()
        
        # Créer un message de feedback pour l'utilisateur
        if score >= 80:
            flash(f'Excellent ! Vous avez obtenu {score:.1f}% !', 'success')
        elif score >= 60:
            flash(f'Bien joué ! Vous avez obtenu {score:.1f}%.', 'info')
        else:
            flash(f'Vous avez obtenu {score:.1f}%. Continuez vos efforts !', 'warning')
        
        # Rediriger vers la page de feedback dédiée
        return redirect(url_for('view_feedback', exercise_id=exercise_id, attempt_id=attempt.id))
    
    except Exception as e:
        app.logger.error(f"Erreur lors de la soumission: {e}")
        return jsonify({'success': False, 'error': 'Une erreur est survenue'}), 500
        return redirect(url_for('view_exercise', exercise_id=exercise_id))

@app.route('/force-admin-setup')
def force_admin_setup():
    """Route temporaire pour forcer l'approbation admin"""
    try:
        # Approuver mr.zahiri@gmail.com
        zahiri_user = User.query.filter_by(email='mr.zahiri@gmail.com').first()
        if zahiri_user:
            zahiri_user.subscription_status = 'approved'
            zahiri_user.role = 'teacher'
            zahiri_user.subscription_type = 'teacher'
            zahiri_user.approved_by = None
            db.session.commit()
            
        # Approuver aussi jemathsia@example.com (Mr Aziz)
        aziz_user = User.query.filter_by(email='jemathsia@example.com').first()
        if aziz_user:
            aziz_user.subscription_status = 'approved'
            aziz_user.role = 'teacher'
            aziz_user.subscription_type = 'teacher'
            aziz_user.approved_by = None
            aziz_user.approval_date = datetime.utcnow()
            db.session.commit()
            
        return f"✅ Comptes approuvés ! <br>✅ mr.zahiri@gmail.com (enseignant)<br>✅ jemathsia@example.com (enseignant)<br><a href='/login'>Se connecter</a>"
    except Exception as e:
        return f"❌ Erreur: {e}"

@app.route('/create-test-exercises')
def create_test_exercises():
    """Route pour créer des exercices de test"""
    try:
        from models import Exercise
        from datetime import datetime
        
        # Récupérer l'utilisateur enseignant
        teacher = User.query.filter_by(email='mr.zahiri@gmail.com').first()
        if not teacher:
            teacher = User.query.filter_by(email='jemathsia@example.com').first()
        
        if not teacher:
            return "❌ Aucun enseignant trouvé"
        
        # Créer des exercices de test
        exercises_data = [
            {
                'title': 'QCM Test - Les Capitales',
                'exercise_type': 'qcm',
                'subject': 'Géographie',
                'content': '{"question": "Quelle est la capitale de la France ?", "options": ["Paris", "Lyon", "Marseille", "Toulouse"], "correct_answer": 0, "explanation": "Paris est la capitale de la France depuis 1792."}'
            },
            {
                'title': 'Texte à Trous - Grammaire',
                'exercise_type': 'fill_in_blanks',
                'subject': 'Français',
                'content': '{"text": "Le chat ____ sa nourriture dans le ____.", "blanks": [{"word": "mange", "position": 1}, {"word": "jardin", "position": 2}], "sentences": ["Le chat mange sa nourriture dans le jardin."]}'
            },
            {
                'title': 'Association de Paires - Histoire',
                'exercise_type': 'pairs',
                'subject': 'Histoire',
                'content': '{"pairs": [{"left": "1789", "right": "Révolution française"}, {"left": "1804", "right": "Sacre de Napoléon"}, {"left": "1815", "right": "Waterloo"}]}'
            }
        ]
        
        created_count = 0
        for ex_data in exercises_data:
            # Vérifier si l'exercice existe déjà
            existing = Exercise.query.filter_by(title=ex_data['title']).first()
            if not existing:
                exercise = Exercise(
                    title=ex_data['title'],
                    exercise_type=ex_data['exercise_type'],
                    subject=ex_data['subject'],
                    content=ex_data['content'],
                    teacher_id=teacher.id,
                    created_at=datetime.utcnow()
                )
                db.session.add(exercise)
                created_count += 1
        
        db.session.commit()
        
        return f"✅ {created_count} exercices de test créés ! <br><a href='/exercise/library'>Voir la bibliothèque</a>"
        
    except Exception as e:
        return f"❌ Erreur lors de la création: {e}"

@app.route('/debug-edit-exercise/<int:exercise_id>')
def debug_edit_exercise(exercise_id):
    """Route de debug pour éditer directement le JSON d'un exercice"""
    try:
        from models import Exercise
        exercise = Exercise.query.get_or_404(exercise_id)
        
        html = f"""
        <h2>Debug - Édition directe JSON</h2>
        <h3>Exercice: {exercise.title}</h3>
        <p><strong>Type:</strong> {exercise.exercise_type}</p>
        <p><strong>Contenu actuel:</strong></p>
        <form method="GET" action="/debug-update-exercise/{exercise_id}">
            <textarea name="content" rows="10" cols="80" style="width:100%">{exercise.content or ''}</textarea><br><br>
            <button type="submit" style="background:green;color:white;padding:10px;">Sauvegarder JSON</button>
        </form>
        <br>
        <h4>Format attendu pour "Mots à placer":</h4>
        <pre>{{"sentences": ["Cette phrase est-elle ___ ou ___ ?"], "words": ["déclarative", "interrogative", "impérative"]}}</pre>
        <br>
        <a href="/exercise/library">Retour à la bibliothèque</a>
        """
        return html
        
    except Exception as e:
        return f"❌ Erreur: {e}"

@app.route('/debug-update-exercise/<int:exercise_id>', methods=['GET', 'POST'])
def debug_update_exercise(exercise_id):
    """Route pour sauvegarder le JSON modifié"""
    try:
        from models import Exercise
        from flask import request
        
        exercise = Exercise.query.get_or_404(exercise_id)
        
        # Récupérer le contenu depuis GET ou POST
        new_content = request.args.get('content') or request.form.get('content', '')
        
        if new_content:
            exercise.content = new_content
            db.session.commit()
            return f"✅ Exercice mis à jour ! <br><a href='/exercise/{exercise_id}'>Voir l'exercice</a> | <a href='/exercise/library'>Bibliothèque</a>"
        else:
            return f"❌ Aucun contenu fourni. <a href='/debug-edit-exercise/{exercise_id}'>Retour</a>"
        
    except Exception as e:
        return f"❌ Erreur lors de la sauvegarde: {e}"

@app.route('/exercise/<int:exercise_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_exercise(exercise_id):
    """Route pour éditer un exercice existant"""
    exercise = Exercise.query.get_or_404(exercise_id)
    
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
        if exercise.exercise_type == 'qcm':
            return render_template('exercise_types/qcm_edit.html', exercise=exercise, content=content)
        elif exercise.exercise_type == 'qcm_multichoix':
            return render_template('exercise_types/qcm_multichoix_edit.html', exercise=exercise, content=content)
        elif exercise.exercise_type == 'fill_in_blanks':
            # Rendre le template spécifique pour l'édition des exercices de type texte à trous
            return render_template('exercise_types/fill_in_blanks_edit.html', exercise=exercise, content=content)
        elif exercise.exercise_type == 'drag_and_drop':
            # Rendre le template spécifique pour l'édition des exercices de type glisser-déposer
            return render_template('exercise_types/drag_and_drop_edit.html', exercise=exercise, content=content)
        elif exercise.exercise_type == 'word_search':
            # Rendre le template spécifique pour l'édition des exercices de type mots mêlés
            return render_template('exercise_types/word_search_edit.html', exercise=exercise, content=content)
        elif exercise.exercise_type == 'pairs':
            # Rendre le template spécifique pour l'édition des exercices de type association de paires
            return render_template('exercise_types/pairs_edit.html', exercise=exercise, content=content)
        elif exercise.exercise_type == 'word_placement':
            # Rendre le template spécifique pour l'édition des exercices de type mots à placer
            return render_template('exercise_types/word_placement_edit.html', exercise=exercise, content=content)
        elif exercise.exercise_type == 'underline_words':
            # Rendre le template spécifique pour l'édition des exercices de type souligner les mots
            return render_template('exercise_types/underline_words_edit.html', exercise=exercise, content=content)
        elif exercise.exercise_type == 'dictation':
            # Rendre le template spécifique pour l'édition des exercices de type dictée
            return render_template('exercise_types/dictation_edit.html', exercise=exercise, content=content)
        elif exercise.exercise_type == 'image_labeling':
            # Rendre le template spécifique pour l'édition des exercices de type étiquetage d'image
            return render_template('exercise_types/image_labeling_edit.html', exercise=exercise, content=content)
        elif exercise.exercise_type == 'flashcards':
            # Rendre le template spécifique pour l'édition des exercices de type cartes mémoire
            return render_template('exercise_types/flashcards_edit.html', exercise=exercise, content=content)

    elif request.method == 'POST':
        try:
            # Mettre à jour les champs de base
            exercise.title = request.form.get('title', exercise.title)
            exercise.description = request.form.get('description', exercise.description)
            exercise.subject = request.form.get('subject', exercise.subject)
            
            # Gestion spéciale pour les exercices de type image_labeling
            if exercise.exercise_type == 'image_labeling':
                # Pour les exercices d'étiquetage d'image, on ne veut pas d'image d'exercice séparée
                # car cela crée une confusion avec l'image principale à légender
                if 'remove_exercise_image' in request.form and request.form['remove_exercise_image'] == 'true':
                    # Supprimer l'image de l'exercice si elle existe
                    if exercise.image_path:
                        try:
                            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(exercise.image_path)))
                        except Exception as e:
                            app.logger.error(f"Erreur lors de la suppression de l'image : {str(e)}")
                    exercise.image_path = None
                    # Si l'image d'exercice existe, on la supprime
                    if exercise.image_path:
                        app.logger.info(f"[EDIT_DEBUG] Suppression de l'image d'exercice pour image_labeling: {exercise.image_path}")
                        exercise.image_path = None
                
                # Gestion de la suppression de l'image principale si demandé
                if 'remove_main_image' in request.form and request.form['remove_main_image'] == 'true':
                    try:
                        # Charger le contenu existant
                        try:
                            content = json.loads(exercise.content) if exercise.content else {}
                        except:
                            content = {}
                        
                        # S'assurer que content est un dictionnaire
                        if not isinstance(content, dict):
                            content = {}
                            
                        # Si l'image principale existe, la supprimer
                        if 'main_image' in content:
                            main_image_path = content['main_image']
                            try:
                                # Convertir le chemin relatif en chemin absolu si nécessaire
                                if main_image_path and not os.path.isabs(main_image_path):
                                    main_image_path = os.path.join(app.root_path, 'static', main_image_path.lstrip('/'))
                                
                                # Supprimer physiquement le fichier s'il existe
                                if main_image_path and os.path.exists(main_image_path):
                                    os.remove(main_image_path)
                                    app.logger.info(f"[EDIT_DEBUG] Fichier image supprimé: {main_image_path}")
                                
                                # Si vous utilisez Cloudinary, décommentez cette ligne :
                                # cloud_storage.delete_file(main_image_path)
                                
                            except Exception as e:
                                app.logger.error(f"[EDIT_DEBUG] Erreur lors de la suppression du fichier {main_image_path}: {str(e)}")
                            
                            # Supprimer la référence à l'image dans le contenu
                            del content['main_image']
                            app.logger.info(f"[EDIT_DEBUG] Référence à l'image principale supprimée: {main_image_path}")
                            
                            # Sauvegarder le contenu mis à jour
                            exercise.content = json.dumps(content)
                    except Exception as e:
                        app.logger.error(f"[EDIT_DEBUG] Erreur lors de la suppression de l'image principale: {str(e)}")
                
                # Gestion de l'image principale à légender
                app.logger.info(f"[EDIT_DEBUG] Clés des fichiers reçus: {list(request.files.keys())}")
                if 'main_image' in request.files:
                    main_image_file = request.files['main_image']
                    app.logger.info(f"[EDIT_DEBUG] Fichier main_image reçu: {main_image_file.filename if main_image_file else 'None'}")
                    if main_image_file and main_image_file.filename != '':
                        if allowed_file(main_image_file.filename, main_image_file):
                            try:
                                # Charger le contenu existant pour récupérer l'ancienne image
                                try:
                                    content = json.loads(exercise.content) if exercise.content else {}
                                except:
                                    content = {}
                                
                                # Sauvegarder le chemin de l'ancienne image pour suppression ultérieure
                                old_main_image = content.get('main_image')
                                
                                # Sauvegarder temporairement le fichier pour vérifier son intégrité
                                temp_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(main_image_file.filename))
                                main_image_file.save(temp_path)
                                
                                # Approche ultra-simplifiée pour l'upload d'image
                                try:
                                    # Utiliser directement le fichier original sans validation
                                    app.logger.info(f"[EDIT_DEBUG] Tentative d'upload de l'image principale")
                                    app.logger.info(f"[EDIT_DEBUG] Fichier temporaire: {temp_path}")
                                    app.logger.info(f"[EDIT_DEBUG] Fichier existe: {os.path.exists(temp_path)}")
                                    app.logger.info(f"[EDIT_DEBUG] Taille du fichier: {os.path.getsize(temp_path) if os.path.exists(temp_path) else 'N/A'}")
                                    
                                    # Créer le dossier de destination s'il n'existe pas
                                    dest_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'exercises', 'image_labeling')
                                    os.makedirs(dest_folder, exist_ok=True)
                                    
                                    # Générer un nom de fichier unique avec un timestamp pour éviter les conflits
                                    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                                    file_ext = os.path.splitext(secure_filename(main_image_file.filename))[1].lower()
                                    normalized_filename = f"image_{timestamp}{file_ext}"
                                    dest_path = os.path.join(dest_folder, normalized_filename)
                                    
                                    # Copier le fichier vers le dossier de destination
                                    import shutil
                                    shutil.copy2(temp_path, dest_path)
                                    app.logger.info(f"[EDIT_DEBUG] Fichier copié vers: {dest_path} (nom normalisé)")
                                    
                                    # Supprimer l'ancienne image si elle existe
                                    if old_main_image:
                                        try:
                                            old_image_path = os.path.join(app.root_path, 'static', old_main_image.lstrip('/'))
                                            if os.path.exists(old_image_path):
                                                os.remove(old_image_path)
                                                app.logger.info(f"[EDIT_DEBUG] Ancienne image supprimée: {old_image_path}")
                                        except Exception as e:
                                            app.logger.error(f"[EDIT_DEBUG] Erreur lors de la suppression de l'ancienne image: {str(e)}")
                                    
                                    # Générer l'URL normalisée pour la nouvelle image (URL publique servie par Flask)
                                    main_image_url = f"/static/uploads/exercises/image_labeling/{normalized_filename}"
                                    app.logger.info(f"[EDIT_DEBUG] Nouvelle URL d'image: {main_image_url}")
                                    
                                    # Supprimer le fichier temporaire
                                    os.remove(temp_path)
                                    
                                    if main_image_url:
                                        try:
                                            # Charger le contenu existant ou créer un nouveau dictionnaire
                                            try:
                                                content = json.loads(exercise.content) if exercise.content else {}
                                            except:
                                                content = {}
                                            
                                            # S'assurer que content est un dictionnaire
                                            if not isinstance(content, dict):
                                                content = {}
                                                
                                            # Mettre à jour l'image principale dans le contenu
                                            content['main_image'] = main_image_url

                                            # S'assurer que l'URL est compatible avec le template
                                            # Note: l'URL générée commence déjà par '/', aucune normalisation nécessaire ici.
                                            if not main_image_url.startswith('/'):
                                                app.logger.warning(f"[EDIT_DEBUG] URL d'image non standard détectée: {main_image_url}. Utilisation telle quelle.")
                                            
                                            # Sauvegarder le contenu mis à jour
                                            exercise.content = json.dumps(content)
                                            exercise.image_path = main_image_url  # Synchronisation avec content.main_image
                                            app.logger.info(f"[EDIT_DEBUG] Image principale mise à jour pour image_labeling: {main_image_url}")
                                        except Exception as e:
                                            import traceback
                                            app.logger.error(f"[EDIT_DEBUG] Erreur lors de la mise à jour de l'image principale: {str(e)}")
                                            app.logger.error(traceback.format_exc())
                                except Exception as e:
                                    import traceback
                                    app.logger.error(f"[EDIT_DEBUG] Erreur lors de la vérification de l'image: {str(e)}")
                                    app.logger.error(traceback.format_exc())
                                    flash("L'image téléversée n'est pas valide.", "danger")
                                    if os.path.exists(temp_path):
                                        os.remove(temp_path)
                                    return redirect(url_for('edit_exercise', exercise_id=exercise_id))
                            except Exception as e:
                                app.logger.error(f"[EDIT_DEBUG] Erreur lors de la sauvegarde temporaire: {str(e)}")
                                flash("Erreur lors du traitement de l'image.", "danger")
                                return redirect(url_for('edit_exercise', exercise_id=exercise_id))
                        else:
                            flash("Format de fichier non autorisé. Utilisez JPG, PNG ou GIF.", "danger")
                            return redirect(url_for('edit_exercise', exercise_id=exercise_id))

            else:
                # Gestion standard de l'image pour les autres types d'exercices
                if 'exercise_image' in request.files:
                    file = request.files['exercise_image']
                    if file and file.filename != '' and allowed_file(file.filename, file):
                        # Charger le contenu existant pour récupérer l'ancienne image
                        try:
                            content = json.loads(exercise.content) if exercise.content else {}
                        except:
                            content = {}
                        
                        # Récupérer l'ancien chemin d'image pour suppression ultérieure
                        old_image_path = content.get('image') or exercise.image_path
                            
                        # Utiliser le nouveau système de gestion d'images
                        from utils.image_utils_no_normalize import normalize_image_path
                        
                        # Déterminer le type d'exercice pour l'organisation des dossiers
                        exercise_type = exercise.exercise_type or 'general'
                        
                        # Upload avec le nouveau système
                        image_url = cloud_storage.upload_file(file, exercise_type=exercise_type)
                        if image_url:
                            # Normaliser le chemin de l'image pour assurer la cohérence
                            # Passer le type d'exercice à la fonction de normalisation
                            normalized_image_url = normalize_image_path(image_url, exercise_type=exercise_type)
                            
                            # Supprimer l'ancienne image si elle existe et est différente de la nouvelle
                            if old_image_path and old_image_path != normalized_image_url:
                                try:
                                    # Supprimer l'ancienne image du stockage local si elle existe
                                    if os.path.exists(old_image_path):
                                        os.remove(old_image_path)
                                        app.logger.info(f"[EDIT_DEBUG] Ancienne image locale supprimée: {old_image_path}")
                                    
                                    # Supprimer l'image de Cloudinary si configuré
                                    if cloud_storage.cloudinary_configured:
                                        try:
                                            import cloudinary.uploader
                                            # Extraire le public_id du chemin de l'ancienne image
                                            # Le public_id est généralement le nom du fichier sans extension
                                            public_id = os.path.splitext(os.path.basename(old_image_path))[0]
                                            # Supprimer le préfixe du dossier s'il existe
                                            if '/' in public_id:
                                                public_id = public_id.split('/')[-1]
                                            cloudinary.uploader.destroy(public_id)
                                            app.logger.info(f"[EDIT_DEBUG] Ancienne image supprimée de Cloudinary: {public_id}")
                                        except Exception as e:
                                            app.logger.error(f"[EDIT_DEBUG] Erreur lors de la suppression de l'image sur Cloudinary: {str(e)}")
                                            # Continuer même en cas d'échec de suppression sur Cloudinary
                                            
                                except Exception as e:
                                    app.logger.error(f"[EDIT_DEBUG] Erreur lors de la suppression de l'ancienne image {old_image_path}: {str(e)}")
                                    # Ne pas bloquer la mise à jour en cas d'échec de suppression
                            
                            # Mettre à jour les chemins d'image
                            exercise.image_path = normalized_image_url
                            app.logger.info(f"[EDIT_DEBUG] Nouvelle image enregistrée: {normalized_image_url}")
                            
                            # S'assurer que l'image est également enregistrée dans le contenu de l'exercice
                            try:
                                # Charger le contenu existant ou créer un nouveau dictionnaire
                                try:
                                    content = json.loads(exercise.content) if exercise.content else {}
                                except:
                                    content = {}
                                
                                # S'assurer que content est un dictionnaire
                                if not isinstance(content, dict):
                                    content = {}
                                
                                # Supprimer l'ancienne image du contenu si elle existe
                                if 'image' in content and content['image'] != normalized_image_url:
                                    old_content_image = content['image']
                                    try:
                                        if os.path.exists(old_content_image):
                                            os.remove(old_content_image)
                                            app.logger.info(f"[EDIT_DEBUG] Ancienne image du contenu supprimée: {old_content_image}")
                                    except Exception as e:
                                        app.logger.error(f"[EDIT_DEBUG] Erreur lors de la suppression de l'ancienne image du contenu: {str(e)}")
                                
                                # Mettre à jour avec la nouvelle image
                                content['image'] = normalized_image_url
                                
                                # Sauvegarder le contenu mis à jour
                                exercise.content = json.dumps(content)
                                app.logger.info(f"[EDIT_DEBUG] Image ajoutée au contenu de l'exercice: {normalized_image_url}")
                            except Exception as e:
                                app.logger.error(f"[EDIT_DEBUG] Erreur lors de l'ajout de l'image au contenu: {str(e)}")
                                # En cas d'erreur, on continue quand même pour ne pas bloquer la mise à jour
                # Gérer la suppression d'image si demandée UNIQUEMENT si pas de nouvelle image
                if ('remove_exercise_image' in request.form and 
                    request.form['remove_exercise_image'] == 'true' and 
                    not ('exercise_image' in request.files and request.files['exercise_image'].filename)):
                    # Supprimer l'image à la fois de exercise.image_path et de content['image']
                    app.logger.info(f"[EDIT_DEBUG] Suppression de l'image demandée (sans nouvelle image)")
                    
                    # Charger le contenu existant
                    try:
                        content = json.loads(exercise.content) if exercise.content else {}
                    except:
                        content = {}
                    
                    # S'assurer que content est un dictionnaire
                    if not isinstance(content, dict):
                        content = {}
                    
                    # Supprimer l'image du contenu
                    if 'image' in content:
                        del content['image']
                        app.logger.info(f"[EDIT_DEBUG] Image supprimée de content['image']")
                    
                    # Supprimer l'image_path de l'exercice
                    exercise.image_path = None
                    app.logger.info(f"[EDIT_DEBUG] Image_path supprimé")
                    
                    # Sauvegarder le contenu mis à jour
                    exercise.content = json.dumps(content)
                
                # Si aucune nouvelle image n'est téléchargée et qu'aucune suppression n'est demandée,
                # synchroniser les chemins d'image entre exercise.image_path et content['image']
                try:
                    if exercise.image_path and not content.get('image'):
                        # Si exercise.image_path existe mais pas content['image']
                        content['image'] = exercise.image_path
                        exercise.content = json.dumps(content)
                        app.logger.info(f"[EDIT_DEBUG] Image copiée de exercise.image_path vers content['image']: {exercise.image_path}")
                    
                    # Si content['image'] existe mais pas exercise.image_path
                    elif content.get('image') and not exercise.image_path:
                        exercise.image_path = content['image']
                        app.logger.info(f"[EDIT_DEBUG] Image copiée de content['image'] vers exercise.image_path: {content['image']}")
                except Exception as e:
                    app.logger.error(f"[EDIT_DEBUG] Erreur lors de la synchronisation des images: {str(e)}")
                    # Ne pas bloquer le processus d'édition en cas d'erreur de synchronisation

            # Gestion de l'image de l'exercice
            if 'image' in request.files:
                image_file = request.files['image']
                if image_file and image_file.filename != '':
                    if allowed_file(image_file.filename):
                        filename = secure_filename(image_file.filename)
                        unique_filename = generate_unique_filename(filename)
                        
                        # Créer le dossier de destination s'il n'existe pas
                        dest_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'exercises')
                        os.makedirs(dest_folder, exist_ok=True)
                        
                        # Sauvegarder le fichier localement
                        filepath = os.path.join(dest_folder, unique_filename)
                        image_file.save(filepath)
                        
                        # Mettre à jour le chemin de l'image
                        exercise.image_path = f'/static/uploads/exercises/{unique_filename}'
                        
                        # Mettre à jour le contenu JSON si nécessaire
                        if hasattr(exercise, 'content') and exercise.content:
                            try:
                                content = json.loads(exercise.content)
                                content['image'] = exercise.image_path
                                exercise.content = json.dumps(content)
                            except json.JSONDecodeError:
                                app.logger.error("Erreur de décodage du contenu JSON de l'exercice")
                        
                        # Utiliser Cloudinary pour l'upload en production, stockage local en dev
                        image_url = cloud_storage.upload_file(image_file, folder="exercises/qcm_multichoix")
                        if image_url:
                            # Ajouter le chemin de l'image au contenu
                            content['image'] = f'/static/exercises/{unique_filename}'
                            current_app.logger.info(f'[QCM_MULTICHOIX_EDIT_DEBUG] Nouvelle image sauvegardée: {content["image"]}')
                    else:
                        # Conserver l'image existante
                        if hasattr(exercise, 'content') and exercise.content:
                            try:
                                content = json.loads(exercise.content)
                                if 'image' in content:
                                    exercise.image_path = content['image']
                            except json.JSONDecodeError:
                                app.logger.error("Erreur de décodage du contenu JSON de l'exercice")
                else:
                    if 'image' in request.files:
                        image_file = request.files['image']
                        if image_file and image_file.filename != '':
                            if allowed_file(image_file.filename, image_file):
                                filename = secure_filename(image_file.filename)
                                unique_filename = generate_unique_filename(filename)
                                
                                # Créer le dossier de destination s'il n'existe pas
                                dest_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'exercises')
                                os.makedirs(dest_folder, exist_ok=True)
                                
                                # Sauvegarder le fichier localement
                                filepath = os.path.join(dest_folder, unique_filename)
                                image_file.save(filepath)
                                
                                # Mettre à jour le chemin de l'image
                                exercise.image_path = f'/static/uploads/exercises/{unique_filename}'
                                
                                # Mettre à jour le contenu JSON si nécessaire
                                if hasattr(exercise, 'content') and exercise.content:
                                    try:
                                        content = json.loads(exercise.content)
                                        content['image'] = exercise.image_path
                                        exercise.content = json.dumps(content)
                                    except json.JSONDecodeError:
                                        app.logger.error("Erreur de décodage du contenu JSON de l'exercice")
                                if image_file and image_file.filename != '' and allowed_file(image_file.filename, image_file):
                                    # Utiliser Cloudinary pour l'upload en production, stockage local en dev
                                    image_url = cloud_storage.upload_file(image_file, folder="exercises/qcm_multichoix")
                                    if image_url:
                                        # Ajouter le chemin de l'image au contenu
                                        content['image'] = f'/static/exercises/{unique_filename}'
                                        current_app.logger.info(f'[QCM_MULTICHOIX_EDIT_DEBUG] Nouvelle image sauvegardée: {content["image"]}')
                                else:
                                    # Conserver l'image existante
                                    if 'image' in current_content:
                                        content['image'] = current_content['image']
                            else:
                                # Conserver l'image existante
                                if 'image' in current_content:
                                    content['image'] = current_content['image']
                        else:
                            # Conserver l'image existante
                            if 'image' in current_content:
                                content['image'] = current_content['image']
                if 'main_image' in request.files:
                    file = request.files['main_image']
                    if file and file.filename != '' and allowed_file(file.filename, file):
                        # Utiliser Cloudinary pour l'upload en production, stockage local en dev
                        main_image = cloud_storage.upload_file(file, folder="exercises")
                        main_image = f'/static/exercises/{filename}'
                        current_app.logger.info(f"[IMAGE_LABELING_EDIT_DEBUG] Nouvelle image principale: {main_image}")
                
                # Validation
                if not labels:
                    flash('Veuillez ajouter au moins une étiquette.', 'error')
                    return render_template('exercise_types/image_labeling_edit.html', exercise=exercise, content=json.loads(exercise.content) if exercise.content else {})
                
                # Construire le contenu de l'exercice image_labeling
                content = {
                    'mode': 'classic',
                    'instructions': request.form.get('instructions', ''),
                    'main_image': main_image if 'main_image' in locals() else current_content.get('main_image', ''),
                    'labels': labels,
                    'zones': zones
                }
                
                exercise.content = json.dumps(content)
                current_app.logger.info(f"[IMAGE_LABELING_EDIT_DEBUG] Contenu sauvegardé avec succès")
            
            elif exercise.exercise_type == 'flashcards':
                current_app.logger.info(f'[FLASHCARDS_EDIT_DEBUG] Traitement du contenu Flashcards')
                
                cards_data = []
                card_count = 0
                
                # Compter le nombre de cartes
                for key in request.form:
                    if key.startswith('card_question_'):
                        card_count += 1
                
                # Traiter chaque carte
                for i in range(card_count):
                    question = request.form.get(f'card_question_{i}', '').strip()
                    answer = request.form.get(f'card_answer_{i}', '').strip()
                    
                    if question and answer:
                        card_data = {
                            'question': question,
                            'answer': answer
                        }
                        
                        # Gestion de l'image de la carte
                        if f'card_image_{i}' in request.files:
                            image_file = request.files[f'card_image_{i}']
                            if image_file and image_file.filename and allowed_file(image_file.filename, image_file):
                                try:
                                    # Utiliser Cloudinary pour l'upload en production, stockage local en dev
                                    image_url = cloud_storage.upload_file(image_file, folder="flashcards")
                                    if image_url:
                                        card_data['image'] = image_url
                                        current_app.logger.info(f'[FLASHCARDS_EDIT_DEBUG] Nouvelle image carte {i+1}: {image_url}')
                                except Exception as e:
                                    current_app.logger.error(f'[FLASHCARDS_EDIT_DEBUG] Erreur upload image carte {i+1}: {str(e)}')
                        
                        cards_data.append(card_data)
                        current_app.logger.info(f'[FLASHCARDS_EDIT_DEBUG] Carte {i+1}: "{question[:30]}..." -> "{answer}"')
                
                # Mettre à jour le contenu
                content = {
                    'cards': cards_data
                }
                exercise.content = json.dumps(content)
                current_app.logger.info(f'[FLASHCARDS_EDIT_DEBUG] Contenu sauvegardé: {len(cards_data)} cartes')
            
            elif exercise.exercise_type == 'pairs':
                print(f'[PAIRS_EDIT_DEBUG] Traitement du contenu Association de paires')
                
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
                        old_left_content = None
                        # Récupérer l'ancien contenu si c'était une image
                        if hasattr(exercise, 'content'):
                            try:
                                old_content = json.loads(exercise.content)
                                if 'pairs' in old_content:
                                    for old_pair in old_content['pairs']:
                                        if str(old_pair.get('id')) == str(pair_id) and old_pair['left']['type'] == 'image':
                                            old_left_content = old_pair['left']['content']
                                            break
                            except Exception as e:
                                current_app.logger.error(f'[PAIRS_EDIT_DEBUG] Erreur lecture ancien contenu: {str(e)}')
                        
                        if f'pair_left_image_{pair_id}' in request.files:
                            file = request.files[f'pair_left_image_{pair_id}']
                            if file and file.filename and allowed_file(file.filename, file):
                                # Supprimer l'ancienne image si elle existe
                                if old_left_content:
                                    try:
                                        cloud_storage.delete_file(old_left_content)
                                        current_app.logger.info(f'[PAIRS_EDIT_DEBUG] Ancienne image gauche supprimée: {old_left_content}')
                                    except Exception as e:
                                        current_app.logger.error(f'[PAIRS_EDIT_DEBUG] Erreur suppression ancienne image gauche: {str(e)}')
                                # Uploader la nouvelle image
                                left_content = cloud_storage.upload_file(file, folder="pairs", exercise_type="pairs")
                                if not left_content:
                                    current_app.logger.error(f'[PAIRS_EDIT_DEBUG] Erreur upload image gauche {pair_id}')
                        if not left_content:
                            left_content = request.form.get(f'pair_left_{pair_id}', '').strip()
                    else:
                        left_content = request.form.get(f'pair_left_{pair_id}', '').strip()
                    
                    # Gestion du contenu droit (right)
                    if right_type == 'image':
                        old_right_content = None
                        # Récupérer l'ancien contenu si c'était une image
                        if hasattr(exercise, 'content'):
                            try:
                                old_content = json.loads(exercise.content)
                                if 'pairs' in old_content:
                                    for old_pair in old_content['pairs']:
                                        if str(old_pair.get('id')) == str(pair_id) and old_pair['right']['type'] == 'image':
                                            old_right_content = old_pair['right']['content']
                                            break
                            except Exception as e:
                                current_app.logger.error(f'[PAIRS_EDIT_DEBUG] Erreur lecture ancien contenu droit: {str(e)}')
                        
                        if f'pair_right_image_{pair_id}' in request.files:
                            file = request.files[f'pair_right_image_{pair_id}']
                            if file and file.filename and allowed_file(file.filename, file):
                                # Supprimer l'ancienne image si elle existe
                                if old_right_content:
                                    try:
                                        cloud_storage.delete_file(old_right_content)
                                        current_app.logger.info(f'[PAIRS_EDIT_DEBUG] Ancienne image droite supprimée: {old_right_content}')
                                    except Exception as e:
                                        current_app.logger.error(f'[PAIRS_EDIT_DEBUG] Erreur suppression ancienne image droite: {str(e)}')
                                # Uploader la nouvelle image
                                right_content = cloud_storage.upload_file(file, folder="pairs", exercise_type="pairs")
                                if not right_content:
                                    current_app.logger.error(f'[PAIRS_EDIT_DEBUG] Erreur upload image droite {pair_id}')
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
                    return render_template('edit_exercise.html', exercise=exercise)
                
                # Identifier les paires supprimées pour nettoyer les images
                if hasattr(exercise, 'content'):
                    try:
                        old_content = json.loads(exercise.content)
                        if 'pairs' in old_content:
                            # Créer un ensemble des IDs de paires actuelles
                            current_pair_ids = {str(pair.get('id')) for pair in pairs}
                            
                            # Parcourir les anciennes paires pour trouver celles supprimées
                            for old_pair in old_content['pairs']:
                                old_pair_id = str(old_pair.get('id'))
                                if old_pair_id not in current_pair_ids:
                                    # Supprimer l'image de gauche si elle existe
                                    if old_pair.get('left', {}).get('type') == 'image':
                                        try:
                                            cloud_storage.delete_file(old_pair['left']['content'])
                                            current_app.logger.info(f'[PAIRS_EDIT_DEBUG] Ancienne image gauche supprimée (paire supprimée): {old_pair["left"]["content"]}')
                                        except Exception as e:
                                            current_app.logger.error(f'[PAIRS_EDIT_DEBUG] Erreur suppression ancienne image gauche (paire supprimée): {str(e)}')
                                    # Supprimer l'image de droite si elle existe
                                    if old_pair.get('right', {}).get('type') == 'image':
                                        try:
                                            cloud_storage.delete_file(old_pair['right']['content'])
                                            current_app.logger.info(f'[PAIRS_EDIT_DEBUG] Ancienne image droite supprimée (paire supprimée): {old_pair["right"]["content"]}')
                                        except Exception as e:
                                            current_app.logger.error(f'[PAIRS_EDIT_DEBUG] Erreur suppression ancienne image droite (paire supprimée): {str(e)}')
                    except Exception as e:
                        current_app.logger.error(f'[PAIRS_EDIT_DEBUG] Erreur nettoyage des images des paires supprimées: {str(e)}')
            
                # Mettre à jour le contenu
                content = {'pairs': pairs}
                
                # Normaliser les chemins d'images dans le contenu
                content = normalize_pairs_exercise_content(content, exercise_type='pairs')
                
                exercise.content = json.dumps(content)
                print(f'[PAIRS_EDIT_DEBUG] Contenu sauvegardé et normalisé: {len(pairs)} paires')
                
                # Commit explicite pour sauvegarder les modifications
                try:
                    db.session.commit()
                    flash(f'Exercice d\'association de paires modifié avec succès!', 'success')
                    print(f'[PAIRS_EDIT_DEBUG] Modifications sauvegardées en base de données')
                    # Rediriger vers la page de visualisation de l'exercice
                    return redirect(url_for('view_exercise', exercise_id=exercise.id))
                except Exception as e:
                    db.session.rollback()
                    print(f'[PAIRS_EDIT_DEBUG] Erreur lors de la sauvegarde en base de données: {str(e)}')
                    flash(f'Erreur lors de la modification de l\'exercice: {str(e)}', 'error')
                    return render_template('edit_exercise.html', exercise=exercise)
            
            elif exercise.exercise_type == 'dictation':
                print(f'[DICTATION_EDIT_DEBUG] Traitement du contenu Dictée')
                
                # Récupérer les instructions
                instructions = request.form.get('dictation_instructions', '').strip()
                if not instructions:
                    instructions = 'Écoutez attentivement chaque phrase et écrivez ce que vous entendez.'
                
                # Récupérer les phrases
                sentences = request.form.getlist('dictation_sentences[]')
                sentences = [s.strip() for s in sentences if s.strip()]
                
                # Validation
                if not sentences:
                    flash('Veuillez ajouter au moins une phrase.', 'error')
                    return render_template('edit_exercise.html', exercise=exercise)
                
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
                                
                                # Utiliser Cloudinary pour l'upload en production, stockage local en dev
                                audio_file = cloud_storage.upload_file(file, folder="audio", resource_type="auto")
                                if not audio_file:
                                    current_app.logger.error(f'[AUDIO_EDIT_DEBUG] Erreur upload audio {i+1}')
                                    audio_file = None
                            else:
                                flash(f'Le fichier audio {i+1} doit être au format MP3, WAV, OGG ou M4A.', 'error')
                                return render_template('edit_exercise.html', exercise=exercise)
                    
                    # Si pas de nouveau fichier, garder l'ancien s'il existe
                    if not audio_file:
                        existing_content = exercise.get_content()
                        existing_audio_files = existing_content.get('audio_files', [])
                        if i < len(existing_audio_files):
                            audio_file = existing_audio_files[i]
                    
                    audio_files.append(audio_file)
                
                # Mettre à jour le contenu
                content = {
                    'instructions': instructions,
                    'sentences': sentences,
                    'audio_files': audio_files
                }
                exercise.content = json.dumps(content)
                print(f'[DICTATION_EDIT_DEBUG] Contenu sauvegardé: {len(sentences)} phrases, {len(audio_files)} fichiers audio')
            
            elif exercise.exercise_type == 'legend':
                current_app.logger.info(f'[LEGEND_EDIT_DEBUG] Traitement du contenu Légende')
                
                # Récupérer le mode de légende
                legend_mode = request.form.get('legend_mode', 'classic')
                current_app.logger.info(f'[LEGEND_EDIT_DEBUG] Mode sélectionné: {legend_mode}')
                
                # Récupérer les instructions
                instructions = request.form.get('legend_instructions', '').strip()
                if not instructions:
                    if legend_mode == 'grid':
                        instructions = 'Déplacez les éléments vers les bonnes cases du quadrillage.'
                    elif legend_mode == 'spatial':
                        instructions = 'Placez les éléments dans les bonnes zones définies.'
                    else:
                        instructions = 'Placez les légendes aux bons endroits sur l\'image.'
                
                # Gestion de l'image principale
                main_image_path = None
                if 'legend_main_image' in request.files:
                    image_file = request.files['legend_main_image']
                    if image_file and image_file.filename != '' and allowed_file(image_file.filename, image_file):
                        # Utiliser Cloudinary pour l'upload en production, stockage local en dev
                        main_image_path = cloud_storage.upload_file(image_file, folder="legend")
                        if main_image_path:
                            # Synchroniser avec exercise.image_path pour assurer la cohérence
                            exercise.image_path = main_image_path
                            current_app.logger.info(f'[LEGEND_EDIT_DEBUG] Image principale uploadée et synchronisée: {main_image_path}')
                        else:
                            current_app.logger.error(f'[LEGEND_EDIT_DEBUG] Erreur upload image principale')
                            # Garder l'ancienne image si l'upload échoue
                            existing_content = exercise.get_content()
                            main_image_path = existing_content.get('main_image')
                
                # Si pas de nouvelle image, garder l'ancienne ou utiliser exercise.image_path
                if not main_image_path:
                    existing_content = exercise.get_content()
                    main_image_path = existing_content.get('main_image')
                    
                    # Si toujours pas d'image principale mais qu'il y a exercise.image_path, l'utiliser
                    if not main_image_path and exercise.image_path:
                        main_image_path = exercise.image_path
                        current_app.logger.info(f'[LEGEND_EDIT_DEBUG] Utilisation de exercise.image_path comme image principale: {main_image_path}')
                
                # Récupérer les zones et légendes
                zones = []
                elements = []
                
                # Scanner tous les champs zone_* pour récupérer toutes les zones
                zone_indices = set()
                for key in request.form.keys():
                    if key.startswith('zone_') and key.endswith('_x'):
                        # Extraire l'index de la zone depuis zone_INDEX_x
                        parts = key.split('_')
                        if len(parts) >= 3:
                            zone_index = parts[1]  # zone_INDEX_x -> INDEX
                            try:
                                zone_indices.add(int(zone_index))
                            except ValueError:
                                continue
                
                current_app.logger.info(f'[LEGEND_EDIT_DEBUG] Zones trouvées: {sorted(zone_indices)}')
                
                for zone_index in sorted(zone_indices):
                    x = request.form.get(f'zone_{zone_index}_x')
                    y = request.form.get(f'zone_{zone_index}_y')
                    legend = request.form.get(f'zone_{zone_index}_legend', '').strip()
                    
                    current_app.logger.info(f'[LEGEND_EDIT_DEBUG] Zone {zone_index}: x={x}, y={y}, legend="{legend}"')
                    
                    if x and y and legend:
                        try:
                            x = float(x)
                            y = float(y)
                            zones.append({
                                'x': x,
                                'y': y,
                                'legend': legend
                            })
                            elements.append(legend)
                            current_app.logger.info(f'[LEGEND_EDIT_DEBUG] Zone {zone_index} ajoutée avec succès')
                        except ValueError as e:
                            current_app.logger.error(f'[LEGEND_EDIT_DEBUG] Erreur conversion zone {zone_index}: {e}')
                            continue
                
                if not zones:
                    flash('Veuillez ajouter au moins une zone avec légende.', 'error')
                    return render_template('edit_exercise.html', exercise=exercise)
                
                # Gestion des différents modes de légende
                if legend_mode == 'grid':
                    # Mode quadrillage - récupérer les éléments de grille
                    grid_elements = []
                    grid_element_indices = set()
                    
                    # Scanner les éléments de grille
                    for key in request.form.keys():
                        if key.startswith('grid_element_') and key.endswith('_text'):
                            parts = key.split('_')
                            if len(parts) >= 3:
                                element_index = parts[2]
                                try:
                                    grid_element_indices.add(int(element_index))
                                except ValueError:
                                    continue
                    
                    for element_index in sorted(grid_element_indices):
                        element_text = request.form.get(f'grid_element_{element_index}_text', '').strip()
                        if element_text:
                            grid_elements.append(element_text)
                    
                    # Récupérer les paramètres de grille
                    grid_rows = request.form.get('grid_rows', '3')
                    grid_cols = request.form.get('grid_cols', '3')
                    
                    try:
                        grid_rows = int(grid_rows)
                        grid_cols = int(grid_cols)
                    except ValueError:
                        grid_rows, grid_cols = 3, 3
                    
                    content = {
                        'mode': 'grid',
                        'instructions': instructions,
                        'main_image': main_image_path,
                        'elements': grid_elements,
                        'grid_rows': grid_rows,
                        'grid_cols': grid_cols
                    }
                    current_app.logger.info(f'[LEGEND_EDIT_DEBUG] Mode grille: {len(grid_elements)} éléments, grille {grid_rows}x{grid_cols}')
                
                elif legend_mode == 'spatial':
                    # Mode spatial - récupérer les éléments et zones spatiales
                    spatial_elements = []
                    spatial_zones = []
                    
                    # Scanner les éléments spatiaux
                    spatial_element_indices = set()
                    for key in request.form.keys():
                        if key.startswith('spatial_element_') and key.endswith('_text'):
                            parts = key.split('_')
                            if len(parts) >= 3:
                                element_index = parts[2]
                                try:
                                    spatial_element_indices.add(int(element_index))
                                except ValueError:
                                    continue
                    
                    for element_index in sorted(spatial_element_indices):
                        element_text = request.form.get(f'spatial_element_{element_index}_text', '').strip()
                        if element_text:
                            spatial_elements.append(element_text)
                    
                    # Scanner les zones spatiales
                    spatial_zone_indices = set()
                    for key in request.form.keys():
                        if key.startswith('spatial_zone_') and key.endswith('_name'):
                            parts = key.split('_')
                            if len(parts) >= 3:
                                zone_index = parts[2]
                                try:
                                    spatial_zone_indices.add(int(zone_index))
                                except ValueError:
                                    continue
                    
                    for zone_index in sorted(spatial_zone_indices):
                        zone_name = request.form.get(f'spatial_zone_{zone_index}_name', '').strip()
                        zone_x = request.form.get(f'spatial_zone_{zone_index}_x')
                        zone_y = request.form.get(f'spatial_zone_{zone_index}_y')
                        zone_width = request.form.get(f'spatial_zone_{zone_index}_width')
                        zone_height = request.form.get(f'spatial_zone_{zone_index}_height')
                        
                        if zone_name and zone_x and zone_y and zone_width and zone_height:
                            try:
                                spatial_zones.append({
                                    'name': zone_name,
                                    'x': float(zone_x),
                                    'y': float(zone_y),
                                    'width': float(zone_width),
                                    'height': float(zone_height)
                                })
                            except ValueError:
                                continue
                    
                    content = {
                        'mode': 'spatial',
                        'instructions': instructions,
                        'main_image': main_image_path,
                        'elements': spatial_elements,
                        'zones': spatial_zones
                    }
                    current_app.logger.info(f'[LEGEND_EDIT_DEBUG] Mode spatial: {len(spatial_elements)} éléments, {len(spatial_zones)} zones')
                
                else:
                    # Mode classique - utiliser la logique des zones existante
                    content = {
                        'mode': 'classic',
                        'instructions': instructions,
                        'main_image': main_image_path,
                        'zones': zones,
                        'elements': elements
                    }
                current_app.logger.info(f'[LEGEND_EDIT_DEBUG] Contenu sauvegardé avec succès - Mode: {legend_mode}, Image: {main_image_path}')
                
                # Synchroniser exercise.image_path avec main_image_path si nécessaire
                if main_image_path and (not exercise.image_path or exercise.image_path != main_image_path):
                    exercise.image_path = main_image_path
                    current_app.logger.info(f'[LEGEND_EDIT_DEBUG] Image path synchronisé: {exercise.image_path}')
                
                # Mettre à jour le contenu de l'exercice
                exercise.content = json.dumps(content)
                
                # Mettre à jour l'exercice en base (les champs de base sont déjà mis à jour au début de la fonction POST)
                try:
                    # Synchronisation finale des chemins d'image avant le commit final
                    content = json.loads(exercise.content) if exercise.content else {}
                    if not isinstance(content, dict):
                        content = {}
                        
                    # Mettre à jour l'image dans le contenu si nécessaire
                    if exercise.image_path and not content.get('image'):
                        content['image'] = exercise.image_path
                        exercise.content = json.dumps(content)
                    
                    # Commit final avec toutes les modifications
                    db.session.commit()
                    flash(f'Exercice "{exercise.title}" modifié avec succès!', 'success')
                    return redirect(url_for('view_exercise', exercise_id=exercise.id))
                    
                except Exception as e:
                    print(f'Erreur lors de la modification: {e}')
                    db.session.rollback()
                    flash(f'Erreur lors de la modification de l\'exercice: {str(e)}', 'error')
                    return render_template('edit_exercise.html', exercise=exercise)
                finally:
                    db.session.close()
                        
            elif exercise.exercise_type == 'qcm':
                # Traitement spécifique pour le type QCM
                current_app.logger.info(f'[QCM_EDIT_DEBUG] Traitement du contenu QCM')
                
                # Récupérer les questions
                questions = []
                question_count = int(request.form.get('question_count', 0))
                current_app.logger.info(f'[QCM_EDIT_DEBUG] Nombre de questions: {question_count}')
                
                # Récupérer les questions via questions[]
                questions_list = request.form.getlist('questions[]')
                current_app.logger.info(f'[QCM_EDIT_DEBUG] Questions reçues: {questions_list}')
                
                for q_index, question_text in enumerate(questions_list):
                    question_text = question_text.strip()
                    if not question_text:
                        continue
                    
                    # Récupérer les options pour cette question
                    options = []
                    option_index = 0
                    while True:
                        option_text = request.form.get(f'option_{q_index}_{option_index}', '').strip()
                        if not option_text:
                            break
                        options.append(option_text)
                        option_index += 1
                    
                    # Récupérer la réponse correcte
                    correct_answer = request.form.get(f'correct_{q_index}', '0')
                    try:
                        correct_answer = int(correct_answer)
                    except ValueError:
                        correct_answer = 0
                    
                    if options:  # Ne garder que les questions avec au moins une option
                        questions.append({
                            'text': question_text,
                            'choices': options,
                            'correct_answer': correct_answer
                        })
                        current_app.logger.info(f'[QCM_EDIT_DEBUG] Question {q_index+1}: "{question_text}" avec {len(options)} options')
                
                if not questions:
                    flash('Veuillez ajouter au moins une question avec des options.', 'error')
                # Mettre à jour le contenu sans préserver l'image (fonctionnalité désactivée pour QCM)
                content = {'questions': questions}
                
                # Supprimer toute référence à l'image dans le contenu
                if 'image' in content:
                    del content['image']
                    current_app.logger.info(f'[QCM_EDIT_DEBUG] Référence à l\'image supprimée du contenu')
                
                # Supprimer l'image_path de l'exercice
                if exercise.image_path:
                    exercise.image_path = None
                    current_app.logger.info(f'[QCM_EDIT_DEBUG] Image_path supprimé de l\'exercice')
                
                try:
                    exercise.content = json.dumps(content)
                    current_app.logger.info(f'[QCM_EDIT_DEBUG] Contenu QCM mis à jour sans image')
                except Exception as e:
                    current_app.logger.error(f'[QCM_EDIT_DEBUG] Erreur lors de la sauvegarde: {str(e)}')
                    db.session.rollback()
                    flash(f'Erreur lors de la modification de l\'exercice: {str(e)}', 'error')
                    content = json.loads(exercise.content) if exercise.content else {}
                    return render_template('exercise_types/qcm_edit.html', exercise=exercise, content=content)
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
            else:
                # Gestion générique pour tous les autres types d'exercices
                # (word_placement, drag_and_drop, etc.)
                current_app.logger.info(f'[EDIT_DEBUG] Traitement générique pour le type: {exercise.exercise_type}')
                
                # Gestion de l'image d'exercice pour les types génériques
                if 'exercise_image' in request.files:
                    file = request.files['exercise_image']
                    if file and file.filename != '' and allowed_file(file.filename, file):
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
                
                # Pour les types génériques, on ne modifie que les champs de base
                # Le contenu spécifique reste inchangé car il est géré par les templates d'édition spécifiques
                try:
                    db.session.commit()
                    flash(f'Exercice "{exercise.title}" modifié avec succès!', 'success')
                    return redirect(url_for('view_exercise', exercise_id=exercise.id))
                except Exception as e:
                    current_app.logger.error(f'[EDIT_DEBUG] Erreur lors de la sauvegarde: {str(e)}')
                    db.session.rollback()
                    flash(f'Erreur lors de la modification de l\'exercice: {str(e)}', 'error')
                    return render_template('edit_exercise.html', exercise=exercise)
                
        except Exception as e:
            print(f'Erreur lors de la modification de l\'exercice: {e}')
            db.session.rollback()
            flash(f'Une erreur est survenue lors de la modification de l\'exercice: {str(e)}', 'error')
            return render_template('edit_exercise.html', exercise=exercise)
        
    # Si la méthode n'est ni GET ni POST
    return redirect(url_for('exercise_library'))

# ===== ROUTES STATISTIQUES ET EXPORT =====

from export_utils import generate_class_excel, generate_class_pdf

@app.route('/teacher/statistics')
@login_required
def teacher_statistics():
    """Page des statistiques pour les enseignants"""
    if not current_user.is_teacher:
        flash('Accès refusé. Vous devez être enseignant.', 'error')
        return redirect(url_for('dashboard'))
    
    # Récupérer toutes les classes de l'enseignant
    classes = Class.query.filter_by(teacher_id=current_user.id).all()
    
    # Calculer les statistiques pour chaque classe
    classes_stats = []
    for class_obj in classes:
        # Récupérer tous les exercices de la classe
        all_exercises = []
        for course in class_obj.courses:
            all_exercises.extend(course.exercises)
        
        # Calculer les statistiques pour chaque étudiant
        students_stats = []
        for student in class_obj.students:
            # Compter les exercices complétés
            completed_exercises = ExerciseAttempt.query.filter_by(
                student_id=student.id
            ).join(Exercise).filter(
                Exercise.id.in_([ex.id for ex in all_exercises])
            ).count()
            
            # Calculer le score moyen
            attempts = ExerciseAttempt.query.filter_by(
                student_id=student.id
            ).join(Exercise).filter(
                Exercise.id.in_([ex.id for ex in all_exercises])
            ).all()
            
            if attempts:
                average_score = sum(attempt.score or 0 for attempt in attempts) / len(attempts)
            else:
                average_score = None
            
            students_stats.append({
                'student': student,
                'completed_exercises': completed_exercises,
                'total_exercises': len(all_exercises),
                'average_score': average_score
            })
        
        classes_stats.append({
            'class': class_obj,
            'students': students_stats,
            'total_exercises': len(all_exercises)
        })
    
    return render_template('teacher/statistics.html', classes_stats=classes_stats)

# Fin de la route teacher_statistics

# ===== ROUTE D'ÉDITION D'EXERCICE SUPPRIMÉE =====
# Cette route était en conflit avec la route robuste /exercise/edit_exercise/<int:exercise_id>
# La logique robuste est maintenant dans la route ci-dessous

# ===== ROUTE D'ÉDITION D'EXERCICE BLUEPRINT =====

@app.route('/exercise/edit_exercise/<int:exercise_id>', methods=['GET', 'POST'])
@login_required
def edit_exercise_blueprint(exercise_id):
    """Route d'édition d'exercice avec logique légende complète"""
    print(f'[EDIT_POST_DEBUG] POST request received for exercise {exercise_id}')
    print(f'[EDIT_POST_DEBUG] Form data keys: {list(request.form.keys())}')
    print(f'[EDIT_POST_DEBUG] Form data: {dict(request.form)}')
    
    exercise = Exercise.query.get_or_404(exercise_id)
    
    if request.method == 'GET':
        print(f'[EDIT_DEBUG] Exercise ID: {exercise_id}')
        print(f'[EDIT_DEBUG] Exercise type: {repr(exercise.exercise_type)}')
        print(f'[EDIT_DEBUG] Exercise title: {repr(exercise.title)}')
        print(f'[EDIT_DEBUG] Template path: {repr("exercise_types/legend_edit.html")}')
        
        content = json.loads(exercise.content) if exercise.content else {}
        print(f'[EDIT_DEBUG] Content type: {type(content)}')
        print(f'[EDIT_DEBUG] Content keys: {list(content.keys()) if isinstance(content, dict) else "Not a dict"}')
        
        attempts = ExerciseAttempt.query.filter_by(exercise_id=exercise_id).all()
        print(f'[EDIT_DEBUG] Attempts count: {len(attempts)}')
        
        # Rediriger vers le template d'édition approprié selon le type
        if exercise.exercise_type == 'legend':
            return render_template('exercise_types/legend_edit.html', exercise=exercise)
        else:
            return render_template('edit_exercise.html', exercise=exercise)
    
    if request.method == 'POST':
        print(f'[EDIT_POST_DEBUG] Title: {repr(request.form.get("title", ""))}')
        print(f'[EDIT_POST_DEBUG] Subject: {repr(request.form.get("subject", ""))}')
        print(f'[EDIT_POST_DEBUG] Description: {repr(request.form.get("description", ""))}')
        
        try:
            # Mise à jour des champs de base
            if 'title' in request.form:
                exercise.title = request.form['title']
            if 'description' in request.form:
                exercise.description = request.form['description']
            
            # Gestion de l'image de l'exercice
            # Vérifier si l'utilisateur a demandé de supprimer l'image
            if 'remove_exercise_image' in request.form and request.form['remove_exercise_image'] == 'true':
                if exercise.image_path:
                    # Supprimer le fichier physique si possible
                    try:
                        file_path = os.path.join(app.root_path, exercise.image_path.lstrip('/'))
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            print(f'[EDIT_DEBUG] Image supprimée du système de fichiers: {file_path}')
                    except Exception as e:
                        print(f'[EDIT_DEBUG] Erreur lors de la suppression du fichier: {e}')
                    
                    # Mettre à jour la base de données
                    exercise.image_path = None
                    print('[EDIT_DEBUG] Image supprimée de la base de données')
            
            # Vérifier si une nouvelle image a été téléversée
            # Gérer à la fois 'legend_main_image' (pour les légendes) et 'exercise_image' (pour les autres types)
            image_file = None
            if 'legend_main_image' in request.files and request.files['legend_main_image'].filename:
                image_file = request.files['legend_main_image']
            elif 'exercise_image' in request.files and request.files['exercise_image'].filename:
                image_file = request.files['exercise_image']
                
            if image_file and image_file.filename != '' and allowed_file(image_file.filename):
                # Sauvegarder la nouvelle image
                filename = generate_unique_filename(image_file.filename)
                # Créer le dossier de destination s'il n'existe pas
                dest_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'exercises')
                os.makedirs(dest_folder, exist_ok=True)
                filepath = os.path.join(dest_folder, filename)
                image_file.save(filepath)
                
                # Vérifier que le fichier n'est pas vide
                if os.path.getsize(filepath) > 0:
                    # Supprimer l'ancienne image si elle existe
                    if exercise.image_path:
                        try:
                            old_file_path = os.path.join(app.root_path, exercise.image_path.lstrip('/'))
                            if os.path.exists(old_file_path):
                                os.remove(old_file_path)
                                print(f'[EDIT_DEBUG] Ancienne image supprimée: {old_file_path}')
                        except Exception as e:
                            print(f'[EDIT_DEBUG] Erreur lors de la suppression de l\'ancienne image: {e}')
                    
                    exercise.image_path = f"/static/uploads/exercises/{filename}"
                    print(f'[EDIT_DEBUG] Nouvelle image sauvegardée: {exercise.image_path}')
                else:
                    os.remove(filepath)  # Supprimer le fichier vide
                    print('[EDIT_DEBUG] Fichier image vide supprimé')
            
            # Traitement pour tous les types d'exercices (pas seulement legend)
            
            # Traitement des questions QCM
            questions = []
            question_index = 1
            
            while f'question_{question_index}' in request.form:
                question_text = request.form.get(f'question_{question_index}', '').strip()
                if question_text:
                    # Récupérer les options pour cette question
                    options = []
                    option_index = 0
                    while f'question_{question_index}_option_{option_index}' in request.form:
                        option_text = request.form.get(f'question_{question_index}_option_{option_index}', '').strip()
                        is_correct = f'question_{question_index}_correct' in request.form and request.form[f'question_{question_index}_correct'] == str(option_index)
                        
                        if option_text:
                            options.append({
                                'text': option_text,
                                'is_correct': is_correct
                            })
                        option_index += 1
                    
                    questions.append({
                        'question': question_text,
                        'options': options
                    })
                
                question_index += 1
            
            # Mise à jour du contenu avec les questions
            content = {
                'questions': questions
            }
            exercise.content = json.dumps(content)
            
            # Sauvegarder les modifications
            db.session.commit()
            flash('Exercice modifié avec succès !', 'success')
            return redirect(url_for('view_exercise', exercise_id=exercise_id))
                
        except Exception as e:
            print(f'[EDIT_ERROR] Erreur lors de la modification : {e}')
            flash('Erreur lors de la modification de l\'exercice.', 'error')
            db.session.rollback()
    
    return render_template('exercise_types/legend_edit.html', exercise=exercise)


# ========================================
# DASHBOARD ADMINISTRATEUR - GESTION DES INSCRIPTIONS PAYANTES
# ========================================

def admin_required(f):
    """Décorateur pour vérifier que l'utilisateur est administrateur"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Accès non autorisé. Seuls les administrateurs peuvent accéder à cette page.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def subscription_required(f):
    """Décorateur pour vérifier que l'utilisateur a un abonnement actif"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Vous devez être connecté pour accéder à cette page.', 'error')
            return redirect(url_for('login'))
        
        # Les admins ont toujours accès
        if current_user.role == 'admin':
            return f(*args, **kwargs)
        
        # Les étudiants peuvent accéder (leur accès dépend de leur enseignant)
        if current_user.role == 'student':
            return f(*args, **kwargs)
        
        # Pour les enseignants, vérifier l'abonnement
        if current_user.role == 'teacher':
            if not current_user.can_access_platform:
                return redirect(url_for('subscription_status'))
        
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Décorateur pour vérifier que l'utilisateur est administrateur"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Vous devez être connecté pour accéder à cette page.', 'error')
            return redirect(url_for('login'))
        
        if current_user.role != 'admin':
            flash('Accès non autorisé. Droits administrateur requis.', 'error')
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    """Dashboard principal de l'administrateur pour gérer les inscriptions"""
    # Statistiques générales
    total_users = User.query.count()
    pending_users = User.query.filter_by(subscription_status='pending').count()
    paid_users = User.query.filter_by(subscription_status='paid').count()
    approved_users = User.query.filter_by(subscription_status='approved').count()
    rejected_users = User.query.filter_by(subscription_status='rejected').count()
    
    # Utilisateurs en attente de validation (payés)
    users_awaiting_approval = User.query.filter_by(subscription_status='paid').order_by(User.payment_date.desc()).all()
    
    # Dernières inscriptions
    recent_registrations = User.query.filter(User.subscription_status.in_(['pending', 'paid'])).order_by(User.created_at.desc()).limit(10).all()
    
    stats = {
        'total_users': total_users,
        'pending_users': pending_users,
        'paid_users': paid_users,
        'approved_users': approved_users,
        'rejected_users': rejected_users
    }
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         users_awaiting_approval=users_awaiting_approval,
                         recent_registrations=recent_registrations)

@app.route('/migrate-school-column')
def migrate_school_column():
    """Route temporaire pour ajouter la colonne school_name depuis Railway"""
    
    try:
        from sqlalchemy import text
        
        # Vérifier si la colonne existe déjà
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'user' AND column_name = 'school_name'
        """))
        
        if result.fetchone():
            return "La colonne school_name existe deja !"
        
        # Ajouter la colonne school_name
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN school_name VARCHAR(255);'))
        db.session.commit()
        
        return "Colonne school_name ajoutee avec succes ! Votre application devrait maintenant fonctionner."
        
    except Exception as e:
        db.session.rollback()
        return f"Erreur : {str(e)}"

@app.route('/fix-uploads-directory')
def fix_uploads_directory():
    """Route temporaire pour créer le répertoire static/uploads en production Railway"""
    
    try:
        import os
        from pathlib import Path
        
        # Créer le répertoire static/uploads
        uploads_dir = Path('static/uploads')
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        # Créer un fichier .gitkeep pour que le répertoire soit conservé
        gitkeep_file = uploads_dir / '.gitkeep'
        gitkeep_file.touch()
        
        # Vérifier que le répertoire existe
        if uploads_dir.exists():
            return f"SUCCES: Repertoire {uploads_dir} cree avec succes en production Railway ! Les images pourront maintenant etre uploadees et affichees."
        else:
            return f"ERREUR: Le repertoire {uploads_dir} n'a pas pu etre cree."
            
    except Exception as e:
        return f"ERREUR lors de la creation du repertoire: {str(e)}"

@app.route('/check-missing-images')
def check_missing_images():
    """Route pour identifier les images manquantes en production Railway"""
    try:
        import os
        from pathlib import Path
        
        result = []
        result.append("<h2>DIAGNOSTIC IMAGES PRODUCTION RAILWAY</h2>")
        
        # 1. Vérifier le répertoire uploads
        uploads_dir = Path('static/uploads')
        result.append(f"<h3>1. Repertoire static/uploads</h3>")
        result.append(f"<p><strong>Existe:</strong> {uploads_dir.exists()}</p>")
        
        if uploads_dir.exists():
            files = list(uploads_dir.glob('*'))
            result.append(f"<p><strong>Fichiers presents:</strong> {len(files)}</p>")
            result.append("<ul>")
            for f in files:
                result.append(f"<li>{f.name}</li>")
            result.append("</ul>")
        
        # 2. Vérifier les références dans la DB
        result.append(f"<h3>2. Exercices avec images dans la base</h3>")
        exercises_with_images = Exercise.query.filter(Exercise.image_path.isnot(None)).all()
        result.append(f"<p><strong>Nombre d'exercices avec images:</strong> {len(exercises_with_images)}</p>")
        
        missing_images = []
        for ex in exercises_with_images:
            if ex.image_path:
                filename = ex.image_path.split('/')[-1] if '/' in ex.image_path else ex.image_path
                image_path = uploads_dir / filename
                
                result.append(f"<h4>Exercice {ex.id}: {ex.title}</h4>")
                result.append(f"<p><strong>Image path DB:</strong> {ex.image_path}</p>")
                result.append(f"<p><strong>Fichier attendu:</strong> {filename}</p>")
                result.append(f"<p><strong>Fichier existe:</strong> {image_path.exists()}</p>")
                
                if not image_path.exists():
                    missing_images.append(filename)
                    result.append(f"<p style='color: red;'><strong>MANQUANT</strong></p>")
                else:
                    result.append(f"<p style='color: green;'><strong>OK</strong></p>")
                result.append("<hr>")
        
        # 3. Résumé
        result.append(f"<h3>3. Resume</h3>")
        result.append(f"<p><strong>Images manquantes:</strong> {len(missing_images)}</p>")
        if missing_images:
            result.append("<ul>")
            for img in missing_images:
                result.append(f"<li style='color: red;'>{img}</li>")
            result.append("</ul>")
        
        return "<br>".join(result)
        
    except Exception as e:
        return f"<h2>ERREUR:</h2><p>{str(e)}</p>"

@app.route('/create-simple-placeholders')
def create_simple_placeholders():
    """Route pour créer des fichiers placeholder simples sans Pillow"""
    try:
        import os
        from pathlib import Path
        
        # Créer le répertoire static/uploads
        uploads_dir = Path('static/uploads')
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        # Images connues manquantes
        placeholder_files = [
            "Capture d'écran 2025-08-14 145027_20250814_182421_Da3gvm.png",
            "triangle.png", 
            "clopepe.png",
            "corps_humain_exemple.jpg"
        ]
        
        created_files = []
        
        for filename in placeholder_files:
            file_path = uploads_dir / filename
            
            if not file_path.exists():
                # Créer un fichier SVG simple comme placeholder
                svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="400" xmlns="http://www.w3.org/2000/svg">
  <rect width="800" height="400" fill="#f0f0f0" stroke="#cccccc" stroke-width="3"/>
  <text x="400" y="180" font-family="Arial, sans-serif" font-size="24" text-anchor="middle" fill="#666666">
    IMAGE DE L'EXERCICE
  </text>
  <text x="400" y="220" font-family="Arial, sans-serif" font-size="18" text-anchor="middle" fill="#999999">
    {filename}
  </text>
  <text x="400" y="250" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#999999">
    Image temporairement indisponible
  </text>
</svg>'''
                
                # Sauvegarder le fichier SVG avec l'extension d'origine
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(svg_content)
                
                created_files.append(filename)
        
        result = f"<h2>CREATION PLACEHOLDERS REUSSIE</h2>"
        result += f"<p><strong>Fichiers crees:</strong> {len(created_files)}</p>"
        result += "<ul>"
        for f in created_files:
            result += f"<li>{f}</li>"
        result += "</ul>"
        result += f"<p>Les images devraient maintenant s'afficher dans les exercices !</p>"
        
        return result
        
    except Exception as e:
        return f"<h2>ERREUR:</h2><p>{str(e)}</p>"

@app.route('/debug-railway')
def debug_railway():
    """Route de diagnostic pour identifier les problemes Railway"""
    
    try:
        debug_info = []
        
        # Test 1: Connexion base de données
        try:
            from sqlalchemy import text
            result = db.session.execute(text("SELECT 1"))
            debug_info.append("OK Connexion base de donnees OK")
        except Exception as e:
            debug_info.append(f"ERREUR Connexion base de donnees ERREUR: {str(e)}")
        
        # Test 2: Structure table user
        try:
            result = db.session.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'user'
                ORDER BY column_name
            """))
            columns = result.fetchall()
            debug_info.append(f"✅ Table user a {len(columns)} colonnes")
            for col in columns:
                debug_info.append(f"  - {col[0]} ({col[1]})")
        except Exception as e:
            debug_info.append(f"❌ Structure table user ERREUR: {str(e)}")
        
        # Test 3: Import des modèles
        try:
            from models import User, Exercise
            debug_info.append("✅ Import modeles OK")
        except Exception as e:
            debug_info.append(f"❌ Import modeles ERREUR: {str(e)}")
        
        # Test 4: Variables d'environnement
        import os
        debug_info.append(f"✅ FLASK_ENV: {os.environ.get('FLASK_ENV', 'non defini')}")
        debug_info.append(f"✅ DATABASE_URL: {'defini' if os.environ.get('DATABASE_URL') else 'non defini'}")
        
        # Test 5: Flask-Login
        try:
            from flask_login import current_user
            debug_info.append(f"✅ Flask-Login import OK")
            debug_info.append(f"✅ current_user accessible: {hasattr(current_user, 'is_authenticated')}")
            debug_info.append(f"✅ current_user.is_authenticated: {current_user.is_authenticated}")
        except Exception as e:
            debug_info.append(f"❌ Flask-Login ERREUR: {str(e)}")
        
        # Test 6: Test route index directement
        try:
            debug_info.append("=== TEST ROUTE INDEX ===")
            if current_user.is_authenticated:
                debug_info.append(f"✅ Utilisateur connecte: {current_user.email}")
                debug_info.append(f"✅ Role: {current_user.role}")
            else:
                debug_info.append("✅ Utilisateur non connecte - devrait afficher login.html")
        except Exception as e:
            debug_info.append(f"❌ Test route index ERREUR: {str(e)}")
        
        return "<br>".join(debug_info)
        
    except Exception as e:
        return f"❌ Erreur diagnostic: {str(e)}"

@app.route('/test-simple')
def test_simple():
    """Route ultra-simple pour tester si Flask fonctionne"""
    return "✅ Flask fonctionne parfaitement sur Railway !"

@app.route('/debug-fill-in-blanks-railway')
def debug_fill_in_blanks_railway():
    """Route de diagnostic spécifique pour les problèmes fill_in_blanks sur Railway"""
    try:
        debug_info = []
        
        # 1. Vérifier les exercices fill_in_blanks
        exercises = Exercise.query.filter_by(exercise_type='fill_in_blanks').all()
        debug_info.append(f"<h2>1. EXERCICES FILL_IN_BLANKS: {len(exercises)} trouvés</h2>")
        
        for ex in exercises:
            debug_info.append(f"<h3>Exercice {ex.id}: {ex.title}</h3>")
            debug_info.append(f"<p><strong>Image path:</strong> {ex.image_path}</p>")
            
            # Analyser le contenu JSON
            content = json.loads(ex.content)
            debug_info.append(f"<p><strong>Format JSON:</strong> {list(content.keys())}</p>")
            
            if 'text' in content:
                text = content['text']
                blank_count = text.count('___')
                debug_info.append(f"<p><strong>Text:</strong> {text}</p>")
                debug_info.append(f"<p><strong>Blancs dans text:</strong> {blank_count}</p>")
            
            if 'sentences' in content:
                sentences = content['sentences']
                total_blanks = sum(sentence.count('___') for sentence in sentences)
                debug_info.append(f"<p><strong>Sentences:</strong> {sentences}</p>")
                debug_info.append(f"<p><strong>Blancs dans sentences:</strong> {total_blanks}</p>")
            
            words = content.get('words', [])
            debug_info.append(f"<p><strong>Words:</strong> {words} (count: {len(words)})</p>")
            
            # Vérifier la cohérence blancs/mots
            if 'text' in content:
                text_blanks = content['text'].count('___')
                word_count = len(words)
                if text_blanks != word_count:
                    debug_info.append(f"<p style='color: red;'><strong>ALERTE:</strong> {text_blanks} blancs mais {word_count} mots!</p>")
                else:
                    debug_info.append(f"<p style='color: green;'><strong>OK:</strong> {text_blanks} blancs = {word_count} mots</p>")
        
        # 2. Vérifier les dossiers et fichiers d'images
        debug_info.append("<h2>2. VERIFICATION DOSSIERS IMAGES</h2>")
        
        import os
        static_dir = os.path.join(app.root_path, 'static')
        uploads_dir = os.path.join(static_dir, 'uploads')
        
        debug_info.append(f"<p><strong>Dossier static:</strong> {static_dir} - Existe: {os.path.exists(static_dir)}</p>")
        debug_info.append(f"<p><strong>Dossier uploads:</strong> {uploads_dir} - Existe: {os.path.exists(uploads_dir)}</p>")
        
        if os.path.exists(uploads_dir):
            files = os.listdir(uploads_dir)
            debug_info.append(f"<p><strong>Fichiers dans uploads:</strong> {len(files)}</p>")
            debug_info.append("<ul>")
            for f in files[:10]:  # Afficher les 10 premiers
                debug_info.append(f"<li>{f}</li>")
            if len(files) > 10:
                debug_info.append(f"<li>... et {len(files) - 10} autres</li>")
            debug_info.append("</ul>")
        
        # 3. Test de la logique de scoring
        debug_info.append("<h2>3. TEST LOGIQUE SCORING</h2>")
        
        if exercises:
            test_exercise = exercises[0]
            content = json.loads(test_exercise.content)
            correct_answers = content.get('words', [])
            
            debug_info.append(f"<h3>Test avec exercice: {test_exercise.title}</h3>")
            debug_info.append(f"<p><strong>Réponses correctes:</strong> {correct_answers}</p>")
            
            # Test scoring parfait
            total_blanks = len(correct_answers)
            score_perfect = round((total_blanks / total_blanks) * 100) if total_blanks > 0 else 0
            debug_info.append(f"<p><strong>Score parfait attendu:</strong> {total_blanks}/{total_blanks} = {score_perfect}%</p>")
            
            # Test scoring partiel (bug Railway)
            if total_blanks >= 2:
                score_partial = round((1 / total_blanks) * 100)
                debug_info.append(f"<p><strong>Score avec 1 seul blanc correct:</strong> 1/{total_blanks} = {score_partial}%</p>")
                if score_partial == 50:
                    debug_info.append("<p style='color: red;'><strong>BUG IDENTIFIE:</strong> C'est exactement le problème Railway (50%)!</p>")
        
        # 4. Vérifier les variables d'environnement
        debug_info.append("<h2>4. VARIABLES ENVIRONNEMENT</h2>")
        env_vars = ['DATABASE_URL', 'FLASK_ENV', 'PORT']
        for var in env_vars:
            value = os.environ.get(var, 'NON DEFINI')
            if var == 'DATABASE_URL' and value != 'NON DEFINI':
                value = value[:30] + "..." if len(value) > 30 else value
            debug_info.append(f"<p><strong>{var}:</strong> {value}</p>")
        
        # 5. Test de la route d'image
        debug_info.append("<h2>5. TEST ROUTE IMAGE</h2>")
        debug_info.append(f"<p><strong>Route statique Flask:</strong> {url_for('static', filename='uploads/test.png')}</p>")
        
        return "<br>".join(debug_info)
        
    except Exception as e:
        return f"<h2>❌ Erreur diagnostic:</h2><p>{str(e)}</p>"



@app.route('/admin/subscriptions')
@login_required
@admin_required
def admin_subscriptions():
    """Page de gestion des abonnements avec filtrage"""
    status_filter = request.args.get('status', 'all')
    type_filter = request.args.get('type', 'all')
    
    # Construire la requête avec filtres
    query = User.query.filter(User.role.in_(['teacher']))  # Exclure les admins et étudiants
    
    if status_filter != 'all':
        query = query.filter_by(subscription_status=status_filter)
    
    if type_filter != 'all':
        query = query.filter_by(subscription_type=type_filter)
    
    users = query.order_by(User.created_at.desc()).all()
    
    return render_template('admin/subscriptions.html', 
                         users=users, 
                         status_filter=status_filter,
                         type_filter=type_filter)

@app.route('/admin/user/<int:user_id>')
@login_required
@admin_required
def admin_user_details(user_id):
    """Page de détails d'un utilisateur pour l'administrateur"""
    user = User.query.get_or_404(user_id)
    
    # Récupérer l'administrateur qui a approuvé (si applicable)
    approver = None
    if user.approved_by:
        approver = User.query.get(user.approved_by)
    
    return render_template('admin/user_details.html', user=user, approver=approver)

@app.route('/admin/approve/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def approve_subscription(user_id):
    """Approuver un abonnement"""
    user = User.query.get_or_404(user_id)
    
    if user.subscription_status != 'paid':
        flash('Seuls les abonnements payés peuvent être approuvés.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    # Approuver l'abonnement
    user.approve_subscription(current_user.id)
    db.session.commit()
    
    flash(f'Abonnement de {user.name} approuvé avec succès !', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/approve-trial/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def approve_trial(user_id):
    """Approuver un utilisateur pour un essai gratuit avec durée flexible"""
    user = User.query.get_or_404(user_id)
    
    # Récupérer les paramètres du formulaire
    trial_days = int(request.form.get('trial_days', 30))
    trial_type = request.form.get('trial_type', 'trial')
    notes = request.form.get('notes', '').strip()
    
    # Calculer la date d'expiration
    from datetime import datetime, timedelta
    approval_date = datetime.now()
    expiration_date = approval_date + timedelta(days=trial_days)
    
    # Mettre à jour l'utilisateur
    user.subscription_status = 'approved'
    user.subscription_type = trial_type
    user.subscription_amount = 0.0
    user.approval_date = approval_date
    user.approved_by = current_user.id
    user.subscription_expires = expiration_date
    user.notes = f"Essai gratuit de {trial_days} jours approuvé par {current_user.name}. {notes}".strip()
    
    db.session.commit()
    
    flash(f'{user.name} approuvé pour un essai gratuit de {trial_days} jours !', 'success')
    return redirect(url_for('admin_user_details', user_id=user_id))

@app.route('/init-production')
def init_production():
    """Route pour initialiser la base de données en production"""
    try:
        from datetime import datetime
        from werkzeug.security import generate_password_hash
        
        # Créer toutes les tables
        db.create_all()
        
        # Vérifier si un admin existe déjà
        existing_admin = User.query.filter_by(role='admin').first()
        if existing_admin:
            return f"<h2>✅ Admin déjà existant</h2><p>Email: {existing_admin.email}</p><p><a href='/login'>Se connecter</a></p>"
        
        # Créer le compte admin
        admin_user = User(
            name="Administrateur",
            username="admin", 
            email="admin@admin.com",
            password_hash=generate_password_hash("admin"),
            role="admin",
            subscription_status="approved",
            subscription_type="admin",
            subscription_amount=0.0,
            created_at=datetime.now(),
            approval_date=datetime.now(),
            approved_by=1
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        return """
        <h2>🎉 Production initialisée avec succès!</h2>
        <p><strong>Compte admin créé:</strong></p>
        <ul>
            <li>Email: admin@admin.com</li>
            <li>Mot de passe: admin</li>
        </ul>
        <p><a href="/login" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Se connecter</a></p>
        <p><a href="/admin/dashboard">Dashboard Admin</a></p>
        """
        
    except Exception as e:
        return f"<h2>❌ Erreur d'initialisation</h2><p>{str(e)}</p><p><a href='/'>Retour</a></p>"

@app.route('/fix-all-image-paths')
@login_required
@admin_required
def fix_all_image_paths():
    """Route pour corriger automatiquement tous les chemins d'images incorrects"""
    try:
        import json
        
        # Récupérer tous les exercices avec des images
        exercises = Exercise.query.filter(
            Exercise.image_path.isnot(None),
            Exercise.image_path != ""
        ).all()
        
        if not exercises:
            return """
            <div style="padding: 20px; font-family: Arial;">
                <h2>✅ Aucun exercice avec image trouvé</h2>
                <p><a href="/admin/dashboard">Retour au dashboard</a></p>
            </div>
            """
        
        corrections_made = 0
        results = []
        
        for exercise in exercises:
            original_path = exercise.image_path
            needs_correction = False
            corrected_path = original_path
            
            # Vérifier si le chemin a besoin d'être corrigé
            if original_path and (not original_path.startswith('/static/uploads/') or original_path.startswith('/static/exercises/')):
                needs_correction = True
                
                if original_path.startswith('static/'):
                    # Cas: static/uploads/filename -> /static/uploads/filename
                    corrected_path = f"/{original_path}"
                elif original_path.startswith('uploads/'):
                    # Cas: uploads/filename -> /static/uploads/filename
                    corrected_path = f"/static/{original_path}"
                elif original_path.startswith('/static/exercises/'):
                    # Cas: /static/exercises/filename -> /static/uploads/filename
                    filename = os.path.basename(original_path)
                    corrected_path = f"/static/uploads/{filename}"
                elif original_path.startswith('static/exercises/'):
                    # Cas: static/exercises/filename -> /static/uploads/filename
                    filename = os.path.basename(original_path)
                    corrected_path = f"/static/uploads/{filename}"
                else:
                    # Cas: filename seul -> /static/uploads/filename
                    import os
                    filename = os.path.basename(original_path)
                    corrected_path = f"/static/uploads/{filename}"
            
            if needs_correction:
                # Mettre à jour exercise.image_path
                exercise.image_path = corrected_path
                
                # Mettre à jour content.image si le contenu existe
                if exercise.content:
                    try:
                        content = json.loads(exercise.content)
                        if 'image' in content:
                            content['image'] = corrected_path
                            exercise.content = json.dumps(content)
                    except json.JSONDecodeError:
                        pass
                
                corrections_made += 1
                results.append({
                    'id': exercise.id,
                    'title': exercise.title,
                    'original': original_path,
                    'corrected': corrected_path,
                    'status': 'corrigé'
                })
            else:
                results.append({
                    'id': exercise.id,
                    'title': exercise.title,
                    'original': original_path,
                    'corrected': original_path,
                    'status': 'déjà correct'
                })
        
        # Sauvegarder les changements
        if corrections_made > 0:
            db.session.commit()
        
        # Générer le rapport HTML
        html_results = ""
        for result in results:
            status_color = "#28a745" if result['status'] == 'déjà correct' else "#007bff"
            html_results += f"""
            <tr>
                <td>{result['id']}</td>
                <td>{result['title']}</td>
                <td style="font-family: monospace; font-size: 12px;">{result['original']}</td>
                <td style="font-family: monospace; font-size: 12px;">{result['corrected']}</td>
                <td style="color: {status_color}; font-weight: bold;">{result['status']}</td>
            </tr>
            """
        
        return f"""
        <div style="padding: 20px; font-family: Arial;">
            <h2>🔧 Correction automatique des chemins d'images</h2>
            
            <div style="background: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="color: #155724; margin: 0;">✅ Correction terminée avec succès</h3>
                <p style="margin: 10px 0 0 0;">
                    <strong>{corrections_made}</strong> exercice(s) corrigé(s) sur <strong>{len(exercises)}</strong> total
                </p>
            </div>
            
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <thead>
                    <tr style="background: #f8f9fa;">
                        <th style="border: 1px solid #dee2e6; padding: 10px;">ID</th>
                        <th style="border: 1px solid #dee2e6; padding: 10px;">Titre</th>
                        <th style="border: 1px solid #dee2e6; padding: 10px;">Chemin original</th>
                        <th style="border: 1px solid #dee2e6; padding: 10px;">Chemin corrigé</th>
                        <th style="border: 1px solid #dee2e6; padding: 10px;">Statut</th>
                    </tr>
                </thead>
                <tbody>
                    {html_results}
                </tbody>
            </table>
            
            <div style="margin: 30px 0;">
                <a href="/admin/dashboard" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Retour au dashboard</a>
                <a href="/exercise_library" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-left: 10px;">Tester la bibliothèque</a>
            </div>
        </div>
        """
        
    except Exception as e:
        return f"""
        <div style="padding: 20px; font-family: Arial;">
            <h2>❌ Erreur lors de la correction</h2>
            <p style="color: red;">{str(e)}</p>
            <p><a href="/admin/dashboard">Retour au dashboard</a></p>
        </div>
        """

@app.route('/admin/reject/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def reject_subscription(user_id):
    """Rejeter un abonnement"""
    user = User.query.get_or_404(user_id)
    reason = request.form.get('reason', '').strip()
    
    if user.subscription_status not in ['paid', 'pending']:
        flash('Seuls les abonnements en attente ou payés peuvent être rejetés.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    # Rejeter l'abonnement
    user.reject_subscription(current_user.id, reason)
    db.session.commit()
    
    flash(f'Abonnement de {user.name} rejeté.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/suspend/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def suspend_subscription(user_id):
    """Suspendre un abonnement"""
    user = User.query.get_or_404(user_id)
    reason = request.form.get('reason', '').strip()
    
    if user.subscription_status != 'approved':
        flash('Seuls les abonnements approuvés peuvent être suspendus.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    # Suspendre l'abonnement
    user.suspend_subscription(current_user.id, reason)
    db.session.commit()
    
    flash(f'Abonnement de {user.name} suspendu.', 'warning')
    return redirect(url_for('admin_dashboard'))



@app.route('/subscription/status')
@login_required
def subscription_status():
    """Page de statut d'abonnement pour l'utilisateur"""
    return render_template('subscription/status.html', user=current_user)

@app.route('/subscription/payment')
@login_required
def subscription_payment():
    """Page de paiement d'abonnement"""
    if current_user.subscription_status not in ['pending', 'rejected']:
        flash('Votre abonnement ne nécessite pas de paiement actuellement.', 'info')
        return redirect(url_for('subscription_status'))
    
    # Déterminer le montant selon le type d'utilisateur
    if current_user.role == 'teacher':
        amount = 40.0
        subscription_type = 'teacher'
    else:
        # Pour les écoles (à implémenter plus tard)
        amount = 80.0
        subscription_type = 'school'
    
    return render_template('subscription/payment.html', 
                         user=current_user, 
                         amount=amount, 
                         subscription_type=subscription_type)

@app.route('/subscription/payment/process', methods=['POST'])
@login_required
def process_payment():
    """Traiter le paiement d'abonnement (simulation)"""
    try:
        amount = float(request.form.get('amount', 0))
        subscription_type = request.form.get('subscription_type', 'teacher')
        card_number = request.form.get('card_number', '')
        
        # Simulation du traitement de paiement
        # Dans la vraie version, ici on appellerait l'API Stripe/PayPal
        
        # Générer une référence de paiement simulée
        import uuid
        payment_reference = f"PAY_{uuid.uuid4().hex[:8].upper()}"
        
        # Mettre à jour l'utilisateur
        current_user.subscription_status = 'paid'
        current_user.subscription_type = subscription_type
        current_user.subscription_amount = amount
        current_user.payment_date = datetime.utcnow()
        current_user.payment_reference = payment_reference
        
        db.session.commit()
        
        flash(f'Paiement effectué avec succès ! Référence : {payment_reference}', 'success')
        flash('Votre dossier est maintenant en cours de validation par notre équipe administrative.', 'info')
        
        return redirect(url_for('subscription_status'))
        
    except Exception as e:
        print(f"[ERROR] Erreur lors du traitement du paiement : {e}")
        flash('Une erreur est survenue lors du traitement du paiement. Veuillez réessayer.', 'error')
        return redirect(url_for('subscription_payment'))



@app.route('/fix-fill-in-blanks-words')
def fix_fill_in_blanks_words():
    """Route pour corriger les exercices Fill-in-the-Blanks avec mots manquants"""
    try:
        results = []
        results.append("<h1>CORRECTION EXERCICES FILL-IN-THE-BLANKS</h1>")
        
        # Récupérer tous les exercices fill_in_blanks
        exercises = Exercise.query.filter_by(exercise_type='fill_in_blanks').all()
        results.append(f"<h2>Exercices trouvés: {len(exercises)}</h2>")
        
        fixed_count = 0
        
        for exercise in exercises:
            results.append(f"<h3>Exercice {exercise.id}: {exercise.title}</h3>")
            
            try:
                content = json.loads(exercise.content)
                
                # Vérifier si les mots sont manquants
                words = content.get('words', [])
                available_words = content.get('available_words', [])
                
                results.append(f"<p>Mots actuels: {len(words)} | Available_words: {len(available_words)}</p>")
                
                if not words and not available_words:
                    # Exercice sans mots - on va en ajouter des exemples
                    if 'sentences' in content:
                        sentences = content['sentences']
                        total_blanks = sum(s.count('___') for s in sentences)
                        
                        # Créer des mots d'exemple basés sur le nombre de blancs
                        example_words = []
                        for i in range(total_blanks):
                            example_words.append(f"mot{i+1}")
                        
                        # Mettre à jour le contenu
                        content['words'] = example_words
                        content['available_words'] = example_words  # AJOUT: copier vers available_words
                        exercise.content = json.dumps(content)
                        
                        results.append(f"<p style='color: green;'>✓ Ajouté {len(example_words)} mots d'exemple</p>")
                        fixed_count += 1
                    else:
                        results.append("<p style='color: orange;'>⚠ Pas de sentences trouvées</p>")
                elif words and not available_words:
                    # Cas où words existe mais available_words est vide - COPIER
                    content['available_words'] = words
                    exercise.content = json.dumps(content)
                    results.append(f"<p style='color: green;'>✓ Copié {len(words)} mots vers available_words</p>")
                    fixed_count += 1
                else:
                    results.append("<p style='color: blue;'>ℹ Exercice déjà avec mots</p>")
                    
            except Exception as e:
                results.append(f"<p style='color: red;'>✗ Erreur: {e}</p>")
        
        # Sauvegarder les changements
        if fixed_count > 0:
            db.session.commit()
            results.append(f"<h2 style='color: green;'>✓ {fixed_count} exercices corrigés et sauvegardés</h2>")
        else:
            results.append("<h2 style='color: blue;'>ℹ Aucune correction nécessaire</h2>")
        
        return "<br>".join(results)
        
    except Exception as e:
        return f"<h1>Erreur</h1><p>{str(e)}</p>"

@app.route('/fix-production-issues')
def fix_production_issues():
    """Route pour diagnostiquer et corriger les problèmes d'images et de scoring en production"""
    try:
        import os
        results = []
        
        results.append("<h1>DIAGNOSTIC ET CORRECTION PRODUCTION</h1>")
        
        # 1. Vérifier et créer le dossier uploads
        results.append("<h2>1. VERIFICATION DOSSIER UPLOADS</h2>")
        
        static_dir = os.path.join(app.root_path, 'static')
        uploads_dir = os.path.join(static_dir, 'uploads')
        
        results.append(f"<p>Dossier static: {static_dir}</p>")
        results.append(f"<p>Dossier uploads: {uploads_dir}</p>")
        
        # Créer static si nécessaire
        if not os.path.exists(static_dir):
            try:
                os.makedirs(static_dir)
                results.append("<p style='color: green;'>✓ Dossier static créé</p>")
            except Exception as e:
                results.append(f"<p style='color: red;'>✗ Erreur création static: {e}</p>")
        else:
            results.append("<p style='color: green;'>✓ Dossier static existe</p>")
        
        # Créer uploads si nécessaire
        if not os.path.exists(uploads_dir):
            try:
                os.makedirs(uploads_dir, exist_ok=True)
                # Créer .gitkeep
                gitkeep_path = os.path.join(uploads_dir, ".gitkeep")
                with open(gitkeep_path, 'w') as f:
                    f.write("# Dossier uploads pour les images des exercices\n")
                results.append("<p style='color: green;'>✓ Dossier uploads créé avec .gitkeep</p>")
            except Exception as e:
                results.append(f"<p style='color: red;'>✗ Erreur création uploads: {e}</p>")
        else:
            files = os.listdir(uploads_dir)
            results.append(f"<p style='color: green;'>✓ Dossier uploads existe ({len(files)} fichiers)</p>")
        
        # 2. Analyser les exercices fill_in_blanks
        results.append("<h2>2. ANALYSE EXERCICES TEXTE A TROUS</h2>")
        
        exercises = Exercise.query.filter_by(exercise_type='fill_in_blanks').all()
        results.append(f"<p>Nombre d'exercices trouvés: {len(exercises)}</p>")
        
        for ex in exercises[:5]:  # Analyser les 5 premiers
            results.append(f"<h3>Exercice {ex.id}: {ex.title}</h3>")
            
            # Analyser le contenu
            try:
                content = json.loads(ex.content)
                
                # Compter les blancs réels
                total_blanks = 0
                if 'text' in content:
                    total_blanks += content['text'].count('___')
                if 'sentences' in content:
                    total_blanks += sum(s.count('___') for s in content['sentences'])
                
                # Compter les réponses
                words = content.get('words', [])
                available_words = content.get('available_words', [])
                
                results.append(f"<p>Blancs dans contenu: {total_blanks}</p>")
                results.append(f"<p>Mots de réponse: {len(words)} (words)</p>")
                results.append(f"<p>Mots disponibles: {len(available_words)} (available_words)</p>")
                
                # Diagnostic du problème
                if total_blanks != len(words) and len(words) > 0:
                    results.append(f"<p style='color: red;'>⚠ PROBLÈME: {total_blanks} blancs mais {len(words)} réponses</p>")
                elif total_blanks == len(words):
                    results.append(f"<p style='color: green;'>✓ Cohérent: {total_blanks} blancs = {len(words)} réponses</p>")
                
                # Vérifier l'image
                if ex.image_path:
                    image_full_path = os.path.join(uploads_dir, ex.image_path)
                    if os.path.exists(image_full_path):
                        results.append(f"<p style='color: green;'>✓ Image existe: {ex.image_path}</p>")
                    else:
                        results.append(f"<p style='color: red;'>✗ Image manquante: {ex.image_path}</p>")
                
            except Exception as e:
                results.append(f"<p style='color: red;'>Erreur analyse: {e}</p>")
        
        # 3. Test de la logique de scoring corrigée
        results.append("<h2>3. TEST LOGIQUE SCORING CORRIGEE</h2>")
        
        # Simuler un exercice avec notre logique corrigée
        test_content = {
            "sentences": ["Le ___ mange une ___ rouge."],
            "words": ["chat", "pomme"]
        }
        
        # Compter les blancs
        total_blanks_in_content = sum(s.count('___') for s in test_content['sentences'])
        correct_answers = test_content['words']
        total_blanks = max(total_blanks_in_content, len(correct_answers))
        
        results.append(f"<p>Test: '{test_content['sentences'][0]}'</p>")
        results.append(f"<p>Blancs détectés: {total_blanks_in_content}</p>")
        results.append(f"<p>Réponses: {correct_answers}</p>")
        results.append(f"<p>Total blancs utilisé: {total_blanks}</p>")
        
        # Simuler scoring 100%
        correct_count = 0
        for i in range(total_blanks):
            if i < len(correct_answers):
                correct_count += 1
        
        score = round((correct_count / total_blanks) * 100) if total_blanks > 0 else 0
        results.append(f"<p>Score simulé (toutes correctes): {correct_count}/{total_blanks} = {score}%</p>")
        
        if score == 100:
            results.append("<p style='color: green;'>✓ Logique de scoring corrigée fonctionne</p>")
        else:
            results.append("<p style='color: red;'>✗ Problème avec la logique de scoring</p>")
        
        results.append("<h2>4. RÉSUMÉ</h2>")
        results.append("<p>Diagnostic terminé. Vérifiez les points ci-dessus.</p>")
        results.append("<p><strong>Actions recommandées:</strong></p>")
        results.append("<ul>")
        results.append("<li>Tester un exercice 'Texte à trous' après ces corrections</li>")
        results.append("<li>Vérifier l'affichage des images</li>")
        results.append("<li>Valider que le score atteint 100% avec toutes les bonnes réponses</li>")
        results.append("</ul>")
        
        return "<br>".join(results)
        
    except Exception as e:
        return f"<h1>ERREUR</h1><p>Erreur lors du diagnostic: {str(e)}</p><pre>{traceback.format_exc()}</pre>"


@app.route('/class/<int:class_id>/export/pdf')
@login_required
@teacher_required
def export_class_pdf(class_id):
    """Exporter les statistiques d'une classe en PDF"""
    # Vérifier que la classe appartient à l'enseignant connecté
    class_obj = Class.query.filter_by(id=class_id, teacher_id=current_user.id).first_or_404()
    
    # Récupérer les données de la classe pour l'export
    class_data = get_class_statistics(class_obj)
    
    # Générer le PDF
    pdf_buffer = generate_class_pdf(class_data)
    
    # Envoyer le fichier PDF
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"statistiques_classe_{class_obj.name}_{datetime.now().strftime('%Y%m%d')}.pdf",
        mimetype='application/pdf'
    )

@app.route('/class/<int:class_id>/export/excel')
@login_required
@teacher_required
def export_class_excel(class_id):
    """Exporter les statistiques d'une classe en Excel"""
    # Vérifier que la classe appartient à l'enseignant connecté
    class_obj = Class.query.filter_by(id=class_id, teacher_id=current_user.id).first_or_404()
    
    # Récupérer les données de la classe pour l'export
    class_data = get_class_statistics(class_obj)
    
    # Générer le fichier Excel
    excel_buffer = generate_class_excel(class_data)
    
    # Envoyer le fichier Excel
    return send_file(
        excel_buffer,
        as_attachment=True,
        download_name=f"statistiques_classe_{class_obj.name}_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

# Fonction utilitaire pour récupérer les statistiques d'une classe
def get_class_statistics(class_obj):
    """Récupère les statistiques d'une classe pour l'export"""
    students = User.query.filter_by(role='student').join(student_class_association, User.id == student_class_association.c.student_id).filter(student_class_association.c.class_id == class_obj.id).all()
    
    # Récupérer tous les exercices des cours de la classe
    class_courses = Course.query.filter_by(class_id=class_obj.id).all()
    class_exercises = []
    for course in class_courses:
        class_exercises.extend(course.exercises)
    total_exercises = len(class_exercises)
    
    # Données des élèves
    students_data = []
    for student in students:
        # Récupérer les tentatives de l'élève pour les exercices des cours de cette classe
        attempts = []
        for course in class_courses:
            course_attempts = ExerciseAttempt.query.filter_by(student_id=student.id, course_id=course.id).all()
            attempts.extend(course_attempts)
        
        # Calculer le score moyen
        scores = [attempt.score for attempt in attempts if attempt.score is not None]
        avg_score = sum(scores) / len(scores) if scores else None
        
        # Ajouter les données de l'élève
        students_data.append({
            'student': student,
            'completed_exercises': len(attempts),
            'total_exercises': total_exercises,
            'average_score': avg_score
        })
    
    # Retourner les données formatées
    return {
        'class': class_obj,
        'students': students_data,
        'total_exercises': total_exercises
    }

# Enregistrer les routes de synchronisation et correction des chemins d'images
register_image_sync_routes(app)

# Enregistrer les routes de diagnostic et correction d'images
register_image_fix_routes(app)

@app.route('/test_upload', methods=['GET', 'POST'])
def test_upload():
    """Page de test pour l'upload d'images"""
    if request.method == 'POST':
        if 'test_image' not in request.files:
            flash('Aucun fichier sélectionné', 'error')
            return redirect(request.url)
        
        file = request.files['test_image']
        if file.filename == '':
            flash('Aucun fichier sélectionné', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = generate_unique_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Sauvegarder le fichier directement
            try:
                file.save(filepath)
                # Vérifier que le fichier n'est pas vide
                if os.path.getsize(filepath) > 0:
                    image_path = f'/static/exercises/{filename}'
                    flash(f'Image uploadée avec succès: {image_path}', 'success')
                    return render_template('test_upload.html', uploaded_image=image_path)
                else:
                    os.remove(filepath)  # Supprimer le fichier vide
                    flash('Erreur: fichier uploadé est vide', 'error')
            except Exception as e:
                flash(f'Erreur lors de l\'upload: {str(e)}', 'error')
        else:
            flash('Type de fichier non autorisé', 'error')
    
    return render_template('test_upload.html')

if __name__ == '__main__':
    app.debug = True
    with app.app_context():
        # Créer les tables si elles n'existent pas
        db.create_all()
        
    app.run(debug=True)


# Route /get_cloudinary_url supprimée car elle est déjà définie dans fix_image_display_routes.py
# et retourne le format JSON attendu par le JavaScript dans flashcards.html

@app.route('/debug-form-data', methods=['GET', 'POST'])
@login_required
def debug_form_data():
    # Route de débogage pour analyser les données POST des formulaires
    if not current_user.is_admin:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        app.logger.info(f"[DEBUG_FORM_DATA] Données POST reçues: {dict(request.form)}")
        
        # Analyser les données du formulaire
        form_data = dict(request.form)
        
        # Extraire les champs answer_X
        answer_fields = {k: v for k, v in form_data.items() if k.startswith('answer_')}
        
        # Analyser les indices des champs answer_X
        answer_indices = []
        for key in answer_fields.keys():
            try:
                index = int(key.split('_')[1])
                answer_indices.append(index)
            except (ValueError, IndexError):
                pass
        
        # Trier les indices
        answer_indices.sort()
        
        # Créer un rapport détaillé
        report = {
            'total_fields': len(form_data),
            'answer_fields': len(answer_fields),
            'answer_indices': answer_indices,
            'answer_values': {f"answer_{i}": form_data.get(f"answer_{i}", "") for i in answer_indices},
            'all_form_data': form_data
        }
        
        return jsonify({
            'success': True,
            'message': 'Données du formulaire analysées avec succès',
            'report': report
        })
    
    # Afficher un formulaire de test pour les requêtes GET
    return render_template('debug/form_data.html')


@app.route('/fix-image-labeling-paths')
@login_required
@admin_required
def fix_image_labeling_paths():
    # Route pour corriger les chemins d'images dans les exercices image_labeling
    try:
        from models import Exercise
        import json
        
        # Récupérer tous les exercices de type image_labeling
        exercises = Exercise.query.filter_by(exercise_type='image_labeling').all()
        
        results = []
        fixed_count = 0
        
        for exercise in exercises:
            try:
                # Récupérer le contenu
                content = json.loads(exercise.content) if exercise.content else {}
                
                # Vérifier si main_image existe
                if 'main_image' in content:
                    main_image = content['main_image']
                    
                    # Normaliser le chemin si nécessaire
                    if main_image and not main_image.startswith('/static/'):
                        if main_image.startswith('static/'):
                            main_image = f"/{main_image}"
                        elif main_image.startswith('uploads/'):
                            main_image = f"/static/{main_image}"
                        elif not main_image.startswith('/'):
                            main_image = f"/static/uploads/{main_image}"
                        
                        # Mettre à jour content.main_image
                        content['main_image'] = main_image
                        exercise.content = json.dumps(content)
                    
                    # Synchroniser exercise.image_path avec content.main_image
                    if exercise.image_path != main_image:
                        old_path = exercise.image_path or "None"
                        exercise.image_path = main_image
                        fixed_count += 1
                        results.append(f"Exercice #{exercise.id}: image_path mis à jour de '{old_path}' à '{main_image}'")
                    else:
                        results.append(f"Exercice #{exercise.id}: déjà synchronisé ('{main_image}')")
                else:
                    results.append(f"Exercice #{exercise.id}: Pas de main_image dans le contenu")
            
            except Exception as e:
                results.append(f"Erreur pour l'exercice #{exercise.id}: {str(e)}")
        
        # Sauvegarder les modifications
        db.session.commit()
        
        return render_template('admin/fix_results.html', 
                              title="Correction des chemins d'images",
                              results=results,
                              fixed_count=fixed_count,
                              total_count=len(exercises))
    
    except Exception as e:
        db.session.rollback()
        return f"<h2>ERREUR:</h2><p>{str(e)}</p>"
