"""
Script de diagnostic pour les images des exercices de type word_placement
"""

import os
import json
import logging
from flask import Flask, render_template
from models import db, Exercise

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('diagnose_word_placement')

# Création de l'application Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def diagnose_exercise_image(exercise_id=None, title=None):
    """
    Diagnostique les problèmes d'image pour un exercice spécifique
    
    Args:
        exercise_id: ID de l'exercice à diagnostiquer
        title: Titre de l'exercice à diagnostiquer (si ID non fourni)
    """
    with app.app_context():
        if exercise_id:
            exercise = Exercise.query.get(exercise_id)
        elif title:
            exercise = Exercise.query.filter(Exercise.title.like(f"%{title}%")).first()
        else:
            logger.error("Aucun ID ou titre d'exercice fourni")
            return
        
        if not exercise:
            logger.error(f"Exercice non trouvé (ID: {exercise_id}, Titre: {title})")
            return
        
        logger.info(f"Diagnostic de l'exercice: {exercise.title} (ID: {exercise.id})")
        logger.info(f"Type d'exercice: {exercise.exercise_type}")
        logger.info(f"Chemin d'image: {exercise.image_path}")
        
        # Vérifier si l'image existe
        if exercise.image_path:
            # Vérifier le chemin absolu
            absolute_path = exercise.image_path
            if absolute_path.startswith('/'):
                absolute_path = absolute_path[1:]
            
            if os.path.exists(absolute_path):
                logger.info(f"✅ L'image existe au chemin absolu: {absolute_path}")
            else:
                logger.error(f"❌ L'image n'existe pas au chemin absolu: {absolute_path}")
                
                # Essayer avec /static/ préfixé
                if not exercise.image_path.startswith('/static/') and not exercise.image_path.startswith('static/'):
                    static_path = f"static/{exercise.image_path}" if not exercise.image_path.startswith('/') else f"static{exercise.image_path}"
                    if os.path.exists(static_path):
                        logger.info(f"✅ L'image existe avec /static/ préfixé: {static_path}")
                    else:
                        logger.error(f"❌ L'image n'existe pas avec /static/ préfixé: {static_path}")
                
                # Essayer avec le nom de fichier uniquement
                filename = os.path.basename(exercise.image_path)
                possible_paths = [
                    os.path.join("static", "uploads", filename),
                    os.path.join("static", "exercises", filename),
                    os.path.join("static", "exercise_images", filename),
                    os.path.join("static", "uploads", "word_placement", filename)
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        logger.info(f"✅ L'image existe au chemin alternatif: {path}")
                        logger.info(f"💡 Correction recommandée: Mettre à jour exercise.image_path vers '/{path}'")
                        break
                else:
                    logger.error(f"❌ L'image n'a pas été trouvée dans les chemins alternatifs")
        else:
            logger.warning("⚠️ Aucun chemin d'image défini pour cet exercice")
        
        # Vérifier le contenu de l'exercice
        try:
            content = exercise.get_content()
            logger.info(f"Contenu de l'exercice: {type(content)}")
            
            if content:
                if isinstance(content, dict):
                    if 'image' in content:
                        logger.info(f"Image dans le contenu: {content['image']}")
                        
                        # Vérifier si l'image dans le contenu existe
                        content_image_path = content['image']
                        if content_image_path.startswith('/'):
                            content_image_path = content_image_path[1:]
                            
                        if os.path.exists(content_image_path):
                            logger.info(f"✅ L'image du contenu existe: {content_image_path}")
                        else:
                            logger.error(f"❌ L'image du contenu n'existe pas: {content_image_path}")
                    else:
                        logger.info("Pas d'image définie dans le contenu")
                        
                    # Vérifier les autres champs du contenu pour les exercices word_placement
                    if exercise.exercise_type == 'word_placement':
                        if 'words' in content:
                            logger.info(f"Mots disponibles: {content['words']}")
                        else:
                            logger.error("❌ Champ 'words' manquant dans le contenu")
                            
                        if 'sentences' in content:
                            logger.info(f"Phrases: {content['sentences']}")
                        else:
                            logger.error("❌ Champ 'sentences' manquant dans le contenu")
                else:
                    logger.error(f"❌ Format de contenu non valide: {type(content)}")
            else:
                logger.error("❌ Contenu de l'exercice vide")
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'accès au contenu: {str(e)}")

def diagnose_all_word_placement_exercises():
    """
    Diagnostique tous les exercices de type word_placement
    """
    with app.app_context():
        exercises = Exercise.query.filter_by(exercise_type='word_placement').all()
        logger.info(f"Nombre d'exercices word_placement trouvés: {len(exercises)}")
        
        for exercise in exercises:
            logger.info(f"\n{'='*50}")
            diagnose_exercise_image(exercise_id=exercise.id)

def fix_word_placement_image(exercise_id, new_image_path):
    """
    Corrige le chemin d'image pour un exercice word_placement
    
    Args:
        exercise_id: ID de l'exercice à corriger
        new_image_path: Nouveau chemin d'image
    """
    with app.app_context():
        exercise = Exercise.query.get(exercise_id)
        if not exercise:
            logger.error(f"Exercice non trouvé (ID: {exercise_id})")
            return
        
        old_path = exercise.image_path
        exercise.image_path = new_image_path
        
        # Mettre à jour l'image dans le contenu si nécessaire
        content = exercise.get_content()
        if content and isinstance(content, dict) and 'image' in content:
            content['image'] = new_image_path
            exercise.content = json.dumps(content)
        
        db.session.commit()
        logger.info(f"✅ Chemin d'image mis à jour: {old_path} -> {new_image_path}")

if __name__ == "__main__":
    print("=== Diagnostic des exercices word_placement ===")
    
    # Diagnostiquer l'exercice "Test mots à placerComplet"
    print("\nDiagnostic de l'exercice 'Test mots à placerComplet'...")
    diagnose_exercise_image(title="Test mots")
    
    # Diagnostiquer tous les exercices word_placement
    print("\nDiagnostic de tous les exercices word_placement...")
    diagnose_all_word_placement_exercises()
