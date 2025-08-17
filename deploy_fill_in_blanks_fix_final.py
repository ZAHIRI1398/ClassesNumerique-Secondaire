import os
import sys
import subprocess
import logging
import time
from datetime import datetime

# Configuration
LOG_FILE = f'deploy_fill_in_blanks_fix_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
COMMIT_MESSAGE = "Fix: Correction du problème de comptage des réponses dans les exercices fill_in_blanks"
BRANCH_NAME = "main"  # ou master selon votre configuration

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

def run_command(command, cwd=None):
    """Exécute une commande shell et retourne le résultat"""
    try:
        logger.info(f"Exécution de la commande: {command}")
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            cwd=cwd,
            universal_newlines=True
        )
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            logger.error(f"Erreur lors de l'exécution de la commande: {stderr}")
            return False, stderr
        
        logger.info(f"Commande exécutée avec succès: {stdout}")
        return True, stdout
    except Exception as e:
        logger.error(f"Exception lors de l'exécution de la commande: {e}")
        return False, str(e)

def check_git_status():
    """Vérifie l'état du dépôt Git"""
    success, output = run_command("git status")
    if not success:
        return False
    
    if "nothing to commit" in output:
        logger.info("Aucune modification à déployer.")
        return False
    
    return True

def verify_app_py_changes():
    """Vérifie que app.py contient les modifications nécessaires"""
    try:
        with open('app.py', 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Vérifier que le code contient la correction pour l'insensibilité à l'ordre
        if "remaining_correct_answers = correct_answers.copy()" not in content:
            logger.error("La correction pour l'insensibilité à l'ordre n'est pas présente dans app.py.")
            return False
        
        # Vérifier que le code utilise la bonne méthode pour calculer total_blanks
        if "total_blanks = max(total_blanks_in_content, len(correct_answers))" not in content:
            logger.error("La correction pour le calcul de total_blanks n'est pas présente dans app.py.")
            return False
        
        logger.info("Les modifications nécessaires sont présentes dans app.py.")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de app.py: {e}")
        return False

def stage_changes():
    """Ajoute les modifications à l'index Git"""
    success, _ = run_command("git add app.py")
    return success

def commit_changes():
    """Commit les modifications"""
    success, _ = run_command(f'git commit -m "{COMMIT_MESSAGE}"')
    return success

def push_changes():
    """Pousse les modifications vers le dépôt distant"""
    success, _ = run_command(f"git push origin {BRANCH_NAME}")
    return success

def check_deployment_status():
    """Vérifie l'état du déploiement sur Railway"""
    logger.info("Vérification de l'état du déploiement...")
    logger.info("Cette étape peut prendre quelques minutes.")
    
    # Simuler une attente pour le déploiement
    for i in range(5):
        logger.info(f"Attente du déploiement... {i+1}/5")
        time.sleep(2)
    
    logger.info("Le déploiement devrait être terminé. Vérifiez manuellement l'état sur Railway.")
    return True

def restart_app():
    """Redémarre l'application sur Railway"""
    logger.info("Pour redémarrer l'application sur Railway:")
    logger.info("1. Connectez-vous à votre compte Railway")
    logger.info("2. Accédez à votre projet")
    logger.info("3. Cliquez sur le service web")
    logger.info("4. Cliquez sur 'Redeploy'")
    logger.info("5. Attendez que le déploiement soit terminé")
    
    return True

def main():
    """Fonction principale"""
    global logger
    logger = setup_logging()
    
    logger.info("=== DÉPLOIEMENT DE LA CORRECTION POUR LES EXERCICES FILL_IN_BLANKS ===")
    
    # Vérifier que app.py contient les modifications nécessaires
    if not verify_app_py_changes():
        logger.error("Les modifications nécessaires ne sont pas présentes dans app.py. Arrêt du déploiement.")
        sys.exit(1)
    
    # Vérifier l'état du dépôt Git
    if not check_git_status():
        logger.warning("Aucune modification à déployer ou problème avec Git. Vérifiez manuellement.")
        
        # Demander à l'utilisateur s'il souhaite continuer
        response = input("Souhaitez-vous forcer le déploiement malgré tout ? (o/n): ")
        if response.lower() != 'o':
            logger.info("Déploiement annulé par l'utilisateur.")
            sys.exit(0)
    
    # Ajouter les modifications à l'index Git
    logger.info("Ajout des modifications à l'index Git...")
    if not stage_changes():
        logger.error("Impossible d'ajouter les modifications à l'index Git. Arrêt du déploiement.")
        sys.exit(1)
    
    # Commit les modifications
    logger.info("Commit des modifications...")
    if not commit_changes():
        logger.error("Impossible de commit les modifications. Arrêt du déploiement.")
        sys.exit(1)
    
    # Demander confirmation avant de pousser les modifications
    response = input("Êtes-vous sûr de vouloir déployer ces modifications ? (o/n): ")
    if response.lower() != 'o':
        logger.info("Déploiement annulé par l'utilisateur.")
        sys.exit(0)
    
    # Pousser les modifications
    logger.info("Déploiement des modifications...")
    if not push_changes():
        logger.error("Impossible de pousser les modifications. Vérifiez manuellement.")
        sys.exit(1)
    
    # Vérifier l'état du déploiement
    if not check_deployment_status():
        logger.warning("Impossible de vérifier l'état du déploiement. Vérifiez manuellement.")
    
    # Redémarrer l'application
    if not restart_app():
        logger.warning("Impossible de redémarrer l'application. Redémarrez-la manuellement.")
    
    logger.info("Déploiement terminé avec succès.")
    logger.info(f"Résultats enregistrés dans {LOG_FILE}")

if __name__ == "__main__":
    main()
