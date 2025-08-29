from app import app, db
from models import Exercise, ExerciseAttempt
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def reset_exercises():
    """
    Efface tous les exercices et tentatives d'exercices de la base de données
    sans toucher aux autres données (utilisateurs, classes, etc.)
    """
    with app.app_context():
        try:
            # Supprimer d'abord les tentatives d'exercices (dépendances)
            attempts_count = ExerciseAttempt.query.count()
            ExerciseAttempt.query.delete()
            
            # Supprimer ensuite tous les exercices
            exercises_count = Exercise.query.count()
            Exercise.query.delete()
            
            # Valider les changements
            db.session.commit()
            
            logger.info(f"Suppression réussie : {exercises_count} exercices et {attempts_count} tentatives d'exercices")
            print(f"Suppression réussie : {exercises_count} exercices et {attempts_count} tentatives d'exercices")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la suppression des exercices : {str(e)}")
            print(f"Erreur lors de la suppression des exercices : {str(e)}")
            return False

if __name__ == "__main__":
    reset_exercises()
    print("Opération terminée. Vous pouvez maintenant créer de nouveaux exercices.")
