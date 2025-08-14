#!/usr/bin/env python3
"""
Script de diagnostic pour tester la logique de scoring de fill_in_blanks
"""

import sys
import json
sys.path.append('.')

from app import app, db, Exercise, ExerciseAttempt

def test_fill_in_blanks_scoring():
    """Test de la logique de scoring pour fill_in_blanks"""
    
    with app.app_context():
        # Récupérer l'exercice fill_in_blanks existant
        exercise = Exercise.query.filter_by(exercise_type='fill_in_blanks').first()
        
        if not exercise:
            print("KO Aucun exercice fill_in_blanks trouve")
            return
        
        print(f"OK Exercice trouve: {exercise.title} (ID: {exercise.id})")
        
        # Analyser le contenu JSON
        content = json.loads(exercise.content)
        print(f"Contenu JSON:")
        print(json.dumps(content, indent=2, ensure_ascii=False))
        
        # Récupérer les réponses correctes
        correct_answers = content.get('words', [])
        print(f"Reponses correctes: {correct_answers}")
        
        # Simuler des réponses utilisateur parfaites
        print(f"\nTest 1: Reponses parfaites")
        user_answers_perfect = {}
        for i, correct_answer in enumerate(correct_answers):
            user_answers_perfect[f'answer_{i}'] = correct_answer
        
        print(f"Reponses utilisateur: {user_answers_perfect}")
        
        # Calculer le score manuellement
        total_blanks = len(correct_answers)
        correct_blanks = 0
        
        for i, correct_answer in enumerate(correct_answers):
            user_answer = user_answers_perfect.get(f'answer_{i}', '').strip()
            is_correct = user_answer.lower() == correct_answer.lower()
            if is_correct:
                correct_blanks += 1
            print(f"  Blanc {i}: '{user_answer}' vs '{correct_answer}' = {'OK' if is_correct else 'KO'}")
        
        score = round((correct_blanks / total_blanks) * 100) if total_blanks > 0 else 0
        print(f"Score calcule: {correct_blanks}/{total_blanks} = {score}%")
        
        # Test avec réponses partielles
        print(f"\nTest 2: Reponses partielles (50%)")
        user_answers_partial = {}
        for i, correct_answer in enumerate(correct_answers):
            if i % 2 == 0:  # Une réponse sur deux correcte
                user_answers_partial[f'answer_{i}'] = correct_answer
            else:
                user_answers_partial[f'answer_{i}'] = "mauvaise"
        
        print(f"Reponses utilisateur: {user_answers_partial}")
        
        correct_blanks_partial = 0
        for i, correct_answer in enumerate(correct_answers):
            user_answer = user_answers_partial.get(f'answer_{i}', '').strip()
            is_correct = user_answer.lower() == correct_answer.lower()
            if is_correct:
                correct_blanks_partial += 1
            print(f"  Blanc {i}: '{user_answer}' vs '{correct_answer}' = {'OK' if is_correct else 'KO'}")
        
        score_partial = round((correct_blanks_partial / total_blanks) * 100) if total_blanks > 0 else 0
        print(f"Score calcule: {correct_blanks_partial}/{total_blanks} = {score_partial}%")
        
        # Vérifier les tentatives récentes
        print(f"\nDernieres tentatives:")
        attempts = ExerciseAttempt.query.filter_by(exercise_id=exercise.id).order_by(ExerciseAttempt.id.desc()).limit(5).all()
        
        for attempt in attempts:
            print(f"  - Score: {attempt.score}%, Réponses: {attempt.answers[:100]}...")
            if attempt.feedback:
                feedback = json.loads(attempt.feedback)
                if isinstance(feedback, dict) and 'score' in feedback:
                    print(f"    Feedback score: {feedback['score']}%")

if __name__ == '__main__':
    test_fill_in_blanks_scoring()
