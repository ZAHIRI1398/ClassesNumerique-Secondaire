"""
Module amélioré pour corriger l'affichage des images dans les exercices
Version avec logs de débogage détaillés pour la route /get_cloudinary_url
"""

import os
import logging
from flask import request, jsonify, current_app
from image_url_service import get_cloudinary_url, ImageUrlService
from utils.image_path_manager import ImagePathManager

def register_image_display_routes(app):
    """
    Enregistre les routes améliorées pour la gestion de l'affichage des images
    
    Args:
        app: L'application Flask
    """
    # Configuration du logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    # Route améliorée pour récupérer l'URL Cloudinary d'une image
    @app.route('/get_cloudinary_url', methods=['GET'])
    def get_cloudinary_url_route():
        """
        Route améliorée pour récupérer l'URL Cloudinary d'une image
        Avec logs de débogage détaillés pour diagnostiquer les problèmes d'affichage
        """
        image_path = request.args.get('image_path')
        logger.debug(f"[DEBUG] Route /get_cloudinary_url appelée avec image_path={image_path}")
        
        if not image_path:
            logger.error("[ERROR] Aucun chemin d'image fourni à /get_cloudinary_url")
            return jsonify({'error': 'Aucun chemin d\'image fourni'}), 400
        
        try:
            # Log du chemin d'image reçu
            logger.debug(f"[DEBUG] Traitement du chemin d'image: {image_path}")
            
            # Vérifier si le fichier existe directement avec ce chemin
            direct_path = image_path
            if direct_path.startswith('/'):
                direct_path = direct_path[1:]
            direct_exists = os.path.exists(direct_path)
            logger.debug(f"[DEBUG] Le fichier existe directement: {direct_exists}")
            
            # Extraire le nom de fichier
            filename = os.path.basename(image_path)
            logger.debug(f"[DEBUG] Nom de fichier extrait: {filename}")
            
            # Vérifier les chemins possibles
            possible_paths = [
                os.path.join("static", "exercises", "general", filename),
                os.path.join("static", "exercises", "flashcards", filename),
                os.path.join("static", "uploads", "flashcards", filename),
                os.path.join("static", "uploads", "general", filename),
                os.path.join("static", "uploads", filename),
                os.path.join("static", "exercises", filename),
                os.path.join("uploads", filename),
                os.path.join("exercises", filename)
            ]
            
            # Log des chemins possibles
            for path in possible_paths:
                exists = os.path.exists(path)
                size = os.path.getsize(path) if exists else None
                logger.debug(f"[DEBUG] Chemin {path}: {'Existe' if exists else 'N\'existe pas'}{f' ({size} octets)' if exists else ''}")
            
            # Utiliser la fonction corrigée pour obtenir l'URL
            url = get_cloudinary_url(image_path)
            logger.debug(f"[DEBUG] URL générée par get_cloudinary_url: {url}")
            
            # Vérifier si l'URL générée pointe vers un fichier existant
            if url and url.startswith('/'):
                url_path = url[1:]
                url_exists = os.path.exists(url_path)
                logger.debug(f"[DEBUG] Le fichier à l'URL générée existe: {url_exists}")
                
                # Si l'URL générée ne pointe pas vers un fichier existant, essayer de corriger
                if not url_exists:
                    logger.debug("[DEBUG] Tentative de correction de l'URL...")
                    
                    # Essayer de trouver le fichier dans les dossiers possibles
                    for path in possible_paths:
                        if os.path.exists(path):
                            logger.debug(f"[DEBUG] Fichier trouvé à: {path}")
                            url = f"/{path}"
                            break
            
            # Retourner l'URL finale
            logger.info(f"[INFO] URL finale retournée: {url}")
            return jsonify({'url': url})
            
        except Exception as e:
            logger.error(f"[ERROR] Erreur lors de la génération de l'URL pour {image_path}: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    # Route de diagnostic pour vérifier les chemins d'images
    @app.route('/debug-image-paths', methods=['GET'])
    def debug_image_paths():
        """
        Route de diagnostic pour vérifier les chemins d'images
        """
        image_path = request.args.get('image_path')
        if not image_path:
            return jsonify({'error': 'Aucun chemin d\'image fourni'}), 400
        
        result = {
            'original_path': image_path,
            'paths_checked': []
        }
        
        # Extraire le nom de fichier
        filename = os.path.basename(image_path)
        result['filename'] = filename
        
        # Vérifier les chemins possibles
        possible_paths = [
            os.path.join("static", "exercises", "general", filename),
            os.path.join("static", "exercises", "flashcards", filename),
            os.path.join("static", "uploads", "flashcards", filename),
            os.path.join("static", "uploads", "general", filename),
            os.path.join("static", "uploads", filename),
            os.path.join("static", "exercises", filename),
            os.path.join("uploads", filename),
            os.path.join("exercises", filename),
            image_path
        ]
        
        for path in possible_paths:
            exists = os.path.exists(path)
            size = os.path.getsize(path) if exists else None
            result['paths_checked'].append({
                'path': path,
                'exists': exists,
                'size': size
            })
        
        # Utiliser la fonction corrigée pour obtenir l'URL
        try:
            url = get_cloudinary_url(image_path)
            result['cloudinary_url'] = url
            
            # Vérifier si l'URL générée pointe vers un fichier existant
            if url and url.startswith('/'):
                url_path = url[1:]
                url_exists = os.path.exists(url_path)
                result['url_exists'] = url_exists
        except Exception as e:
            result['cloudinary_error'] = str(e)
        
        return jsonify(result)
