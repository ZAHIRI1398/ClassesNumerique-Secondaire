import json
from flask import Flask
from app import app, db, Exercise

def check_current_exercise():
    """
    Vérifie la structure actuelle de l'exercice ID 7
    """
    with app.app_context():
        # Récupérer l'exercice
        exercise_id = 7
        exercise = Exercise.query.get(exercise_id)
        
        if not exercise:
            print(f"Exercice ID {exercise_id} non trouvé")
            return
        
        print(f"Exercice ID {exercise_id}: {exercise.title}")
        print(f"Type: {exercise.exercise_type}")
        
        try:
            content = json.loads(exercise.content)
            print("\nStructure actuelle du contenu:")
            print(json.dumps(content, indent=2, ensure_ascii=False))
            
        except json.JSONDecodeError:
            print(f"Erreur: Le contenu de l'exercice n'est pas un JSON valide")
            print(f"Contenu brut: {exercise.content}")

if __name__ == "__main__":
    check_current_exercise()
