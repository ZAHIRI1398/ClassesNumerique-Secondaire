from app import app, db
from models import Exercise, ExerciseAttempt
import json

with app.app_context():
    # Récupérer l'exercice 8
    exercise = Exercise.query.get(8)
    content = exercise.get_content()
    
    print(f"=== EXERCICE 8 ===")
    print(f"Éléments: {content['draggable_items']}")
    print(f"Ordre correct: {content['correct_order']}")
    
    # Récupérer la dernière tentative
    latest_attempt = ExerciseAttempt.query.filter_by(exercise_id=8).order_by(ExerciseAttempt.id.desc()).first()
    
    if latest_attempt:
        print(f"\n=== DERNIÈRE TENTATIVE (ID {latest_attempt.id}) ===")
        print(f"Score sauvegardé: {latest_attempt.score}")
        
        # Parser les réponses
        answers = json.loads(latest_attempt.answers)
        print(f"Réponses brutes: {answers}")
        print(f"Type des réponses: {type(answers)}")
        
        # Reconstruire user_order
        user_order = []
        draggable_items = content['draggable_items']
        
        if isinstance(answers, list):
            print("PROBLÈME: Les réponses sont une liste vide au lieu d'un dictionnaire!")
            print("Cela signifie que les champs cachés du formulaire ne sont pas remplis.")
            user_order = [-1] * len(draggable_items)  # Toutes les réponses sont invalides
        else:
            # Format dictionnaire attendu
            for i in range(len(draggable_items)):
                val = answers.get(f'answer_{i}')
                try:
                    idx = int(val) if val is not None else -1
                    user_order.append(idx)
                except (ValueError, TypeError):
                    user_order.append(-1)
        
        print(f"Ordre utilisateur: {user_order}")
        print(f"Ordre correct: {content['correct_order']}")
        
        # Calculer le score manuellement
        correct_order = content['correct_order']
        score_count = 0
        
        print(f"\n=== COMPARAISON DÉTAILLÉE ===")
        for i, (user_idx, correct_idx) in enumerate(zip(user_order, correct_order)):
            is_correct = user_idx == correct_idx
            user_item = draggable_items[user_idx] if 0 <= user_idx < len(draggable_items) else "INVALIDE"
            correct_item = draggable_items[correct_idx] if 0 <= correct_idx < len(draggable_items) else "INVALIDE"
            
            status = "OK" if is_correct else "KO"
            print(f"Zone {i+1}: {status} - User: {user_item} (idx {user_idx}) vs Correct: {correct_item} (idx {correct_idx})")
            
            if is_correct:
                score_count += 1
        
        calculated_score = (score_count / len(correct_order)) * 100 if len(correct_order) > 0 else 0
        print(f"\nScore calculé: {calculated_score}% ({score_count}/{len(correct_order)})")
        print(f"Score sauvegardé: {latest_attempt.score}%")
        
        if abs(calculated_score - latest_attempt.score) > 0.1:
            print(f"PROBLÈME: Différence entre score calculé et score sauvegardé!")
        else:
            print(f"Les scores correspondent.")
            
    else:
        print("Aucune tentative trouvée")
