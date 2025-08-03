from app import app, db
from models import Exercise

with app.app_context():
    # Tester l'exercice 4 (existant)
    ex4 = Exercise.query.get(4)
    if ex4:
        print('=== EXERCICE 4 (existant) ===')
        print(f'Titre: {ex4.title}')
        print(f'Type: {ex4.exercise_type}')
        content4 = ex4.get_content()
        print(f'Elements a glisser: {content4.get("draggable_items", [])}')
        print(f'Zones de depot: {content4.get("drop_zones", [])}')
        print(f'Ordre correct: {content4.get("correct_order", [])}')
        print()
    
    # Tester l'exercice 8 (nouveau)
    ex8 = Exercise.query.get(8)
    if ex8:
        print('=== EXERCICE 8 (nouveau) ===')
        print(f'Titre: {ex8.title}')
        print(f'Type: {ex8.exercise_type}')
        content8 = ex8.get_content()
        print(f'Elements a glisser: {content8.get("draggable_items", [])}')
        print(f'Zones de depot: {content8.get("drop_zones", [])}')
        print(f'Ordre correct: {content8.get("correct_order", [])}')
        print()
    
    print('=== VERIFICATION ===')
    print(f'Exercice 4 existe: {ex4 is not None}')
    print(f'Exercice 8 existe: {ex8 is not None}')
    
    # Lister tous les exercices
    all_exercises = Exercise.query.all()
    print(f'\nTous les exercices ({len(all_exercises)}):')
    for ex in all_exercises:
        print(f'- ID {ex.id}: {ex.title} ({ex.exercise_type})')
