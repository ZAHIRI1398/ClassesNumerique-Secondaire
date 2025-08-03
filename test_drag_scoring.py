from app import app, db
from models import Exercise, ExerciseAttempt, User
import json

with app.app_context():
    # Récupérer l'exercice 8 (notre test drag_and_drop)
    exercise = Exercise.query.get(8)
    if not exercise:
        print("Exercice 8 non trouvé")
        exit()
    
    print(f"=== TEST SCORING EXERCICE {exercise.id} ===")
    print(f"Titre: {exercise.title}")
    print(f"Type: {exercise.exercise_type}")
    
    content = exercise.get_content()
    print(f"Éléments à glisser: {content.get('draggable_items', [])}")
    print(f"Zones de dépôt: {content.get('drop_zones', [])}")
    print(f"Ordre correct: {content.get('correct_order', [])}")
    print()
    
    # Simuler différentes réponses utilisateur
    test_cases = [
        {
            "name": "Réponse parfaite",
            "answers": {"answer_0": "1", "answer_1": "0", "answer_2": "2", "answer_3": "3"},  # Ordre correct
            "expected_score": 100
        },
        {
            "name": "Réponse partiellement correcte",
            "answers": {"answer_0": "0", "answer_1": "1", "answer_2": "2", "answer_3": "3"},  # 2 bonnes réponses
            "expected_score": 50
        },
        {
            "name": "Réponse incorrecte",
            "answers": {"answer_0": "3", "answer_1": "2", "answer_2": "1", "answer_3": "0"},  # Tout faux
            "expected_score": 0
        }
    ]
    
    for test_case in test_cases:
        print(f"--- {test_case['name']} ---")
        
        # Simuler la logique de scoring de app.py
        user_order = []
        for i in range(len(content['draggable_items'])):
            val = test_case['answers'].get(f'answer_{i}')
            try:
                idx = int(val)
                user_order.append(idx)
            except (ValueError, TypeError):
                user_order.append(-1)
        
        correct_order = content.get('correct_order', [])
        score_count = 0
        feedback = []
        
        for i, (user_idx, correct_idx) in enumerate(zip(user_order, correct_order)):
            user_item = content['draggable_items'][user_idx] if 0 <= user_idx < len(content['draggable_items']) else None
            correct_item = content['draggable_items'][correct_idx] if 0 <= correct_idx < len(content['draggable_items']) else None
            is_correct = user_idx == correct_idx
            
            feedback.append({
                'zone': i+1,
                'expected': correct_item,
                'given': user_item,
                'is_correct': is_correct
            })
            
            if is_correct:
                score_count += 1
        
        max_score = len(correct_order)
        score = (score_count / max_score) * 100 if max_score > 0 else 0
        
        print(f"Réponses utilisateur: {user_order}")
        print(f"Ordre correct: {correct_order}")
        print(f"Score calculé: {score}% ({score_count}/{max_score})")
        print(f"Score attendu: {test_case['expected_score']}%")
        print(f"Test {'RÉUSSI' if abs(score - test_case['expected_score']) < 0.1 else 'ÉCHOUÉ'}")
        print()
        
        # Afficher le détail du feedback
        for fb in feedback:
            status = "OK" if fb['is_correct'] else "KO"
            print(f"  Zone {fb['zone']}: {status} Attendu: {fb['expected']}, Donne: {fb['given']}")
        print()
