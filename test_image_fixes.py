"""
Script de test pour vérifier que les corrections d'images fonctionnent correctement.
Ce script simule l'édition d'un exercice avec upload d'image et vérifie que
l'image est correctement traitée et affichée.
"""

import os
import sys
import json
import unittest
import tempfile
from io import BytesIO
from PIL import Image
from flask import Flask, url_for
from werkzeug.datastructures import FileStorage

# Importer l'application Flask
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import app, db
from models import Exercise, User
from utils.image_handler import handle_exercise_image
import cloud_storage

class TestImageFixes(unittest.TestCase):
    """Tests pour vérifier les corrections d'images"""
    
    def setUp(self):
        """Configuration avant chaque test"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Créer un utilisateur de test
        self.user = User(
            username='test_user',
            email='test@example.com',
            is_admin=True
        )
        self.user.set_password('password')
        db.session.add(self.user)
        db.session.commit()
        
        # Créer un exercice de test
        self.exercise = Exercise(
            title='Test Exercise',
            description='Test Description',
            exercise_type='qcm',
            teacher_id=self.user.id,
            content=json.dumps({
                'questions': [
                    {
                        'question': 'Test Question',
                        'options': ['Option 1', 'Option 2', 'Option 3', 'Option 4'],
                        'correct_option': 0
                    }
                ]
            })
        )
        db.session.add(self.exercise)
        db.session.commit()
        
        # Créer une image de test
        self.test_image = self._create_test_image()
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        db.session.remove()
        self.app_context.pop()
    
    def _create_test_image(self):
        """Crée une image de test"""
        img = Image.new('RGB', (100, 100), color='blue')
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return FileStorage(
            stream=img_io,
            filename='test_image.png',
            content_type='image/png'
        )
    
    def _login(self):
        """Connecte l'utilisateur de test"""
        return self.client.post('/login', data={
            'username': 'test_user',
            'password': 'password'
        }, follow_redirects=True)
    
    def test_handle_exercise_image(self):
        """Teste la fonction handle_exercise_image"""
        # Vérifier que la fonction handle_exercise_image fonctionne correctement
        result = handle_exercise_image(self.test_image, self.exercise, 'qcm')
        self.assertTrue(result)
        self.assertIsNotNone(self.exercise.image_path)
        
        # Vérifier que l'image est dans le contenu JSON
        content = json.loads(self.exercise.content)
        self.assertIn('image', content)
        self.assertEqual(content['image'], self.exercise.image_path)
    
    def test_edit_exercise_with_image(self):
        """Teste l'édition d'un exercice avec upload d'image"""
        # Se connecter
        self._login()
        
        # Éditer l'exercice avec une nouvelle image
        response = self.client.post(
            f'/exercise/{self.exercise.id}/edit',
            data={
                'title': 'Updated Exercise',
                'description': 'Updated Description',
                'subject': 'math',
                'exercise_image': self.test_image
            },
            content_type='multipart/form-data',
            follow_redirects=True
        )
        
        # Vérifier que la réponse est OK
        self.assertEqual(response.status_code, 200)
        
        # Recharger l'exercice depuis la base de données
        updated_exercise = Exercise.query.get(self.exercise.id)
        
        # Vérifier que l'exercice a été mis à jour
        self.assertEqual(updated_exercise.title, 'Updated Exercise')
        self.assertEqual(updated_exercise.description, 'Updated Description')
        
        # Vérifier que l'image a été mise à jour
        self.assertIsNotNone(updated_exercise.image_path)
        
        # Vérifier que l'image est dans le contenu JSON
        content = json.loads(updated_exercise.content)
        self.assertIn('image', content)
        self.assertEqual(content['image'], updated_exercise.image_path)
    
    def test_remove_exercise_image(self):
        """Teste la suppression d'une image d'exercice"""
        # D'abord ajouter une image
        self.test_handle_exercise_image()
        
        # Se connecter
        self._login()
        
        # Supprimer l'image
        response = self.client.post(
            f'/exercise/{self.exercise.id}/edit',
            data={
                'title': 'Exercise Without Image',
                'description': 'No Image',
                'subject': 'math',
                'remove_exercise_image': 'true'
            },
            follow_redirects=True
        )
        
        # Vérifier que la réponse est OK
        self.assertEqual(response.status_code, 200)
        
        # Recharger l'exercice depuis la base de données
        updated_exercise = Exercise.query.get(self.exercise.id)
        
        # Vérifier que l'image a été supprimée
        self.assertIsNone(updated_exercise.image_path)
        
        # Vérifier que l'image a été supprimée du contenu JSON
        content = json.loads(updated_exercise.content)
        self.assertNotIn('image', content)

if __name__ == '__main__':
    unittest.main()
