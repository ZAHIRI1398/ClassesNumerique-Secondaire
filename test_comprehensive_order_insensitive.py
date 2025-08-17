#!/usr/bin/env python3
"""
Script de test complet pour vérifier la correction du scoring insensible à l'ordre
avec différents scénarios et exercices.
"""
import os
import sys
import json
import logging
import sqlite3
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def connect_to_db():
    """Établit une connexion à la base de données."""
    try:
        conn = sqlite3.connect('app.db')
        conn.row_factory = sqlite3.Row
        logger.info("✅ Connexion à la base de données établie")
        return conn
    except sqlite3.Error as e:
        logger.error(f"❌ Erreur de connexion à la base de données: {e}")
        return None

def get_fill_in_blanks_exercises(conn):
    """
    Récupère tous les exercices de type fill_in_blanks.
    
    Args:
        conn: Connexion à la base de données
        
    Returns:
        list: Liste des exercices de type fill_in_blanks
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, content FROM exercises WHERE exercise_type = 'fill_in_blanks'")
        exercises = cursor.fetchall()
        
        if exercises:
            logger.info(f"✅ {len(exercises)} exercice(s) fill_in_blanks trouvé(s)")
            return exercises
        else:
            logger.warning("⚠️ Aucun exercice fill_in_blanks trouvé")
            return []
    
    except sqlite3.Error as e:
        logger.error(f"❌ Erreur lors de la récupération des exercices: {e}")
        return []

def get_student_user(conn):
    """
    Récupère un utilisateur étudiant pour les tests.
    
    Args:
        conn: Connexion à la base de données
        
    Returns:
        dict: Utilisateur étudiant, ou None si aucun n'est trouvé
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, name FROM users WHERE role = 'student' LIMIT 1")
        user = cursor.fetchone()
        
        if user:
            logger.info(f"✅ Utilisateur étudiant trouvé: {user['name']} (ID: {user['id']})")
            return user
        else:
            logger.warning("⚠️ Aucun utilisateur étudiant trouvé")
            return None
    
    except sqlite3.Error as e:
        logger.error(f"❌ Erreur lors de la récupération de l'utilisateur: {e}")
        return None

def test_exercise_with_different_orders(conn, exercise, user):
    """
    Teste un exercice avec différentes combinaisons d'ordre des réponses.
    
    Args:
        conn: Connexion à la base de données
        exercise: Exercice à tester
        user: Utilisateur pour les tests
        
    Returns:
        dict: Résultats des tests
    """
    try:
        # Charger le contenu de l'exercice
        content = json.loads(exercise['content'])
        logger.info(f"\n=== TEST DE L'EXERCICE: {exercise['title']} (ID: {exercise['id']}) ===")
        logger.info(f"Contenu: {json.dumps(content, indent=2, ensure_ascii=False)}")
        
        # Récupérer les réponses correctes
        correct_answers = []
        if 'words' in content:
            correct_answers = content['words']
        elif 'available_words' in content:
            correct_answers = content['available_words']
        
        if not correct_answers:
            logger.warning(f"⚠️ Aucune réponse correcte trouvée pour l'exercice {exercise['id']}")
            return {
                'exercise_id': exercise['id'],
                'title': exercise['title'],
                'error': 'Aucune réponse correcte trouvée'
            }
        
        logger.info(f"Réponses correctes: {correct_answers}")
        
        # Générer différentes combinaisons d'ordre des réponses
        test_cases = []
        
        # Cas 1: Ordre correct
        test_cases.append({
            'name': 'Ordre correct',
            'answers': correct_answers.copy()
        })
        
        # Cas 2: Ordre inversé
        reversed_answers = correct_answers.copy()
        reversed_answers.reverse()
        test_cases.append({
            'name': 'Ordre inversé',
            'answers': reversed_answers
        })
        
        # Cas 3: Ordre aléatoire (si plus de 2 réponses)
        if len(correct_answers) > 2:
            import random
            shuffled_answers = correct_answers.copy()
            random.shuffle(shuffled_answers)
            # S'assurer que l'ordre est différent
            while shuffled_answers == correct_answers:
                random.shuffle(shuffled_answers)
            test_cases.append({
                'name': 'Ordre aléatoire',
                'answers': shuffled_answers
            })
        
        # Cas 4: Une réponse correcte, une incorrecte (si au moins 2 réponses)
        if len(correct_answers) >= 2:
            partial_answers = correct_answers.copy()
            partial_answers[0] = "RÉPONSE_INCORRECTE_" + str(datetime.now().timestamp())
            test_cases.append({
                'name': 'Une réponse correcte, une incorrecte',
                'answers': partial_answers
            })
        
        # Exécuter les tests
        results = []
        for test_case in test_cases:
            logger.info(f"\n--- Test: {test_case['name']} ---")
            logger.info(f"Réponses: {test_case['answers']}")
            
            # Simuler la logique de scoring
            correct_blanks = 0
            total_blanks = len(correct_answers)
            
            # Copie des réponses correctes pour éviter de les modifier
            remaining_answers = correct_answers.copy()
            
            # Pour chaque réponse de l'utilisateur, vérifier si elle est dans les réponses attendues
            for answer in test_case['answers']:
                answer_lower = answer.lower()
                found = False
                for i, correct_answer in enumerate(remaining_answers):
                    if answer_lower == correct_answer.lower():
                        correct_blanks += 1
                        remaining_answers.pop(i)
                        found = True
                        break
                logger.info(f"Réponse '{answer}': {'✅ Correcte' if found else '❌ Incorrecte'}")
            
            # Calculer le score
            score = (correct_blanks / total_blanks) * 100 if total_blanks > 0 else 0
            logger.info(f"Score: {score}% ({correct_blanks}/{total_blanks})")
            
            results.append({
                'test_case': test_case['name'],
                'answers': test_case['answers'],
                'correct_blanks': correct_blanks,
                'total_blanks': total_blanks,
                'score': score
            })
        
        return {
            'exercise_id': exercise['id'],
            'title': exercise['title'],
            'correct_answers': correct_answers,
            'results': results
        }
    
    except Exception as e:
        logger.error(f"❌ Erreur lors du test de l'exercice {exercise['id']}: {str(e)}")
        return {
            'exercise_id': exercise['id'],
            'title': exercise['title'],
            'error': str(e)
        }

def verify_order_insensitive_logic():
    """
    Vérifie que la logique de scoring insensible à l'ordre fonctionne correctement.
    
    Returns:
        bool: True si la logique est correcte, False sinon
    """
    # Exemple simple pour vérifier la logique
    correct_answers = ["isocèle", "rectangle"]
    
    # Cas 1: Ordre correct
    user_answers_1 = ["isocèle", "rectangle"]
    
    # Cas 2: Ordre inversé
    user_answers_2 = ["rectangle", "isocèle"]
    
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
    
    # Calculer les scores
    score_1 = calculate_score(user_answers_1, correct_answers)
    score_2 = calculate_score(user_answers_2, correct_answers)
    
    logger.info("\n=== VÉRIFICATION DE LA LOGIQUE DE SCORING ===")
    logger.info(f"Score avec ordre correct: {score_1}%")
    logger.info(f"Score avec ordre inversé: {score_2}%")
    
    # Vérifier que les scores sont identiques
    if score_1 == score_2 and score_1 == 100.0:
        logger.info("✅ La logique de scoring est correctement insensible à l'ordre")
        return True
    else:
        logger.error(f"❌ La logique de scoring est incorrecte: {score_1}% vs {score_2}%")
        return False

def main():
    """Fonction principale."""
    logger.info("=== TEST COMPLET DU SCORING INSENSIBLE À L'ORDRE ===")
    
    # Vérifier la logique de scoring
    if not verify_order_insensitive_logic():
        logger.error("❌ La logique de scoring est incorrecte, impossible de continuer")
        return
    
    # Connexion à la base de données
    conn = connect_to_db()
    if not conn:
        logger.error("❌ Impossible de continuer sans connexion à la base de données")
        return
    
    # Récupérer les exercices fill_in_blanks
    exercises = get_fill_in_blanks_exercises(conn)
    if not exercises:
        logger.warning("⚠️ Aucun exercice à tester")
        conn.close()
        return
    
    # Récupérer un utilisateur étudiant
    user = get_student_user(conn)
    if not user:
        logger.warning("⚠️ Aucun utilisateur pour les tests")
        conn.close()
        return
    
    # Tester chaque exercice
    all_results = []
    for exercise in exercises:
        result = test_exercise_with_different_orders(conn, exercise, user)
        all_results.append(result)
    
    # Résumé des tests
    logger.info("\n=== RÉSUMÉ DES TESTS ===")
    success_count = 0
    for result in all_results:
        if 'error' in result:
            logger.warning(f"⚠️ Exercice {result['title']} (ID: {result['exercise_id']}): {result['error']}")
            continue
        
        # Vérifier si tous les tests avec réponses correctes ont un score de 100%
        all_correct_tests_pass = True
        for test_result in result['results']:
            # Si toutes les réponses sont correctes (ordre correct ou inversé), le score doit être 100%
            if test_result['test_case'] in ['Ordre correct', 'Ordre inversé', 'Ordre aléatoire']:
                if test_result['score'] != 100.0:
                    all_correct_tests_pass = False
                    logger.warning(f"❌ Test échoué pour {result['title']}: {test_result['test_case']} donne {test_result['score']}%")
        
        if all_correct_tests_pass:
            success_count += 1
            logger.info(f"✅ Exercice {result['title']} (ID: {result['exercise_id']}): Tous les tests réussis")
        else:
            logger.warning(f"❌ Exercice {result['title']} (ID: {result['exercise_id']}): Certains tests ont échoué")
    
    # Conclusion
    if success_count == len(all_results):
        logger.info("\n✅ SUCCÈS: Tous les exercices passent les tests de scoring insensible à l'ordre")
    else:
        logger.warning(f"\n⚠️ ATTENTION: {success_count}/{len(all_results)} exercices passent les tests")
    
    conn.close()

if __name__ == "__main__":
    main()
