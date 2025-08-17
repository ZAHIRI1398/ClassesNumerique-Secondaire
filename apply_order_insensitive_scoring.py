#!/usr/bin/env python3
"""
Script pour appliquer une logique de scoring insensible à l'ordre des réponses
pour les exercices de type fill_in_blanks.

Ce script modifie la fonction de scoring dans app.py pour permettre aux élèves
de placer les réponses dans n'importe quel ordre tout en obtenant un score correct.
"""
import os
import sys
import json
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

def test_modified_scoring():
    """
    Teste la nouvelle logique de scoring avec un exemple simple.
    
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
        def calculate_score(user_answers, correct_answers):
            correct_blanks = 0
            total_blanks = len(correct_answers)
            
            # Copie des réponses correctes pour éviter de les modifier
            remaining_answers = correct_answers.copy()
            
            # Pour chaque réponse de l'utilisateur, vérifier si elle est dans les réponses attendues
            for answer in user_answers:
                answer_lower = answer.lower()
                for i, correct_answer in enumerate(remaining_answers):
                    if answer_lower == correct_answer.lower():
                        correct_blanks += 1
                        remaining_answers.pop(i)
                        break
            
            return (correct_blanks / total_blanks) * 100 if total_blanks > 0 else 0
        
        # Tester avec l'ordre correct
        score_1 = calculate_score(user_answers_correct_order, content["words"])
        
        # Tester avec l'ordre inversé
        score_2 = calculate_score(user_answers_inverse_order, content["words"])
        
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

def update_app_py():
    """Met à jour le fichier app.py avec la nouvelle logique de scoring."""
    try:
        # Lire le contenu du fichier app.py
        with open("app.py", "r", encoding="utf-8") as f:
            app_content = f.read()
        
        # Rechercher le bloc de code qui vérifie les réponses dans les exercices fill_in_blanks
        # Nous cherchons la section qui commence par la vérification de chaque blanc
        pattern = r'(# Vérifier chaque blanc individuellement.*?score = \(correct_blanks / total_blanks\) \* 100 if total_blanks > 0 else 0)'
        
        match = re.search(pattern, app_content, re.DOTALL)
        
        if not match:
            logger.error("❌ Section de vérification des réponses non trouvée")
            return False
        
        original_code = match.group(1)
        
        # Nouvelle logique de scoring insensible à l'ordre
        new_code = """# Vérifier chaque blanc individuellement - Logique insensible à l'ordre
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Traitement de {total_blanks} blancs au total")
            
            # Récupérer toutes les réponses de l'utilisateur
            user_answers_list = []
            for i in range(total_blanks):
                user_answer = request.form.get(f'answer_{i}', '').strip()
                user_answers_list.append(user_answer)
                user_answers_data[f'answer_{i}'] = user_answer
            
            # Copie des réponses correctes pour éviter de les modifier
            remaining_correct_answers = correct_answers.copy() if correct_answers else []
            
            # Pour chaque réponse de l'utilisateur, vérifier si elle est dans les réponses attendues
            feedback_details = []
            for i, user_answer in enumerate(user_answers_list):
                is_correct = False
                matched_correct_answer = ""
                
                # Vérifier si la réponse est dans la liste des réponses correctes restantes
                for j, correct_answer in enumerate(remaining_correct_answers):
                    if user_answer.lower() == correct_answer.lower():
                        is_correct = True
                        matched_correct_answer = correct_answer
                        remaining_correct_answers.pop(j)
                        correct_blanks += 1
                        break
                
                # Déterminer l'index de la phrase à laquelle appartient ce blanc
                sentence_index = -1
                if 'sentences' in content:
                    blank_count = 0
                    for idx, sentence in enumerate(content['sentences']):
                        blanks_in_sentence = sentence.count('___')
                        if blank_count <= i < blank_count + blanks_in_sentence:
                            sentence_index = idx
                            break
                        blank_count += blanks_in_sentence
                
                # Créer le feedback pour ce blanc
                feedback_details.append({
                    'blank_index': i,
                    'user_answer': user_answer or '',
                    'correct_answer': matched_correct_answer if is_correct else correct_answers[i] if i < len(correct_answers) else '',
                    'is_correct': is_correct,
                    'status': 'Correct' if is_correct else f'Attendu: {correct_answers[i] if i < len(correct_answers) else ""}, Réponse: {user_answer or "Vide"}',
                    'sentence_index': sentence_index,
                    'sentence': content['sentences'][sentence_index] if sentence_index >= 0 and 'sentences' in content else ''
                })
            
            # Calculer le score final basé sur le nombre réel de blancs
            score = (correct_blanks / total_blanks) * 100 if total_blanks > 0 else 0"""
        
        # Remplacer l'ancien code par le nouveau
        modified_content = app_content.replace(original_code, new_code)
        
        # Écrire le nouveau contenu dans app.py
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(modified_content)
        
        logger.info("✅ Fichier app.py mis à jour avec la nouvelle logique de scoring insensible à l'ordre")
        return True
    
    except Exception as e:
        logger.error(f"❌ Erreur lors de la mise à jour de app.py: {str(e)}")
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
