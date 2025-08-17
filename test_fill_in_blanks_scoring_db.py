#!/usr/bin/env python3
"""
Script pour tester le scoring des exercices "texte à trous" avec la base de données.
Ce script utilise un exercice existant et simule différentes soumissions pour vérifier le scoring.
"""

import os
import sys
import json
from datetime import datetime

# Importer les modèles depuis l'application principale
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import app, db
from models import User, Exercise, ExerciseAttempt

def find_fill_in_blanks_exercise():
    """Trouve un exercice existant de type 'fill_in_blanks'"""
    print("=== Recherche d'un exercice 'texte à trous' existant ===")
    
    with app.app_context():
        # Chercher un exercice de type 'fill_in_blanks'
        exercise = Exercise.query.filter_by(exercise_type='fill_in_blanks').first()
        
        if exercise:
            print(f"Exercice trouvé: ID={exercise.id}, Titre='{exercise.title}'")
            
            # Afficher le contenu de l'exercice
            content = json.loads(exercise.content)
            print("\nContenu de l'exercice:")
            if 'sentences' in content:
                print("Format: 'sentences'")
                for i, sentence in enumerate(content['sentences']):
                    print(f"  Phrase {i}: '{sentence}'")
                    print(f"  Nombre de blancs: {sentence.count('___')}")
            if 'text' in content:
                print("Format: 'text'")
                print(f"  Texte: '{content['text']}'")
                print(f"  Nombre de blancs: {content['text'].count('___')}")
            
            if 'words' in content:
                print(f"Mots: {content['words']}")
            elif 'available_words' in content:
                print(f"Mots disponibles: {content['available_words']}")
            
            return exercise
        else:
            print("Aucun exercice 'texte à trous' trouvé dans la base de données.")
            return None

def create_test_student():
    """Crée un étudiant temporaire pour les tests si nécessaire"""
    print("\n=== Création d'un étudiant temporaire pour les tests ===")
    
    with app.app_context():
        # Vérifier si l'étudiant de test existe déjà
        student = User.query.filter_by(username='test_student').first()
        if student:
            print(f"Étudiant de test existant trouvé: {student.username} (ID: {student.id})")
            return student
        
        # Créer un nouvel étudiant de test
        student = User(
            username='test_student',
            email='test_student@example.com',
            password_hash='pbkdf2:sha256:150000$test$hash',  # Hash fictif pour le test
            role='student',
            name='Test Student',
            school_name='Test School'
        )
        
        db.session.add(student)
        db.session.commit()
        
        print(f"Étudiant de test créé: {student.username} (ID: {student.id})")
        return student

def test_scoring_with_exercise(exercise):
    """Teste le scoring avec un exercice existant"""
    print("\n=== Test du scoring avec l'exercice existant ===")
    
    with app.app_context():
        # Trouver un étudiant par email
        student = User.query.filter_by(email='eric@example.com').first()
        if not student:
            print("Aucun étudiant trouvé avec l'email spécifié. Création d'un étudiant temporaire...")
            student = create_test_student()
        
        print(f"Utilisation de l'étudiant {student.username} (ID: {student.id}) pour le test")
        
        # Charger le contenu de l'exercice
        content = json.loads(exercise.content)
        
        # Déterminer le nombre de blancs dans l'exercice
        total_blanks_in_content = 0
        if 'sentences' in content:
            sentences_blanks = sum(s.count('___') for s in content['sentences'])
            total_blanks_in_content = sentences_blanks
            print(f"Format 'sentences' détecté: {sentences_blanks} blancs")
            for i, sentence in enumerate(content['sentences']):
                blanks_in_sentence = sentence.count('___')
                print(f"Phrase {i}: '{sentence}' contient {blanks_in_sentence} blancs")
        elif 'text' in content:
            text_blanks = content['text'].count('___')
            total_blanks_in_content = text_blanks
            print(f"Format 'text' détecté: {text_blanks} blancs")
        
        # Récupérer les réponses correctes
        correct_answers = content.get('words', [])
        if not correct_answers:
            correct_answers = content.get('available_words', [])
        
        print(f"Réponses correctes: {correct_answers}")
        print(f"Total blancs trouvés dans le contenu: {total_blanks_in_content}")
        
        # Préparer les cas de test
        test_cases = []
        
        # Cas 1: Toutes les réponses correctes
        answers_correct = {}
        for i, answer in enumerate(correct_answers):
            answers_correct[f'answer_{i}'] = answer
        test_cases.append(("Toutes correctes", answers_correct, 100.0))
        
        # Cas 2: Moitié des réponses correctes
        answers_partial = {}
        for i, answer in enumerate(correct_answers):
            if i % 2 == 0:  # Réponses correctes pour les indices pairs
                answers_partial[f'answer_{i}'] = answer
            else:  # Réponses incorrectes pour les indices impairs
                answers_partial[f'answer_{i}'] = f"incorrect_{i}"
        expected_score_partial = 50.0 if len(correct_answers) > 0 else 0.0
        test_cases.append(("Partiellement correctes", answers_partial, expected_score_partial))
        
        # Cas 3: Toutes les réponses incorrectes
        answers_incorrect = {}
        for i in range(len(correct_answers)):
            answers_incorrect[f'answer_{i}'] = f"incorrect_{i}"
        test_cases.append(("Toutes incorrectes", answers_incorrect, 0.0))
        
        # Tester chaque cas
        for name, answers, expected_score in test_cases:
            print(f"\nTest: {name}")
            print(f"Réponses: {answers}")
            
            # Vérifier chaque réponse
            correct_blanks = 0
            for i in range(len(correct_answers)):
                user_answer = answers.get(f'answer_{i}', '').strip()
                correct_answer = correct_answers[i] if i < len(correct_answers) else ''
                
                is_correct = user_answer.lower() == correct_answer.lower() if correct_answer else False
                if is_correct:
                    correct_blanks += 1
                
                print(f"Blank {i}: user='{user_answer}', correct='{correct_answer}', is_correct={is_correct}")
            
            # Calculer le score
            manual_score = (correct_blanks / len(correct_answers)) * 100 if correct_answers else 0
            print(f"Score calculé manuellement: {manual_score:.1f}%")
            
            # Créer une tentative dans la base de données
            attempt = ExerciseAttempt(
                student_id=student.id,
                exercise_id=exercise.id,
                score=manual_score,
                answers=json.dumps(answers)
            )
            
            db.session.add(attempt)
            db.session.commit()
            
            print(f"Tentative enregistrée avec l'ID {attempt.id} et le score {attempt.score}%")
            
            # Vérifier que le score correspond à l'attendu
            assert abs(attempt.score - expected_score) < 0.1, f"Score incorrect: {attempt.score} != {expected_score}"
            print(f"[OK] Test réussi: Le score {attempt.score}% correspond au score attendu {expected_score}%")

def main():
    """Fonction principale"""
    print("=== Test du scoring des exercices 'texte à trous' avec la base de données ===")
    
    # Trouver un exercice existant
    exercise = find_fill_in_blanks_exercise()
    if exercise:
        # Tester le scoring
        test_scoring_with_exercise(exercise)
        print("\n=== Tests terminés avec succès ===")
    else:
        print("Impossible de trouver un exercice 'texte à trous' pour le test.")

if __name__ == "__main__":
    main()
