from app import app, db
from models import Exercise, ExerciseAttempt
import json

with app.app_context():
    # Récupérer l'exercice 8
    exercise = Exercise.query.get(8)
    if not exercise:
        print("Exercice 8 non trouvé")
        exit()
    
    print(f"=== DIAGNOSTIC EXERCICE {exercise.id} ===")
    print(f"Titre: {exercise.title}")
    print(f"Type: {exercise.exercise_type}")
    
    content = exercise.get_content()
    print(f"\nContenu de l'exercice:")
    print(f"Éléments à glisser: {content.get('draggable_items', [])}")
    print(f"Zones de dépôt: {content.get('drop_zones', [])}")
    print(f"Ordre correct: {content.get('correct_order', [])}")
    
    # Analyser l'ordre correct
    draggable_items = content.get('draggable_items', [])
    correct_order = content.get('correct_order', [])
    
    print(f"\n=== ANALYSE DE L'ORDRE CORRECT ===")
    for i, correct_idx in enumerate(correct_order):
        if correct_idx < len(draggable_items):
            item = draggable_items[correct_idx]
            print(f"Zone {i+1} doit contenir l'élément {correct_idx}: '{item}'")
        else:
            print(f"Zone {i+1}: INDEX INVALIDE {correct_idx}")
    
    # Vérifier les dernières tentatives
    print(f"\n=== DERNIÈRES TENTATIVES ===")
    attempts = ExerciseAttempt.query.filter_by(exercise_id=exercise.id).limit(3).all()
    
    for attempt in attempts:
        print(f"\nTentative ID {attempt.id}:")
        print(f"  Score: {attempt.score}/{attempt.max_score}")
        print(f"  Réponses: {attempt.answers}")
        
        # Parser les réponses
        try:
            answers = json.loads(attempt.answers)
            print(f"  Réponses parsées: {answers}")
            
            # Reconstruire user_order comme dans app.py
            user_order = []
            for i in range(len(draggable_items)):
                val = answers.get(f'answer_{i}')
                try:
                    idx = int(val) if val is not None else -1
                    user_order.append(idx)
                except (ValueError, TypeError):
                    user_order.append(-1)
            
            print(f"  Ordre utilisateur reconstruit: {user_order}")
            print(f"  Ordre correct attendu: {correct_order}")
            
            # Recalculer le score
            score_count = 0
            for i, (user_idx, correct_idx) in enumerate(zip(user_order, correct_order)):
                is_correct = user_idx == correct_idx
                user_item = draggable_items[user_idx] if 0 <= user_idx < len(draggable_items) else "INVALIDE"
                correct_item = draggable_items[correct_idx] if 0 <= correct_idx < len(draggable_items) else "INVALIDE"
                
                print(f"    Zone {i+1}: {'✓' if is_correct else '✗'} User={user_item} vs Correct={correct_item}")
                if is_correct:
                    score_count += 1
            
            recalculated_score = (score_count / len(correct_order)) * 100 if len(correct_order) > 0 else 0
            print(f"  Score recalculé: {recalculated_score}% ({score_count}/{len(correct_order)})")
            
        except Exception as e:
            print(f"  Erreur lors du parsing: {e}")
    
    print(f"\n=== VÉRIFICATION DU PROBLÈME ===")
    # Simuler une soumission parfaite
    perfect_answers = {}
    for i in range(len(draggable_items)):
        perfect_answers[f'answer_{i}'] = str(correct_order[i])
    
    print(f"Réponses parfaites simulées: {perfect_answers}")
    
    # Calculer le score avec ces réponses
    user_order = []
    for i in range(len(draggable_items)):
        val = perfect_answers.get(f'answer_{i}')
        try:
            idx = int(val) if val is not None else -1
            user_order.append(idx)
        except (ValueError, TypeError):
            user_order.append(-1)
    
    score_count = 0
    for i, (user_idx, correct_idx) in enumerate(zip(user_order, correct_order)):
        is_correct = user_idx == correct_idx
        if is_correct:
            score_count += 1
    
    perfect_score = (score_count / len(correct_order)) * 100 if len(correct_order) > 0 else 0
    print(f"Score avec réponses parfaites: {perfect_score}% ({score_count}/{len(correct_order)})")
