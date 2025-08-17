import os
import sys
import json
import sqlite3
from datetime import datetime

# Configuration
DB_PATH = 'app.db'
EXERCISE_ID = 2  # ID de l'exercice "Texte à trous - Les verbes"
LOG_FILE = f'diagnostic_exercise_{EXERCISE_ID}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

def setup_logging():
    """Configure le système de logging"""
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def connect_to_db():
    """Établit une connexion à la base de données"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Erreur de connexion à la base de données: {e}")
        sys.exit(1)

def get_exercise_details(conn, exercise_id):
    """Récupère les détails de l'exercice depuis la base de données"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM exercise WHERE id = ?", (exercise_id,))
        exercise = cursor.fetchone()
        
        if not exercise:
            logger.error(f"Aucun exercice trouvé avec l'ID {exercise_id}")
            return None
            
        return dict(exercise)
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de la récupération de l'exercice: {e}")
        return None

def analyze_exercise_content(content):
    """Analyse le contenu de l'exercice pour comprendre sa structure"""
    logger.info("=== ANALYSE DU CONTENU DE L'EXERCICE ===")
    
    # Vérifier le format du contenu
    if isinstance(content, str):
        try:
            content = json.loads(content)
        except json.JSONDecodeError:
            logger.error("Le contenu n'est pas un JSON valide")
            return
    
    # Afficher les clés principales
    logger.info(f"Clés dans le contenu: {', '.join(content.keys())}")
    
    # Analyser les blancs dans le texte ou les phrases
    total_blanks = 0
    if 'text' in content:
        text_blanks = content['text'].count('___')
        logger.info(f"Blancs dans 'text': {text_blanks}")
        total_blanks += text_blanks
    
    if 'sentences' in content:
        sentences_blanks = sum(s.count('___') for s in content['sentences'])
        logger.info(f"Blancs dans 'sentences': {sentences_blanks}")
        for i, sentence in enumerate(content['sentences']):
            logger.info(f"  Phrase {i+1}: '{sentence}' - {sentence.count('___')} blancs")
        total_blanks += sentences_blanks
    
    # Analyser les mots disponibles
    words = []
    if 'words' in content:
        words = content['words']
        logger.info(f"Mots dans 'words': {words}")
    
    if 'available_words' in content:
        available_words = content['available_words']
        logger.info(f"Mots dans 'available_words': {available_words}")
        if not words:
            words = available_words
    
    # Vérifier la cohérence
    logger.info(f"Total des blancs trouvés: {total_blanks}")
    logger.info(f"Nombre de mots disponibles: {len(words)}")
    
    if total_blanks != len(words):
        logger.warning(f"INCOHÉRENCE: Le nombre de blancs ({total_blanks}) ne correspond pas au nombre de mots ({len(words)})")
    
    return {
        'total_blanks': total_blanks,
        'words': words
    }

def simulate_scoring(content, user_answers):
    """Simule la logique de scoring pour différentes combinaisons de réponses"""
    logger.info("=== SIMULATION DE SCORING ===")
    
    # Extraire les informations nécessaires
    analysis = analyze_exercise_content(content)
    if not analysis:
        return
    
    total_blanks = analysis['total_blanks']
    correct_answers = analysis['words']
    
    logger.info(f"Réponses correctes: {correct_answers}")
    
    # Simuler différentes combinaisons de réponses
    test_cases = [
        {
            'name': "Réponses correctes dans l'ordre original",
            'answers': correct_answers.copy() if correct_answers else []
        },
        {
            'name': "Réponses correctes dans l'ordre inverse",
            'answers': correct_answers.copy()[::-1] if correct_answers else []
        },
        {
            'name': "Première réponse correcte, deuxième incorrecte",
            'answers': [correct_answers[0], "réponse_incorrecte"] if len(correct_answers) >= 2 else []
        },
        {
            'name': "Première réponse incorrecte, deuxième correcte",
            'answers': ["réponse_incorrecte", correct_answers[-1]] if len(correct_answers) >= 2 else []
        }
    ]
    
    for test_case in test_cases:
        logger.info(f"\nTest: {test_case['name']}")
        logger.info(f"Réponses utilisateur: {test_case['answers']}")
        
        # Simuler la logique de scoring actuelle
        correct_blanks = 0
        remaining_correct_answers = correct_answers.copy()
        
        for i, user_answer in enumerate(test_case['answers']):
            is_correct = False
            for j, correct_answer in enumerate(remaining_correct_answers):
                if user_answer.lower() == correct_answer.lower():
                    is_correct = True
                    remaining_correct_answers.pop(j)
                    correct_blanks += 1
                    logger.info(f"Réponse {i+1} correcte: '{user_answer}' correspond à '{correct_answer}'")
                    break
            
            if not is_correct:
                logger.info(f"Réponse {i+1} incorrecte: '{user_answer}'")
        
        score = (correct_blanks / total_blanks) * 100 if total_blanks > 0 else 0
        logger.info(f"Score calculé: {score:.1f}% ({correct_blanks}/{total_blanks})")

def get_recent_attempts(conn, exercise_id, limit=5):
    """Récupère les tentatives récentes pour cet exercice"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ea.*, u.username 
            FROM exercise_attempt ea
            JOIN user u ON ea.student_id = u.id
            WHERE ea.exercise_id = ?
            ORDER BY ea.created_at DESC
            LIMIT ?
        """, (exercise_id, limit))
        
        attempts = cursor.fetchall()
        return [dict(attempt) for attempt in attempts]
    except sqlite3.Error as e:
        logger.error(f"Erreur lors de la récupération des tentatives: {e}")
        return []

def analyze_attempts(attempts):
    """Analyse les tentatives récentes pour comprendre les problèmes de scoring"""
    logger.info("\n=== ANALYSE DES TENTATIVES RÉCENTES ===")
    
    if not attempts:
        logger.info("Aucune tentative récente trouvée")
        return
    
    for i, attempt in enumerate(attempts):
        logger.info(f"\nTentative {i+1} - Utilisateur: {attempt['username']} - Score: {attempt['score']}%")
        
        try:
            answers = json.loads(attempt['answers'])
            logger.info(f"Réponses: {answers}")
        except (json.JSONDecodeError, TypeError):
            logger.info(f"Impossible de décoder les réponses: {attempt['answers']}")
        
        try:
            feedback = json.loads(attempt['feedback'])
            logger.info(f"Feedback: {feedback}")
            
            if 'correct_blanks' in feedback and 'total_blanks' in feedback:
                logger.info(f"Blancs corrects: {feedback['correct_blanks']}/{feedback['total_blanks']}")
            
            if 'details' in feedback:
                for j, detail in enumerate(feedback['details']):
                    logger.info(f"  Détail {j+1}: {detail}")
        except (json.JSONDecodeError, TypeError):
            logger.info(f"Impossible de décoder le feedback: {attempt['feedback']}")

def main():
    """Fonction principale"""
    global logger
    logger = setup_logging()
    
    logger.info(f"=== DIAGNOSTIC DE L'EXERCICE {EXERCISE_ID} ===")
    
    # Vérifier si la base de données existe
    if not os.path.exists(DB_PATH):
        logger.error(f"Base de données non trouvée: {DB_PATH}")
        sys.exit(1)
    
    # Connexion à la base de données
    conn = connect_to_db()
    
    # Récupérer les détails de l'exercice
    exercise = get_exercise_details(conn, EXERCISE_ID)
    if not exercise:
        conn.close()
        sys.exit(1)
    
    logger.info(f"Exercice trouvé: {exercise['title']} (Type: {exercise['exercise_type']})")
    
    # Analyser le contenu de l'exercice
    try:
        content = json.loads(exercise['content'])
        analyze_exercise_content(content)
        
        # Simuler le scoring avec différentes combinaisons de réponses
        simulate_scoring(content, [])
        
        # Analyser les tentatives récentes
        attempts = get_recent_attempts(conn, EXERCISE_ID)
        analyze_attempts(attempts)
        
    except json.JSONDecodeError:
        logger.error("Le contenu de l'exercice n'est pas un JSON valide")
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse: {e}")
    
    conn.close()
    logger.info(f"\nDiagnostic terminé. Résultats enregistrés dans {LOG_FILE}")

if __name__ == "__main__":
    main()
