from app import app, db
from models import Exercise
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_duplicate_exercises():
    """
    Nettoie les exercices dupliqués en gardant seulement les plus récents
    (ceux avec les IDs les plus élevés).
    """
    with app.app_context():
        try:
            # Récupérer tous les exercices
            all_exercises = Exercise.query.all()
            logger.info(f"Nombre total d'exercices avant nettoyage: {len(all_exercises)}")
            
            # Identifier les exercices uniques par titre
            unique_titles = set()
            duplicates = []
            
            # Trier les exercices par ID (décroissant) pour garder les plus récents
            sorted_exercises = sorted(all_exercises, key=lambda ex: ex.id, reverse=True)
            
            for exercise in sorted_exercises:
                if exercise.title in unique_titles:
                    # C'est un doublon, on le marque pour suppression
                    duplicates.append(exercise)
                else:
                    # C'est un exercice unique, on garde son titre
                    unique_titles.add(exercise.title)
            
            # Supprimer les doublons
            for duplicate in duplicates:
                logger.info(f"Suppression de l'exercice dupliqué: ID {duplicate.id}, Titre: {duplicate.title}")
                db.session.delete(duplicate)
            
            # Sauvegarder les changements
            db.session.commit()
            
            # Vérifier le résultat
            remaining_exercises = Exercise.query.all()
            logger.info(f"Nombre d'exercices après nettoyage: {len(remaining_exercises)}")
            
            print(f"Nettoyage terminé. {len(duplicates)} exercices dupliqués supprimés.")
            print(f"Il reste {len(remaining_exercises)} exercices uniques dans la base de données.")
            
            # Afficher les exercices restants
            print("\nExercices restants:")
            for ex in remaining_exercises:
                print(f"ID: {ex.id}, Titre: {ex.title}, Type: {ex.exercise_type}")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors du nettoyage des exercices dupliqués: {str(e)}")
            print(f"Erreur: {str(e)}")
            return False

if __name__ == "__main__":
    clean_duplicate_exercises()
