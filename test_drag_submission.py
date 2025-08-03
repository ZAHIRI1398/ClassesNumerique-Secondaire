#!/usr/bin/env python3
"""
Script pour tester la soumission d'un exercice drag_and_drop
et vérifier si notre nouvelle logique backend fonctionne.
"""

from flask import Flask
from models import db, Exercise, ExerciseAttempt, User
import json
import os

# Configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def test_drag_drop_submission():
    with app.app_context():
        # Récupérer l'exercice 4 (drag_and_drop)
        exercise = Exercise.query.get(4)
        if not exercise:
            print("❌ Exercice 4 non trouvé!")
            return
            
        print(f"[OK] Exercice trouve: {exercise.title}")
        print(f"   Type: {exercise.exercise_type}")
        
        content = json.loads(exercise.content)
        print(f"   Elements: {content['draggable_items']}")
        print(f"   Ordre correct: {content['correct_order']}")
        
        # Simuler une soumission avec les bonnes réponses
        form_data = {
            'answer_0': '1',  # Zone 0 -> élément 1 (0,08)
            'answer_1': '0',  # Zone 1 -> élément 0 (0,8) 
            'answer_2': '2',  # Zone 2 -> élément 2 (0,85)
            'answer_3': '3',  # Zone 3 -> élément 3 (0,9)
        }
        
        print(f"\n[DATA] Donnees simulees: {form_data}")
        
        # Simuler le traitement backend
        user_order = []
        for i in range(len(content['draggable_items'])):
            val = form_data.get(f'answer_{i}')
            try:
                idx = int(val) if val is not None else -1
                user_order.append(idx)
            except (ValueError, TypeError):
                user_order.append(-1)
        
        correct_order = content.get('correct_order', [])
        print(f"[USER] Ordre utilisateur: {user_order}")
        print(f"[CORRECT] Ordre correct: {correct_order}")
        
        # Calculer le score
        score_count = 0
        for i, (user_idx, correct_idx) in enumerate(zip(user_order, correct_order)):
            is_correct = user_idx == correct_idx
            if is_correct:
                score_count += 1
            print(f"   Zone {i+1}: {'OK' if is_correct else 'KO'} User={user_idx} vs Correct={correct_idx}")
        
        max_score = len(correct_order)
        score = (score_count / max_score) * 100 if max_score > 0 else 0
        
        print(f"\n[SCORE] Score final: {score}% ({score_count}/{max_score})")
        
        # Vérifier la dernière tentative réelle
        latest_attempt = ExerciseAttempt.query.filter_by(exercise_id=4).order_by(ExerciseAttempt.id.desc()).first()
        if latest_attempt:
            print(f"\n[ATTEMPT] Derniere tentative reelle:")
            print(f"   ID: {latest_attempt.id}")
            print(f"   Score: {latest_attempt.score}")
            print(f"   Réponses: {latest_attempt.answers}")
            answers = json.loads(latest_attempt.answers)
            print(f"   Type réponses: {type(answers)}")
            if isinstance(answers, list):
                print("   [ERROR] PROBLEME: Les reponses sont une liste au lieu d'un dictionnaire!")
            else:
                print("   [OK] Les reponses sont un dictionnaire")

if __name__ == '__main__':
    test_drag_drop_submission()
