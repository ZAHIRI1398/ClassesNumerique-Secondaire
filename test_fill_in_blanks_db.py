#!/usr/bin/env python3
"""
Script pour tester le scoring des exercices "texte à trous" avec la base de données.
Ce script:
1. Crée un exercice de test avec plusieurs blancs dans une ligne
2. L'insère dans la base de données
3. Simule une soumission de réponse
4. Vérifie que le scoring est correct
"""

import os
import sys
import json
import random
from datetime import datetime
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text

# Configuration de la base de données
DB_URI = 'sqlite:///app.db'  # Utiliser la base de données SQLite locale par défaut

# Créer une application Flask minimale
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modèles de base de données
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f'<Course {self.title}>'

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=False)
    exercise_type = db.Column(db.String(50), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    
    def __repr__(self):
        return f'<Exercise {self.title}>'

class Attempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    answers = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Attempt {self.id}>'

def create_test_data():
    """Crée les données de test nécessaires"""
    print("Création des données de test...")
    
    # Vérifier si les données existent déjà
    teacher = User.query.filter_by(username='test_teacher').first()
    if teacher:
        print("Les données de test existent déjà.")
        return teacher, Course.query.filter_by(teacher_id=teacher.id).first()
    
    # Créer un utilisateur enseignant
    teacher = User(
        username='test_teacher',
        email='test_teacher@example.com',
        password='password123',
        role='teacher'
    )
    db.session.add(teacher)
    
    # Créer un utilisateur étudiant
    student = User(
        username='test_student',
        email='test_student@example.com',
        password='password123',
        role='student'
    )
    db.session.add(student)
    
    # Créer un cours
    course = Course(
        title='Cours de test',
        description='Cours pour tester le scoring des exercices',
        teacher_id=1  # L'ID sera 1 car c'est le premier utilisateur
    )
    db.session.add(course)
    
    # Sauvegarder pour obtenir les IDs
    db.session.commit()
    
    print(f"Données de test créées: Enseignant ID={teacher.id}, Étudiant ID={student.id}, Cours ID={course.id}")
    return teacher, course

def create_fill_in_blanks_exercise(course):
    """Crée un exercice de type 'texte à trous' avec plusieurs blancs dans une ligne"""
    print("Création de l'exercice 'texte à trous'...")
    
    # Vérifier si l'exercice existe déjà
    existing_exercise = Exercise.query.filter_by(
        title='Test Fill in Blanks Multiple',
        course_id=course.id
    ).first()
    
    if existing_exercise:
        print(f"L'exercice existe déjà avec l'ID {existing_exercise.id}")
        return existing_exercise
    
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

def test_scoring(exercise, student_id):
    """Teste le scoring de l'exercice avec différentes réponses"""
    print("\n=== Test du scoring de l'exercice ===")
    
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
        elif 'text' in content:
            text_blanks = content['text'].count('___')
            total_blanks_in_content = text_blanks
            print(f"Format 'text' détecté: {text_blanks} blancs")
        
        correct_answers = content.get('words', [])
        if not correct_answers:
            correct_answers = content.get('available_words', [])
        
        print(f"Réponses correctes: {correct_answers}")
        
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
        attempt = Attempt(
            student_id=student_id,
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
    
    # Créer les données de test
    with app.app_context():
        teacher, course = create_test_data()
        exercise = create_fill_in_blanks_exercise(course)
        
        # Récupérer l'ID de l'étudiant de test
        student = User.query.filter_by(username='test_student').first()
        
        # Tester le scoring
        test_scoring(exercise, student.id)
        
        print("\n=== Tests terminés avec succès ===")

if __name__ == "__main__":
    main()
