"""
Script pour corriger les problèmes d'images 404 dans les exercices de type 'pairs'
Ce script:
1. Identifie tous les exercices de type 'pairs' dans la base de données
2. Normalise les chemins d'images dans leur contenu JSON
3. Copie les fichiers physiques vers les nouveaux emplacements normalisés
4. Met à jour la base de données avec les nouveaux chemins
"""

import os
import sys
import json
import logging
from datetime import datetime

# Configuration du logging
log_filename = f"fix_pairs_images_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Ajouter le répertoire courant au path pour les imports
sys.path.append(os.getcwd())

# Import des modules nécessaires
try:
    from app import app, db
    from models import Exercise
    from image_file_mover import process_pairs_exercise_images
    logger.info("Modules importés avec succès")
except ImportError as e:
    logger.error(f"Erreur lors de l'import des modules: {str(e)}")
    sys.exit(1)

def fix_all_pairs_exercises():
    """
    Corrige tous les exercices de type 'pairs' dans la base de données
    """
    with app.app_context():
        # Récupérer tous les exercices de type 'pairs'
        pairs_exercises = Exercise.query.filter_by(type='pairs').all()
        logger.info(f"Nombre d'exercices de type 'pairs' trouvés: {len(pairs_exercises)}")
        
        # Compteurs pour les statistiques
        total_exercises = len(pairs_exercises)
        processed_exercises = 0
        successful_fixes = 0
        failed_fixes = 0
        
        # Traiter chaque exercice
        for exercise in pairs_exercises:
            processed_exercises += 1
            logger.info(f"Traitement de l'exercice {exercise.id} ({processed_exercises}/{total_exercises})")
            
            try:
                # Vérifier si l'exercice a un contenu
                if not exercise.content:
                    logger.warning(f"L'exercice {exercise.id} n'a pas de contenu, ignoré")
                    failed_fixes += 1
                    continue
                
                # Parser le contenu JSON
                content = json.loads(exercise.content)
                
                # Traiter les images
                success, updated_content = process_pairs_exercise_images(content, app.root_path)
                
                if success:
                    # Mettre à jour le contenu de l'exercice
                    exercise.content = json.dumps(updated_content)
                    db.session.commit()
                    logger.info(f"Exercice {exercise.id} corrigé avec succès")
                    successful_fixes += 1
                else:
                    logger.warning(f"Échec de la correction de l'exercice {exercise.id}")
                    failed_fixes += 1
            
            except Exception as e:
                logger.error(f"Erreur lors du traitement de l'exercice {exercise.id}: {str(e)}")
                failed_fixes += 1
        
        # Afficher les statistiques
        logger.info("=== Statistiques ===")
        logger.info(f"Total des exercices traités: {processed_exercises}")
        logger.info(f"Corrections réussies: {successful_fixes}")
        logger.info(f"Échecs: {failed_fixes}")
        
        return successful_fixes, failed_fixes

def fix_specific_exercise(exercise_id):
    """
    Corrige un exercice spécifique de type 'pairs'
    
    Args:
        exercise_id (int): ID de l'exercice à corriger
        
    Returns:
        bool: True si la correction a réussi, False sinon
    """
    with app.app_context():
        # Récupérer l'exercice
        exercise = Exercise.query.get(exercise_id)
        
        if not exercise:
            logger.error(f"Exercice {exercise_id} non trouvé")
            return False
        
        if exercise.type != 'pairs':
            logger.warning(f"L'exercice {exercise_id} n'est pas de type 'pairs' (type: {exercise.type})")
            return False
        
        try:
            # Vérifier si l'exercice a un contenu
            if not exercise.content:
                logger.warning(f"L'exercice {exercise_id} n'a pas de contenu")
                return False
            
            # Parser le contenu JSON
            content = json.loads(exercise.content)
            
            # Traiter les images
            success, updated_content = process_pairs_exercise_images(content, app.root_path)
            
            if success:
                # Mettre à jour le contenu de l'exercice
                exercise.content = json.dumps(updated_content)
                db.session.commit()
                logger.info(f"Exercice {exercise_id} corrigé avec succès")
                return True
            else:
                logger.warning(f"Échec de la correction de l'exercice {exercise_id}")
                return False
        
        except Exception as e:
            logger.error(f"Erreur lors du traitement de l'exercice {exercise_id}: {str(e)}")
            return False

def create_route_handler():
    """
    Crée une fonction de gestionnaire de route pour Flask
    à intégrer dans app.py
    """
    code = """
@app.route('/admin/fix-pairs-images', methods=['GET'])
@login_required
@admin_required
def fix_pairs_images():
    from fix_pairs_exercise_images import fix_all_pairs_exercises
    
    try:
        successful_fixes, failed_fixes = fix_all_pairs_exercises()
        flash(f'Correction des images terminée. Réussites: {successful_fixes}, Échecs: {failed_fixes}', 'success')
    except Exception as e:
        app.logger.error(f"Erreur lors de la correction des images: {str(e)}")
        flash(f'Erreur lors de la correction des images: {str(e)}', 'danger')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/fix-pairs-image/<int:exercise_id>', methods=['GET'])
@login_required
@admin_required
def fix_specific_pairs_image(exercise_id):
    from fix_pairs_exercise_images import fix_specific_exercise
    
    try:
        success = fix_specific_exercise(exercise_id)
        if success:
            flash(f'Correction des images de l\'exercice {exercise_id} réussie', 'success')
        else:
            flash(f'Échec de la correction des images de l\'exercice {exercise_id}', 'warning')
    except Exception as e:
        app.logger.error(f"Erreur lors de la correction des images de l'exercice {exercise_id}: {str(e)}")
        flash(f'Erreur lors de la correction des images: {str(e)}', 'danger')
    
    return redirect(url_for('view_exercise', exercise_id=exercise_id))
"""
    print("Code du gestionnaire de route à ajouter à app.py:")
    print(code)
    return code

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Mode exercice spécifique
        try:
            exercise_id = int(sys.argv[1])
            logger.info(f"Correction de l'exercice spécifique {exercise_id}")
            success = fix_specific_exercise(exercise_id)
            if success:
                logger.info(f"Exercice {exercise_id} corrigé avec succès")
            else:
                logger.error(f"Échec de la correction de l'exercice {exercise_id}")
        except ValueError:
            logger.error(f"ID d'exercice invalide: {sys.argv[1]}")
    else:
        # Mode tous les exercices
        logger.info("Correction de tous les exercices de type 'pairs'")
        successful_fixes, failed_fixes = fix_all_pairs_exercises()
        logger.info(f"Correction terminée. Réussites: {successful_fixes}, Échecs: {failed_fixes}")
        
        # Afficher le code du gestionnaire de route
        create_route_handler()
