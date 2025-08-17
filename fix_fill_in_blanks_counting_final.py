import os
import sys
import re
import shutil
import logging
from datetime import datetime

# Configuration
APP_PY_PATH = 'app.py'
BACKUP_PATH = f'app.py.bak.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
LOG_FILE = f'fix_fill_in_blanks_counting_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

def setup_logging():
    """Configure le système de logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def backup_file(file_path, backup_path):
    """Crée une sauvegarde du fichier"""
    try:
        shutil.copy2(file_path, backup_path)
        logger.info(f"Sauvegarde créée: {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la création de la sauvegarde: {e}")
        return False

def fix_fill_in_blanks_counting(file_path):
    """Corrige le problème de comptage des réponses dans les exercices fill_in_blanks"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        logger.info("Recherche du code de scoring fill_in_blanks...")
        
        # Vérifier si le code contient déjà la correction pour l'insensibilité à l'ordre
        if "remaining_correct_answers = correct_answers.copy()" in content:
            logger.info("La correction pour l'insensibilité à l'ordre est déjà présente.")
        else:
            logger.error("La correction pour l'insensibilité à l'ordre n'est pas présente dans le code.")
            return False
        
        # Rechercher et corriger le problème de comptage des réponses
        # Nous devons nous assurer que le nombre total de blancs est correctement calculé
        
        # Rechercher le pattern où le nombre total de blancs est défini
        total_blanks_pattern = re.compile(r'total_blanks\s*=\s*max\(total_blanks_in_content,\s*len\(correct_answers\)\)')
        
        if total_blanks_pattern.search(content):
            logger.info("Le code utilise déjà max(total_blanks_in_content, len(correct_answers)) pour calculer total_blanks.")
            
            # Vérifier si le code utilise correctement les réponses correctes
            if "correct_answers = content.get('words', [])" in content and "if not correct_answers:" in content and "correct_answers = content.get('available_words', [])" in content:
                logger.info("Le code récupère correctement les réponses correctes depuis 'words' ou 'available_words'.")
            else:
                logger.warning("Le code pourrait ne pas récupérer correctement les réponses correctes.")
            
            # Vérifier si le code traite correctement les blancs dans le contenu
            if "if 'sentences' in content:" in content and "sentences_blanks = sum(s.count('___') for s in content['sentences'])" in content:
                logger.info("Le code compte correctement les blancs dans 'sentences'.")
            else:
                logger.warning("Le code pourrait ne pas compter correctement les blancs dans 'sentences'.")
            
            # Vérifier si le code traite correctement le cas où il n'y a pas de réponses correctes
            if "remaining_correct_answers = correct_answers.copy() if correct_answers else []" in content:
                logger.info("Le code gère correctement le cas où il n'y a pas de réponses correctes.")
            else:
                logger.warning("Le code pourrait ne pas gérer correctement le cas où il n'y a pas de réponses correctes.")
            
            # Pas de modification nécessaire si tout est correct
            logger.info("Aucune modification n'est nécessaire pour le comptage des réponses.")
            return True
        
        # Si nous arrivons ici, c'est que le code n'utilise pas la bonne méthode pour calculer total_blanks
        logger.warning("Le code n'utilise pas la bonne méthode pour calculer total_blanks.")
        
        # Rechercher le pattern à remplacer
        pattern_to_replace = re.compile(r'(total_blanks\s*=\s*)[^;\n]+')
        
        # Remplacer par la bonne méthode
        modified_content = pattern_to_replace.sub(r'\1max(total_blanks_in_content, len(correct_answers))', content)
        
        if content == modified_content:
            logger.warning("Aucune modification n'a été effectuée. Le pattern n'a pas été trouvé.")
            return False
        
        # Écrire le contenu modifié dans le fichier
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)
        
        logger.info("Le code a été modifié pour corriger le comptage des réponses.")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la correction du code: {e}")
        return False

def verify_fix():
    """Vérifie que la correction a été appliquée correctement"""
    try:
        with open(APP_PY_PATH, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Vérifier que le code contient la correction
        if "total_blanks = max(total_blanks_in_content, len(correct_answers))" in content:
            logger.info("Vérification réussie: La correction a été appliquée correctement.")
            return True
        else:
            logger.warning("Vérification échouée: La correction n'a pas été appliquée correctement.")
            return False
    except Exception as e:
        logger.error(f"Erreur lors de la vérification: {e}")
        return False

def main():
    """Fonction principale"""
    global logger
    logger = setup_logging()
    
    logger.info("=== CORRECTION DU COMPTAGE DES RÉPONSES DANS LES EXERCICES FILL_IN_BLANKS ===")
    
    # Vérifier si le fichier app.py existe
    if not os.path.exists(APP_PY_PATH):
        logger.error(f"Le fichier {APP_PY_PATH} n'existe pas.")
        sys.exit(1)
    
    # Créer une sauvegarde du fichier
    if not backup_file(APP_PY_PATH, BACKUP_PATH):
        logger.error("Impossible de créer une sauvegarde. Arrêt du script.")
        sys.exit(1)
    
    # Corriger le code
    if fix_fill_in_blanks_counting(APP_PY_PATH):
        logger.info("Correction appliquée avec succès.")
        
        # Vérifier la correction
        if verify_fix():
            logger.info("La correction a été vérifiée et est correcte.")
        else:
            logger.warning("La correction n'a pas pu être vérifiée.")
    else:
        logger.error("La correction n'a pas pu être appliquée.")
        logger.info(f"Vous pouvez restaurer la sauvegarde avec: copy {BACKUP_PATH} {APP_PY_PATH}")
    
    logger.info(f"Correction terminée. Résultats enregistrés dans {LOG_FILE}")

if __name__ == "__main__":
    main()
