from app import app, db
from models import Exercise

with app.app_context():
    print('Exercices disponibles:')
    exercises = Exercise.query.all()
    for ex in exercises:
        print(f'ID: {ex.id}, Type: {ex.exercise_type}, Titre: {ex.title}, Image: {ex.image_path}')
