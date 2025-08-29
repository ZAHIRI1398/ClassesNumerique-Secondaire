import os
import sys
import json
import requests
import time
import unittest
import sqlite3
from flask import Flask, session
from flask_testing import TestCase
from app import app, db, Exercise
from werkzeug.datastructures import FileStorage
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

class TestFixAllImagePathsRoute(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Désactiver CSRF pour les tests
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/test_app.db'
        app.config['UPLOAD_FOLDER'] = 'static/uploads/test'
        return app

    def setUp(self):
        db.create_all()
        # Créer des exercices de test avec des chemins d'images incohérents
        self.create_test_exercises_with_inconsistent_paths()
        
        # Créer un dossier pour les uploads de test s'il n'existe pas
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER']), exist_ok=True)
        
        # Générer des images de test
        self.create_test_images()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        # Supprimer les images de test
        for path in self.test_image_paths:
            if os.path.exists(path):
                os.remove(path)

    def create_test_images(self):
        """Crée des images de test pour les exercices"""
        self.test_image_paths = []
        
        # Créer des images pour différents formats de chemins
        image_paths = [
            'static/uploads/test_image1.png',
            'static/uploads/test_image2.png',
            'static/uploads/test_image3.png',
            'static/uploads/test_image4.png',
            'static/exercises/test_image5.png'
        ]
        
        for path in image_paths:
            full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            self.create_test_image(full_path)
            self.test_image_paths.append(full_path)

    def create_test_image(self, path, width=400, height=300):
        """Crée une image de test avec du texte"""
        image = Image.new('RGB', (width, height), color=(73, 109, 137))
        d = ImageDraw.Draw(image)
        
        # Essayer de charger une police, sinon utiliser la police par défaut
        try:
            font = ImageFont.truetype("arial.ttf", 15)
        except IOError:
            font = ImageFont.load_default()
            
        d.text((10, 10), "Image de test pour correction de chemins", fill=(255, 255, 0), font=font)
        d.text((10, 50), f"Timestamp: {time.time()}", fill=(255, 255, 0), font=font)
        d.text((10, 90), f"Chemin: {path}", fill=(255, 255, 0), font=font)
            
        image.save(path)
        return path

    def create_test_exercises_with_inconsistent_paths(self):
        """Crée des exercices de test avec des chemins d'images incohérents"""
        # Cas 1: image_path sans /static/ mais content.main_image avec /static/
        exercise1 = Exercise(
            title="Test Legend Exercise 1",
            description="Test exercise with inconsistent paths 1",
            exercise_type="legend",
            subject="Test",
            content=json.dumps({
                "instructions": "Test instructions",
                "legend_mode": "classic",
                "zones": [],
                "main_image": "/static/uploads/test_image1.png"
            }),
            image_path="uploads/test_image1.png",
            created_by=1
        )
        
        # Cas 2: image_path avec /static/ mais content.main_image sans /static/
        exercise2 = Exercise(
            title="Test Legend Exercise 2",
            description="Test exercise with inconsistent paths 2",
            exercise_type="legend",
            subject="Test",
            content=json.dumps({
                "instructions": "Test instructions",
                "legend_mode": "classic",
                "zones": [],
                "main_image": "uploads/test_image2.png"
            }),
            image_path="/static/uploads/test_image2.png",
            created_by=1
        )
        
        # Cas 3: image_path existe mais pas content.main_image
        exercise3 = Exercise(
            title="Test Image Labeling Exercise 3",
            description="Test exercise with missing content.main_image",
            exercise_type="image_labeling",
            subject="Test",
            content=json.dumps({
                "labels": ["Label 1", "Label 2"],
                "zones": []
            }),
            image_path="/static/uploads/test_image3.png",
            created_by=1
        )
        
        # Cas 4: content.main_image existe mais pas image_path
        exercise4 = Exercise(
            title="Test Image Labeling Exercise 4",
            description="Test exercise with missing image_path",
            exercise_type="image_labeling",
            subject="Test",
            content=json.dumps({
                "labels": ["Label 1", "Label 2"],
                "zones": [],
                "main_image": "/static/uploads/test_image4.png"
            }),
            image_path=None,
            created_by=1
        )
        
        # Cas 5: chemin avec /static/exercises/ au lieu de /static/uploads/
        exercise5 = Exercise(
            title="Test Legend Exercise 5",
            description="Test exercise with /static/exercises/ path",
            exercise_type="legend",
            subject="Test",
            content=json.dumps({
                "instructions": "Test instructions",
                "legend_mode": "classic",
                "zones": [],
                "main_image": "/static/exercises/test_image5.png"
            }),
            image_path="/static/exercises/test_image5.png",
            created_by=1
        )
        
        db.session.add_all([exercise1, exercise2, exercise3, exercise4, exercise5])
        db.session.commit()
        
        self.exercise_ids = [exercise1.id, exercise2.id, exercise3.id, exercise4.id, exercise5.id]

    def test_fix_all_image_paths_route(self):
        """Teste la route de correction automatique des chemins d'images"""
        with self.client as c:
            # Simuler une connexion en tant qu'administrateur
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['is_authenticated'] = True
                sess['is_teacher'] = True
                sess['is_admin'] = True
            
            # Appeler la route de correction
            response = c.get('/fix-all-image-paths', follow_redirects=True)
            
            # Vérifier que la requête a réussi
            self.assertEqual(response.status_code, 200)
            
            # Vérifier que la page contient un message de succès
            self.assertIn(b'chemins d\'images corrig', response.data)
            
            # Vérifier que les exercices ont été corrigés
            for exercise_id in self.exercise_ids:
                exercise = Exercise.query.get(exercise_id)
                content = json.loads(exercise.content)
                
                # Vérifier que les chemins sont maintenant cohérents
                if 'main_image' in content:
                    # Les deux chemins doivent être identiques
                    self.assertEqual(content['main_image'], exercise.image_path)
                    
                    # Les deux chemins doivent commencer par /static/
                    self.assertTrue(exercise.image_path.startswith('/static/'))
                    self.assertTrue(content['main_image'].startswith('/static/'))
                    
                    # Les chemins doivent utiliser /static/uploads/ et non /static/exercises/
                    self.assertIn('/static/uploads/', exercise.image_path)
                    self.assertIn('/static/uploads/', content['main_image'])
                    self.assertNotIn('/static/exercises/', exercise.image_path)
                    self.assertNotIn('/static/exercises/', content['main_image'])
                    
                    print(f"Exercice {exercise_id} corrigé: {exercise.image_path}")

    def test_fix_all_image_paths_unauthorized(self):
        """Teste que la route est protégée contre les accès non autorisés"""
        with self.client as c:
            # Simuler une connexion en tant qu'enseignant non administrateur
            with c.session_transaction() as sess:
                sess['user_id'] = 2
                sess['is_authenticated'] = True
                sess['is_teacher'] = True
                sess['is_admin'] = False
            
            # Appeler la route de correction
            response = c.get('/fix-all-image-paths', follow_redirects=True)
            
            # Vérifier que l'accès est refusé ou redirigé
            self.assertNotEqual(response.status_code, 200)
            # Ou vérifier qu'un message d'erreur est présent
            self.assertNotIn(b'chemins d\'images corrig', response.data)

if __name__ == '__main__':
    unittest.main()
