#!/usr/bin/env python3
"""
Script pour tester spécifiquement le scoring de l'exercice 2 (Texte à trous - Les verbes)
avec différents scénarios de réponses.
"""
import json
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_exercise_2_scoring():
    """
    Teste le scoring de l'exercice 2 avec différents scénarios de réponses.
    """
    # Contenu de l'exercice 2 (extrait de la base de données)
    content = {
        "sentences": [
            "Un triangle qui possède un angle droit et deux cotés isometriques est un triangle  ___  ___"
        ],
        "words": [
            "isocèle",
            "rectangle"
        ]
    }
    
    logger.info("=== TEST DE SCORING POUR L'EXERCICE 2 ===")
    logger.info(f"Contenu: {json.dumps(content, indent=2)}")
    
    # Compter les blancs selon la logique corrigée
    total_blanks = 0
    if 'sentences' in content:
        sentences_blanks = sum(s.count('___') for s in content['sentences'])
        total_blanks = sentences_blanks
    elif 'text' in content:
        text_blanks = content['text'].count('___')
        total_blanks = text_blanks
    
    logger.info(f"Nombre total de blancs (logique corrigée): {total_blanks}")
    
    # Récupérer les réponses correctes
    correct_answers = []
    if 'words' in content:
        correct_answers = content['words']
    elif 'available_words' in content:
        correct_answers = content['available_words']
    
    logger.info(f"Réponses correctes: {correct_answers}")
    
    # Scénario 1: Toutes les réponses sont correctes
    logger.info("\n=== SCÉNARIO 1: TOUTES LES RÉPONSES CORRECTES ===")
    user_answers = ["isocèle", "rectangle"]
    score_scenario_1 = test_scoring(content, user_answers)
    
    # Scénario 2: Une réponse correcte, une incorrecte
    logger.info("\n=== SCÉNARIO 2: UNE RÉPONSE CORRECTE, UNE INCORRECTE ===")
    user_answers = ["isocèle", "équilatéral"]
    score_scenario_2 = test_scoring(content, user_answers)
    
    # Scénario 3: Toutes les réponses sont incorrectes
    logger.info("\n=== SCÉNARIO 3: TOUTES LES RÉPONSES INCORRECTES ===")
    user_answers = ["scalène", "équilatéral"]
    score_scenario_3 = test_scoring(content, user_answers)
    
    # Scénario 4: Réponses dans le mauvais ordre
    logger.info("\n=== SCÉNARIO 4: RÉPONSES DANS LE MAUVAIS ORDRE ===")
    user_answers = ["rectangle", "isocèle"]
    score_scenario_4 = test_scoring(content, user_answers)
    
    # Résumé des tests
    logger.info("\n=== RÉSUMÉ DES TESTS ===")
    logger.info(f"Scénario 1 (Toutes correctes): {score_scenario_1}%")
    logger.info(f"Scénario 2 (Une correcte, une incorrecte): {score_scenario_2}%")
    logger.info(f"Scénario 3 (Toutes incorrectes): {score_scenario_3}%")
    logger.info(f"Scénario 4 (Mauvais ordre): {score_scenario_4}%")
    
    # Vérifier si les résultats sont cohérents avec la logique attendue
    expected_score_1 = 100.0
    expected_score_2 = 50.0
    expected_score_3 = 0.0
    
    if score_scenario_1 == expected_score_1:
        logger.info("✅ Scénario 1: Score correct")
    else:
        logger.warning(f"❌ Scénario 1: Score incorrect (attendu: {expected_score_1}%, obtenu: {score_scenario_1}%)")
    
    if score_scenario_2 == expected_score_2:
        logger.info("✅ Scénario 2: Score correct")
    else:
        logger.warning(f"❌ Scénario 2: Score incorrect (attendu: {expected_score_2}%, obtenu: {score_scenario_2}%)")
    
    if score_scenario_3 == expected_score_3:
        logger.info("✅ Scénario 3: Score correct")
    else:
        logger.warning(f"❌ Scénario 3: Score incorrect (attendu: {expected_score_3}%, obtenu: {score_scenario_3}%)")
    
    # Pour le scénario 4, vérifier si l'ordre est important ou non
    if score_scenario_4 == expected_score_1:
        logger.info("✅ Scénario 4: L'ordre des réponses n'est PAS important (score 100%)")
    else:
        logger.info(f"ℹ️ Scénario 4: L'ordre des réponses EST important (score {score_scenario_4}%)")

def test_scoring(content, user_answers):
    """
    Simule la logique de scoring de l'application pour les exercices fill_in_blanks.
    
    Args:
        content: Le contenu JSON de l'exercice
        user_answers: Les réponses de l'utilisateur
    
    Returns:
        Le score calculé (0-100)
    """
    logger.info(f"Réponses utilisateur: {user_answers}")
    
    # Compter les blancs selon la logique corrigée
    total_blanks = 0
    if 'sentences' in content:
        sentences_blanks = sum(s.count('___') for s in content['sentences'])
        total_blanks = sentences_blanks
        logger.info(f"Blancs dans 'sentences': {total_blanks}")
    elif 'text' in content:
        text_blanks = content['text'].count('___')
        total_blanks = text_blanks
        logger.info(f"Blancs dans 'text': {total_blanks}")
    
    # Récupérer les réponses correctes
    correct_answers = []
    if 'words' in content:
        correct_answers = content['words']
    elif 'available_words' in content:
        correct_answers = content['available_words']
    
    logger.info(f"Réponses correctes: {correct_answers}")
    
    # Vérifier si le nombre de réponses utilisateur correspond au nombre de blancs
    if len(user_answers) != total_blanks:
        logger.warning(f"⚠️ Le nombre de réponses utilisateur ({len(user_answers)}) ne correspond pas au nombre de blancs ({total_blanks})")
    
    # Compter les réponses correctes
    correct_count = 0
    for i, answer in enumerate(user_answers):
        if i < len(correct_answers) and answer == correct_answers[i]:
            correct_count += 1
            logger.info(f"Réponse {i+1}: '{answer}' ✅ Correcte")
        else:
            logger.info(f"Réponse {i+1}: '{answer}' ❌ Incorrecte")
    
    # Calculer le score
    if total_blanks > 0:
        score = (correct_count / total_blanks) * 100
    else:
        score = 0
    
    logger.info(f"Score calculé: {score}% ({correct_count}/{total_blanks})")
    return score

def test_scoring_with_order_insensitive(content, user_answers):
    """
    Simule une logique de scoring alternative où l'ordre des réponses n'est pas important.
    
    Args:
        content: Le contenu JSON de l'exercice
        user_answers: Les réponses de l'utilisateur
    
    Returns:
        Le score calculé (0-100)
    """
    logger.info(f"Réponses utilisateur: {user_answers}")
    
    # Compter les blancs selon la logique corrigée
    total_blanks = 0
    if 'sentences' in content:
        sentences_blanks = sum(s.count('___') for s in content['sentences'])
        total_blanks = sentences_blanks
        logger.info(f"Blancs dans 'sentences': {total_blanks}")
    elif 'text' in content:
        text_blanks = content['text'].count('___')
        total_blanks = text_blanks
        logger.info(f"Blancs dans 'text': {total_blanks}")
    
    # Récupérer les réponses correctes
    correct_answers = []
    if 'words' in content:
        correct_answers = content['words']
    elif 'available_words' in content:
        correct_answers = content['available_words']
    
    logger.info(f"Réponses correctes: {correct_answers}")
    
    # Vérifier si le nombre de réponses utilisateur correspond au nombre de blancs
    if len(user_answers) != total_blanks:
        logger.warning(f"⚠️ Le nombre de réponses utilisateur ({len(user_answers)}) ne correspond pas au nombre de blancs ({total_blanks})")
    
    # Compter les réponses correctes sans tenir compte de l'ordre
    correct_count = 0
    remaining_correct_answers = correct_answers.copy()
    
    for answer in user_answers:
        if answer in remaining_correct_answers:
            correct_count += 1
            remaining_correct_answers.remove(answer)
            logger.info(f"Réponse '{answer}' ✅ Correcte (sans tenir compte de l'ordre)")
        else:
            logger.info(f"Réponse '{answer}' ❌ Incorrecte")
    
    # Calculer le score
    if total_blanks > 0:
        score = (correct_count / total_blanks) * 100
    else:
        score = 0
    
    logger.info(f"Score calculé (sans tenir compte de l'ordre): {score}% ({correct_count}/{total_blanks})")
    return score

if __name__ == "__main__":
    test_exercise_2_scoring()
