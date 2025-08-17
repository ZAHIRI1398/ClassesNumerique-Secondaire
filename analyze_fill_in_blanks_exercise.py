from app import app, db
import sys
import json
import logging
from datetime import datetime
from models import Exercise, ExerciseAttempt

# Configuration
LOG_FILE = f'analyze_fill_in_blanks_exercise_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

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

def analyze_exercise(exercise_id):
    """Analyse un exercice spécifique"""
    logger.info(f"=== ANALYSE DE L'EXERCICE {exercise_id} ===")
    
    with app.app_context():
        # Récupérer l'exercice
        exercise = Exercise.query.get(exercise_id)
        
        if not exercise:
            logger.error(f"Exercice {exercise_id} non trouvé.")
            return
        
        # Afficher les attributs disponibles
        logger.info(f"Attributs disponibles: {dir(exercise)}")
        
        # Afficher les attributs de base
        logger.info(f"ID: {exercise.id}")
        logger.info(f"Titre: {exercise.title if hasattr(exercise, 'title') else 'Non disponible'}")
        
        # Déterminer le type d'exercice à partir du contenu
        content = exercise.get_content()
        exercise_type = 'fill_in_blanks' if 'sentences' in content or 'text' in content else 'unknown'
        logger.info(f"Type déterminé: {exercise_type}")

        
        # Récupérer le contenu
        content = exercise.get_content()
        logger.info(f"Contenu brut: {content}")
        
        # Analyser la structure
        if exercise_type == 'fill_in_blanks':
            analyze_fill_in_blanks_structure(content)
        else:
            logger.warning(f"Type d'exercice non pris en charge: {exercise_type}")

def analyze_fill_in_blanks_structure(content):
    """Analyse la structure d'un exercice fill_in_blanks"""
    logger.info("\n=== STRUCTURE DE L'EXERCICE FILL_IN_BLANKS ===")
    
    # Vérifier les champs requis
    required_fields = ['sentences', 'text', 'words', 'available_words']
    for field in required_fields:
        if field in content:
            logger.info(f"Champ '{field}' présent: {content[field]}")
        else:
            logger.info(f"Champ '{field}' absent")
    
    # Compter les blancs dans sentences
    sentences_blanks = 0
    if 'sentences' in content:
        sentences_blanks = sum(s.count('___') for s in content['sentences'])
        logger.info(f"Nombre de blancs dans 'sentences': {sentences_blanks}")
        for i, sentence in enumerate(content['sentences']):
            logger.info(f"  Phrase {i+1}: {sentence} ({sentence.count('___')} blancs)")
    
    # Compter les blancs dans text
    text_blanks = 0
    if 'text' in content:
        text_blanks = content['text'].count('___')
        logger.info(f"Nombre de blancs dans 'text': {text_blanks}")
    
    # Compter les mots disponibles
    words_count = 0
    if 'words' in content:
        words_count = len(content['words'])
        logger.info(f"Nombre de mots dans 'words': {words_count}")
        logger.info(f"Mots: {content['words']}")
    
    available_words_count = 0
    if 'available_words' in content:
        available_words_count = len(content['available_words'])
        logger.info(f"Nombre de mots dans 'available_words': {available_words_count}")
        logger.info(f"Mots disponibles: {content['available_words']}")
    
    # Vérifier la cohérence
    total_blanks = max(sentences_blanks, text_blanks)
    total_words = max(words_count, available_words_count)
    
    logger.info(f"\nTotal des blancs: {total_blanks}")
    logger.info(f"Total des mots: {total_words}")
    
    if total_blanks != total_words:
        logger.warning(f"INCOHÉRENCE: Le nombre de blancs ({total_blanks}) ne correspond pas au nombre de mots ({total_words}).")
    else:
        logger.info("COHÉRENCE: Le nombre de blanks correspond au nombre de mots.")

def analyze_attempts(exercise_id, limit=5):
    """Analyse les dernières tentatives pour un exercice"""
    logger.info(f"\n=== ANALYSE DES TENTATIVES POUR L'EXERCICE {exercise_id} ===")
    
    with app.app_context():
        try:
            # Récupérer l'exercice
            exercise = Exercise.query.get(exercise_id)
            
            if not exercise:
                logger.error(f"Exercice {exercise_id} non trouvé.")
                return
            
            # Récupérer le contenu
            content = exercise.get_content()
            
            # Déterminer le type d'exercice
            exercise_type = 'fill_in_blanks' if 'sentences' in content or 'text' in content else 'unknown'
            
            # Récupérer les dernières tentatives
            attempts = ExerciseAttempt.query.filter_by(exercise_id=exercise_id).order_by(ExerciseAttempt.id.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données: {e}")
            return
        
        if not attempts:
            logger.info("Aucune tentative trouvée.")
            return
        
        logger.info(f"Nombre de tentatives analysées: {len(attempts)}")
        
        for i, attempt in enumerate(attempts):
            logger.info(f"\n--- Tentative {i+1} (ID: {attempt.id}) ---")
            logger.info(f"Attributs disponibles: {dir(attempt)}")
            
            # Afficher les attributs disponibles
            if hasattr(attempt, 'student_id'):
                logger.info(f"Étudiant: {attempt.student_id}")
            elif hasattr(attempt, 'user_id'):
                logger.info(f"Utilisateur: {attempt.user_id}")
                
            if hasattr(attempt, 'timestamp'):
                logger.info(f"Date: {attempt.timestamp}")
            elif hasattr(attempt, 'created_at'):
                logger.info(f"Date: {attempt.created_at}")
                
            logger.info(f"Score: {attempt.score}%")
            
            # Analyser les réponses
            try:
                answers = json.loads(attempt.answers)
                logger.info(f"Réponses brutes: {answers}")
                
                # Reconstruire les réponses utilisateur
                user_answers = []
                for j in range(100):  # Limite arbitraire pour éviter une boucle infinie
                    answer_key = f'answer_{j}'
                    if answer_key not in answers:
                        break
                    user_answers.append(answers[answer_key])
                
                logger.info(f"Réponses utilisateur: {user_answers}")
                
                # Récupérer les réponses correctes
                correct_answers = content.get('words', content.get('available_words', []))
                logger.info(f"Réponses correctes: {correct_answers}")
                
                # Simuler le scoring
                simulate_scoring(user_answers, correct_answers)
                
            except Exception as e:
                logger.error(f"Erreur lors de l'analyse des réponses: {e}")

def simulate_scoring(user_answers, correct_answers):
    """Simule la logique de scoring"""
    logger.info("\n--- Simulation du scoring ---")
    
    # Copie des réponses correctes
    remaining_correct_answers = correct_answers.copy()
    
    # Compteurs
    total_blanks = len(correct_answers)
    correct_blanks = 0
    
    # Pour chaque réponse utilisateur
    for i, user_answer in enumerate(user_answers):
        is_correct = False
        matched_answer = None
        
        # Vérifier si la réponse est dans les réponses correctes restantes
        for j, correct_answer in enumerate(remaining_correct_answers):
            if user_answer.lower() == correct_answer.lower():
                is_correct = True
                matched_answer = correct_answer
                remaining_correct_answers.pop(j)
                correct_blanks += 1
                break
        
        status = "CORRECTE" if is_correct else "INCORRECTE"
        match_info = f" (correspond à '{matched_answer}')" if matched_answer else ""
        logger.info(f"Réponse {i+1}: '{user_answer}' - {status}{match_info}")
    
    # Calculer le score
    score = (correct_blanks / total_blanks) * 100 if total_blanks > 0 else 0
    logger.info(f"Score calculé: {score:.1f}% ({correct_blanks}/{total_blanks})")
    
    return score

def analyze_form_submission():
    """Analyse la soumission du formulaire"""
    logger.info("\n=== ANALYSE DE LA SOUMISSION DU FORMULAIRE ===")
    
    logger.info("Pour analyser la soumission du formulaire, vérifiez les points suivants:")
    logger.info("1. Le formulaire HTML contient-il les champs input avec les noms corrects (answer_0, answer_1, etc.)?")
    logger.info("2. Tous les champs sont-ils soumis correctement au serveur?")
    logger.info("3. Y a-t-il des erreurs JavaScript qui empêchent la soumission complète?")
    
    logger.info("\nPour vérifier cela, vous pouvez:")
    logger.info("1. Inspecter le code HTML du formulaire")
    logger.info("2. Utiliser les outils de développement du navigateur pour surveiller la soumission")
    logger.info("3. Ajouter une route de débogage pour afficher les données du formulaire")

def main():
    """Fonction principale"""
    global logger
    logger = setup_logging()
    
    logger.info("=== ANALYSE DES EXERCICES FILL_IN_BLANKS ===")
    
    # Utiliser directement l'ID d'exercice 2
    exercise_id = 2
    logger.info(f"Analyse de l'exercice {exercise_id} (Les verbes)")

    
    # Analyser l'exercice
    analyze_exercise(exercise_id)
    
    # Analyser les tentatives
    analyze_attempts(exercise_id)
    
    # Analyser la soumission du formulaire
    analyze_form_submission()
    
    logger.info(f"\nAnalyse terminée. Résultats enregistrés dans {LOG_FILE}")

if __name__ == "__main__":
    main()
