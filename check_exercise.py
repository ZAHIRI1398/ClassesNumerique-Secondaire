#!/usr/bin/env python3
from flask import Flask
from models import db, Exercise
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    ex8 = Exercise.query.get(8)
    if ex8:
        print(f'Exercice 8: {ex8.title}')
        print(f'Type: {ex8.exercise_type}')
        content = json.loads(ex8.content)
        if 'draggable_items' in content:
            print(f'Elements: {content["draggable_items"]}')
            print(f'Ordre correct: {content.get("correct_order", "MANQUANT")}')
        else:
            print('Pas un exercice drag_and_drop!')
    else:
        print('Exercice 8 non trouve')
        for exercise in exercises:
            print(f"\nExercice {exercise.id} :")
            print("-" * 50)
            print(f"Titre: {exercise.title}")
            print(f"Type: {exercise.exercise_type}")
            print("\nContenu brut:")
            print(exercise.content)
            print("\nContenu parsé:")
            try:
                content = exercise.get_content()
                print(json.dumps(content, indent=2, ensure_ascii=False))
            except Exception as e:
                print(f"Erreur lors du parsing: {str(e)}")
    else:
        print("Aucun exercice de type texte à trous trouvé")
