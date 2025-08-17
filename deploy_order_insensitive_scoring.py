#!/usr/bin/env python3
"""
Script pour déployer la correction du scoring insensible à l'ordre des réponses.
Ce script vérifie que tout est prêt pour le déploiement, puis effectue les commandes git nécessaires.
"""
import os
import sys
import logging
import subprocess
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_files_exist():
    """Vérifie que tous les fichiers nécessaires existent."""
    required_files = [
        "app.py",
        "DOCUMENTATION_ORDER_INSENSITIVE_SCORING.md"
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            logger.error(f"❌ Fichier manquant: {file}")
            return False
    
    logger.info("✅ Tous les fichiers nécessaires sont présents")
    return True

def check_git_status():
    """Vérifie le statut git du projet."""
    try:
        # Vérifier si git est installé
        subprocess.run(["git", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Vérifier si le répertoire est un dépôt git
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Obtenir le statut git
        status = subprocess.run(["git", "status", "--porcelain"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Vérifier les fichiers modifiés
        modified_files = status.stdout.decode('utf-8').strip().split('\n')
        modified_files = [f for f in modified_files if f]
        
        if not modified_files:
            logger.warning("⚠️ Aucun fichier modifié détecté")
            return False
        
        # Vérifier si app.py est modifié
        app_py_modified = any("app.py" in f for f in modified_files)
        if not app_py_modified:
            logger.warning("⚠️ app.py n'a pas été modifié")
        
        logger.info(f"✅ Statut git vérifié: {len(modified_files)} fichier(s) modifié(s)")
        return True
    
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erreur git: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur lors de la vérification du statut git: {str(e)}")
        return False

def run_git_commands():
    """Exécute les commandes git pour déployer la correction."""
    try:
        # Ajouter les fichiers modifiés
        subprocess.run(["git", "add", "app.py", "DOCUMENTATION_ORDER_INSENSITIVE_SCORING.md"], check=True)
        logger.info("✅ Fichiers ajoutés au staging")
        
        # Commit des changements
        commit_message = "Scoring insensible à l'ordre des réponses pour les exercices fill_in_blanks"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        logger.info(f"✅ Commit créé: {commit_message}")
        
        # Demander confirmation avant de pousser vers Railway
        print("\n=== CONFIRMATION DE DÉPLOIEMENT ===")
        print("Vous êtes sur le point de déployer la correction vers Railway.")
        print("Cette action mettra à jour l'application en production.")
        confirmation = input("Êtes-vous sûr de vouloir continuer ? (o/n): ")
        
        if confirmation.lower() != 'o':
            logger.info("❌ Déploiement annulé par l'utilisateur")
            return False
        
        # Pousser vers Railway
        subprocess.run(["git", "push", "railway", "main"], check=True)
        logger.info("✅ Changements poussés vers Railway")
        
        return True
    
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erreur lors de l'exécution des commandes git: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur lors du déploiement: {str(e)}")
        return False

def main():
    """Fonction principale."""
    logger.info("=== DÉPLOIEMENT DE LA CORRECTION DU SCORING INSENSIBLE À L'ORDRE ===")
    
    # Vérifier que tous les fichiers nécessaires existent
    if not check_files_exist():
        logger.error("❌ Impossible de continuer: fichiers manquants")
        return
    
    # Vérifier le statut git
    if not check_git_status():
        logger.warning("⚠️ Vérifiez le statut git avant de continuer")
        proceed = input("Voulez-vous continuer malgré tout ? (o/n): ")
        if proceed.lower() != 'o':
            logger.info("❌ Déploiement annulé")
            return
    
    # Exécuter les commandes git
    if run_git_commands():
        logger.info("\n=== DÉPLOIEMENT RÉUSSI ===")
        logger.info("La correction du scoring insensible à l'ordre a été déployée avec succès!")
        logger.info(f"Date de déploiement: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        # Vérifier l'application après déploiement
        logger.info("\nPour vérifier que tout fonctionne correctement:")
        logger.info("1. Accédez à l'application: https://classesnumeriques.up.railway.app")
        logger.info("2. Connectez-vous avec un compte étudiant")
        logger.info("3. Testez l'exercice 'Les verbes' avec des réponses dans un ordre différent")
    else:
        logger.error("❌ Le déploiement a échoué")
        logger.info("Vérifiez les erreurs ci-dessus et réessayez")

if __name__ == "__main__":
    main()
