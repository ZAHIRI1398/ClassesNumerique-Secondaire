from app import app, db
from models import Exercise

with app.app_context():
    # Tester l'exercice 6
    ex = Exercise.query.get(6)
    if ex:
        print(f'Exercise 6: {ex.title}')
        print(f'Type: {ex.exercise_type}')
        
        content = ex.get_content()
        print(f'Content keys: {list(content.keys())}')
        
        if 'pairs' in content:
            print(f'Number of pairs: {len(content["pairs"])}')
            for i, pair in enumerate(content['pairs']):
                print(f'Pair {i+1}:')
                print(f'  Left: {pair.get("left", {})}')
                print(f'  Right: {pair.get("right", {})}')
        else:
            print('No pairs found in content')
            print(f'Raw content: {ex.content}')
    else:
        print('Exercise 6 not found')
