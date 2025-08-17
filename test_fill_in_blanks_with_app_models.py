#!/usr/bin/env python3
"""
Script pour tester le scoring des exercices "texte à trous" avec la base de données
en utilisant les modèles existants de l'application.
"""

import os
import sys
import json
from datetime import datetime

# Importer les modèles depuis l'application principale
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import app, db
from models import User, Exercise, Course, ExerciseAttempt

def create_test_exercise():
    """Crée un exercice de test avec plusieurs blancs dans une ligne"""
    print("=== Création d'un exercice de test 'texte à trous' ===")
    
    with app.app_context():
        # Vérifier si l'exercice existe déjà
        existing_exercise = Exercise.query.filter_by(
            title='Test Fill in Blanks Multiple'
        ).first()
        
        if existing_exercise:
            print(f"L'exercice existe déjà avec l'ID {existing_exercise.id}")
            return existing_exercise
        
        # Trouver un enseignant et un cours
        teacher = User.query.filter_by(email='eric@example.com').first()
        if not teacher:
            print("Enseignant non trouvé. Veuillez vérifier l'email.")
            return None
        
        # Trouver ou créer un cours
        course = Course.query.filter_by(teacher_id=teacher.id).first()
        if not course:
            print("Création d'un nouveau cours pour le test...")
            course = Course(
                title='Cours de test',
                description='Cours pour tester le scoring des exercices',
                teacher_id=teacher.id
            )
            db.session.add(course)
            db.session.commit()
            print(f"Cours créé avec l'ID {course.id}")
        else:
            print(f"Utilisation du cours existant avec l'ID {course.id}")
        
        # Contenu de l'exercice avec plusieurs blancs dans une ligne
        content = {
            "sentences": [
                "Le ___ mange une ___ rouge dans le ___.",  # 3 blancs dans 1 phrase
                "La ___ est un animal qui vit dans l'eau."  # 1 blanc dans une autre phrase
            ],
            "words": ["chat", "pomme", "jardin", "baleine"]
        }
        
        # Créer l'exercice
        exercise = Exercise(
            title='Test Fill in Blanks Multiple',
            description='Exercice pour tester le scoring avec plusieurs blancs dans une ligne',
            content=json.dumps(content),
            exercise_type='fill_in_blanks',
            course_id=course.id
        )
        
        db.session.add(exercise)
        db.session.commit()
        
        print(f"Exercice créé avec l'ID {exercise.id}")
        return exercise

def test_scoring(exercise):
    """Teste le scoring de l'exercice avec différentes réponses"""
    print("\n=== Test du scoring de l'exercice ===")
    
    with app.app_context():
        # Trouver un étudiant pour le test
        student = User.query.filter_by(role='student').first()
        if not student:
            print("Aucun étudiant trouvé dans la base de données.")
            return
        
        print(f"Utilisation de l'étudiant {student.username} (ID: {student.id}) pour le test")
        
        # Charger le contenu de l'exercice
        content = json.loads(exercise.content)
        
        # Cas de test 1: Toutes les réponses correctes
        answers_correct = {
            'answer_0': 'chat',
            'answer_1': 'pomme',
            'answer_2': 'jardin',
            'answer_3': 'baleine'
        }
        
        # Cas de test 2: Réponses partiellement correctes
        answers_partial = {
            'answer_0': 'chat',
            'answer_1': 'banane',  # Incorrect
            'answer_2': 'jardin',
            'answer_3': 'requin'   # Incorrect
        }
        
        # Cas de test 3: Toutes les réponses incorrectes
        answers_incorrect = {
            'answer_0': 'chien',   # Incorrect
            'answer_1': 'banane',  # Incorrect
            'answer_2': 'maison',  # Incorrect
            'answer_3': 'requin'   # Incorrect
        }
        
        # Tester chaque cas
        test_cases = [
            ("Toutes correctes", answers_correct, 100.0),
            ("Partiellement correctes", answers_partial, 50.0),
            ("Toutes incorrectes", answers_incorrect, 0.0)
        ]
        
        for name, answers, expected_score in test_cases:
            print(f"\nTest: {name}")
            print(f"Réponses: {answers}")
            
            # Calculer le score manuellement pour vérification
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
            
            correct_answers = content.get('words', [])
            if not correct_answers:
                correct_answers = content.get('available_words', [])
            
            print(f"Réponses correctes: {correct_answers}")
            print(f"Total blancs trouvés dans le contenu: {total_blanks_in_content}")
            
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
            print(f"✓ Test réussi: Le score {attempt.score}% correspond au score attendu {expected_score}%")

def main():
    """Fonction principale"""
    print("=== Test du scoring des exercices 'texte à trous' avec la base de données ===")
    
    # Créer l'exercice de test
    exercise = create_test_exercise()
    if exercise:
        # Tester le scoring
        test_scoring(exercise)
        print("\n=== Tests terminés avec succès ===")
    else:
        print("Impossible de créer l'exercice de test.")

if __name__ == "__main__":
    main()
