from flask import Flask
from models import db, Exercise
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    # Récupérer l'exercice avec l'ID 5
    exercise = Exercise.query.get(5)
    
    if exercise:
        print(f"Exercice ID: {exercise.id}")
        print(f"Titre: {exercise.title}")
        print(f"Type: {exercise.exercise_type}")
        print(f"Image path: {exercise.image_path}")
        
        # Analyser le contenu JSON
        content = json.loads(exercise.content)
        print("\nContenu JSON:")
        print(json.dumps(content, indent=2, ensure_ascii=False))
        
        # Vérifier si l'image est dans le contenu
        if 'image' in content:
            print(f"\nImage dans content['image']: {content['image']}")
        elif 'main_image' in content:
            print(f"\nImage dans content['main_image']: {content['main_image']}")
        else:
            print("\nAucune image trouvée dans le contenu JSON")
    else:
        print(f"Aucun exercice trouvé avec l'ID 5")
