#!/usr/bin/env python3
"""
Script pour tester le scoring de l'exercice 2 sans tenir compte de l'ordre des réponses.
"""
import json
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_order_insensitive_scoring():
    """
    Teste le scoring de l'exercice 2 sans tenir compte de l'ordre des réponses.
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
    
    logger.info("=== TEST DE SCORING SANS TENIR COMPTE DE L'ORDRE ===")
    logger.info(f"Contenu: {json.dumps(content, indent=2)}")
    
    # Scénario 1: Ordre correct
    logger.info("\n=== SCÉNARIO 1: ORDRE CORRECT ===")
    user_answers_1 = ["isocèle", "rectangle"]
    score_1 = test_scoring_with_order_insensitive(content, user_answers_1)
    
    # Scénario 2: Ordre inversé
    logger.info("\n=== SCÉNARIO 2: ORDRE INVERSÉ ===")
    user_answers_2 = ["rectangle", "isocèle"]
    score_2 = test_scoring_with_order_insensitive(content, user_answers_2)
    
    # Résumé des tests
    logger.info("\n=== RÉSUMÉ DES TESTS ===")
    logger.info(f"Scénario 1 (Ordre correct): {score_1}%")
    logger.info(f"Scénario 2 (Ordre inversé): {score_2}%")
    
    # Vérifier si les résultats sont cohérents
    if score_1 == score_2:
        logger.info("✅ Les deux scénarios donnent le même score: l'ordre n'est pas important")
    else:
        logger.warning(f"❌ Les deux scénarios donnent des scores différents: l'ordre est important")
    
    # Comparer avec le scoring sensible à l'ordre
    logger.info("\n=== COMPARAISON AVEC SCORING SENSIBLE À L'ORDRE ===")
    score_order_sensitive_1 = test_scoring_with_order_sensitive(content, user_answers_1)
    score_order_sensitive_2 = test_scoring_with_order_sensitive(content, user_answers_2)
    
    logger.info(f"Scoring sensible à l'ordre - Scénario 1 (Ordre correct): {score_order_sensitive_1}%")
    logger.info(f"Scoring sensible à l'ordre - Scénario 2 (Ordre inversé): {score_order_sensitive_2}%")
    
    # Conclusion
    logger.info("\n=== CONCLUSION ===")
    if score_order_sensitive_1 != score_order_sensitive_2:
        logger.info("La logique actuelle de scoring est sensible à l'ordre des réponses.")
        logger.info("Si l'ordre ne devrait pas être important, il faudrait modifier la logique de scoring.")
    else:
        logger.info("La logique actuelle de scoring n'est pas sensible à l'ordre des réponses.")

def test_scoring_with_order_insensitive(content, user_answers):
    """
    Simule une logique de scoring où l'ordre des réponses n'est pas important.
    
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

def test_scoring_with_order_sensitive(content, user_answers):
    """
    Simule la logique de scoring actuelle où l'ordre des réponses est important.
    
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
    elif 'text' in content:
        text_blanks = content['text'].count('___')
        total_blanks = text_blanks
    
    # Récupérer les réponses correctes
    correct_answers = []
    if 'words' in content:
        correct_answers = content['words']
    elif 'available_words' in content:
        correct_answers = content['available_words']
    
    # Compter les réponses correctes
    correct_count = 0
    for i, answer in enumerate(user_answers):
        if i < len(correct_answers) and answer == correct_answers[i]:
            correct_count += 1
    
    # Calculer le score
    if total_blanks > 0:
        score = (correct_count / total_blanks) * 100
    else:
        score = 0
    
    return score

if __name__ == "__main__":
    test_order_insensitive_scoring()
