"""
Image Path Manager - Système de gestion des chemins d'images propre et cohérent
"""

import os
import uuid
from datetime import datetime
from .image_utils import normalize_image_path

class ImagePathManager:
    """Gestionnaire centralisé pour les chemins d'images"""
    
    # Mapping des types d'exercices vers leurs dossiers
    EXERCISE_TYPE_FOLDERS = {
        'qcm': 'qcm',
        'fill_in_blanks': 'fill_in_blanks',
        'flashcards': 'flashcards',
        'pairs': 'pairs',
        'image_labeling': 'image_labeling',
        'legend': 'legend',
        'word_placement': 'word_placement',
        'drag_and_drop': 'drag_and_drop'
    }
    
    BASE_UPLOAD_DIR = 'static/exercises'
    
    @classmethod
    def get_upload_folder(cls, exercise_type=None):
        """
        Retourne le dossier d'upload pour un type d'exercice
        
        Args:
            exercise_type (str): Type d'exercice
            
        Returns:
            str: Chemin du dossier d'upload
        """
        if exercise_type and exercise_type in cls.EXERCISE_TYPE_FOLDERS:
            return f"{cls.BASE_UPLOAD_DIR}/{cls.EXERCISE_TYPE_FOLDERS[exercise_type]}"
        else:
            return f"{cls.BASE_UPLOAD_DIR}/general"
    
    @classmethod
    def generate_unique_filename(cls, original_filename, exercise_type=None):
        """
        Génère un nom de fichier unique avec préfixe du type d'exercice
        
        Args:
            original_filename (str): Nom de fichier original
            exercise_type (str): Type d'exercice
            
        Returns:
            str: Nom de fichier unique
        """
        # Normaliser le nom de fichier original
        normalized_filename = normalize_image_path(original_filename)
        name, ext = os.path.splitext(normalized_filename)
        
        # Générer timestamp et UUID court
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        short_uuid = str(uuid.uuid4())[:8]
        
        # Préfixe basé sur le type d'exercice
        prefix = exercise_type if exercise_type in cls.EXERCISE_TYPE_FOLDERS else 'general'
        
        return f"{prefix}_{timestamp}_{short_uuid}{ext}"
    
    @classmethod
    def get_full_upload_path(cls, filename, exercise_type=None):
        """
        Retourne le chemin complet d'upload pour un fichier
        
        Args:
            filename (str): Nom du fichier
            exercise_type (str): Type d'exercice
            
        Returns:
            str: Chemin complet d'upload
        """
        folder = cls.get_upload_folder(exercise_type)
        return f"{folder}/{filename}"
    
    @classmethod
    def get_web_path(cls, filename, exercise_type=None):
        """
        Retourne le chemin web pour affichage dans les templates
        
        Args:
            filename (str): Nom du fichier
            exercise_type (str): Type d'exercice
            
        Returns:
            str: Chemin web avec /static/uploads/
        """
        if not filename:
            return None
            
        # Si c'est déjà un chemin complet, le retourner tel quel
        if filename.startswith('/static/exercises/') or filename.startswith('/static/uploads/') or filename.startswith('http'):
            return filename
            
        # Construire le chemin web
        folder = cls.get_upload_folder(exercise_type)
        return f"/{folder}/{filename}"
    
    @classmethod
    def extract_filename_from_path(cls, image_path):
        """
        Extrait le nom de fichier d'un chemin d'image
        
        Args:
            image_path (str): Chemin d'image complet
            
        Returns:
            str: Nom de fichier seulement
        """
        if not image_path:
            return None
            
        # Pour les URLs externes, retourner tel quel
        if image_path.startswith('http'):
            return image_path
            
        # Extraire le nom de fichier
        return os.path.basename(image_path)
    
    @classmethod
    def clean_duplicate_paths(cls, image_path):
        """
        Nettoie les chemins dupliqués comme /static/uploads/static/uploads/
        
        Args:
            image_path (str): Chemin d'image à nettoyer
            
        Returns:
            str: Chemin nettoyé
        """
        if not image_path:
            return None
            
        # Gérer les duplications de /static/uploads/ et /static/exercises/
        if '/static/uploads/static/uploads/' in image_path:
            filename = image_path.split('/static/uploads/static/uploads/')[-1]
            return f"/static/exercises/{filename}"
        elif '/static/exercises/static/exercises/' in image_path:
            filename = image_path.split('/static/exercises/static/exercises/')[-1]
            return f"/static/exercises/{filename}"
        elif image_path.count('/static/uploads/') > 1:
            parts = image_path.split('/static/uploads/')
            filename = parts[-1]  # Prendre la dernière partie
            return f"/static/exercises/{filename}"
        elif image_path.count('/static/exercises/') > 1:
            parts = image_path.split('/static/exercises/')
            filename = parts[-1]  # Prendre la dernière partie
            return f"/static/exercises/{filename}"
            
        return image_path
    
    @classmethod
    def ensure_directory_exists(cls, exercise_type=None):
        """
        S'assure que le répertoire d'upload existe
        
        Args:
            exercise_type (str): Type d'exercice
            
        Returns:
            str: Chemin du répertoire créé
        """
        folder_path = cls.get_upload_folder(exercise_type)
        os.makedirs(folder_path, exist_ok=True)
        
        # Créer un fichier .gitkeep si nécessaire
        gitkeep_path = os.path.join(folder_path, '.gitkeep')
        if not os.path.exists(gitkeep_path):
            with open(gitkeep_path, 'w') as f:
                f.write('')
        
        return folder_path


def get_image_display_path(exercise, content=None):
    """
    Fonction utilitaire pour obtenir le chemin d'affichage d'une image d'exercice
    Compatible avec les anciens et nouveaux systèmes
    
    Args:
        exercise: Objet exercice avec potentiellement image_path
        content: Contenu JSON de l'exercice (optionnel)
        
    Returns:
        str: Chemin d'image pour affichage ou None
    """
    # Priorité 1: exercise.image_path (nouveau système)
    if hasattr(exercise, 'image_path') and exercise.image_path:
        return ImagePathManager.clean_duplicate_paths(exercise.image_path)
    
    # Priorité 2: content.image (ancien système)
    if content and isinstance(content, dict):
        if 'image' in content and content['image']:
            return ImagePathManager.clean_duplicate_paths(content['image'])
        if 'main_image' in content and content['main_image']:
            return ImagePathManager.clean_duplicate_paths(content['main_image'])
    
    # Priorité 3: Si content est une chaîne JSON, la parser
    if content and isinstance(content, str):
        try:
            import json
            parsed_content = json.loads(content)
            return get_image_display_path(exercise, parsed_content)
        except (json.JSONDecodeError, TypeError):
            pass
    
    return None


def migrate_image_path(old_path, exercise_type=None):
    """
    Migre un ancien chemin d'image vers le nouveau système
    
    Args:
        old_path (str): Ancien chemin d'image
        exercise_type (str): Type d'exercice
        
    Returns:
        str: Nouveau chemin d'image
    """
    if not old_path:
        return None
        
    # Si c'est déjà une URL externe, la garder
    if old_path.startswith('http'):
        return old_path
        
    # Nettoyer les duplications
    cleaned_path = ImagePathManager.clean_duplicate_paths(old_path)
    
    # Extraire le nom de fichier
    filename = ImagePathManager.extract_filename_from_path(cleaned_path)
    
    # Retourner le nouveau chemin web
    return ImagePathManager.get_web_path(filename, exercise_type)
