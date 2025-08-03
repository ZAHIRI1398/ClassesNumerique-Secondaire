from app import app, db
from models import Exercise, User
import json

with app.app_context():
    # Vérifier tous les exercices
    exercises = Exercise.query.all()
    print(f"Total exercises in database: {len(exercises)}")
    
    for exercise in exercises:
        print(f"\nExercise {exercise.id}:")
        print(f"  Title: {exercise.title}")
        print(f"  Type: {exercise.exercise_type}")
        print(f"  Content: {exercise.content}")
        
        if exercise.id == 3:
            try:
                content = exercise.get_content()
                print(f"  Parsed content keys: {list(content.keys())}")
                if 'left_items' in content:
                    print(f"  Left items: {content['left_items']}")
                if 'right_items' in content:
                    print(f"  Right items: {content['right_items']}")
            except Exception as e:
                print(f"  Error parsing content: {e}")
    
    # Vérifier les utilisateurs
    users = User.query.all()
    print(f"\nTotal users: {len(users)}")
    for user in users:
        print(f"  User: {user.username} ({user.role})")
