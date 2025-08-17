import sys
import logging
from datetime import datetime

# Configuration
LOG_FILE = f'analyze_fill_in_blanks_scoring_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

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

def simulate_scoring(correct_answers, user_answers_list):
    """Simule la logique de scoring actuelle dans app.py"""
    logger.info(f"Simulation avec réponses correctes: {correct_answers}")
    logger.info(f"Réponses utilisateur: {user_answers_list}")
    
    # Copie des réponses correctes pour éviter de les modifier
    remaining_correct_answers = correct_answers.copy() if correct_answers else []
    
    # Compteurs
    total_blanks = len(correct_answers)
    correct_blanks = 0
    
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
                logger.info(f"Réponse correcte trouvée: '{user_answer}' correspond à '{matched_correct_answer}'")
                break
        
        if not is_correct:
            logger.info(f"Réponse incorrecte: '{user_answer}'")
    
    # Calculer le score final
    score = (correct_blanks / total_blanks) * 100 if total_blanks > 0 else 0
    logger.info(f"Score final: {score:.1f}% ({correct_blanks}/{total_blanks})")
    
    return {
        'score': score,
        'correct_blanks': correct_blanks,
        'total_blanks': total_blanks
    }

def test_exercise_2():
    """Teste spécifiquement l'exercice 2 avec différentes combinaisons de réponses"""
    logger.info("=== TEST DE L'EXERCICE 2 - TEXTE À TROUS - LES VERBES ===")
    
    # D'après les captures d'écran, les réponses correctes sont "rectangle" et "isocèle"
    correct_answers = ["rectangle", "isocèle"]
    
    # Tester différentes combinaisons
    test_cases = [
        {
            'name': "Réponses correctes dans l'ordre original",
            'answers': ["rectangle", "isocèle"]
        },
        {
            'name': "Réponses correctes dans l'ordre inverse",
            'answers': ["isocèle", "rectangle"]
        },
        {
            'name': "Première réponse correcte, deuxième avec faute d'orthographe",
            'answers': ["rectangle", "isocele"]  # sans accent
        },
        {
            'name': "Première avec faute d'orthographe, deuxième correcte",
            'answers': ["retangle", "isocèle"]  # sans 'c'
        },
        {
            'name': "Première correcte, deuxième vide",
            'answers': ["rectangle", ""]
        },
        {
            'name': "Première vide, deuxième correcte",
            'answers': ["", "isocèle"]
        },
        {
            'name': "Réponses incorrectes",
            'answers': ["triangl", "equilateral"]
        }
    ]
    
    for test_case in test_cases:
        logger.info(f"\n=== Test: {test_case['name']} ===")
        result = simulate_scoring(correct_answers, test_case['answers'])
        logger.info(f"Résultat: {result['score']:.1f}% ({result['correct_blanks']}/{result['total_blanks']})")

def test_exercise_with_custom_answers():
    """Teste avec des réponses personnalisées"""
    logger.info("\n=== TEST AVEC RÉPONSES PERSONNALISÉES ===")
    
    correct_answers = input("Entrez les réponses correctes séparées par des virgules: ").split(",")
    correct_answers = [answer.strip() for answer in correct_answers]
    
    user_answers = input("Entrez les réponses utilisateur séparées par des virgules: ").split(",")
    user_answers = [answer.strip() for answer in user_answers]
    
    simulate_scoring(correct_answers, user_answers)

def analyze_code_issue():
    """Analyse le problème potentiel dans le code"""
    logger.info("\n=== ANALYSE DU PROBLÈME POTENTIEL ===")
    
    logger.info("Le code actuel dans app.py utilise la logique suivante pour le scoring:")
    logger.info("1. Récupère toutes les réponses de l'utilisateur dans une liste")
    logger.info("2. Crée une copie des réponses correctes")
    logger.info("3. Pour chaque réponse utilisateur, vérifie si elle est dans la liste des réponses correctes restantes")
    logger.info("4. Si une correspondance est trouvée, incrémente le compteur et retire cette réponse de la liste des réponses correctes")
    
    logger.info("\nCette logique devrait fonctionner correctement pour rendre le scoring insensible à l'ordre.")
    logger.info("Si le problème persiste, voici les causes possibles:")
    
    logger.info("\n1. Problème de structure de l'exercice:")
    logger.info("   - L'exercice pourrait avoir une structure différente de celle attendue")
    logger.info("   - Les réponses correctes pourraient ne pas être correctement définies dans la base de données")
    
    logger.info("\n2. Problème de déploiement:")
    logger.info("   - La version déployée pourrait ne pas contenir les dernières modifications")
    logger.info("   - Un redémarrage du serveur pourrait être nécessaire")
    
    logger.info("\n3. Problème de validation des réponses:")
    logger.info("   - La comparaison des réponses pourrait être sensible à la casse ou aux accents")
    logger.info("   - Des espaces supplémentaires pourraient affecter la comparaison")
    
    logger.info("\n4. Problème de comptage des blancs:")
    logger.info("   - Le nombre total de blancs pourrait être mal calculé")
    logger.info("   - La structure de l'exercice pourrait mélanger 'text' et 'sentences'")

def main():
    """Fonction principale"""
    global logger
    logger = setup_logging()
    
    logger.info("=== ANALYSE DU SCORING FILL_IN_BLANKS ===")
    
    # Tester l'exercice 2
    test_exercise_2()
    
    # Analyser le problème potentiel
    analyze_code_issue()
    
    logger.info(f"\nAnalyse terminée. Résultats enregistrés dans {LOG_FILE}")

if __name__ == "__main__":
    main()
