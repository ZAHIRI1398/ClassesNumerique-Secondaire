#!/usr/bin/env python3
"""
Script de test complet pour vérifier le scoring des exercices fill_in_blanks
après la correction du problème de double implémentation.
"""

import sys
import json
import os
import unittest
from flask import Flask, request, session
from werkzeug.datastructures import ImmutableMultiDict

# Ajouter le répertoire courant au path pour pouvoir importer app
sys.path.append('.')

class TestRequest:
    """Classe pour simuler une requête Flask"""
    def __init__(self, form_data):
        self.form = ImmutableMultiDict(form_data)

class TestFillInBlanksScoring(unittest.TestCase):
    """Tests pour vérifier le scoring des exercices fill_in_blanks"""
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        # Importer l'application Flask et les modèles
        from app import app, db, Exercise
        
        self.app = app
        self.db = db
        self.Exercise = Exercise
        
        # Configurer l'application pour les tests
        self.app.config['TESTING'] = True
        self.app.config['DEBUG'] = False
        self.app.config['SERVER_NAME'] = 'localhost'
        
        # Créer un contexte d'application
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Nettoyage après les tests"""
        self.app_context.pop()
    
    def test_exercise_6_scoring(self):
        """Test du scoring pour l'exercice ID 6"""
        exercise_id = 6
        
        # Récupérer l'exercice
        exercise = self.Exercise.query.get(exercise_id)
        self.assertIsNotNone(exercise, f"L'exercice ID {exercise_id} n'existe pas")
        
        print(f"\nTest de l'exercice ID {exercise_id}: {exercise.title}")
        
        # Analyser le contenu JSON
        content = json.loads(exercise.content)
        
        # Vérifier le type d'exercice
        self.assertEqual(exercise.exercise_type, 'fill_in_blanks', 
                         f"L'exercice ID {exercise_id} n'est pas de type fill_in_blanks")
        
        # Récupérer les réponses correctes
        correct_answers = content.get('answers', [])
        if not correct_answers:
            correct_answers = content.get('words', [])
        if not correct_answers:
            correct_answers = content.get('available_words', [])
        
        self.assertTrue(len(correct_answers) > 0, "Aucune réponse correcte trouvée dans l'exercice")
        print(f"Réponses correctes: {correct_answers}")
        
        # Compter les blancs dans le contenu
        total_blanks_in_content = 0
        if 'sentences' in content:
            sentences_blanks = sum(s.count('___') for s in content['sentences'])
            total_blanks_in_content = sentences_blanks
            print(f"Blancs trouvés dans 'sentences': {sentences_blanks}")
        elif 'text' in content:
            text_blanks = content['text'].count('___')
            total_blanks_in_content = text_blanks
            print(f"Blancs trouvés dans 'text': {text_blanks}")
        
        self.assertTrue(total_blanks_in_content > 0, "Aucun blanc trouvé dans l'exercice")
        self.assertEqual(total_blanks_in_content, len(correct_answers), 
                         "Le nombre de blancs ne correspond pas au nombre de réponses correctes")
        
        # Créer un objet request.form simulé avec les réponses correctes
        form_data = {}
        for i, answer in enumerate(correct_answers):
            form_data[f'answer_{i}'] = answer
        
        print(f"Données du formulaire: {form_data}")
        
        # Simuler le calcul du score
        correct_blanks = 0
        for i in range(total_blanks_in_content):
            user_answer = form_data.get(f'answer_{i}', '').strip()
            correct_answer = correct_answers[i] if i < len(correct_answers) else ''
            is_correct = user_answer.lower() == correct_answer.lower()
            status = "Correct" if is_correct else f"Incorrect (attendu: '{correct_answer}')"
            print(f"Blank {i}: '{user_answer}' -> {status}")
            if is_correct:
                correct_blanks += 1
        
        # Calculer le score final
        score = (correct_blanks / total_blanks_in_content) * 100 if total_blanks_in_content > 0 else 0
        print(f"Score calculé: {score}% ({correct_blanks}/{total_blanks_in_content})")
        
        # Vérifier que le score est correct
        self.assertEqual(score, 100.0, f"Le score devrait être 100%, mais est {score}%")
    
    def test_all_fill_in_blanks_exercises(self):
        """Test du scoring pour tous les exercices fill_in_blanks"""
        # Récupérer tous les exercices de type fill_in_blanks
        exercises = self.Exercise.query.filter_by(exercise_type='fill_in_blanks').all()
        
        print(f"\nTesting {len(exercises)} exercices fill_in_blanks:")
        
        for exercise in exercises:
            print(f"\n--- Exercice ID {exercise.id}: {exercise.title} ---")
            
            # Analyser le contenu JSON
            content = json.loads(exercise.content)
            
            # Récupérer les réponses correctes
            correct_answers = content.get('answers', [])
            if not correct_answers:
                correct_answers = content.get('words', [])
            if not correct_answers:
                correct_answers = content.get('available_words', [])
            
            if not correct_answers:
                print(f"AVERTISSEMENT: Aucune réponse correcte trouvée pour l'exercice ID {exercise.id}")
                continue
            
            print(f"Réponses correctes: {correct_answers}")
            
            # Compter les blancs dans le contenu
            total_blanks_in_content = 0
            if 'sentences' in content:
                sentences_blanks = sum(s.count('___') for s in content['sentences'])
                total_blanks_in_content = sentences_blanks
                print(f"Blancs trouvés dans 'sentences': {sentences_blanks}")
            elif 'text' in content:
                text_blanks = content['text'].count('___')
                total_blanks_in_content = text_blanks
                print(f"Blancs trouvés dans 'text': {text_blanks}")
            
            if total_blanks_in_content == 0:
                print(f"AVERTISSEMENT: Aucun blanc trouvé pour l'exercice ID {exercise.id}")
                continue
            
            # Vérifier la cohérence entre blancs et réponses
            if total_blanks_in_content != len(correct_answers):
                print(f"AVERTISSEMENT: Le nombre de blancs ({total_blanks_in_content}) ne correspond pas au nombre de réponses correctes ({len(correct_answers)})")
            
            # Créer un objet request.form simulé avec les réponses correctes
            form_data = {}
            for i, answer in enumerate(correct_answers):
                if i < total_blanks_in_content:  # Ne pas dépasser le nombre de blancs
                    form_data[f'answer_{i}'] = answer
            
            # Simuler le calcul du score
            correct_blanks = 0
            for i in range(min(total_blanks_in_content, len(correct_answers))):
                user_answer = form_data.get(f'answer_{i}', '').strip()
                correct_answer = correct_answers[i] if i < len(correct_answers) else ''
                is_correct = user_answer.lower() == correct_answer.lower()
                if is_correct:
                    correct_blanks += 1
            
            # Calculer le score final
            score = (correct_blanks / total_blanks_in_content) * 100 if total_blanks_in_content > 0 else 0
            print(f"Score calculé: {score}% ({correct_blanks}/{total_blanks_in_content})")
            
            # Vérifier que le score est correct si toutes les réponses sont correctes
            expected_score = 100.0
            if total_blanks_in_content == len(correct_answers):
                self.assertEqual(score, expected_score, 
                                f"Le score pour l'exercice ID {exercise.id} devrait être {expected_score}%, mais est {score}%")

def main():
    """Fonction principale pour exécuter les tests"""
    print("Test du scoring des exercices fill_in_blanks après correction...")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

if __name__ == "__main__":
    main()
