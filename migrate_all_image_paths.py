#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de migration pour normaliser tous les chemins d'images dans la base de données.
Ce script traite tous les types d'exercices et assure une cohérence dans les chemins d'images.
"""

import os
import json
import logging
from flask import Flask
from models import db, Exercise
from unified_image_service import UnifiedImageService

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('migration_all_images.log')
    ]
)
logger = logging.getLogger(__name__)

def migrate_image_paths():
    """
    Migre les chemins d'images pour tous les types d'exercices.
    Normalise les chemins dans la colonne image_path et dans le contenu JSON.
    """
    try:
        # Créer une application Flask minimale pour le contexte
        app = Flask(__name__)
        app.config.from_object('config.DevelopmentConfig')
        
        # Initialiser la base de données avec l'application
        db.init_app(app)
        
        with app.app_context():
            # Récupérer tous les exercices
            exercises = Exercise.query.all()
            logger.info(f"Traitement de {len(exercises)} exercices au total")
            
            updated_count = 0
            for exercise in exercises:
                try:
                    exercise_type = exercise.exercise_type
                    logger.info(f"Traitement de l'exercice ID {exercise.id} de type '{exercise_type}'")
                    
                    # Charger le contenu JSON
                    content = json.loads(exercise.content) if exercise.content else {}
                    content_updated = False
                    
                    # Traitement spécifique selon le type d'exercice
                    if exercise_type == 'pairs':
                        # Traiter les paires
                        if 'pairs' in content and isinstance(content['pairs'], list):
                            for pair in content['pairs']:
                                # Traiter l'élément de gauche
                                if 'left' in pair and pair['left'].get('type') == 'image' and pair['left'].get('content'):
                                    old_path = pair['left']['content']
                                    new_path = UnifiedImageService.migrate_image_path(old_path, 'pairs')
                                    if old_path != new_path:
                                        pair['left']['content'] = new_path
                                        logger.info(f"Exercice ID {exercise.id}: Chemin d'image gauche normalisé: {old_path} -> {new_path}")
                                        content_updated = True
                                
                                # Traiter l'élément de droite
                                if 'right' in pair and pair['right'].get('type') == 'image' and pair['right'].get('content'):
                                    old_path = pair['right']['content']
                                    new_path = UnifiedImageService.migrate_image_path(old_path, 'pairs')
                                    if old_path != new_path:
                                        pair['right']['content'] = new_path
                                        logger.info(f"Exercice ID {exercise.id}: Chemin d'image droite normalisé: {old_path} -> {new_path}")
                                        content_updated = True
                        
                        # Traiter les éléments de gauche et de droite séparés
                        if 'left_items' in content and isinstance(content['left_items'], list):
                            for item in content['left_items']:
                                if isinstance(item, dict) and item.get('type') == 'image' and item.get('content'):
                                    old_path = item['content']
                                    new_path = UnifiedImageService.migrate_image_path(old_path, 'pairs')
                                    if old_path != new_path:
                                        item['content'] = new_path
                                        logger.info(f"Exercice ID {exercise.id}: Chemin d'image left_items normalisé: {old_path} -> {new_path}")
                                        content_updated = True
                        
                        if 'shuffled_right_items' in content and isinstance(content['shuffled_right_items'], list):
                            for item in content['shuffled_right_items']:
                                if isinstance(item, dict) and item.get('type') == 'image' and item.get('content'):
                                    old_path = item['content']
                                    new_path = UnifiedImageService.migrate_image_path(old_path, 'pairs')
                                    if old_path != new_path:
                                        item['content'] = new_path
                                        logger.info(f"Exercice ID {exercise.id}: Chemin d'image shuffled_right_items normalisé: {old_path} -> {new_path}")
                                        content_updated = True
                    
                    elif exercise_type == 'image_labeling':
                        # Traiter l'image principale
                        if 'main_image' in content and content['main_image']:
                            old_path = content['main_image']
                            new_path = UnifiedImageService.migrate_image_path(old_path, 'image_labeling')
                            if old_path != new_path:
                                content['main_image'] = new_path
                                logger.info(f"Exercice ID {exercise.id}: Chemin d'image principale normalisé: {old_path} -> {new_path}")
                                content_updated = True
                    
                    elif exercise_type == 'flashcards':
                        # Traiter les flashcards
                        if 'cards' in content and isinstance(content['cards'], list):
                            for card in content['cards']:
                                if 'image' in card and card['image']:
                                    old_path = card['image']
                                    new_path = UnifiedImageService.migrate_image_path(old_path, 'flashcards')
                                    if old_path != new_path:
                                        card['image'] = new_path
                                        logger.info(f"Exercice ID {exercise.id}: Chemin d'image flashcard normalisé: {old_path} -> {new_path}")
                                        content_updated = True
                    
                    elif exercise_type == 'word_placement':
                        # Traiter l'image de fond
                        if 'background_image' in content and content['background_image']:
                            old_path = content['background_image']
                            new_path = UnifiedImageService.migrate_image_path(old_path, 'word_placement')
                            if old_path != new_path:
                                content['background_image'] = new_path
                                logger.info(f"Exercice ID {exercise.id}: Chemin d'image de fond normalisé: {old_path} -> {new_path}")
                                content_updated = True
                    
                    elif exercise_type == 'legend':
                        # Traiter l'image de légende
                        if 'image' in content and content['image']:
                            old_path = content['image']
                            new_path = UnifiedImageService.migrate_image_path(old_path, 'legend')
                            if old_path != new_path:
                                content['image'] = new_path
                                logger.info(f"Exercice ID {exercise.id}: Chemin d'image légende normalisé: {old_path} -> {new_path}")
                                content_updated = True
                    
                    # Traiter le chemin d'image dans la colonne image_path pour tous les types d'exercices
                    if exercise.image_path:
                        old_path = exercise.image_path
                        new_path = UnifiedImageService.migrate_image_path(old_path, exercise_type)
                        if old_path != new_path:
                            exercise.image_path = new_path
                            logger.info(f"Exercice ID {exercise.id}: Chemin d'image dans image_path normalisé: {old_path} -> {new_path}")
                            updated_count += 1
                    
                    # Mettre à jour le contenu JSON si nécessaire
                    if content_updated:
                        exercise.content = json.dumps(content)
                        updated_count += 1
                    
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
    logger.info("Début de la migration des chemins d'images pour tous les types d'exercices...")
    success = migrate_image_paths()
    
    if success:
        logger.info("Migration des chemins d'images terminée avec succès.")
    else:
        logger.error("La migration des chemins d'images a échoué.")

if __name__ == "__main__":
    main()
