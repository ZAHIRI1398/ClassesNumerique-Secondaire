from app import app, db
from models import Exercise
import json
import os

def inspect_exercises():
    print(f"Chemin de la base de données : {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    print(f"Instance path : {app.instance_path}")
    print(f"La base existe : {os.path.exists(os.path.join(app.instance_path, 'app.db'))}")
    
    with app.app_context():
        print("\nRécupération des exercices...")
        try:
            exercises = Exercise.query.all()
            print(f"Nombre d'exercices trouvés : {len(exercises)}")
            
            print("\n=== Liste des exercices ===\n")
            for e in exercises:
                print(f"ID: {e.id}")
                print(f"Titre: {e.title}")
                print(f"Type: {e.exercise_type}")
                try:
                    content = json.loads(e.content) if e.content else {}
                    print(f"Contenu JSON: {json.dumps(content, indent=2, ensure_ascii=False)}")
                except json.JSONDecodeError:
                    print(f"Erreur: Contenu JSON invalide: {e.content}")
                print("-" * 50)
        except Exception as e:
            print(f"Erreur lors de la récupération des exercices : {str(e)}")

if __name__ == '__main__':
    inspect_exercises()
