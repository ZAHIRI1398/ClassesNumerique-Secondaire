from flask import Flask
from models import db, Exercise
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    try:
        # Récupérer tous les exercices
        exercises = Exercise.query.all()
        print(f"\nNombre total d'exercices : {len(exercises)}")
        
        # Afficher les types d'exercices présents
        types = {ex.exercise_type for ex in exercises}
        print("\nTypes d'exercices présents :")
        for t in sorted(types):
            count = sum(1 for ex in exercises if ex.exercise_type == t)
            print(f"- {t}: {count} exercice(s)")
        
        # Afficher les détails de chaque exercice
        for ex in exercises:
            print(f"\n{'='*50}")
            print(f"ID: {ex.id}")
            print(f"Titre: {ex.title}")
            print(f"Type: {ex.exercise_type}")
            print(f"Description: {ex.description or 'Pas de description'}")
            
            # Essayer de charger le contenu JSON
            try:
                content = json.loads(ex.content) if ex.content else {}
                print("\nContenu:")
                print(json.dumps(content, indent=2, ensure_ascii=False))
            except json.JSONDecodeError:
                print("ERREUR: Contenu JSON invalide")
                print("Contenu brut:", ex.content)
            
    except Exception as e:
        print(f"Erreur: {str(e)}")

if __name__ == '__main__':
    with app.app_context():
        try:
            # Récupérer tous les exercices
            exercises = Exercise.query.all()
            print(f"\nNombre total d'exercices : {len(exercises)}")
            
            # Afficher les types d'exercices présents
            types = {ex.exercise_type for ex in exercises}
            print("\nTypes d'exercices présents :")
            for t in sorted(types):
                count = sum(1 for ex in exercises if ex.exercise_type == t)
                print(f"- {t}: {count} exercice(s)")
            
            # Afficher les détails de chaque exercice
            for ex in exercises:
                print(f"\n{'='*50}")
                print(f"Exercice {ex.id}:")
                print(f"Titre: {ex.title}")
                print(f"Type: {ex.exercise_type}")
                
                # Essayer de charger le contenu JSON
                try:
                    content = json.loads(ex.content) if ex.content else {}
                    print("\nContenu:")
                    print(json.dumps(content, indent=2, ensure_ascii=False))
                except json.JSONDecodeError:
                    print("ERREUR: Contenu JSON invalide")
                    print("Contenu brut:", ex.content)
                    
        except Exception as e:
            print(f"Erreur lors de la vérification des exercices: {e}")
