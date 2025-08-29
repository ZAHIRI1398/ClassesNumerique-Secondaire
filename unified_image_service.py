"""
Service unifié pour la gestion des chemins d'images dans l'application
Ce module centralise toutes les fonctionnalités liées à la gestion des chemins d'images
pour assurer une cohérence dans toute l'application.
"""

import os
import re
import logging
from urllib.parse import urlparse
from flask import current_app
from utils.image_path_manager import ImagePathManager
from image_fallback_handler import ImageFallbackHandler

# Configuration du logger
logger = logging.getLogger(__name__)

class UnifiedImageService:
    """
    Service unifié pour la gestion des chemins d'images
    """
    
    @staticmethod
    def get_image_url(image_path, exercise_type=None):
        """
        Obtient l'URL d'une image en tenant compte du type d'exercice
        
        Args:
            image_path (str): Chemin de l'image
            exercise_type (str, optional): Type d'exercice
            
        Returns:
            str: URL de l'image
        """
        if not image_path:
            logger.warning("Chemin d'image vide, utilisation de l'image par défaut")
            return ImageFallbackHandler.get_fallback_image_url(image_path, exercise_type)
            
        # Nettoyer le chemin d'image
        clean_path = ImagePathManager.clean_duplicate_paths(image_path)
        
        # Vérifier si c'est une URL Cloudinary
        if 'cloudinary.com' in clean_path or clean_path.startswith(('http://', 'https://')) and 'localhost' not in clean_path:
            return clean_path
            
        # Normaliser le chemin d'image
        normalized_path = UnifiedImageService.normalize_image_path(clean_path, exercise_type)
        
        # Générer le chemin web final
        web_path = ImagePathManager.get_web_path(normalized_path, exercise_type)
        
        # Vérifier si l'image existe physiquement
        try:
            if not ImageFallbackHandler.image_exists(web_path):
                # Essayer de trouver l'image dans des chemins alternatifs
                alternative_path = ImageFallbackHandler.find_image_in_alternative_paths(web_path, exercise_type)
                if alternative_path:
                    logger.info(f"Image trouvée dans un chemin alternatif: {alternative_path}")
                    return alternative_path
                    
                logger.warning(f"Image non trouvée: {web_path}, utilisation de l'image par défaut")
                return ImageFallbackHandler.get_fallback_image_url(web_path, exercise_type)
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de l'existence de l'image: {str(e)}")
            # En cas d'erreur, utiliser l'image par défaut
            return ImageFallbackHandler.get_fallback_image_url(web_path, exercise_type)
        
        return web_path
    
    @staticmethod
    def normalize_image_path(path, exercise_type=None):
        """
        Normalise le chemin d'image pour assurer un format cohérent
        
        Args:
            path (str): Le chemin d'image à normaliser
            exercise_type (str, optional): Type d'exercice pour organiser les images
            
        Returns:
            str: Le chemin normalisé
        """
        if not path:
            return path
            
        # Nettoyer les chemins dupliqués
        path = ImagePathManager.clean_duplicate_paths(path)
        
        # Extraire le nom de fichier
        filename = os.path.basename(path)
        
        # Normaliser le nom du fichier (remplacer les espaces par des underscores, supprimer les apostrophes)
        normalized_filename = filename.replace(' ', '_').replace("'", '')
        
        # Construire le chemin normalisé avec le type d'exercice si fourni
        if exercise_type:
            # Vérifier si le chemin contient déjà le type d'exercice
            if exercise_type in path:
                # Le chemin contient déjà le type d'exercice, juste normaliser le nom de fichier
                directory = os.path.dirname(path)
                return os.path.join(directory, normalized_filename).replace('\\', '/')
            else:
                # Ajouter le type d'exercice au chemin
                return f"/static/uploads/{exercise_type}/{normalized_filename}"
        else:
            # Sans type d'exercice, juste normaliser le nom de fichier
            directory = os.path.dirname(path)
            if directory:
                return os.path.join(directory, normalized_filename).replace('\\', '/')
            else:
                return normalized_filename
    
    @staticmethod
    def migrate_image_path(old_path, exercise_type):
        """
        Migre un ancien chemin d'image vers le nouveau format standardisé
        
        Args:
            old_path (str): Ancien chemin d'image
            exercise_type (str): Type d'exercice
            
        Returns:
            str: Nouveau chemin d'image normalisé
        """
        if not old_path:
            return None
            
        # Nettoyer les chemins dupliqués
        clean_path = ImagePathManager.clean_duplicate_paths(old_path)
        
        # Extraire le nom de fichier
        filename = os.path.basename(clean_path)
        
        # Normaliser le nom du fichier
        normalized_filename = filename.replace(' ', '_').replace("'", '')
        
        # Construire le nouveau chemin
        new_path = f"/static/uploads/{exercise_type}/{normalized_filename}"
        
        return new_path

# Créer une instance du service pour l'utilisation globale
image_service = UnifiedImageService()

# Fonction de compatibilité pour l'ancienne API
def get_cloudinary_url(image_path, exercise_type=None):
    """
    Fonction de compatibilité pour maintenir la rétrocompatibilité avec le code existant
    
    Args:
        image_path (str): Chemin de l'image
        exercise_type (str, optional): Type d'exercice
        
    Returns:
        str: URL de l'image
    """
    return image_service.get_image_url(image_path, exercise_type)
