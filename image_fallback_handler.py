"""
Module pour gérer les images manquantes et fournir des images de remplacement
"""

import os
import logging
from flask import current_app

# Configuration du logger
logger = logging.getLogger(__name__)

class ImageFallbackHandler:
    """
    Gestionnaire pour les images manquantes
    """
    
    # Chemin de l'image par défaut
    DEFAULT_IMAGE_PATH = "/static/images/placeholder-image.png"
    
    @staticmethod
    def ensure_default_image_exists():
        """
        S'assure que l'image par défaut existe, la crée si nécessaire
        
        Returns:
            bool: True si l'image existe ou a été créée, False sinon
        """
        # Chemin physique de l'image par défaut
        static_folder = current_app.static_folder
        default_image_dir = os.path.join(static_folder, "images")
        default_image_path = os.path.join(default_image_dir, "placeholder-image.png")
        
        # Vérifier si le dossier existe
        if not os.path.exists(default_image_dir):
            try:
                os.makedirs(default_image_dir)
                logger.info(f"Dossier créé pour l'image par défaut: {default_image_dir}")
            except Exception as e:
                logger.error(f"Erreur lors de la création du dossier pour l'image par défaut: {str(e)}")
                return False
        
        # Vérifier si l'image existe
        if not os.path.exists(default_image_path):
            try:
                # Créer une image par défaut simple (un carré gris avec un texte)
                from PIL import Image, ImageDraw, ImageFont
                
                # Créer une image 200x200 grise
                img = Image.new('RGB', (200, 200), color=(240, 240, 240))
                d = ImageDraw.Draw(img)
                
                # Ajouter un texte
                try:
                    # Essayer de charger une police
                    font = ImageFont.truetype("arial.ttf", 16)
                except:
                    # Utiliser la police par défaut si arial n'est pas disponible
                    font = ImageFont.load_default()
                
                d.text((40, 90), "Image non disponible", fill=(100, 100, 100), font=font)
                
                # Sauvegarder l'image
                img.save(default_image_path)
                logger.info(f"Image par défaut créée: {default_image_path}")
                return True
            except Exception as e:
                logger.error(f"Erreur lors de la création de l'image par défaut: {str(e)}")
                return False
        
        return True
    
    @staticmethod
    def get_fallback_image_url(original_path=None, exercise_type=None):
        """
        Retourne l'URL de l'image par défaut
        
        Args:
            original_path (str, optional): Chemin original de l'image manquante
            exercise_type (str, optional): Type d'exercice
            
        Returns:
            str: URL de l'image par défaut
        """
        # S'assurer que l'image par défaut existe
        ImageFallbackHandler.ensure_default_image_exists()
        
        # Loguer l'utilisation de l'image par défaut
        if original_path:
            logger.warning(f"Utilisation de l'image par défaut pour: {original_path} (type: {exercise_type})")
        
        return ImageFallbackHandler.DEFAULT_IMAGE_PATH
    
    @staticmethod
    def image_exists(image_path):
        """
        Vérifie si une image existe physiquement
        
        Args:
            image_path (str): Chemin de l'image à vérifier
            
        Returns:
            bool: True si l'image existe, False sinon
        """
        if not image_path:
            return False
            
        # Si c'est une URL externe, on considère qu'elle existe
        if image_path.startswith(('http://', 'https://')):
            return True
            
        # Convertir le chemin web en chemin physique
        if image_path.startswith('/static/'):
            physical_path = os.path.join(current_app.static_folder, image_path[8:])
            return os.path.isfile(physical_path)
            
        return False
        
    @staticmethod
    def find_image_in_alternative_paths(image_path, exercise_type=None):
        """
        Recherche une image dans les chemins alternatifs possibles
        
        Args:
            image_path (str): Chemin de l'image à rechercher
            exercise_type (str, optional): Type d'exercice
            
        Returns:
            str: Chemin de l'image si trouvée, None sinon
        """
        if not image_path or not exercise_type:
            return None
            
        # Extraire le nom du fichier
        filename = os.path.basename(image_path)
        
        # Liste des chemins alternatifs possibles
        alternative_paths = [
            f"/static/{exercise_type}/{filename}",
            f"/static/uploads/{exercise_type}/{filename}",
            f"/static/exercises/{exercise_type}/{filename}",
            f"/static/exercise-images/{exercise_type}/{filename}",
            f"/static/exercise_images/{exercise_type}/{filename}",
            f"/static/uploads/exercises/{exercise_type}/{filename}",  # Ajout du chemin manquant
            # Chemins spécifiques pour certains types d'exercices
            f"/static/uploads/general/{filename}",
            f"/static/uploads/general/{exercise_type}_{filename}",
            f"/static/uploads/{filename}",
            # Ajout du chemin sans le type d'exercice pour les images stockées à la racine
            f"/static/uploads/{filename.replace(f'{exercise_type}_', '')}",
            # Ajout du chemin spécifique pour les images QCM
            f"/static/uploads/qcm/{filename}"
        ]
        
        # Ajout de chemins spécifiques pour les types d'exercices connus
        if exercise_type in ['qcm', 'fill_in_blanks', 'word_placement', 'image_labeling', 'legend', 'flashcards']:
            alternative_paths.extend([
                f"/static/{exercise_type.replace('_', '-')}/{filename}",
                f"/static/uploads/{exercise_type.replace('_', '-')}/{filename}",
                f"/static/exercises/{exercise_type.replace('_', '-')}/{filename}"
            ])
        
        # Vérifier chaque chemin alternatif
        for alt_path in alternative_paths:
            if ImageFallbackHandler.image_exists(alt_path):
                logger.info(f"Image trouvée dans un chemin alternatif: {alt_path} (original: {image_path})")
                return alt_path
                
        return None
