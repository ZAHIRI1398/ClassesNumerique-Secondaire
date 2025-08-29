#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de migration pour corriger les chemins d'images existants dans la base de données.
Ce script normalise les chemins d'images pour les exercices de type 'image_labeling'.
"""

import os
import json
import logging
from flask import Flask
from models import db, Exercise

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('migration_images.log')
    ]
)
logger = logging.getLogger(__name__)

def normalize_image_path(path):
    """
    Normalise le chemin d'image pour assurer un format cohérent
    
    Args:
        path (str): Le chemin d'image à normaliser
        
    Returns:
        str: Le chemin normalisé
    """
    if not path:
        return path
        
    # Extraire juste le nom du fichier
    filename = os.path.basename(path)
    
    # Normaliser le nom du fichier (remplacer les espaces par des underscores, supprimer les apostrophes)
    normalized_filename = filename.replace(' ', '_').replace("'", '')
    
    # Retourner le chemin standard
    return f"/static/uploads/exercises/image_labeling/{normalized_filename}"

def migrate_image_paths():
    """
    Migre les chemins d'images existants pour les exercices de type 'image_labeling'.
    Normalise les chemins dans la colonne image_path et dans le contenu JSON.
    """
    try:
        # Créer une application Flask minimale pour le contexte
        app = Flask(__name__)
        app.config.from_object('config.DevelopmentConfig')
        
        # Initialiser la base de données avec l'application
        db.init_app(app)
        
        with app.app_context():
            # Récupérer tous les exercices de type 'image_labeling'
            exercises = Exercise.query.filter_by(exercise_type='image_labeling').all()
            logger.info(f"Trouvé {len(exercises)} exercices de type 'image_labeling'")
            
            updated_count = 0
            for exercise in exercises:
                try:
                    # Charger le contenu JSON
                    content = json.loads(exercise.content) if exercise.content else {}
                    
                    # Vérifier si l'exercice a une image principale dans son contenu
                    if 'main_image' in content and content['main_image']:
                        old_path = content['main_image']
                        new_path = normalize_image_path(old_path)
                        
                        # Mettre à jour le chemin dans le contenu JSON
                        if old_path != new_path:
                            content['main_image'] = new_path
                            exercise.content = json.dumps(content)
                            logger.info(f"Exercice ID {exercise.id}: Chemin d'image normalisé dans le contenu JSON: {old_path} -> {new_path}")
                            updated_count += 1
                    
                    # Vérifier si l'exercice a un chemin d'image dans la colonne image_path
                    if exercise.image_path:
                        old_path = exercise.image_path
                        new_path = normalize_image_path(old_path)
                        
                        # Mettre à jour le chemin dans la colonne image_path
                        if old_path != new_path:
                            exercise.image_path = new_path
                            logger.info(f"Exercice ID {exercise.id}: Chemin d'image normalisé dans image_path: {old_path} -> {new_path}")
                            updated_count += 1
                    
                    # Vérifier si des fichiers physiques doivent être renommés
                    # Note: Cette partie est commentée car elle nécessite une vérification manuelle
                    # pour éviter de perdre des fichiers
                    """
                    if 'main_image' in content and content['main_image']:
                        # Chemin physique du fichier
                        base_path = app.config['UPLOAD_FOLDER']
                        old_filename = os.path.basename(old_path)
                        new_filename = os.path.basename(new_path)
                        old_file_path = os.path.join(base_path, 'exercises', 'image_labeling', old_filename)
                        new_file_path = os.path.join(base_path, 'exercises', 'image_labeling', new_filename)
                        
                        # Renommer le fichier physique si nécessaire
                        if os.path.exists(old_file_path) and old_filename != new_filename:
                            os.rename(old_file_path, new_file_path)
                            logger.info(f"Fichier renommé: {old_file_path} -> {new_file_path}")
                    """
                    
                except Exception as e:
                    logger.error(f"Erreur lors du traitement de l'exercice ID {exercise.id}: {str(e)}")
            
            # Sauvegarder les modifications dans la base de données
            if updated_count > 0:
                db.session.commit()
                logger.info(f"Migration terminée avec succès. {updated_count} chemins d'images ont été normalisés.")
            else:
                logger.info("Aucun chemin d'image n'a été modifié.")
                
    except Exception as e:
        logger.error(f"Erreur lors de la migration: {str(e)}")
        return False
    
    return True

def main():
    """Fonction principale"""
    logger.info("Début de la migration des chemins d'images...")
    success = migrate_image_paths()
    
    if success:
        logger.info("Migration des chemins d'images terminée avec succès.")
    else:
        logger.error("La migration des chemins d'images a échoué.")

if __name__ == "__main__":
    main()
