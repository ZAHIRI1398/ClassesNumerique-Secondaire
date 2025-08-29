"""
Script de test pour les routes de correction des images dans les exercices de type 'pairs'
"""
import os
import sys
import json
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"test_fix_pairs_routes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Ajouter le répertoire parent au chemin pour pouvoir importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importer les modules nécessaires
try:
    from fix_pairs_exercise_images import fix_all_pairs_exercises, fix_specific_exercise
    logger.info("Modules importés avec succès")
except ImportError as e:
    logger.error(f"Erreur lors de l'importation des modules: {str(e)}")
    sys.exit(1)

def test_fix_specific_exercise(exercise_id):
    """
    Teste la correction d'un exercice spécifique
    """
    logger.info(f"Test de correction de l'exercice {exercise_id}")
    try:
        success = fix_specific_exercise(exercise_id)
        if success:
            logger.info(f"✅ Correction de l'exercice {exercise_id} réussie")
        else:
            logger.warning(f"❌ Échec de la correction de l'exercice {exercise_id}")
        return success
    except Exception as e:
        logger.error(f"❌ Erreur lors de la correction de l'exercice {exercise_id}: {str(e)}")
        return False

def test_fix_all_exercises():
    """
    Teste la correction de tous les exercices de type 'pairs'
    """
    logger.info("Test de correction de tous les exercices de type 'pairs'")
    try:
        successful_fixes, failed_fixes = fix_all_pairs_exercises()
        logger.info(f"✅ Correction terminée. Réussites: {successful_fixes}, Échecs: {failed_fixes}")
        return successful_fixes, failed_fixes
    except Exception as e:
        logger.error(f"❌ Erreur lors de la correction des exercices: {str(e)}")
        return 0, 0

def main():
    """
    Fonction principale pour tester les routes
    """
    logger.info("=== Début des tests des routes de correction des images ===")
    
    # Test de correction d'un exercice spécifique
    # Remplacer 123 par un ID d'exercice valide de type 'pairs'
    exercise_id = input("Entrez l'ID d'un exercice de type 'pairs' à corriger (ou laissez vide pour ignorer): ")
    if exercise_id:
        try:
            exercise_id = int(exercise_id)
            test_fix_specific_exercise(exercise_id)
        except ValueError:
            logger.error("L'ID d'exercice doit être un nombre entier")
    
    # Test de correction de tous les exercices
    test_all = input("Voulez-vous tester la correction de tous les exercices de type 'pairs'? (o/n): ")
    if test_all.lower() == 'o':
        successful_fixes, failed_fixes = test_fix_all_exercises()
        print(f"Correction terminée. Réussites: {successful_fixes}, Échecs: {failed_fixes}")
    
    logger.info("=== Fin des tests des routes de correction des images ===")

if __name__ == "__main__":
    main()
