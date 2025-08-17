#!/usr/bin/env python3
"""
Script pour déployer la correction complète du scoring pour les exercices
- fill_in_blanks (texte à trous)
- word_placement (mots à placer)

Ce script:
1. Vérifie que les corrections sont présentes dans app.py
2. Commit et push les changements vers GitHub
3. Vérifie le déploiement sur Railway
"""

import os
import sys
import time
import subprocess
import requests
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# URL de l'application Railway
RAILWAY_URL = "https://classenumerique.up.railway.app"

def check_app_py_corrections():
    """Vérifie que les corrections sont présentes dans app.py"""
    logger.info("Vérification des corrections dans app.py...")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier la correction pour fill_in_blanks
        fill_in_blanks_fixed = False
        if "if 'sentences' in content:" in content and "elif 'text' in content:" in content:
            logger.info("✅ Correction pour fill_in_blanks trouvée")
            fill_in_blanks_fixed = True
        else:
            logger.warning("❌ Correction pour fill_in_blanks NON trouvée")
        
        # Vérifier la correction pour word_placement
        word_placement_fixed = False
        if "total_blanks_in_sentences = sum(s.count('___') for s in sentences)" in content:
            logger.info("✅ Correction pour word_placement trouvée")
            word_placement_fixed = True
        else:
            logger.warning("❌ Correction pour word_placement NON trouvée")
            
            # Appliquer la correction pour word_placement si nécessaire
            if not word_placement_fixed:
                logger.info("Application de la correction pour word_placement...")
                
                old_code = """    elif exercise.exercise_type == 'word_placement':
        print("\\n=== DÉBUT SCORING WORD_PLACEMENT ===")
        content = exercise.get_content()
        print(f"[WORD_PLACEMENT_DEBUG] Content: {content}")
        
        if not isinstance(content, dict) or 'sentences' not in content or 'answers' not in content:
            print("[WORD_PLACEMENT_DEBUG] Structure invalide!")
            flash('Structure de l\\'exercice invalide.', 'error')
            return redirect(url_for('view_exercise', exercise_id=exercise_id))

        sentences = content['sentences']
        correct_answers = content['answers']
        total_blanks = len(correct_answers)
        correct_count = 0"""

                new_code = """    elif exercise.exercise_type == 'word_placement':
        print("\\n=== DÉBUT SCORING WORD_PLACEMENT ===")
        content = exercise.get_content()
        print(f"[WORD_PLACEMENT_DEBUG] Content: {content}")
        
        if not isinstance(content, dict) or 'sentences' not in content or 'answers' not in content:
            print("[WORD_PLACEMENT_DEBUG] Structure invalide!")
            flash('Structure de l\\'exercice invalide.', 'error')
            return redirect(url_for('view_exercise', exercise_id=exercise_id))

        sentences = content['sentences']
        correct_answers = content['answers']
        
        # CORRECTION: Compter le nombre réel de blancs dans les phrases
        total_blanks_in_sentences = sum(s.count('___') for s in sentences)
        total_blanks = max(total_blanks_in_sentences, len(correct_answers))
        correct_count = 0"""
                
                # Remplacer le code
                modified_content = content.replace(old_code, new_code)
                
                # Vérifier si le remplacement a été effectué
                if modified_content != content:
                    with open('app.py', 'w', encoding='utf-8') as f:
                        f.write(modified_content)
                    logger.info("✅ Correction pour word_placement appliquée avec succès")
                    word_placement_fixed = True
                else:
                    logger.error("❌ Impossible d'appliquer la correction pour word_placement")
        
        return fill_in_blanks_fixed and word_placement_fixed
    
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des corrections: {str(e)}")
        return False

def commit_and_push():
    """Commit et push les changements vers GitHub"""
    logger.info("Commit et push des changements...")
    
    try:
        # Vérifier s'il y a des changements à committer
        status = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if not status.stdout.strip():
            logger.info("Aucun changement à committer")
            return True
        
        # Ajouter les changements
        subprocess.run(['git', 'add', 'app.py'], check=True)
        
        # Commit
        commit_message = "Fix: Correction du scoring pour les exercices fill_in_blanks et word_placement"
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        # Push
        subprocess.run(['git', 'push'], check=True)
        
        logger.info("✅ Changements committés et pushés avec succès")
        return True
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur lors du commit/push: {str(e)}")
        return False

def check_railway_deployment():
    """Vérifie le déploiement sur Railway"""
    logger.info("Vérification du déploiement sur Railway...")
    
    max_retries = 10
    retry_interval = 30  # secondes
    
    for i in range(max_retries):
        try:
            logger.info(f"Tentative {i+1}/{max_retries}...")
            
            response = requests.get(RAILWAY_URL, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"✅ Application accessible sur {RAILWAY_URL}")
                
                # Vérifier si la page contient du contenu attendu
                if "Classe Numérique" in response.text:
                    logger.info("✅ Contenu de la page vérifié")
                    return True
                else:
                    logger.warning("⚠️ La page ne contient pas le contenu attendu")
            else:
                logger.warning(f"⚠️ Code de statut: {response.status_code}")
            
            if i < max_retries - 1:
                logger.info(f"Attente de {retry_interval} secondes avant la prochaine tentative...")
                time.sleep(retry_interval)
        
        except requests.RequestException as e:
            logger.warning(f"Erreur de connexion: {str(e)}")
            
            if i < max_retries - 1:
                logger.info(f"Attente de {retry_interval} secondes avant la prochaine tentative...")
                time.sleep(retry_interval)
    
    logger.error("❌ Échec de la vérification du déploiement après plusieurs tentatives")
    return False

def main():
    """Fonction principale"""
    logger.info("=== DÉPLOIEMENT DE LA CORRECTION COMPLÈTE DU SCORING ===")
    
    # 1. Vérifier les corrections
    corrections_ok = check_app_py_corrections()
    if not corrections_ok:
        logger.error("❌ Les corrections ne sont pas complètes")
        return
    
    # 2. Commit et push
    push_ok = commit_and_push()
    if not push_ok:
        logger.error("❌ Échec du commit/push")
        return
    
    # 3. Vérifier le déploiement
    logger.info("Attente du déclenchement du déploiement Railway (30 secondes)...")
    time.sleep(30)
    
    deployment_ok = check_railway_deployment()
    if deployment_ok:
        logger.info("""
=== DÉPLOIEMENT RÉUSSI ===

La correction complète du scoring pour les exercices fill_in_blanks et word_placement
a été déployée avec succès sur Railway.

Vous pouvez maintenant vérifier que:
1. L'exercice "Les coordonnées" affiche un score correct
2. Tous les exercices de type texte à trous fonctionnent correctement
3. Tous les exercices de type mots à placer fonctionnent correctement

Pour diagnostiquer d'éventuels problèmes en production, utilisez:
- debug_railway_fill_in_blanks.py
- debug_railway_coordonnees.py
""")
    else:
        logger.error("""
=== ÉCHEC DU DÉPLOIEMENT ===

Le déploiement n'a pas pu être vérifié. Vérifiez:
1. L'état du déploiement sur Railway
2. Les logs de l'application
3. La connectivité réseau
""")

if __name__ == "__main__":
    main()
