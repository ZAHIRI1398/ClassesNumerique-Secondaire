from flask import request, current_app, send_from_directory
import os
import re
from functools import wraps
import logging
from .image_path_handler import normalize_qcm_multichoix_image_path

class ImageFallbackMiddleware:
    """
    Middleware pour intercepter les requêtes d'images et rediriger vers des chemins alternatifs
    si l'image n'est pas trouvée au chemin demandé.
    
    Particulièrement utile pour les images QCM Multichoix qui peuvent être dans différents répertoires.
    """
    
    def __init__(self, app=None):
        self.app = app
        self.logger = logging.getLogger(__name__)
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialise le middleware avec l'application Flask"""
        self.app = app
        
        # Enregistrer une fonction pour intercepter les requêtes d'images
        @app.before_request
        def handle_image_request():
            # Vérifier si c'est une requête pour une image
            if not request.path.startswith('/static/'):
                return None
                
            # Vérifier si c'est une image QCM Multichoix
            if 'qcm_multichoix' in request.path and request.path.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                # Extraire le chemin du fichier demandé
                file_path = request.path.lstrip('/')
                
                # Vérifier si le fichier existe
                if not os.path.exists(os.path.join(current_app.root_path, file_path)):
                    self.logger.warning(f"Image QCM Multichoix non trouvée: {file_path}")
                    
                    # Chercher l'image dans des chemins alternatifs
                    alt_path = self.find_image_in_alternative_paths(file_path)
                    if alt_path:
                        self.logger.info(f"Image trouvée dans un chemin alternatif: {alt_path}")
                        
                        # Rediriger vers le chemin alternatif
                        return send_from_directory(
                            os.path.dirname(os.path.join(current_app.root_path, alt_path)),
                            os.path.basename(alt_path)
                        )
        
        # Ajouter une route pour vérifier les images QCM Multichoix
        @app.route('/admin/verify-qcm-multichoix-images')
        def verify_qcm_multichoix_images():
            from flask import jsonify
            from flask_login import login_required, current_user
            
            # Vérifier si l'utilisateur est administrateur
            if not current_user.is_authenticated or not current_user.is_admin:
                return jsonify({'error': 'Accès non autorisé'}), 403
            
            # Exécuter la vérification
            from verify_qcm_multichoix_images import verify_qcm_multichoix_images as run_verification
            issues = run_verification()
            
            # Générer un rapport
            return jsonify({
                'status': 'success',
                'message': f"{len(issues)} problèmes détectés" if issues else "Aucun problème détecté",
                'issues': issues
            })
    
    def find_image_in_alternative_paths(self, image_path):
        """
        Cherche une image dans des chemins alternatifs
        
        Args:
            image_path (str): Le chemin de l'image demandée
            
        Returns:
            str: Le chemin alternatif trouvé ou None
        """
        # Extraire le nom du fichier
        filename = os.path.basename(image_path)
        
        # Chemins alternatifs à vérifier
        alt_paths = [
            os.path.join('static', 'exercises', 'general', filename),
            os.path.join('static', 'exercises', 'qcm', filename),
            os.path.join('static', 'uploads', filename),
            os.path.join('static', 'exercises', filename)
        ]
        
        # Vérifier chaque chemin alternatif
        for alt_path in alt_paths:
            if os.path.exists(os.path.join(current_app.root_path, alt_path)):
                # Copier l'image vers le chemin demandé pour les futures requêtes
                try:
                    import shutil
                    target_dir = os.path.dirname(os.path.join(current_app.root_path, image_path))
                    
                    # Créer le répertoire cible s'il n'existe pas
                    if not os.path.exists(target_dir):
                        os.makedirs(target_dir)
                        self.logger.info(f"Répertoire créé: {target_dir}")
                    
                    # Copier l'image
                    shutil.copy2(
                        os.path.join(current_app.root_path, alt_path),
                        os.path.join(current_app.root_path, image_path)
                    )
                    self.logger.info(f"Image copiée: {alt_path} -> {image_path}")
                except Exception as e:
                    self.logger.error(f"Erreur lors de la copie de l'image: {str(e)}")
                
                return alt_path
        
        return None

def register_image_fallback_middleware(app):
    """
    Fonction utilitaire pour enregistrer le middleware dans l'application Flask
    
    Args:
        app: L'application Flask
    """
    middleware = ImageFallbackMiddleware(app)
    return middleware
