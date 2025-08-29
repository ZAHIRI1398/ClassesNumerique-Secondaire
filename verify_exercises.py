from app import app, db
from models import Exercise
import json

def verify_exercises():
    with app.app_context():
        exercises = Exercise.query.all()
        print(f"Total exercises in database: {len(exercises)}")
        
        print("\nExercise list:")
        for ex in exercises:
            print(f"ID: {ex.id}, Title: {ex.title}, Type: {ex.exercise_type}")
            
        # Check for each exercise type
        exercise_types = {
            "fill_in_blanks": "Texte à trous",
            "qcm": "QCM",
            "pairs": "Appariement",
            "drag_and_drop": "Glisser-déposer",
            "legend": "Légende",
            "word_placement": "Placement de mots",
            "image_labeling": "Étiquetage d'image"
        }
        
        print("\nExercises by type:")
        for ex_type, ex_name in exercise_types.items():
            count = Exercise.query.filter_by(exercise_type=ex_type).count()
            print(f"{ex_name} ({ex_type}): {count}")
            
        # Check image paths
        print("\nImage paths:")
        for ex in exercises:
            print(f"ID: {ex.id}, Title: {ex.title}, Image path: {ex.image_path}")

if __name__ == "__main__":
    verify_exercises()
