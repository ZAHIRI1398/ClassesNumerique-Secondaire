#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db
from models import User, Exercise, ExerciseAttempt

def debug_exercise_4():
    with app.app_context():
        # Récupérer l'exercice 4 (celui affiché dans la capture)
        exercise_id = 4
        exercise = Exercise.query.get(exercise_id)
        
        if not exercise:
            print(f"Exercice {exercise_id} non trouve!")
            return
            
        print(f"Exercice trouve: {exercise.title}")
        print(f"Type: {exercise.exercise_type}")
        
        # Vérifier les tentatives pour cet exercice
        attempts = ExerciseAttempt.query.filter_by(exercise_id=exercise_id).all()
        print(f"\n=== TENTATIVES POUR L'EXERCICE {exercise_id} ===")
        print(f"Nombre total de tentatives: {len(attempts)}")
        
        if attempts:
            for attempt in attempts:
                student = User.query.get(attempt.student_id)
                print(f"  - Tentative ID: {attempt.id}")
                print(f"    Etudiant ID: {attempt.student_id}")
                print(f"    Nom etudiant: {student.name if student else 'INCONNU'}")
                print(f"    Email etudiant: {student.email if student else 'INCONNU'}")
                print(f"    Role: {student.role if student else 'INCONNU'}")
                print(f"    Score: {attempt.score}")
                print()
        else:
            print("AUCUNE TENTATIVE TROUVEE pour l'exercice 4!")
            print("C'est pourquoi la section eleves ne s'affiche pas!")
        
        # Vérifier les étudiants (role='student') qui ont fait l'exercice
        print(f"\n=== ETUDIANTS (role='student') QUI ONT FAIT L'EXERCICE ===")
        unique_attempts = ExerciseAttempt.query.filter_by(exercise_id=exercise_id).distinct(ExerciseAttempt.student_id).all()
        student_ids = [a.student_id for a in unique_attempts]
        students_who_attempted = User.query.filter(User.id.in_(student_ids), User.role=='student').all()
        
        print(f"Nombre d'etudiants (role='student'): {len(students_who_attempted)}")
        if students_who_attempted:
            for student in students_who_attempted:
                print(f"  - {student.name or student.username} ({student.email})")
        else:
            print("AUCUN ETUDIANT (role='student') n'a fait cet exercice!")
            print("Seuls des enseignants ou autres roles ont peut-etre fait l'exercice.")
        
        # Simuler la logique du backend pour student_progress
        print(f"\n=== SIMULATION DE LA LOGIQUE BACKEND ===")
        student_progress = []
        
        # Sans cours spécifié, montrer tous les étudiants qui ont déjà fait l'exercice
        for student in students_who_attempted:
            progress = exercise.get_student_progress(student.id)
            if progress:
                student_progress.append({
                    'student': student,
                    'progress': progress
                })
        
        print(f"student_progress final: {len(student_progress)} elements")
        if student_progress:
            print("La section devrait s'afficher!")
            for item in student_progress:
                print(f"  - {item['student'].name}: {item['progress']}")
        else:
            print("student_progress est vide - la section ne s'affichera pas!")

if __name__ == '__main__':
    debug_exercise_4()
