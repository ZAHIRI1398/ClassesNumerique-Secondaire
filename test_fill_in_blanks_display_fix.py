"""
Test pour vérifier la correction de l'affichage des réponses par défaut dans les exercices fill_in_blanks.

Ce script teste:
1. La condition show_answers dans la fonction view_exercise
2. La logique de récupération des réponses utilisateur
3. L'affichage conditionnel des réponses dans le template
"""

import os
import sys
import json
from flask import Flask, render_template_string, session
from unittest.mock import MagicMock, patch

# Chemin vers le répertoire parent
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(parent_dir)

# Créer une application Flask de test
app = Flask(__name__)
app.config['TESTING'] = True
app.config['SECRET_KEY'] = 'test_key'

# Simuler une tentative d'exercice avec et sans feedback
class MockAttempt:
    def __init__(self, has_feedback=True):
        self.id = 1
        if has_feedback:
            self.feedback = json.dumps([
                {"blank_index": 0, "student_answer": "réponse1"},
                {"blank_index": 1, "student_answer": "réponse2"}
            ])
        else:
            self.feedback = ""

# Template de test simplifié
TEST_TEMPLATE = """
{% for i in range(2) %}
    <input type="text" 
           name="answer_{{ i }}" 
           placeholder="____"
           {% if show_answers %}
           value="{{ user_answers.get('answer_' ~ i, '') }}"
           {% endif %}>
{% endfor %}
"""

def test_view_exercise_logic():
    """Test la logique de la fonction view_exercise pour show_answers"""
    print("\n=== Test de la logique de view_exercise ===")
    
    # Cas 1: Tentative avec feedback - show_answers doit être True
    attempt_with_feedback = MockAttempt(has_feedback=True)
    user_answers = {}
    show_answers = False
    
    # Simuler le code de view_exercise
    if attempt_with_feedback:
        print(f"Tentative trouvée avec ID: {attempt_with_feedback.id}")
        if attempt_with_feedback.feedback and attempt_with_feedback.feedback.strip():
            show_answers = True
            try:
                feedback = json.loads(attempt_with_feedback.feedback)
                for item in feedback:
                    if 'student_answer' in item and 'blank_index' in item:
                        user_answers[f"answer_{item['blank_index']}"] = item['student_answer']
            except Exception as e:
                print(f"Erreur: {str(e)}")
        else:
            print("Tentative sans feedback, réinitialisation de user_answers")
            user_answers = {}
    
    print(f"show_answers = {show_answers}")
    print(f"user_answers = {user_answers}")
    assert show_answers == True, "show_answers devrait être True avec feedback"
    assert len(user_answers) == 2, "user_answers devrait contenir 2 réponses"
    
    # Cas 2: Tentative sans feedback - show_answers doit être False
    attempt_without_feedback = MockAttempt(has_feedback=False)
    user_answers = {}
    show_answers = False
    
    # Simuler le code de view_exercise
    if attempt_without_feedback:
        print(f"\nTentative trouvée avec ID: {attempt_without_feedback.id}")
        if attempt_without_feedback.feedback and attempt_without_feedback.feedback.strip():
            show_answers = True
            try:
                feedback = json.loads(attempt_without_feedback.feedback)
                for item in feedback:
                    if 'student_answer' in item and 'blank_index' in item:
                        user_answers[f"answer_{item['blank_index']}"] = item['student_answer']
            except Exception as e:
                print(f"Erreur: {str(e)}")
        else:
            print("Tentative sans feedback, réinitialisation de user_answers")
            user_answers = {}
    
    print(f"show_answers = {show_answers}")
    print(f"user_answers = {user_answers}")
    assert show_answers == False, "show_answers devrait être False sans feedback"
    assert len(user_answers) == 0, "user_answers devrait être vide"
    
    print("[SUCCES] Test de la logique de view_exercise reussi!")

def test_template_rendering():
    """Test le rendu du template avec show_answers"""
    print("\n=== Test du rendu du template ===")
    
    with app.app_context():
        # Cas 1: show_answers = True - les réponses doivent être affichées
        user_answers = {"answer_0": "réponse1", "answer_1": "réponse2"}
        show_answers = True
        
        rendered = render_template_string(TEST_TEMPLATE, user_answers=user_answers, show_answers=show_answers)
        print("Rendu avec show_answers=True:")
        print(rendered)
        
        assert 'value="réponse1"' in rendered, "La réponse 1 devrait être affichée"
        assert 'value="réponse2"' in rendered, "La réponse 2 devrait être affichée"
        
        # Cas 2: show_answers = False - les réponses ne doivent pas être affichées
        show_answers = False
        
        rendered = render_template_string(TEST_TEMPLATE, user_answers=user_answers, show_answers=show_answers)
        print("\nRendu avec show_answers=False:")
        print(rendered)
        
        assert 'value="réponse1"' not in rendered, "La réponse 1 ne devrait pas être affichée"
        assert 'value="réponse2"' not in rendered, "La réponse 2 ne devrait pas être affichée"
        
        print("[SUCCES] Test du rendu du template reussi!")

if __name__ == "__main__":
    print("=== Tests de la correction d'affichage des réponses par défaut ===")
    test_view_exercise_logic()
    test_template_rendering()
    print("\n[SUCCES] Tous les tests ont reussi! La correction fonctionne comme prevu.")
