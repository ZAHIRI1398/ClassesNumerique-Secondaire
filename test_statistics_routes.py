import unittest
import os
import sys
import io
import random
from flask import url_for
from app import app, db
from models import User, Class, Exercise, ExerciseAttempt, ClassExercise, class_exercise

class TestStatisticsRoutes(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
            self.create_test_data()
    
    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def create_test_data(self):
        # Générer un timestamp pour rendre les noms d'utilisateur uniques
        import time
        timestamp = int(time.time())
        
        # Créer un enseignant
        teacher = User(username=f'teacher_test_{timestamp}', email=f'teacher{timestamp}@test.com', role='teacher')
        teacher.set_password('password')
        db.session.add(teacher)
        db.session.commit()
        
        # Créer une classe
        test_class = Class(name='Classe Test', teacher_id=teacher.id)
        db.session.add(test_class)
        db.session.commit()
        
        # Créer des élèves
        students = []
        for i in range(5):
            student = User(username=f'student_{timestamp}_{i}', email=f'student{timestamp}_{i}@test.com', 
                           role='student', class_id=test_class.id)
            student.set_password('password')
            students.append(student)
            db.session.add(student)
        db.session.commit()
        
        # Créer des exercices
        exercises = []
        for i in range(3):
            exercise = Exercise(title=f'Exercice {i}', content=f'Contenu {i}', 
                               exercise_type='quiz', teacher_id=teacher.id)
            exercises.append(exercise)
            db.session.add(exercise)
        db.session.commit()
        
        # Associer les exercices à la classe
        for exercise in exercises:
            db.session.execute(class_exercise.insert().values(
                class_id=test_class.id,
                exercise_id=exercise.id
            ))
        db.session.commit()
        
        # Créer des tentatives d'exercices pour les élèves
        for student in students:
            for exercise in exercises:
                # Pas tous les élèves font tous les exercices
                if random.random() > 0.3:  # 70% de chance de faire l'exercice
                    attempt = ExerciseAttempt(
                        user_id=student.id,
                        exercise_id=exercise.id,
                        score=random.randint(50, 100),
                        completed=True
                    )
                    db.session.add(attempt)
        db.session.commit()
        
        self.teacher_id = teacher.id
        self.class_id = test_class.id
    
    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)
    
    def logout(self):
        return self.app.get('/logout', follow_redirects=True)
    
    def test_statistics_route_access(self):
        # Stocker les noms d'utilisateur dans des variables pour les réutiliser
        with app.app_context():
            teacher = User.query.filter_by(role='teacher').first()
            student = User.query.filter_by(role='student').first()
            teacher_username = teacher.username
            student_username = student.username
        
        # Test accès non autorisé (non connecté)
        response = self.app.get('/statistics', follow_redirects=True)
        self.assertIn(b'Please log in to access this page', response.data)
        
        # Test accès en tant qu'élève (non autorisé)
        self.login(student_username, 'password')
        response = self.app.get('/statistics', follow_redirects=True)
        self.assertIn(b'Acc\xc3\xa8s non autoris\xc3\xa9', response.data)
        self.logout()
        
        # Test accès en tant qu'enseignant (autorisé)
        self.login(teacher_username, 'password')
        response = self.app.get('/statistics')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Statistiques des classes', response.data)
        self.logout()
    
    def test_pdf_export_route(self):
        # Se connecter en tant qu'enseignant
        self.login('teacher_test', 'password')
        
        # Tester la route d'export PDF
        response = self.app.get(f'/teacher/export/pdf/{self.class_id}')
        
        # Si ReportLab est disponible, vérifier que le PDF est généré
        if 'REPORTLAB_AVAILABLE' in app.config and app.config['REPORTLAB_AVAILABLE']:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.mimetype, 'application/pdf')
        else:
            # Sinon, vérifier la redirection avec message d'erreur
            self.assertEqual(response.status_code, 302)  # Redirection
        
        self.logout()
    
    def test_excel_export_route(self):
        # Se connecter en tant qu'enseignant
        self.login('teacher_test', 'password')
        
        # Tester la route d'export Excel
        response = self.app.get(f'/teacher/export/excel/{self.class_id}')
        
        # Si openpyxl est disponible, vérifier que l'Excel est généré
        if 'OPENPYXL_AVAILABLE' in app.config and app.config['OPENPYXL_AVAILABLE']:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.mimetype, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        else:
            # Sinon, vérifier la redirection avec message d'erreur
            self.assertEqual(response.status_code, 302)  # Redirection
        
        self.logout()

if __name__ == '__main__':
    unittest.main()
