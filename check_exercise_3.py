from flask import Flask
from models import db, Exercise
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///classe_numerique.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    # Récupérer l'exercice 3
    exercise = Exercise.query.get(3)
    
    if exercise:
        print(f"Exercice ID: {exercise.id}")
        print(f"Titre: {exercise.title}")
        print(f"Type: {exercise.exercise_type}")
        print(f"Image path: {exercise.image_path}")
        
        # Afficher le contenu JSON
        content = json.loads(exercise.content)
        print("\nContenu JSON:")
        print(json.dumps(content, indent=4, ensure_ascii=False))
        
        # Vérifier si l'image est présente dans le contenu JSON
        if 'image' in content:
            print(f"\nImage dans content['image']: {content['image']}")
        else:
            print("\nPas d'image dans content['image']")
            
        if 'main_image' in content:
            print(f"Image dans content['main_image']: {content['main_image']}")
        else:
            print("Pas d'image dans content['main_image']")
    else:
        print("Exercice 3 non trouvé")
