"""
Script de test pour vérifier le traitement des images QCM
"""
import os
import sys
import unittest
from unittest.mock import MagicMock, patch
from flask import Flask, request
from werkzeug.datastructures import FileStorage, MultiDict

# Créer une application Flask pour le contexte
app = Flask(__name__)

# Importer la fonction à tester
# Note: Cette importation sera effectuée dans le contexte de l'application
# pour éviter les erreurs de current_app

class TestQCMImageProcessing(unittest.TestCase):
    """Tests pour la fonction process_qcm_question_images"""
    
    def setUp(self):
        """Configuration avant chaque test"""
        self.app_context = app.app_context()
        self.app_context.push()
        
        # Configurer le logger mock
        self.logger_mock = MagicMock()
        app.logger = self.logger_mock
        
        # Importer la fonction dans le contexte de l'application
        from app import process_qcm_question_images
        self.process_qcm_question_images = process_qcm_question_images
        
        # Créer un répertoire temporaire pour les tests
        app.static_folder = 'static'
        os.makedirs('static/uploads', exist_ok=True)
        
        # Créer un fichier test pour simuler une image existante
        with open('static/uploads/test_image.jpg', 'w') as f:
            f.write('test image content')
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        self.app_context.pop()
        
        # Supprimer le fichier test
        if os.path.exists('static/uploads/test_image.jpg'):
            os.remove('static/uploads/test_image.jpg')
    
    @patch('app.cloud_storage')
    @patch('app.allowed_file')
    def test_process_new_image(self, mock_allowed_file, mock_cloud_storage):
        """Test l'ajout d'une nouvelle image"""
        # Configurer les mocks
        mock_allowed_file.return_value = True
        mock_cloud_storage.upload_file.return_value = 'uploads/new_image.jpg'
        
        # Créer une requête simulée avec un fichier
        test_file = FileStorage(
            stream=open(__file__, 'rb'),
            filename='test_upload.jpg',
            content_type='image/jpeg'
        )
        
        with app.test_request_context(method='POST'):
            # Ajouter le fichier à la requête
            request.files = MultiDict([('question_image_0', test_file)])
            request.form = MultiDict([('question_image_path_0', '')])
            
            # Exécuter la fonction
            questions = [{}]
            result = self.process_qcm_question_images(request, questions, 1)
            
            # Vérifier que l'image a été correctement ajoutée avec le chemin normalisé
            self.assertEqual(result[0]['image'], '/static/uploads/new_image.jpg')
    
    @patch('app.cloud_storage')
    @patch('app.allowed_file')
    def test_keep_existing_image(self, mock_allowed_file, mock_cloud_storage):
        """Test la conservation d'une image existante"""
        # Configurer les mocks
        mock_allowed_file.return_value = True
        
        with app.test_request_context(method='POST'):
            # Simuler une image existante
            request.files = MultiDict()
            request.form = MultiDict([('question_image_path_0', 'uploads/existing.jpg')])
            
            # Exécuter la fonction
            questions = [{'image': 'uploads/existing.jpg'}]
            result = self.process_qcm_question_images(request, questions, 1)
            
            # Vérifier que l'image existante a été normalisée
            self.assertEqual(result[0]['image'], '/static/uploads/existing.jpg')
    
    @patch('app.cloud_storage')
    @patch('app.allowed_file')
    @patch('os.path.exists')
    @patch('os.remove')
    def test_remove_image(self, mock_remove, mock_exists, mock_allowed_file, mock_cloud_storage):
        """Test la suppression d'une image"""
        # Configurer les mocks
        mock_exists.return_value = True
        
        with app.test_request_context(method='POST'):
            # Simuler une demande de suppression
            request.files = MultiDict()
            request.form = MultiDict([
                ('question_image_path_0', '/static/uploads/to_remove.jpg'),
                ('remove_question_image_0', 'true')
            ])
            
            # Exécuter la fonction
            questions = [{'image': '/static/uploads/to_remove.jpg'}]
            result = self.process_qcm_question_images(request, questions, 1)
            
            # Vérifier que l'image a été supprimée
            self.assertNotIn('image', result[0])
            mock_remove.assert_called_once()
    
    @patch('app.cloud_storage')
    @patch('app.allowed_file')
    def test_replace_image(self, mock_allowed_file, mock_cloud_storage):
        """Test le remplacement d'une image existante par une nouvelle"""
        # Configurer les mocks
        mock_allowed_file.return_value = True
        mock_cloud_storage.upload_file.return_value = 'uploads/replacement.jpg'
        
        # Créer une requête simulée avec un fichier
        test_file = FileStorage(
            stream=open(__file__, 'rb'),
            filename='replacement.jpg',
            content_type='image/jpeg'
        )
        
        with app.test_request_context(method='POST'):
            # Ajouter le fichier à la requête
            request.files = MultiDict([('question_image_0', test_file)])
            request.form = MultiDict([('question_image_path_0', '/static/uploads/old.jpg')])
            
            # Exécuter la fonction
            questions = [{'image': '/static/uploads/old.jpg'}]
            result = self.process_qcm_question_images(request, questions, 1)
            
            # Vérifier que l'image a été remplacée avec le chemin normalisé
            self.assertEqual(result[0]['image'], '/static/uploads/replacement.jpg')

if __name__ == '__main__':
    unittest.main()
