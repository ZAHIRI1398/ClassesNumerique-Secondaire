import os
import json
import sqlite3
from flask import Flask, request, redirect, url_for, current_app
from werkzeug.middleware.proxy_fix import ProxyFix
from functools import wraps

class ImageFallbackMiddleware:
    """
    Middleware qui détecte les requêtes d'images manquantes et tente de les servir
    depuis des chemins alternatifs, tout en corrigeant la base de données.
    """
    
    def __init__(self, app):
        self.app = app
        self.wsgi_app = app.wsgi_app
        self.app.wsgi_app = self
        
        # Chemins alternatifs pour rechercher les images QCM Multichoix
        self.alternative_paths = [
            'static/exercises/qcm_multichoix/',
            'static/uploads/qcm_multichoix/',
            'static/uploads/exercises/qcm_multichoix/',
            'static/uploads/',
            'static/exercises/'
        ]
        
        # Configuration de la base de données
        self.db_path = os.path.join(app.root_path, 'instance/app.db')
    
    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        
        # Vérifier si c'est une requête pour une image
        if path.startswith('/static/') and self._is_image_path(path):
            # Vérifier si l'image existe à l'emplacement demandé
            file_path = os.path.join(self.app.root_path, path.lstrip('/'))
            
            if not os.path.exists(file_path):
                # L'image n'existe pas à l'emplacement demandé, essayer les chemins alternatifs
                filename = os.path.basename(path)
                found_path = self._find_image_in_alternative_paths(filename)
                
                if found_path:
                    # Image trouvée dans un chemin alternatif
                    self.app.logger.info(f"Image {path} trouvée à {found_path}")
                    
                    # Rediriger vers le bon chemin
                    new_path = '/' + found_path
                    environ['PATH_INFO'] = new_path
                    
                    # Corriger la référence dans la base de données
                    self._fix_image_reference(path, new_path)
        
        return self.wsgi_app(environ, start_response)
    
    def _is_image_path(self, path):
        """Vérifie si le chemin correspond à une image."""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
        return any(path.lower().endswith(ext) for ext in image_extensions)
    
    def _find_image_in_alternative_paths(self, filename):
        """Recherche l'image dans les chemins alternatifs."""
        for path in self.alternative_paths:
            full_path = os.path.join(self.app.root_path, path, filename)
            if os.path.exists(full_path):
                return os.path.join(path, filename)
        return None
    
    def _fix_image_reference(self, old_path, new_path):
        """Corrige la référence de l'image dans la base de données."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Mettre à jour les références directes dans le champ image_path
            cursor.execute("UPDATE exercise SET image_path = ? WHERE image_path = ?", 
                          (new_path, old_path))
            
            # Mettre à jour les références dans le contenu JSON
            cursor.execute("SELECT id, content FROM exercise WHERE content LIKE ?", 
                          (f'%{old_path}%',))
            
            for exercise_id, content_json in cursor.fetchall():
                try:
                    content = json.loads(content_json)
                    if 'image' in content and content['image'] == old_path:
                        content['image'] = new_path
                        cursor.execute("UPDATE exercise SET content = ? WHERE id = ?", 
                                      (json.dumps(content), exercise_id))
                except (json.JSONDecodeError, TypeError):
                    continue
            
            conn.commit()
            self.app.logger.info(f"Référence d'image corrigée: {old_path} -> {new_path}")
        
        except Exception as e:
            self.app.logger.error(f"Erreur lors de la correction de la référence d'image: {e}")
        
        finally:
            if 'conn' in locals() and conn:
                conn.close()

def setup_image_fallback(app):
    """Configure le middleware de fallback d'images pour l'application Flask."""
    ImageFallbackMiddleware(app)
    app.logger.info("Middleware de fallback d'images configuré")

# Exemple d'utilisation dans app.py:
# from image_fallback_middleware import setup_image_fallback
# setup_image_fallback(app)
