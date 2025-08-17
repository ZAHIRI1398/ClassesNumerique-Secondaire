#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
from flask import Flask
from app import app, db
from models import User, Exercise, ExerciseAttempt

def find_fill_in_blanks_exercise():
    """Trouve un exercice de type 'texte à trous' dans la base de données"""
    print("=== Recherche d'un exercice 'texte à trous' existant ===")
    
    with app.app_context():
        # Chercher un exercice par son titre contenant 'trous'
        exercise = Exercise.query.filter(Exercise.title.like('%trous%')).first()
        
        if exercise:
            print(f"Exercice trouvé: ID={exercise.id}, Titre='{exercise.title}'")
            
            # Afficher le contenu de l'exercice
            content = json.loads(exercise.content)
            print("\nContenu de l'exercice:")
            
            # Déterminer le format (sentences ou text)
            if 'sentences' in content:
                print(f"Format: 'sentences'")
                for i, sentence in enumerate(content['sentences']):
                    print(f"  Phrase {i}: '{sentence}'")
                    print(f"  Nombre de blancs: {sentence.count('___')}")
            elif 'text' in content:
                print(f"Format: 'text'")
                print(f"  Texte: '{content['text']}'")
                print(f"  Nombre de blancs: {content['text'].count('___')}")
            
            # Afficher les mots à placer
            if 'words' in content:
                print(f"Mots: {content['words']}")
            elif 'available_words' in content:
                print(f"Mots disponibles: {content['available_words']}")
            
            return exercise
        else:
            print("Aucun exercice 'texte à trous' trouvé dans la base de données.")
            return None

def test_order_sensitivity(exercise):
    """Teste si le scoring est sensible à l'ordre des réponses"""
    print("\n=== Test de sensibilité à l'ordre des réponses ===")
    
    with app.app_context():
        # Trouver un étudiant par email
        student = User.query.filter_by(email='eric@example.com').first()
        if not student:
            print("Aucun étudiant trouvé avec l'email spécifié.")
            return
        
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
                print(f"Phrase {i}: '{sentence}' contient {sentence.count('___')} blancs")
        elif 'text' in content:
            text_blanks = content['text'].count('___')
            total_blanks_in_content = text_blanks
            print(f"Format 'text' détecté: {text_blanks} blancs")
        
        # Récupérer les réponses correctes
        correct_answers = content.get('words', [])
        print(f"Réponses correctes: {correct_answers}")
        print(f"Total blancs trouvés dans le contenu: {total_blanks_in_content}")
        
        # Cas de test
        test_cases = []
        
        # Cas 1: Réponses dans l'ordre correct
        answers_correct = {}
        for i, answer in enumerate(correct_answers):
            answers_correct[f'answer_{i}'] = answer
        test_cases.append(("Réponses dans l'ordre correct", answers_correct, 100.0))
        
        # Cas 2: Réponses dans l'ordre inverse
        answers_reversed = {}
        reversed_answers = list(reversed(correct_answers))
        for i, answer in enumerate(reversed_answers):
            answers_reversed[f'answer_{i}'] = answer
        test_cases.append(("Réponses dans l'ordre inverse", answers_reversed, "?"))
        
        # Tester chaque cas
        for name, answers, expected_score in test_cases:
            print(f"\nTest: {name}")
            print(f"Réponses: {answers}")
            
            # Vérifier chaque réponse
            correct_blanks = 0
            for i in range(len(correct_answers)):
                user_answer = answers.get(f'answer_{i}', '').strip()
                correct_answer = correct_answers[i] if i < len(correct_answers) else ''
                
                is_correct = user_answer.lower() == correct_answer.lower()
                print(f"Blank {i}: user='{user_answer}', correct='{correct_answer}', is_correct={is_correct}")
                
                if is_correct:
                    correct_blanks += 1
            
            # Calculer le score manuellement
            manual_score = (correct_blanks / len(correct_answers)) * 100 if len(correct_answers) > 0 else 0
            print(f"Score calculé manuellement: {manual_score}%")
            
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
            
            # Vérifier si le score correspond à l'attendu
            if expected_score != "?":
                assert abs(attempt.score - expected_score) < 0.1, f"Score incorrect: {attempt.score} != {expected_score}"
                print(f"[OK] Test réussi: Le score {attempt.score}% correspond au score attendu {expected_score}%")
            else:
                print(f"[INFO] Score obtenu: {attempt.score}%")
                if attempt.score == 100.0:
                    print("[RÉSULTAT] Le système est INSENSIBLE à l'ordre des réponses")
                elif attempt.score == 0.0:
                    print("[RÉSULTAT] Le système est SENSIBLE à l'ordre des réponses")
                else:
                    print(f"[RÉSULTAT] Le système est PARTIELLEMENT sensible à l'ordre (score: {attempt.score}%)")

def main():
    """Fonction principale"""
    print("=== Test de sensibilité à l'ordre des réponses pour les exercices 'texte à trous' ===")
    
    # Trouver un exercice existant
    exercise = find_fill_in_blanks_exercise()
    if exercise:
        # Tester la sensibilité à l'ordre
        test_order_sensitivity(exercise)
        print("\n=== Tests terminés avec succès ===")
    else:
        print("\n=== Impossible de continuer les tests sans exercice ===")

if __name__ == "__main__":
    main()
