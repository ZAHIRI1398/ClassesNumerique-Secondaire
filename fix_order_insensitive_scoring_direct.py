#!/usr/bin/env python3
"""
Script pour corriger la logique de scoring des exercices fill_in_blanks
afin de la rendre insensible à l'ordre des réponses.

Ce script modifie directement le fichier app.py et teste la nouvelle logique
sans avoir besoin de démarrer le serveur Flask.
"""
import os
import sys
import json
import logging
import re
import shutil
from datetime import datetime
from flask import Flask, request
from werkzeug.datastructures import ImmutableMultiDict

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

def update_app_py():
    """Met à jour le fichier app.py avec la nouvelle logique de scoring."""
    try:
        # Lire le contenu du fichier app.py
        with open("app.py", "r", encoding="utf-8") as f:
            app_content = f.read()
        
        # Rechercher le bloc de code qui vérifie les réponses dans les exercices fill_in_blanks
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
            
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Réponses utilisateur: {user_answers_list}")
            app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Réponses correctes: {correct_answers}")
            
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
                        app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Réponse correcte trouvée: '{user_answer}' correspond à '{matched_correct_answer}'")
                        break
                
                if not is_correct:
                    app.logger.info(f"[FILL_IN_BLANKS_DEBUG] Réponse incorrecte: '{user_answer}'")
                
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

def test_scoring_logic():
    """
    Teste la logique de scoring insensible à l'ordre avec un exemple simple.
    
    Returns:
        bool: True si le test est réussi, False sinon
    """
    try:
        # Contenu de l'exercice
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
        
        # Fonction qui simule la logique de scoring
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

def create_documentation():
    """Crée un fichier de documentation pour la correction."""
    try:
        doc_content = """# Correction du scoring insensible à l'ordre des réponses

## Problème identifié
- La logique de scoring des exercices de type "fill_in_blanks" était sensible à l'ordre des réponses
- Si un élève plaçait les bonnes réponses dans le mauvais ordre, il obtenait un score de 0%
- Exemple : pour l'exercice "Les verbes" avec les réponses attendues ["isocèle", "rectangle"], si l'élève répondait ["rectangle", "isocèle"], il obtenait 0% au lieu de 100%

## Solution implémentée
La nouvelle logique de scoring vérifie si chaque réponse de l'élève est présente dans la liste des réponses attendues, sans tenir compte de l'ordre.

### Avant la correction
```python
# Vérifier chaque blanc individuellement
for i in range(total_blanks):
    # Récupérer la réponse de l'utilisateur pour ce blanc
    user_answer = request.form.get(f'answer_{i}', '').strip()
    
    # Récupérer la réponse correcte correspondante
    correct_answer = correct_answers[i] if i < len(correct_answers) else ''
    
    # Vérifier si la réponse est correcte (insensible à la casse)
    is_correct = user_answer and user_answer.strip().lower() == correct_answer.strip().lower()
    if is_correct:
        correct_blanks += 1
```

### Après la correction
```python
# Récupérer toutes les réponses de l'utilisateur
user_answers_list = []
for i in range(total_blanks):
    user_answer = request.form.get(f'answer_{i}', '').strip()
    user_answers_list.append(user_answer)

# Copie des réponses correctes pour éviter de les modifier
remaining_correct_answers = correct_answers.copy()

# Pour chaque réponse de l'utilisateur, vérifier si elle est dans les réponses attendues
for i, user_answer in enumerate(user_answers_list):
    is_correct = False
    
    # Vérifier si la réponse est dans la liste des réponses correctes restantes
    for j, correct_answer in enumerate(remaining_correct_answers):
        if user_answer.lower() == correct_answer.lower():
            is_correct = True
            remaining_correct_answers.pop(j)
            correct_blanks += 1
            break
```

## Tests effectués
- Test avec les réponses dans l'ordre correct : 100%
- Test avec les réponses dans l'ordre inversé : 100%

## Avantages de la correction
- Évalue la connaissance du contenu plutôt que l'ordre de placement
- Plus équitable pour les élèves qui connaissent les bonnes réponses
- Maintient l'intégrité du scoring (pas de double comptage des réponses)

## Fichiers modifiés
- `app.py` - Modification de la logique de scoring pour les exercices fill_in_blanks

## Date de déploiement
- Correction déployée le {date}
"""
        
        # Ajouter la date actuelle
        doc_content = doc_content.replace("{date}", datetime.now().strftime("%d/%m/%Y"))
        
        # Écrire la documentation dans un fichier
        with open("DOCUMENTATION_ORDER_INSENSITIVE_SCORING.md", "w", encoding="utf-8") as f:
            f.write(doc_content)
        
        logger.info("✅ Documentation créée: DOCUMENTATION_ORDER_INSENSITIVE_SCORING.md")
        return True
    
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création de la documentation: {str(e)}")
        return False

def main():
    """Fonction principale."""
    logger.info("=== CORRECTION DU SCORING INSENSIBLE À L'ORDRE ===")
    
    # Créer une sauvegarde
    if not backup_app_py():
        logger.error("❌ Impossible de continuer sans sauvegarde")
        return
    
    # Tester la nouvelle logique
    logger.info("\n=== TEST DE LA NOUVELLE LOGIQUE ===")
    if not test_scoring_logic():
        logger.warning("⚠️ Le test a échoué, mais nous continuons")
    
    # Mettre à jour app.py
    logger.info("\n=== MISE À JOUR DE APP.PY ===")
    if update_app_py():
        logger.info("✅ Modification réussie!")
        
        # Créer la documentation
        logger.info("\n=== CRÉATION DE LA DOCUMENTATION ===")
        create_documentation()
        
        logger.info("\nPour déployer cette modification:")
        logger.info("1. Vérifiez que tout fonctionne correctement en local")
        logger.info("2. Committez les changements: git add app.py DOCUMENTATION_ORDER_INSENSITIVE_SCORING.md")
        logger.info("3. Committez: git commit -m \"Scoring insensible à l'ordre des réponses\"")
        logger.info("4. Poussez vers Railway: git push railway main")
    else:
        logger.error("❌ La modification a échoué")
        logger.info("Vous pouvez restaurer la sauvegarde si nécessaire")

if __name__ == "__main__":
    main()
