from flask import current_app
import os
import json
import re
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

def normalize_filename(filename):
    """
    Normalise un nom de fichier en remplaçant les caractères spéciaux
    comme le fait l'application lors de l'enregistrement en base de données
    
    Args:
        filename (str): Le nom de fichier à normaliser
        
    Returns:
        str: Le nom de fichier normalisé
    """
    if not filename:
        return filename
        
    # Remplacer les apostrophes et espaces par des underscores
    normalized = filename.replace("'", "_").replace(" ", "_")
    
    # Remplacer les caractères accentués
    normalized = normalized.replace("é", "e").replace("è", "e").replace("ê", "e").replace("ë", "e")
    normalized = normalized.replace("à", "a").replace("â", "a").replace("ä", "a")
    normalized = normalized.replace("î", "i").replace("ï", "i")
    normalized = normalized.replace("ô", "o").replace("ö", "o")
    normalized = normalized.replace("ù", "u").replace("û", "u").replace("ü", "u")
    normalized = normalized.replace("ç", "c")
    
    # Remplacer d'autres caractères spéciaux
    normalized = re.sub(r'[^a-zA-Z0-9_.-]', '_', normalized)
    
    return normalized

def normalize_image_path(path):
    """
    Normalise un chemin d'image pour garantir qu'il commence par /static/
    et pointe vers le bon répertoire tout en préservant la structure de dossiers intermédiaires.
    
    Args:
        path (str): Le chemin d'image à normaliser
        
    Returns:
        str: Le chemin normalisé
    """
    if not path:
        return path
        
    # Si le chemin est déjà une URL externe, le laisser tel quel
    if path.startswith(('http://', 'https://')):
        return path
    
    # Remplacer les backslashes par des slashes
    path = path.replace('\\', '/')
        
    # Extraire le nom du fichier et le normaliser
    filename = os.path.basename(path)
    normalized_filename = normalize_filename(filename)
    
    # Remplacer le nom du fichier dans le chemin
    if normalized_filename != filename:
        path = path.replace(filename, normalized_filename)
    
    # Préserver la structure de dossiers intermédiaires
    path_parts = path.split('/')
    
    # Assurer que le chemin commence par /static/
    if not path.startswith('/static/'):
        if path.startswith('static/'):
            path = f'/{path}'
        elif path.startswith('uploads/'):
            # Préserver la structure après 'uploads/'
            path = f'/static/{path}'
        else:
            # Si c'est juste un nom de fichier, le mettre dans uploads
            if len(path_parts) == 1:
                path = f'/static/uploads/{normalized_filename}'
            else:
                # Préserver la structure existante
                path = f'/static/{path}'
    
    # Nettoyer les chemins dupliqués
    duplicates = [
        ('/static/uploads/static/uploads/', '/static/uploads/'),
        ('static/uploads/static/uploads/', '/static/uploads/'),
        ('/static/exercises/static/exercises/', '/static/exercises/'),
        ('static/exercises/static/exercises/', '/static/exercises/'),
        ('/static/uploads/uploads/', '/static/uploads/'),
        ('static/uploads/uploads/', '/static/uploads/'),
        ('/static/exercises/exercises/', '/static/exercises/'),
        ('static/exercises/exercises/', '/static/exercises/')
    ]
    
    for duplicate, replacement in duplicates:
        if duplicate in path:
            path = path.replace(duplicate, replacement)
    
    return path

def clean_duplicated_path_segments(path):
    """
    Nettoie les segments dupliqués dans un chemin d'image
    comme /static/uploads/static/uploads/ -> /static/uploads/
    
    Args:
        path (str): Le chemin d'image à nettoyer
        
    Returns:
        str: Le chemin nettoyé sans segments dupliqués
    """
    if not path:
        return path
        
    # Si le chemin est déjà une URL externe, le laisser tel quel
    if path.startswith(('http://', 'https://')):
        return path
    
    # Définir les motifs de duplication à nettoyer
    duplicates = [
        ('/static/uploads/static/uploads/', '/static/uploads/'),
        ('static/uploads/static/uploads/', '/static/uploads/'),
        ('/static/exercises/static/exercises/', '/static/exercises/'),
        ('static/exercises/static/exercises/', '/static/exercises/'),
        ('/static/uploads/uploads/', '/static/uploads/'),
        ('static/uploads/uploads/', '/static/uploads/'),
        ('/static/exercises/exercises/', '/static/exercises/'),
        ('static/exercises/exercises/', '/static/exercises/')
    ]
    
    # Nettoyer les chemins dupliqués
    cleaned_path = path
    for duplicate, replacement in duplicates:
        if duplicate in cleaned_path:
            cleaned_path = cleaned_path.replace(duplicate, replacement)
    
    return cleaned_path

def fix_exercise_image_path(exercise):
    """
    Corrige le chemin d'image d'un exercice en normalisant à la fois
    exercise.image_path et content.image.
    
    Args:
        exercise: L'objet Exercise à corriger
        
    Returns:
        bool: True si des modifications ont été apportées, False sinon
    """
    modified = False
    
    try:
        # Normaliser exercise.image_path
        if exercise.image_path:
            normalized_path = normalize_image_path(exercise.image_path)
            if normalized_path != exercise.image_path:
                exercise.image_path = normalized_path
                modified = True
                current_app.logger.info(f"Normalized exercise.image_path: {normalized_path}")
        
        # Normaliser content.image
        if exercise.content:
            content = json.loads(exercise.content)
            if 'image' in content and content['image']:
                normalized_content_path = normalize_image_path(content['image'])
                if normalized_content_path != content['image']:
                    content['image'] = normalized_content_path
                    exercise.content = json.dumps(content)
                    modified = True
                    current_app.logger.info(f"Normalized content.image: {normalized_content_path}")
            
            # Synchroniser content.image et exercise.image_path
            if 'image' in content and exercise.image_path and content['image'] != exercise.image_path:
                # Privilégier content.image car c'est ce qui est utilisé dans les templates
                exercise.image_path = content['image']
                modified = True
                current_app.logger.info(f"Synchronized paths: {content['image']}")
    
    except Exception as e:
        current_app.logger.error(f"Error fixing image path for exercise {exercise.id}: {str(e)}")
    
    return modified

def find_image_file(path):
    """
    Cherche un fichier image dans différents répertoires
    
    Args:
        path (str): Le chemin d'image à chercher
        
    Returns:
        str: Le chemin trouvé ou None si aucun fichier n'est trouvé
    """
    if not path:
        return None
    
    # Extraire le nom du fichier
    filename = os.path.basename(path)
    
    # Essayer avec le nom normalisé également
    normalized_filename = normalize_filename(filename)
    
    # Chemins possibles
    possible_paths = [
        os.path.join(current_app.root_path, "static", "uploads", filename),
        os.path.join(current_app.root_path, "static", "uploads", "exercises", filename),
        os.path.join(current_app.root_path, "static", "uploads", "exercises", "qcm", filename),
        os.path.join(current_app.root_path, "static", "uploads", "exercises", "flashcards", filename),
        os.path.join(current_app.root_path, "static", "uploads", "exercises", "word_placement", filename),
        os.path.join(current_app.root_path, "static", "uploads", "exercises", "image_labeling", filename),
        os.path.join(current_app.root_path, "static", "uploads", "exercises", "legend", filename),
        os.path.join(current_app.root_path, "static", "exercises", filename),
        os.path.join(current_app.root_path, "static", "exercises", "qcm", filename),
        os.path.join(current_app.root_path, "static", "exercises", "flashcards", filename),
        os.path.join(current_app.root_path, "static", "exercises", "word_placement", filename),
        os.path.join(current_app.root_path, "static", "exercises", "image_labeling", filename),
        os.path.join(current_app.root_path, "static", "exercises", "legend", filename)
    ]
    
    # Chercher le fichier avec le nom original
    for possible_path in possible_paths:
        if os.path.exists(possible_path):
            # Normaliser le chemin pour le web
            web_path = f"/{os.path.relpath(possible_path, current_app.root_path).replace('\\', '/')}"
            return web_path
    
    # Si non trouvé, essayer avec le nom normalisé
    normalized_possible_paths = [
        p.replace(filename, normalized_filename) for p in possible_paths
    ]
    
    # Chercher le fichier avec le nom normalisé
    for possible_path in normalized_possible_paths:
        if os.path.exists(possible_path):
            # Normaliser le chemin pour le web
            web_path = f"/{os.path.relpath(possible_path, current_app.root_path).replace('\\', '/')}"
            return web_path
    
    return None

def get_image_url(path):
    """
    Retourne une URL valide pour un chemin d'image, en gérant les
    chemins /static/exercises/ et /static/uploads/ et les problèmes de caractères spéciaux
    
    Args:
        path (str): Le chemin d'image à convertir
        
    Returns:
        str: L'URL de l'image
    """
    if not path:
        return None
        
    # Si c'est déjà une URL externe, la retourner telle quelle
    if path.startswith(('http://', 'https://')):
        return path
    
    # Normaliser le chemin
    normalized_path = normalize_image_path(path)
    
    # Vérifier si le fichier existe dans le chemin normalisé
    physical_path = os.path.join(current_app.root_path, normalized_path.lstrip('/'))
    if os.path.exists(physical_path):
        current_app.logger.debug(f"Image trouvée avec le chemin normalisé: {normalized_path}")
        return normalized_path
    
    # Extraire le nom du fichier et essayer avec le nom non normalisé
    filename = os.path.basename(normalized_path)
    original_filename = os.path.basename(path)
    if filename != original_filename:
        # Essayer avec le nom original
        original_path = normalized_path.replace(filename, original_filename)
        physical_original_path = os.path.join(current_app.root_path, original_path.lstrip('/'))
        if os.path.exists(physical_original_path):
            current_app.logger.debug(f"Image trouvée avec le nom original: {original_path}")
            return original_path
    
    # Si le fichier n'existe pas dans le chemin normalisé, essayer l'autre format
    if '/static/uploads/' in normalized_path:
        # Essayer avec /static/exercises/
        alt_path = normalized_path.replace('/static/uploads/', '/static/exercises/')
        physical_alt_path = os.path.join(current_app.root_path, alt_path.lstrip('/'))
        if os.path.exists(physical_alt_path):
            current_app.logger.debug(f"Image trouvée dans le répertoire exercises: {alt_path}")
            return alt_path
    elif '/static/exercises/' in normalized_path:
        # Essayer avec /static/uploads/
        alt_path = normalized_path.replace('/static/exercises/', '/static/uploads/')
        physical_alt_path = os.path.join(current_app.root_path, alt_path.lstrip('/'))
        if os.path.exists(physical_alt_path):
            current_app.logger.debug(f"Image trouvée dans le répertoire uploads: {alt_path}")
            return alt_path
    
    # Essayer de trouver le fichier dans différents répertoires
    found_path = find_image_file(path)
    if found_path:
        current_app.logger.debug(f"Image trouvée par recherche approfondie: {found_path}")
        return found_path
    
    # Si aucun fichier n'existe, retourner le chemin normalisé
    current_app.logger.warning(f"Image non trouvée, retour du chemin normalisé: {normalized_path}")
    return normalized_path

def normalize_pairs_exercise_content(content, exercise_type='pairs'):
    """
    Normalise les chemins d'images dans le contenu JSON des exercices de type pairs.
    
    Args:
        content (dict): Le contenu JSON de l'exercice
        exercise_type (str): Le type d'exercice (par défaut 'pairs')
        
    Returns:
        dict: Le contenu JSON avec les chemins d'images normalisés
    """
    if not content or not isinstance(content, dict):
        return content
        
    if 'pairs' not in content:
        return content
        
    normalized_pairs = []
    
    for pair in content['pairs']:
        normalized_pair = pair.copy()
        
        # Normaliser le contenu gauche s'il s'agit d'une image
        if pair.get('left', {}).get('type') == 'image':
            left_content = pair['left']['content']
            if left_content:
                normalized_left = normalize_image_path(left_content, exercise_type)
                normalized_pair['left']['content'] = normalized_left
                current_app.logger.info(f'[PAIRS_NORMALIZE] Image gauche normalisée: {left_content} -> {normalized_left}')
        
        # Normaliser le contenu droit s'il s'agit d'une image
        if pair.get('right', {}).get('type') == 'image':
            right_content = pair['right']['content']
            if right_content:
                normalized_right = normalize_image_path(right_content, exercise_type)
                normalized_pair['right']['content'] = normalized_right
                current_app.logger.info(f'[PAIRS_NORMALIZE] Image droite normalisée: {right_content} -> {normalized_right}')
        
        normalized_pairs.append(normalized_pair)
    
    # Mettre à jour le contenu avec les paires normalisées
    normalized_content = content.copy()
    normalized_content['pairs'] = normalized_pairs
    
    return normalized_content

def normalize_qcm_multichoix_image_path(path):
    """
    Normalise spécifiquement les chemins d'images pour les exercices QCM Multichoix.
    Gère les cas particuliers comme les images dans le dossier 'general'.
    
    Args:
        path (str): Le chemin d'image à normaliser
        
    Returns:
        str: Le chemin normalisé pour QCM Multichoix
    """
    if not path:
        return path
        
    # Si le chemin est déjà une URL externe, le laisser tel quel
    if path.startswith(('http://', 'https://')):
        return path
    
    # Normaliser d'abord avec la fonction standard
    normalized_path = normalize_image_path(path)
    
    # Extraire le nom du fichier
    filename = os.path.basename(normalized_path)
    
    # Vérifier si le fichier existe dans le chemin normalisé
    physical_path = os.path.join(current_app.root_path, normalized_path.lstrip('/'))
    if os.path.exists(physical_path):
        current_app.logger.debug(f"Image QCM Multichoix trouvée avec le chemin normalisé: {normalized_path}")
        return normalized_path
    
    # Vérifier si l'image existe dans le dossier 'general'
    general_path = f"/static/exercises/general/{filename}"
    physical_general_path = os.path.join(current_app.root_path, general_path.lstrip('/'))
    if os.path.exists(physical_general_path):
        current_app.logger.info(f"Image QCM Multichoix trouvée dans le dossier 'general': {general_path}")
        return general_path
    
    # Vérifier si l'image existe dans le dossier 'qcm_multichoix'
    qcm_path = f"/static/uploads/qcm_multichoix/{filename}"
    physical_qcm_path = os.path.join(current_app.root_path, qcm_path.lstrip('/'))
    
    # Si le dossier n'existe pas, le créer
    qcm_dir = os.path.dirname(physical_qcm_path)
    if not os.path.exists(qcm_dir):
        try:
            os.makedirs(qcm_dir)
            current_app.logger.info(f"Répertoire créé: {qcm_dir}")
        except Exception as e:
            current_app.logger.error(f"Erreur lors de la création du répertoire {qcm_dir}: {str(e)}")
    
    # Chercher l'image dans d'autres répertoires et la copier si trouvée
    possible_paths = [
        os.path.join(current_app.root_path, "static", "uploads", filename),
        os.path.join(current_app.root_path, "static", "exercises", filename),
        os.path.join(current_app.root_path, "static", "exercises", "general", filename),
        os.path.join(current_app.root_path, "static", "exercises", "qcm", filename),
        os.path.join(current_app.root_path, "static", "uploads", "qcm", filename)
    ]
    
    for possible_path in possible_paths:
        if os.path.exists(possible_path):
            try:
                import shutil
                shutil.copy2(possible_path, physical_qcm_path)
                current_app.logger.info(f"Image copiée de {possible_path} vers {physical_qcm_path}")
                return qcm_path
            except Exception as e:
                current_app.logger.error(f"Erreur lors de la copie de l'image: {str(e)}")
                break
    
    # Si l'image n'a pas été trouvée, retourner le chemin normalisé
    current_app.logger.warning(f"Image QCM Multichoix non trouvée, retour du chemin normalisé: {normalized_path}")
    return normalized_path

def normalize_qcm_multichoix_content(content):
    """
    Normalise les chemins d'images dans le contenu JSON des exercices de type QCM Multichoix.
    
    Args:
        content (dict): Le contenu JSON de l'exercice
        
    Returns:
        dict: Le contenu JSON avec les chemins d'images normalisés
    """
    if not content or not isinstance(content, dict):
        return content
    
    # Normaliser l'image principale si elle existe
    if 'image' in content and content['image']:
        normalized_image = normalize_qcm_multichoix_image_path(content['image'])
        if normalized_image != content['image']:
            content['image'] = normalized_image
            current_app.logger.info(f'[QCM_MULTICHOIX] Image principale normalisée: {content["image"]} -> {normalized_image}')
    
    # Normaliser les images dans les questions si elles existent
    if 'questions' in content and isinstance(content['questions'], list):
        for i, question in enumerate(content['questions']):
            if 'image' in question and question['image']:
                normalized_image = normalize_qcm_multichoix_image_path(question['image'])
                if normalized_image != question['image']:
                    question['image'] = normalized_image
                    current_app.logger.info(f'[QCM_MULTICHOIX] Image de question {i} normalisée: {question["image"]} -> {normalized_image}')
    
    return content
