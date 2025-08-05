#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db
from models import User, Exercise, ExerciseAttempt, Course, Class

def debug_student_progress():
    with app.app_context():
        # Récupérer l'exercice 5 (celui affiché dans la capture)
        exercise_id = 5
        exercise = Exercise.query.get(exercise_id)
        
        if not exercise:
            print(f"Exercice {exercise_id} non trouve!")
            return
            
        print(f"Exercice trouve: {exercise.title}")
        print(f"Type: {exercise.exercise_type}")
        print(f"Enseignant ID: {exercise.teacher_id}")
        
        # Vérifier les tentatives pour cet exercice
        attempts = ExerciseAttempt.query.filter_by(exercise_id=exercise_id).all()
        print(f"\n=== TENTATIVES POUR L'EXERCICE {exercise_id} ===")
        print(f"Nombre total de tentatives: {len(attempts)}")
        
        if attempts:
            for attempt in attempts:
                student = User.query.get(attempt.student_id)
                print(f"  - Tentative ID: {attempt.id}")
                print(f"    Étudiant ID: {attempt.student_id}")
                print(f"    Nom étudiant: {student.name if student else 'INCONNU'}")
                print(f"    Email étudiant: {student.email if student else 'INCONNU'}")
                print(f"    Score: {attempt.score}")
                print(f"    Date: {attempt.created_at}")
                print(f"    Complété: {attempt.completed}")
                print()
        else:
            print("AUCUNE TENTATIVE TROUVEE - C'est pourquoi la section eleves est vide!")
        
        # Vérifier les étudiants qui ont fait l'exercice
        print(f"\n=== ÉTUDIANTS UNIQUES QUI ONT FAIT L'EXERCICE ===")
        unique_attempts = ExerciseAttempt.query.filter_by(exercise_id=exercise_id).distinct(ExerciseAttempt.student_id).all()
        student_ids = [a.student_id for a in unique_attempts]
        students_who_attempted = User.query.filter(User.id.in_(student_ids), User.role=='student').all()
        
        print(f"Nombre d'étudiants uniques: {len(students_who_attempted)}")
        for student in students_who_attempted:
            print(f"  - {student.name or student.username} ({student.email})")
        
        # Tester la méthode get_student_progress
        print(f"\n=== TEST DE get_student_progress ===")
        for student in students_who_attempted:
            progress = exercise.get_student_progress(student.id)
            print(f"Étudiant: {student.name or student.username}")
            if progress:
                print(f"  Progress trouvé: {progress}")
                print(f"  Attributs: {dir(progress)}")
            else:
                print(f"  Aucun progress trouve!")
        
        # Vérifier les statistiques globales
        print(f"\n=== STATISTIQUES GLOBALES ===")
        stats = exercise.get_stats()
        if stats:
            print(f"Stats trouvées: {stats}")
            print(f"Total attempts: {getattr(stats, 'total_attempts', 'N/A')}")
        else:
            print("Aucune statistique trouvee!")

if __name__ == '__main__':
    debug_student_progress()
