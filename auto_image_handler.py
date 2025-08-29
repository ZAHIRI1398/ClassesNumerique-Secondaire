import os
import json
import sqlite3
import shutil
import logging
from datetime import datetime
from flask import Flask, request, current_app, g

class AutoImageHandler:
    """
    Gestionnaire automatique des images pour les exercices QCM Multichoix.
    Cette classe s'occupe de :
    1. Standardiser les chemins d'images lors de l'upload
    2. Corriger automatiquement les références d'images manquantes
    3. Générer des rapports pour l'administrateur
    """
    
    def __init__(self, app=None):
        self.app = app
        
        # Chemin standard pour les nouvelles images
        self.standard_path = 'static/uploads/qcm_multichoix/'
        
        if app is not None:
            self.init_app(app)
        
        # Configuration du logging
        logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Chemins alternatifs pour rechercher les images QCM Multichoix
        self.alternative_paths = [
            'static/exercises/qcm_multichoix/',
            'static/uploads/qcm_multichoix/',
            'static/uploads/exercises/qcm_multichoix/',
            'static/uploads/',
            'static/exercises/'
        ]
        
        # Chemin standard pour les nouvelles images
        self.standard_path = 'static/uploads/qcm_multichoix/'
    
    def init_app(self, app):
        """Initialise l'extension avec l'application Flask."""
        self.app = app
        
        # S'assurer que le répertoire standard existe
        os.makedirs(os.path.join(app.root_path, self.standard_path), exist_ok=True)
        
        # Enregistrer les hooks pour les opérations automatiques
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        
        # Ajouter une commande Flask pour la vérification manuelle
        @app.cli.command('verify-qcm-multichoix-images')
        def verify_images_command():
            """Vérifie et corrige les chemins d'images des exercices QCM Multichoix."""
            with app.app_context():
                issues = self.verify_images()
                if issues:
                    self.logger.warning(f"{len(issues)} problèmes d'images détectés et corrigés.")
                else:
                    self.logger.info("Aucun problème d'image détecté.")
    
    def _before_request(self):
        """Hook exécuté avant chaque requête."""
        # Vérifier si c'est une requête d'upload d'image pour un exercice QCM Multichoix
        if request.endpoint == 'exercise.upload_image' and request.method == 'POST':
            g.auto_image_handler = True
    
    def _after_request(self, response):
        """Hook exécuté après chaque requête."""
        # Si c'était une requête d'upload d'image pour un exercice QCM Multichoix
        if hasattr(g, 'auto_image_handler') and g.auto_image_handler:
            # Standardiser le chemin de l'image si nécessaire
            if response.status_code == 200 and 'image_path' in response.json:
                image_path = response.json['image_path']
                standardized_path = self.standardize_image_path(image_path)
                if standardized_path != image_path:
                    response.json['image_path'] = standardized_path
        
        return response
    
    def standardize_image_path(self, image_path):
        """Standardise le chemin d'une image en la déplaçant si nécessaire."""
        if not image_path:
            return image_path
        
        # Supprimer le slash initial si présent
        if image_path.startswith('/'):
            path_without_slash = image_path[1:]
        else:
            path_without_slash = image_path
        
        # Vérifier si l'image existe à l'emplacement actuel
        if os.path.exists(os.path.join(self.app.root_path, path_without_slash)):
            # Extraire le nom du fichier
            filename = os.path.basename(path_without_slash)
            
            # Construire le nouveau chemin standardisé
            new_path = os.path.join(self.standard_path, filename)
            new_path_with_slash = '/' + new_path
            
            # Si l'image n'est pas déjà au bon endroit, la déplacer
            if path_without_slash != new_path:
                try:
                    # Créer le répertoire de destination si nécessaire
                    os.makedirs(os.path.dirname(os.path.join(self.app.root_path, new_path)), exist_ok=True)
                    
                    # Copier l'image vers le nouvel emplacement
                    shutil.copy2(
                        os.path.join(self.app.root_path, path_without_slash),
                        os.path.join(self.app.root_path, new_path)
                    )
                    
                    # Mettre à jour la référence dans la base de données
                    self._update_image_reference(image_path, new_path_with_slash)
                    
                    self.logger.info(f"Image standardisée: {image_path} -> {new_path_with_slash}")
                    return new_path_with_slash
                
                except Exception as e:
                    self.logger.error(f"Erreur lors de la standardisation de l'image: {e}")
        
        return image_path
    
    def verify_images(self):
        """Vérifie et corrige les chemins d'images des exercices QCM Multichoix."""
        issues = []
        
        try:
            # Connexion à la base de données
            db_path = os.path.join(self.app.root_path, 'instance/app.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Récupérer tous les exercices QCM Multichoix
            cursor.execute("SELECT id, title, content, image_path FROM exercise WHERE exercise_type = 'qcm_multichoix'")
            exercises = cursor.fetchall()
            
            self.logger.info(f"Vérification de {len(exercises)} exercices QCM Multichoix")
            
            for exercise_id, title, content_json, db_image_path in exercises:
                try:
                    # Déterminer le chemin d'image à utiliser
                    if db_image_path:
                        image_path = db_image_path
                        source = "image_path"
                    else:
                        # Vérifier l'image dans le contenu JSON
                        content = json.loads(content_json) if content_json else {}
                        image_path = content.get('image', '')
                        source = "content.image"
                    
                    if not image_path:
                        continue
                    
                    # Supprimer le slash initial si présent
                    if image_path.startswith('/'):
                        path_without_slash = image_path[1:]
                    else:
                        path_without_slash = image_path
                    
                    # Vérifier si l'image existe à l'emplacement actuel
                    if not os.path.exists(os.path.join(self.app.root_path, path_without_slash)):
                        # L'image n'existe pas à l'emplacement actuel, essayer les chemins alternatifs
                        filename = os.path.basename(path_without_slash)
                        found = False
                        
                        for alt_path in self.alternative_paths:
                            full_path = os.path.join(self.app.root_path, alt_path, filename)
                            if os.path.exists(full_path):
                                # Image trouvée dans un chemin alternatif
                                new_path = os.path.join(self.standard_path, filename)
                                new_path_with_slash = '/' + new_path
                                
                                # Créer le répertoire de destination si nécessaire
                                os.makedirs(os.path.dirname(os.path.join(self.app.root_path, new_path)), exist_ok=True)
                                
                                # Copier l'image vers le nouvel emplacement
                                shutil.copy2(full_path, os.path.join(self.app.root_path, new_path))
                                
                                # Mettre à jour la référence dans la base de données
                                if source == "image_path":
                                    cursor.execute("UPDATE exercise SET image_path = ? WHERE id = ?", 
                                                (new_path_with_slash, exercise_id))
                                else:
                                    content = json.loads(content_json)
                                    content['image'] = new_path_with_slash
                                    cursor.execute("UPDATE exercise SET content = ? WHERE id = ?", 
                                                (json.dumps(content), exercise_id))
                                
                                conn.commit()
                                
                                self.logger.info(f"Image corrigée: {image_path} -> {new_path_with_slash} pour l'exercice #{exercise_id} ({title})")
                                issues.append({
                                    'exercise_id': exercise_id,
                                    'title': title,
                                    'old_path': image_path,
                                    'new_path': new_path_with_slash
                                })
                                
                                found = True
                                break
                        
                        if not found:
                            self.logger.warning(f"Image introuvable: {image_path} pour l'exercice #{exercise_id} ({title})")
                
                except Exception as e:
                    self.logger.error(f"Erreur lors de la vérification de l'exercice #{exercise_id} ({title}): {e}")
            
            # Générer un rapport si des problèmes ont été détectés
            if issues:
                self._generate_report(issues)
            
            return issues
        
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification des images: {e}")
            return []
        
        finally:
            if 'conn' in locals() and conn:
                conn.close()
    
    def _update_image_reference(self, old_path, new_path):
        """Met à jour les références d'images dans la base de données."""
        try:
            db_path = os.path.join(self.app.root_path, 'instance/app.db')
            conn = sqlite3.connect(db_path)
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
        
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour des références d'images: {e}")
        
        finally:
            if 'conn' in locals() and conn:
                conn.close()
    
    def _generate_report(self, issues):
        """Génère un rapport des problèmes d'images corrigés."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(self.app.root_path, f'qcm_multichoix_images_report_{timestamp}.md')
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Rapport de correction automatique des images QCM Multichoix\n\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"## {len(issues)} images corrigées automatiquement:\n\n")
            f.write("| ID | Titre | Ancien chemin | Nouveau chemin |\n")
            f.write("|----|--------------------|---------------|---------------|\n")
            
            for issue in issues:
                f.write(f"| {issue['exercise_id']} | {issue['title'][:20]}... | {issue['old_path']} | {issue['new_path']} |\n")
        
        self.logger.info(f"Rapport de correction généré: {report_path}")

# Fonction d'aide pour initialiser l'extension dans app.py
def setup_auto_image_handler(app):
    """Configure le gestionnaire automatique d'images pour l'application Flask."""
    handler = AutoImageHandler(app)
    app.auto_image_handler = handler
    return handler

# Exemple d'utilisation dans app.py:
# from auto_image_handler import setup_auto_image_handler
# setup_auto_image_handler(app)
