"""
Service autonome pour la gestion des URLs d'images
Remplace la fonction get_cloudinary_url du module cloud_storage
"""

import os
import logging
import re
from flask import current_app

class ImageUrlService:
    """
    Service pour la gestion des URLs d'images
    """
    
    @staticmethod
    def normalize_path(path):
        """
        Normalise un chemin d'image en remplaçant les backslashes par des slashes
        """
        if not path:
            return None
        return path.replace('\\', '/')
    
    @staticmethod
    def clean_duplicate_paths(path):
        """
        Nettoie les chemins dupliqués comme /static/uploads/static/uploads/
        """
        if not path:
            return path
            
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
        
        cleaned_path = path
        for duplicate, replacement in duplicates:
            if duplicate in cleaned_path:
                cleaned_path = cleaned_path.replace(duplicate, replacement)
                
        return cleaned_path
    
    @staticmethod
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
    
    @staticmethod
    def extract_filename(path):
        """
        Extrait le nom de fichier d'un chemin
        """
        if not path:
            return None
        return os.path.basename(path)
    
    @staticmethod
    def get_image_url(image_path):
        """
        Retourne une URL valide pour une image, en vérifiant que le fichier existe
        et en gérant les problèmes de caractères spéciaux dans les noms de fichiers
        
        Args:
            image_path: Le chemin de l'image
            
        Returns:
            L'URL de l'image
        """
        logger = logging.getLogger('image_url_service')
        
        if not image_path:
            logger.warning("get_image_url appelée avec un chemin vide")
            return None
        
        # Vérifier le type de chemin d'image
        if not isinstance(image_path, str):
            logger.warning(f"Type de chemin d'image non valide: {type(image_path)}")
            return None
        
        logger.debug(f"get_image_url appelée avec image_path={image_path}")
        
        # Si c'est déjà une URL externe, la retourner telle quelle
        if image_path.startswith('http'):
            logger.debug(f"URL externe détectée: {image_path}")
            return image_path
        
        # Nettoyer les chemins dupliqués
        cleaned_path = ImageUrlService.clean_duplicate_paths(image_path)
        if cleaned_path != image_path:
            logger.debug(f"Chemin nettoyé: {cleaned_path} (original: {image_path})")
            image_path = cleaned_path
        
        # Extraire le nom de fichier
        filename = ImageUrlService.extract_filename(image_path)
        logger.debug(f"Nom de fichier extrait: {filename}")
        
        # Normaliser le nom de fichier pour gérer les caractères spéciaux
        normalized_filename = ImageUrlService.normalize_filename(filename)
        if normalized_filename != filename:
            logger.debug(f"Nom de fichier normalisé: {normalized_filename} (original: {filename})")
            # Créer un chemin avec le nom de fichier normalisé
            normalized_filename_path = image_path.replace(filename, normalized_filename)
            logger.debug(f"Chemin avec nom de fichier normalisé: {normalized_filename_path}")
        else:
            normalized_filename_path = image_path
        
        # Vérifier si le fichier existe directement avec le chemin original
        direct_path = image_path
        if direct_path.startswith('/'):
            direct_path = direct_path[1:]
        direct_exists = os.path.exists(direct_path)
        logger.debug(f"Le fichier existe directement avec le chemin original: {direct_exists}")
        
        # Vérifier si le fichier existe avec le chemin normalisé (nom de fichier normalisé)
        normalized_direct_path = normalized_filename_path
        if normalized_direct_path.startswith('/'):
            normalized_direct_path = normalized_direct_path[1:]
        normalized_direct_exists = os.path.exists(normalized_direct_path)
        logger.debug(f"Le fichier existe avec le nom normalisé: {normalized_direct_exists}")
        
        # Si le fichier existe avec le chemin original, l'utiliser
        if direct_exists:
            normalized_path = ImageUrlService.normalize_path(image_path if image_path.startswith('/') else f"/{image_path}")
            logger.debug(f"Retour du chemin original: {normalized_path}")
            return normalized_path
        
        # Si le fichier existe avec le nom normalisé, l'utiliser
        if normalized_direct_exists:
            normalized_path = ImageUrlService.normalize_path(normalized_filename_path if normalized_filename_path.startswith('/') else f"/{normalized_filename_path}")
            logger.debug(f"Retour du chemin avec nom normalisé: {normalized_path}")
            return normalized_path
        
        # Si le chemin commence par /static/ ou static/, normaliser et vérifier
        if image_path.startswith('/static/') or image_path.startswith('static/'):
            normalized_path = ImageUrlService.normalize_path(image_path if image_path.startswith('/') else f"/{image_path}")
            
            # Vérifier si le fichier existe avec ce chemin normalisé
            normalized_exists = os.path.exists(normalized_path[1:] if normalized_path.startswith('/') else normalized_path)
            logger.debug(f"Le fichier existe avec le chemin normalisé: {normalized_exists}")
            
            if normalized_exists:
                # Remplacer les backslashes par des slashes pour la cohérence des URLs
                normalized_path = normalized_path.replace('\\', '/')
                logger.debug(f"Retour du chemin normalisé: {normalized_path}")
                return normalized_path
        
        # Vérifier les chemins possibles avec le nom de fichier original
        possible_paths = [
            os.path.join("static", "uploads", filename),
            os.path.join("static", "uploads", "exercises", filename),
            os.path.join("static", "uploads", "exercises", "qcm", filename),
            os.path.join("static", "uploads", "exercises", "flashcards", filename),
            os.path.join("static", "uploads", "exercises", "word_placement", filename),
            os.path.join("static", "uploads", "exercises", "image_labeling", filename),
            os.path.join("static", "uploads", "exercises", "legend", filename),
            os.path.join("static", "uploads", "flashcards", filename),
            os.path.join("static", "uploads", "general", filename),
            os.path.join("static", "exercises", filename),
            os.path.join("static", "exercises", "qcm", filename),
            os.path.join("static", "exercises", "flashcards", filename),
            os.path.join("static", "exercises", "word_placement", filename),
            os.path.join("static", "exercises", "image_labeling", filename),
            os.path.join("static", "exercises", "legend", filename),
            os.path.join("static", "exercises", "general", filename)
        ]
        
        # Chercher le fichier dans les chemins possibles avec le nom original
        for path in possible_paths:
            if os.path.exists(path):
                # Remplacer les backslashes par des slashes pour la cohérence des URLs
                web_path = f"/{path.replace('\\', '/')}"  
                logger.debug(f"Fichier trouvé à: {path}, URL retournée: {web_path}")
                return web_path
                
        # Si non trouvé, essayer avec le nom normalisé
        normalized_possible_paths = [
            path.replace(filename, normalized_filename) for path in possible_paths
        ]
        
        # Chercher le fichier dans les chemins possibles avec le nom normalisé
        for path in normalized_possible_paths:
            if os.path.exists(path):
                # Remplacer les backslashes par des slashes pour la cohérence des URLs
                web_path = f"/{path.replace('\\', '/')}"  
                logger.debug(f"Fichier trouvé avec nom normalisé à: {path}, URL retournée: {web_path}")
                return web_path
        
        # Si le chemin commence par "uploads/", essayer avec "/static/uploads/"
        if image_path.startswith('uploads/'):
            corrected_path = f"/static/{image_path}"
            corrected_path = corrected_path.replace('\\', '/')
            logger.debug(f"Correction du chemin uploads/: {corrected_path}")
            
            # Vérifier si le fichier existe avec ce chemin corrigé
            corrected_exists = os.path.exists(corrected_path[1:] if corrected_path.startswith('/') else corrected_path)
            if corrected_exists:
                logger.debug(f"Le fichier existe avec le chemin corrigé: {corrected_exists}")
                return corrected_path
        
        # Si le fichier n'existe pas avec le nom original ou normalisé, essayer de le trouver dans d'autres répertoires
        if current_app:
            try:
                # Essayer de trouver le fichier dans le répertoire static de l'application
                app_static_paths = [
                    os.path.join(current_app.root_path, "static", "uploads", filename),
                    os.path.join(current_app.root_path, "static", "exercises", filename),
                    os.path.join(current_app.root_path, "static", "uploads", "exercises", filename),
                    os.path.join(current_app.root_path, "static", "exercises", "exercises", filename)
                ]
                
                for app_path in app_static_paths:
                    if os.path.exists(app_path):
                        web_path = f"/{os.path.relpath(app_path, current_app.root_path).replace('\\', '/')}"  
                        logger.debug(f"Fichier trouvé dans l'application à: {app_path}, URL retournée: {web_path}")
                        return web_path
                        
                # Essayer avec le nom normalisé
                app_static_normalized_paths = [
                    os.path.join(current_app.root_path, "static", "uploads", normalized_filename),
                    os.path.join(current_app.root_path, "static", "exercises", normalized_filename),
                    os.path.join(current_app.root_path, "static", "uploads", "exercises", normalized_filename),
                    os.path.join(current_app.root_path, "static", "exercises", "exercises", normalized_filename)
                ]
                
                for app_path in app_static_normalized_paths:
                    if os.path.exists(app_path):
                        web_path = f"/{os.path.relpath(app_path, current_app.root_path).replace('\\', '/')}"  
                        logger.debug(f"Fichier trouvé dans l'application avec nom normalisé à: {app_path}, URL retournée: {web_path}")
                        return web_path
            except Exception as e:
                logger.error(f"Erreur lors de la recherche dans les répertoires de l'application: {str(e)}")
        
        # Si aucun fichier n'a été trouvé, retourner le chemin original avec /static/ préfixé si nécessaire
        if not image_path.startswith('/'):
            if not image_path.startswith('static/'):
                # Utiliser le nom normalisé pour le chemin par défaut
                final_path = f"/static/uploads/{normalized_filename}"
            else:
                final_path = f"/{image_path}"
        else:
            final_path = image_path
        
        final_path = final_path.replace('\\', '/')
        logger.warning(f"Aucun fichier trouvé, retour du chemin par défaut: {final_path}")
        return final_path

# Fonction de compatibilité pour remplacer cloud_storage.get_cloudinary_url
def get_cloudinary_url(image_path):
    """
    Fonction de compatibilité pour remplacer cloud_storage.get_cloudinary_url
    """
    return ImageUrlService.get_image_url(image_path)
