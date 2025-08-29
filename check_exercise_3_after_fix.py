import os
import sys
import json
from flask import Flask
from models import db, Exercise

# Configuration minimale pour accéder à la base de données
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///classe_numerique.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def check_exercise(exercise_id):
    """Vérifie l'état d'un exercice après correction"""
    with app.app_context():
        exercise = Exercise.query.get(exercise_id)
        if not exercise:
            print(f"Erreur: Exercice ID {exercise_id} non trouvé")
            return
        
        print(f"Exercice ID: {exercise.id}")
        print(f"Titre: {exercise.title}")
        print(f"Type: {exercise.exercise_type}")
        print(f"Image path: {exercise.image_path}")
        print()
        
        try:
            content = json.loads(exercise.content) if exercise.content else {}
        except:
            content = {}
            print("Erreur: Impossible de charger le contenu JSON")
        
        print("Contenu JSON:")
        print(json.dumps(content, indent=4))
        print()
        
        # Vérifier la cohérence entre exercise.image_path et content['main_image']
        if exercise.exercise_type == 'image_labeling':
            main_image = content.get('main_image')
            if main_image:
                print(f"Image dans content['main_image']: {main_image}")
                if exercise.image_path:
                    print(f"Image dans exercise.image_path: {exercise.image_path}")
                    if main_image == exercise.image_path:
                        print("✅ Les chemins d'image sont synchronisés correctement!")
                    else:
                        print("❌ Les chemins d'image ne sont pas synchronisés!")
                else:
                    print("❌ exercise.image_path est vide!")
            else:
                print("❌ Pas d'image dans content['main_image']!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            exercise_id = int(sys.argv[1])
            check_exercise(exercise_id)
        except ValueError:
            print("Erreur: L'ID d'exercice doit être un nombre entier")
    else:
        print("Usage: python check_exercise_3_after_fix.py <exercise_id>")
