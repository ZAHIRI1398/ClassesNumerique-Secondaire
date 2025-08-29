import os
import sys
import json
import requests
import time
from flask import Flask, session
from flask_testing import TestCase
from app import app, db, Exercise
from werkzeug.datastructures import FileStorage
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import unittest
import random
import string

class TestImageLabelingUpload(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Désactiver CSRF pour les tests
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/test_app.db'
        app.config['UPLOAD_FOLDER'] = 'static/uploads/test'
        return app

    def setUp(self):
        db.create_all()
        # Créer un exercice de test de type image_labeling
        exercise = Exercise(
            title="Test Image Labeling Exercise",
            description="Test exercise for image upload",
            exercise_type="image_labeling",
            subject="Test",
            content=json.dumps({
                "labels": ["Label 1", "Label 2"],
                "zones": []
            }),
            created_by=1
        )
        db.session.add(exercise)
        db.session.commit()
        self.exercise_id = exercise.id
        
        # Créer un dossier pour les uploads de test s'il n'existe pas
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER']), exist_ok=True)
        
        # Générer une image de test
        self.test_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'test_image_labeling.png')
        self.create_test_image(self.test_image_path)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        # Supprimer l'image de test si elle existe
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)

    def create_test_image(self, path, width=400, height=300):
        """Crée une image de test avec du texte"""
        image = Image.new('RGB', (width, height), color=(73, 109, 137))
        d = ImageDraw.Draw(image)
        
        # Essayer de charger une police, sinon utiliser la police par défaut
        try:
            font = ImageFont.truetype("arial.ttf", 15)
        except IOError:
            font = ImageFont.load_default()
            
        d.text((10, 10), "Image de test pour Image Labeling", fill=(255, 255, 0), font=font)
        d.text((10, 50), f"Timestamp: {time.time()}", fill=(255, 255, 0), font=font)
        
        # Dessiner quelques zones pour les étiquettes
        for i in range(3):
            x = random.randint(50, width-50)
            y = random.randint(50, height-50)
            d.rectangle((x-20, y-20, x+20, y+20), outline=(255, 0, 0))
            d.text((x-15, y), f"Zone {i+1}", fill=(255, 255, 255), font=font)
            
        image.save(path)
        return path

    def test_image_labeling_upload(self):
        """Test l'upload d'une image pour un exercice Image Labeling"""
        with open(self.test_image_path, 'rb') as img:
            img_data = img.read()
        
        with self.client as c:
            # Simuler une connexion
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['is_authenticated'] = True
                sess['is_teacher'] = True
            
            # Obtenir le token CSRF
            response = c.get(f'/exercise/{self.exercise_id}/edit')
            self.assertEqual(response.status_code, 200)
            
            # Préparer les données du formulaire avec l'image
            data = {
                'title': 'Test Image Labeling Exercise Updated',
                'description': 'Updated description',
                'subject': 'Test',
                'image_labels[]': ['Label A', 'Label B', 'Label C'],
                'zone_x[]': ['100', '200', '300'],
                'zone_y[]': ['100', '150', '200'],
                'zone_label[]': ['Label A', 'Label B', 'Label C']
            }
            
            # Créer un fichier en mémoire pour l'upload
            img_file = BytesIO(img_data)
            files = {
                'main_image': (os.path.basename(self.test_image_path), img_file, 'image/png')
            }
            
            # Soumettre le formulaire avec l'image
            response = c.post(
                f'/exercise/{self.exercise_id}/edit',
                data=data,
                content_type='multipart/form-data',
                follow_redirects=True,
                buffered=True,
                files=files
            )
            
            # Vérifier que la requête a réussi
            self.assertEqual(response.status_code, 200)
            
            # Vérifier que l'exercice a été mis à jour avec l'image
            exercise = Exercise.query.get(self.exercise_id)
            content = json.loads(exercise.content)
            
            print(f"Contenu après upload: {content}")
            
            # Vérifier que l'image a été enregistrée dans le contenu
            self.assertIn('main_image', content)
            self.assertTrue(content['main_image'].startswith('/static/'))
            
            # Vérifier que le chemin d'image est cohérent entre content.main_image et exercise.image_path
            self.assertEqual(content['main_image'], exercise.image_path)
            
            # Vérifier que le fichier existe physiquement
            image_path = content['main_image'].lstrip('/')
            full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), image_path)
            self.assertTrue(os.path.exists(full_path), f"Le fichier {full_path} n'existe pas")
            
            # Stocker le chemin pour le test de suppression
            self.uploaded_image_path = full_path
            
            return exercise, content

    def test_image_labeling_removal(self):
        """Test la suppression d'une image pour un exercice Image Labeling"""
        # D'abord, uploader une image
        exercise, content = self.test_image_labeling_upload()
        
        with self.client as c:
            # Simuler une connexion
            with c.session_transaction() as sess:
                sess['user_id'] = 1
                sess['is_authenticated'] = True
                sess['is_teacher'] = True
            
            # Préparer les données du formulaire avec la demande de suppression d'image
            data = {
                'title': exercise.title,
                'description': exercise.description,
                'subject': exercise.subject,
                'remove_main_image': 'true',  # Marquer l'image pour suppression
                'image_labels[]': content.get('labels', []),
                'zone_x[]': [],
                'zone_y[]': [],
                'zone_label[]': []
            }
            
            # Soumettre le formulaire avec la demande de suppression
            response = c.post(
                f'/exercise/{self.exercise_id}/edit',
                data=data,
                follow_redirects=True
            )
            
            # Vérifier que la requête a réussi
            self.assertEqual(response.status_code, 200)
            
            # Vérifier que l'exercice a été mis à jour sans l'image
            exercise = Exercise.query.get(self.exercise_id)
            content = json.loads(exercise.content)
            
            print(f"Contenu après suppression: {content}")
            
            # Vérifier que l'image a été supprimée du contenu
            self.assertNotIn('main_image', content)
            
            # Vérifier que le chemin d'image a été supprimé de exercise.image_path
            self.assertIsNone(exercise.image_path)
            
            # Vérifier que le fichier a été supprimé physiquement
            self.assertFalse(os.path.exists(self.uploaded_image_path), 
                            f"Le fichier {self.uploaded_image_path} existe toujours")

if __name__ == '__main__':
    unittest.main()
