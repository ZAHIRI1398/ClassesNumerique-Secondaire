import json
from flask import Flask
from app import app, db, Exercise

def restore_exercise_original():
    """
    Restaure l'exercice ID 7 à sa structure originale
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
        
        # Structure originale de l'exercice
        original_content = {
            "sentences": [
                "Un triangle qui possède un angle droit et deux cotés isometriques est un triangle ___ ___",
                "Un triangle rectangle possède un angle___",
                "Un triangle obtusangle possède un angle___"
            ],
            "words": [
                "isocèle",
                "rectangle",
                "droit",
                "obtus"
            ]
        }
        
        try:
            # Afficher la structure actuelle
            current_content = json.loads(exercise.content)
            print("\nStructure actuelle du contenu:")
            print(json.dumps(current_content, indent=2, ensure_ascii=False))
            
            # Restaurer la structure originale
            print("\nRestauration de la structure originale:")
            print(json.dumps(original_content, indent=2, ensure_ascii=False))
            
            exercise.content = json.dumps(original_content, ensure_ascii=False)
            db.session.commit()
            print("\nExercice restauré avec succès à sa version originale")
            
        except json.JSONDecodeError:
            print(f"Erreur: Le contenu de l'exercice n'est pas un JSON valide")
            print(f"Contenu brut: {exercise.content}")
        except Exception as e:
            print(f"Erreur lors de la restauration: {str(e)}")

if __name__ == "__main__":
    restore_exercise_original()
