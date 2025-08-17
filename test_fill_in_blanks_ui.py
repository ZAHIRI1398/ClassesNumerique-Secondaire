"""
Script de test pour simuler une soumission de formulaire pour un exercice fill_in_blanks
avec plusieurs blancs sur la même ligne.

Ce script crée un exercice de test avec deux phrases contenant chacune deux blancs,
puis simule une soumission de formulaire avec des réponses.
"""

import os
import sys
import json
from datetime import datetime
from flask import Flask, request, session
from app import app, db
from models import User, Exercise, ExerciseAttempt

def create_test_exercise():
    """Crée un exercice de test avec plusieurs blancs par ligne"""
    print("=== CRÉATION D'UN EXERCICE DE TEST FILL_IN_BLANKS AVEC PLUSIEURS BLANCS PAR LIGNE ===\n")
    
    # Vérifier si l'exercice existe déjà
    test_exercise = Exercise.query.filter_by(title="Test Fill in Blanks - Multiple Blanks Per Line").first()
    
    if test_exercise:
        print(f"[INFO] L'exercice de test existe déjà avec l'ID {test_exercise.id}")
        return test_exercise
    
    # Créer un nouvel exercice
    content = {
        "sentences": [
            "Le ___ mange une ___ rouge.",
            "La ___ vole vers son ___."
        ],
        "words": ["chat", "pomme", "mouche", "nid"]
    }
    
    # Trouver un enseignant pour associer l'exercice
    teacher = User.query.filter_by(role='teacher').first()
    if not teacher:
        print("[ERREUR] Aucun enseignant trouvé pour créer l'exercice")
        return None
    
    new_exercise = Exercise(
        title="Test Fill in Blanks - Multiple Blanks Per Line",
        description="Test pour vérifier le scoring avec plusieurs blancs par ligne",
        exercise_type="fill_in_blanks",
        content=json.dumps(content),
        created_at=datetime.utcnow(),
        teacher_id=teacher.id  # Utiliser l'ID d'un enseignant existant
    )
    
    try:
        db.session.add(new_exercise)
        db.session.commit()
        print(f"[OK] Exercice de test créé avec l'ID {new_exercise.id}")
        return new_exercise
    except Exception as e:
        db.session.rollback()
        print(f"[ERREUR] Impossible de créer l'exercice de test: {str(e)}")
        return None

def simulate_form_submission(exercise_id, answers):
    """Simule une soumission de formulaire pour l'exercice"""
    print(f"\n=== SIMULATION DE SOUMISSION DE FORMULAIRE POUR L'EXERCICE {exercise_id} ===\n")
    
    # Utiliser le contexte d'application Flask
    with app.app_context():
        # Trouver un étudiant pour le test
        test_user = User.query.filter_by(role='student').first()
        if not test_user:
            print("[ERREUR] Aucun utilisateur étudiant trouvé pour le test")
            return None
        
        # Récupérer l'exercice
        exercise = Exercise.query.get(exercise_id)
        if not exercise:
            print(f"[ERREUR] Exercice avec ID {exercise_id} non trouvé")
            return None
        
        # Préparer les données du formulaire
        form_data = {}
        for i, answer in enumerate(answers):
            form_data[f'answer_{i}'] = answer
        
        print(f"[INFO] Données du formulaire: {form_data}")
        
        # Calculer le score manuellement en utilisant la logique de app.py
        content = exercise.get_content()
        total_blanks = 0
        correct_blanks = 0
        
        # Compter les blancs dans les phrases ou dans le texte
        if 'sentences' in content:
            sentences = content['sentences']
            total_blanks = sum(s.count('___') for s in sentences)
        elif 'text' in content:
            total_blanks = content['text'].count('___')
        
        # Vérifier les réponses
        correct_answers = content.get('words', content.get('available_words', []))
        for i, answer in enumerate(answers):
            if i < len(correct_answers) and answer.lower() == correct_answers[i].lower():
                correct_blanks += 1
        
        # Calculer le score
        score = (correct_blanks / total_blanks * 100) if total_blanks > 0 else 0
        
        # Créer une tentative manuellement
        attempt = ExerciseAttempt(
            student_id=test_user.id,
            exercise_id=exercise_id,
            score=score,
            answers=json.dumps(answers),
            created_at=datetime.utcnow()
        )
        
        try:
            db.session.add(attempt)
            db.session.commit()
            print(f"[OK] Tentative enregistrée avec le score: {attempt.score}%")
            print(f"[INFO] Réponses enregistrées: {attempt.answers}")
            print(f"[INFO] Blancs corrects: {correct_blanks}/{total_blanks}")
            return attempt
        except Exception as e:
            db.session.rollback()
            print(f"[ERREUR] Impossible d'enregistrer la tentative: {str(e)}")
            return None

def main():
    """Fonction principale"""
    # Utiliser le contexte d'application Flask
    with app.app_context():
        # Créer l'exercice de test
        exercise = create_test_exercise()
        if not exercise:
            print("[ERREUR] Impossible de continuer sans exercice de test")
            return
        
        # Simuler une soumission avec des réponses correctes
        correct_answers = ["chat", "pomme", "mouche", "nid"]
        attempt_correct = simulate_form_submission(exercise.id, correct_answers)
        
        # Simuler une soumission avec des réponses partiellement correctes
        partial_answers = ["chat", "orange", "mouche", "arbre"]
        attempt_partial = simulate_form_submission(exercise.id, partial_answers)
        
        # Afficher le résumé
        print("\n=== RÉSUMÉ DES TESTS ===\n")
        print(f"Exercice ID: {exercise.id}")
        print(f"Nombre total de blancs: 4")
        
        if attempt_correct:
            print(f"Test avec réponses correctes: Score {attempt_correct.score}% (attendu: 100%)")
        
        if attempt_partial:
            print(f"Test avec réponses partiellement correctes: Score {attempt_partial.score}% (attendu: 50%)")
        
        print("\nTest terminé!")

if __name__ == "__main__":
    main()
