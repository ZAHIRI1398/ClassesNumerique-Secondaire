#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db
from models import User, Exercise, ExerciseAttempt

def debug_detailed_stats():
    with app.app_context():
        exercise_id = 4
        exercise = Exercise.query.get(exercise_id)
        
        print(f"=== DEBUG DÉTAILLÉ POUR EXERCICE {exercise_id} ===")
        print(f"Exercice: {exercise.title}")
        
        # ÉTAPE 1: Récupérer toutes les tentatives
        print(f"\n--- ÉTAPE 1: Récupération des tentatives ---")
        attempts = ExerciseAttempt.query.filter_by(exercise_id=exercise.id).all()
        print(f"Nombre total de tentatives: {len(attempts)}")
        
        # ÉTAPE 2: Extraire les student_ids uniques
        print(f"\n--- ÉTAPE 2: Extraction des student_ids ---")
        student_ids_raw = [a.student_id for a in attempts]
        print(f"student_ids bruts: {student_ids_raw}")
        
        student_ids_unique = list(set(student_ids_raw))
        print(f"student_ids uniques: {student_ids_unique}")
        
        # ÉTAPE 3: Récupérer les utilisateurs correspondants
        print(f"\n--- ÉTAPE 3: Récupération des utilisateurs ---")
        if student_ids_unique:
            all_users = User.query.filter(User.id.in_(student_ids_unique)).all()
            print(f"Tous les utilisateurs trouvés: {len(all_users)}")
            for user in all_users:
                print(f"  - ID: {user.id}, Email: {user.email}, Role: {user.role}, Name: {user.name}")
        else:
            print("Aucun student_id unique trouvé!")
            return
        
        # ÉTAPE 4: Filtrer par role='student'
        print(f"\n--- ÉTAPE 4: Filtrage par role='student' ---")
        students_to_show = User.query.filter(User.id.in_(student_ids_unique), User.role=='student').all()
        print(f"Étudiants (role='student') trouvés: {len(students_to_show)}")
        for student in students_to_show:
            print(f"  - ID: {student.id}, Email: {student.email}, Name: {student.name}")
        
        # ÉTAPE 5: Tester get_student_progress pour chaque étudiant
        print(f"\n--- ÉTAPE 5: Test de get_student_progress ---")
        student_progress = []
        
        for student in students_to_show:
            print(f"Test pour étudiant {student.email}:")
            progress = exercise.get_student_progress(student.id)
            print(f"  Progress retourné: {progress}")
            print(f"  Type: {type(progress)}")
            
            if progress:
                print(f"  ✅ Progress valide - ajout à student_progress")
                student_progress.append({
                    'student': student,
                    'progress': progress
                })
            else:
                print(f"  ❌ Progress vide/None - pas d'ajout")
        
        # ÉTAPE 6: Résultat final
        print(f"\n--- ÉTAPE 6: Résultat final ---")
        print(f"student_progress final: {len(student_progress)} éléments")
        
        if len(student_progress) == 0:
            print("❌ PROBLÈME IDENTIFIÉ: student_progress est vide!")
            print("Causes possibles:")
            print("  1. Aucun utilisateur avec role='student'")
            print("  2. get_student_progress() retourne None/False")
            print("  3. Problème dans la logique de filtrage")
        else:
            print("✅ student_progress contient des données - le template devrait s'afficher")

if __name__ == '__main__':
    debug_detailed_stats()
