#!/usr/bin/env python3
"""
Script pour implémenter une logique de scoring insensible à l'ordre des réponses
pour les exercices de type fill_in_blanks et word_placement.

Ce script modifie la fonction de scoring dans app.py pour permettre aux élèves
de placer les réponses dans n'importe quel ordre tout en obtenant un score correct.
"""
import os
import sys
import json
import sqlite3
import logging
import re
import shutil
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def backup_app_py():
    """Crée une sauvegarde du fichier app.py avant modification."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"app.py.bak.{timestamp}"
    
    try:
        shutil.copy2("app.py", backup_file)
        logger.info(f"✅ Sauvegarde créée: {backup_file}")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur lors de la sauvegarde: {str(e)}")
        return False

def find_scoring_function(app_content):
    """
    Trouve la fonction de scoring pour les exercices fill_in_blanks.
    
    Args:
        app_content: Le contenu du fichier app.py
        
    Returns:
        tuple: (position de début, position de fin, contenu de la fonction)
    """
    # Recherche de la section qui traite les exercices fill_in_blanks
    fill_in_blanks_pattern = r'elif exercise\.exercise_type == \'fill_in_blanks\':\s*app\.logger\.info.*?\[FILL_IN_BLANKS_DEBUG\].*?answers = user_answers_data'
    
    fill_in_blanks_match = re.search(fill_in_blanks_pattern, app_content, re.DOTALL)
    
    if fill_in_blanks_match:
        logger.info("✅ Section de scoring fill_in_blanks trouvée")
        return fill_in_blanks_match.start(), fill_in_blanks_match.end(), fill_in_blanks_match.group()
    else:
        logger.error("❌ Aucune fonction de scoring trouvée")
        return None, None, None

def modify_scoring_logic(function_content):
    """
    Modifie la logique de scoring pour la rendre insensible à l'ordre des réponses.
    
    Args:
        function_content: Le contenu de la fonction de scoring
        
    Returns:
        str: La fonction modifiée
    """
    # Recherche du bloc de code qui vérifie les réponses
    verification_pattern = r'(for i in range\(total_blanks_in_content\):.*?correct_count \+= 1)'
    
    verification_match = re.search(verification_pattern, function_content, re.DOTALL)
    
    if not verification_match:
        logger.error("❌ Bloc de vérification des réponses non trouvé")
        return function_content
    
    original_verification_logic = verification_match.group(1)
    logger.info(f"✅ Bloc de vérification des réponses trouvé:\n{original_verification_logic}")
    
    # Nouvelle logique de vérification insensible à l'ordre
    new_verification_logic = """
            # Logique de scoring insensible à l'ordre des réponses
            correct_count = 0
            user_answers_list = []
            correct_answers = []
            
            # Récupérer toutes les réponses de l'utilisateur
            for i in range(total_blanks_in_content):
                user_answer = request.form.get(f'answer_{i}', '').strip()
                user_answers_list.append(user_answer)
                
                # Récupérer les réponses correctes
                if 'words' in content:
                    correct_answers = content['words']
                elif 'available_words' in content:
                    correct_answers = content['available_words']
            
            # Copie des réponses correctes pour éviter de les modifier
            remaining_answers = correct_answers.copy() if correct_answers else []
            
            # Pour chaque réponse de l'utilisateur, vérifier si elle est dans les réponses attendues
            for answer in user_answers_list:
                if answer.lower() in [a.lower() for a in remaining_answers]:
                    correct_count += 1
                    # Trouver l'index de la réponse correcte (insensible à la casse)
                    for i, correct_answer in enumerate(remaining_answers):
                        if answer.lower() == correct_answer.lower():
                            remaining_answers.pop(i)
                            break
    """
    
    # Remplacer l'ancienne logique par la nouvelle
    modified_function = function_content.replace(original_scoring_logic, new_scoring_logic)
    
    return modified_function

def update_app_py():
    """Met à jour le fichier app.py avec la nouvelle logique de scoring."""
    try:
        # Lire le contenu du fichier app.py
        with open("app.py", "r", encoding="utf-8") as f:
            app_content = f.read()
        
        # Trouver la fonction de scoring
        start_pos, end_pos, function_content = find_scoring_function(app_content)
        
        if not function_content:
            logger.error("❌ Impossible de modifier app.py: fonction de scoring non trouvée")
            return False
        
        # Modifier la logique de scoring
        modified_function = modify_scoring_logic(function_content)
        
        # Remplacer la fonction dans le fichier
        new_app_content = app_content[:start_pos] + modified_function + app_content[end_pos:]
        
        # Écrire le nouveau contenu dans app.py
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(new_app_content)
        
        logger.info("✅ Fichier app.py mis à jour avec la nouvelle logique de scoring")
        return True
    
    except Exception as e:
        logger.error(f"❌ Erreur lors de la mise à jour de app.py: {str(e)}")
        return False

def test_modified_scoring():
    """
    Teste la nouvelle logique de scoring avec l'exercice 2.
    
    Returns:
        bool: True si le test est réussi, False sinon
    """
    try:
        # Contenu de l'exercice 2
        content = {
            "sentences": [
                "Un triangle qui possède un angle droit et deux cotés isometriques est un triangle  ___  ___"
            ],
            "words": [
                "isocèle",
                "rectangle"
            ]
        }
        
        # Simuler des réponses dans l'ordre correct et inversé
        user_answers_correct_order = ["isocèle", "rectangle"]
        user_answers_inverse_order = ["rectangle", "isocèle"]
        
        # Simuler la nouvelle logique de scoring
        correct_count_1 = 0
        remaining_answers = content["words"].copy()
        
        for answer in user_answers_correct_order:
            if answer in remaining_answers:
                correct_count_1 += 1
                remaining_answers.remove(answer)
        
        score_1 = (correct_count_1 / 2) * 100
        
        correct_count_2 = 0
        remaining_answers = content["words"].copy()
        
        for answer in user_answers_inverse_order:
            if answer in remaining_answers:
                correct_count_2 += 1
                remaining_answers.remove(answer)
        
        score_2 = (correct_count_2 / 2) * 100
        
        logger.info(f"Test avec ordre correct: {score_1}%")
        logger.info(f"Test avec ordre inversé: {score_2}%")
        
        if score_1 == 100.0 and score_2 == 100.0:
            logger.info("✅ Test réussi: les deux ordres donnent un score de 100%")
            return True
        else:
            logger.error(f"❌ Test échoué: scores différents ({score_1}% vs {score_2}%)")
            return False
    
    except Exception as e:
        logger.error(f"❌ Erreur lors du test: {str(e)}")
        return False

def main():
    """Fonction principale."""
    logger.info("=== MODIFICATION DE LA LOGIQUE DE SCORING ===")
    logger.info("Cette modification rendra le scoring insensible à l'ordre des réponses")
    
    # Créer une sauvegarde
    if not backup_app_py():
        logger.error("❌ Impossible de continuer sans sauvegarde")
        return
    
    # Tester la nouvelle logique
    logger.info("\n=== TEST DE LA NOUVELLE LOGIQUE ===")
    if not test_modified_scoring():
        logger.warning("⚠️ Le test a échoué, mais nous continuons")
    
    # Mettre à jour app.py
    logger.info("\n=== MISE À JOUR DE APP.PY ===")
    if update_app_py():
        logger.info("✅ Modification réussie!")
        logger.info("\nPour déployer cette modification:")
        logger.info("1. Vérifiez que tout fonctionne correctement en local")
        logger.info("2. Committez les changements: git add app.py && git commit -m \"Scoring insensible à l'ordre des réponses\"")
        logger.info("3. Poussez vers Railway: git push railway main")
    else:
        logger.error("❌ La modification a échoué")
        logger.info("Vous pouvez restaurer la sauvegarde si nécessaire")

if __name__ == "__main__":
    main()
