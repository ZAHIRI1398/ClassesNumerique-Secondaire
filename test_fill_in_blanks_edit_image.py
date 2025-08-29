"""
Script de test pour valider la gestion des images dans l'édition des exercices fill_in_blanks.

Ce script teste les différents scénarios de gestion d'images:
1. Ajout d'une nouvelle image
2. Remplacement d'une image existante
3. Suppression d'une image existante
4. Validation que les chemins d'images sont correctement mis à jour
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys
import json
import io

# Ajouter le répertoire parent au path pour pouvoir importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importer la fonction à tester
from fix_fill_in_blanks_edit_complete import fix_fill_in_blanks_edit

class TestFillInBlanksEditImage(unittest.TestCase):
    """Tests pour la gestion des images dans l'édition des exercices fill_in_blanks"""

    def setUp(self):
        """Configuration initiale pour chaque test"""
        # Mock pour l'application Flask
        self.app_mock = MagicMock()
        self.app_mock.config = {'UPLOAD_FOLDER': '/path/to/uploads'}
        
        # Mock pour la base de données
        self.db_mock = MagicMock()
        
        # Mock pour l'exercice
        self.exercise_mock = MagicMock()
        self.exercise_mock.id = 1
        self.exercise_mock.title = "Test Exercise"
        self.exercise_mock.content = json.dumps({
            'sentences': ['This is a ___ test.'],
            'words': ['simple']
        })
        self.exercise_mock.image_path = None  # Par défaut, pas d'image

    @patch('fix_fill_in_blanks_edit_complete.request')
    @patch('fix_fill_in_blanks_edit_complete.flash')
    @patch('fix_fill_in_blanks_edit_complete.render_template')
    @patch('fix_fill_in_blanks_edit_complete.redirect')
    @patch('fix_fill_in_blanks_edit_complete.url_for')
    @patch('fix_fill_in_blanks_edit_complete.current_app')
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_add_new_image(self, makedirs_mock, exists_mock, current_app_mock, url_for_mock, 
                          redirect_mock, render_template_mock, flash_mock, request_mock):
        """Test l'ajout d'une nouvelle image à un exercice sans image"""
        # Configuration des mocks
        request_mock.form.getlist.side_effect = lambda key: {
            'sentences[]': ['This is a ___ test.'],
            'words[]': ['simple']
        }[key]
        request_mock.form.get.return_value = None  # Pas de suppression d'image
        
        # Mock pour le fichier uploadé
        mock_file = MagicMock()
        mock_file.filename = 'test_image.png'
        request_mock.files = {'exercise_image': mock_file}
        
        # Mock pour os.path.exists
        exists_mock.return_value = False
        
        # Mock pour la redirection
        url_for_mock.return_value = '/view_exercise/1'
        redirect_mock.return_value = 'redirect_result'
        
        # Exécution de la fonction à tester
        with patch('fix_fill_in_blanks_edit_complete.open', mock_open()), \
             patch('fix_fill_in_blanks_edit_complete.generate_unique_filename', return_value='1234567890_abcdef.png'), \
             patch('fix_fill_in_blanks_edit_complete.allowed_file', return_value=True):
            
            success, result = fix_fill_in_blanks_edit(self.exercise_mock, self.db_mock, self.app_mock)
        
        # Vérifications
        self.assertTrue(success)
        self.assertEqual(result, 'redirect_result')
        mock_file.save.assert_called_once()
        self.assertEqual(self.exercise_mock.image_path, '/static/uploads/exercises/1234567890_abcdef.png')
        self.db_mock.session.commit.assert_called_once()
        flash_mock.assert_called_once_with('Exercice "Test Exercise" modifié avec succès!', 'success')

    @patch('fix_fill_in_blanks_edit_complete.request')
    @patch('fix_fill_in_blanks_edit_complete.flash')
    @patch('fix_fill_in_blanks_edit_complete.render_template')
    @patch('fix_fill_in_blanks_edit_complete.redirect')
    @patch('fix_fill_in_blanks_edit_complete.url_for')
    @patch('fix_fill_in_blanks_edit_complete.current_app')
    @patch('os.path.exists')
    @patch('os.remove')
    @patch('os.makedirs')
    def test_replace_existing_image(self, makedirs_mock, remove_mock, exists_mock, current_app_mock, 
                                  url_for_mock, redirect_mock, render_template_mock, flash_mock, request_mock):
        """Test le remplacement d'une image existante"""
        # Configuration de l'exercice avec une image existante
        self.exercise_mock.image_path = '/static/uploads/exercises/old_image.png'
        
        # Configuration des mocks
        request_mock.form.getlist.side_effect = lambda key: {
            'sentences[]': ['This is a ___ test.'],
            'words[]': ['simple']
        }[key]
        request_mock.form.get.return_value = None  # Pas de suppression d'image
        
        # Mock pour le fichier uploadé
        mock_file = MagicMock()
        mock_file.filename = 'new_image.png'
        request_mock.files = {'exercise_image': mock_file}
        
        # Mock pour os.path.exists
        exists_mock.return_value = True
        
        # Mock pour la redirection
        url_for_mock.return_value = '/view_exercise/1'
        redirect_mock.return_value = 'redirect_result'
        
        # Exécution de la fonction à tester
        with patch('fix_fill_in_blanks_edit_complete.open', mock_open()), \
             patch('fix_fill_in_blanks_edit_complete.generate_unique_filename', return_value='1234567890_abcdef.png'), \
             patch('fix_fill_in_blanks_edit_complete.allowed_file', return_value=True):
            
            success, result = fix_fill_in_blanks_edit(self.exercise_mock, self.db_mock, self.app_mock)
        
        # Vérifications
        self.assertTrue(success)
        self.assertEqual(result, 'redirect_result')
        remove_mock.assert_called_once()  # L'ancienne image a été supprimée
        mock_file.save.assert_called_once()  # La nouvelle image a été sauvegardée
        self.assertEqual(self.exercise_mock.image_path, '/static/uploads/exercises/1234567890_abcdef.png')
        self.db_mock.session.commit.assert_called_once()

    @patch('fix_fill_in_blanks_edit_complete.request')
    @patch('fix_fill_in_blanks_edit_complete.flash')
    @patch('fix_fill_in_blanks_edit_complete.render_template')
    @patch('fix_fill_in_blanks_edit_complete.redirect')
    @patch('fix_fill_in_blanks_edit_complete.url_for')
    @patch('fix_fill_in_blanks_edit_complete.current_app')
    @patch('os.path.exists')
    @patch('os.remove')
    def test_remove_existing_image(self, remove_mock, exists_mock, current_app_mock, 
                                url_for_mock, redirect_mock, render_template_mock, flash_mock, request_mock):
        """Test la suppression d'une image existante"""
        # Configuration de l'exercice avec une image existante
        self.exercise_mock.image_path = '/static/uploads/exercises/old_image.png'
        
        # Configuration des mocks
        request_mock.form.getlist.side_effect = lambda key: {
            'sentences[]': ['This is a ___ test.'],
            'words[]': ['simple']
        }[key]
        request_mock.form.get.return_value = 'true'  # Demande de suppression d'image
        request_mock.files = {}  # Pas de nouvelle image
        
        # Mock pour os.path.exists
        exists_mock.return_value = True
        
        # Mock pour la redirection
        url_for_mock.return_value = '/view_exercise/1'
        redirect_mock.return_value = 'redirect_result'
        
        # Exécution de la fonction à tester
        success, result = fix_fill_in_blanks_edit(self.exercise_mock, self.db_mock, self.app_mock)
        
        # Vérifications
        self.assertTrue(success)
        self.assertEqual(result, 'redirect_result')
        remove_mock.assert_called_once()  # L'image a été supprimée
        self.assertIsNone(self.exercise_mock.image_path)  # Le chemin d'image a été réinitialisé
        self.db_mock.session.commit.assert_called_once()

    @patch('fix_fill_in_blanks_edit_complete.request')
    @patch('fix_fill_in_blanks_edit_complete.flash')
    @patch('fix_fill_in_blanks_edit_complete.render_template')
    @patch('fix_fill_in_blanks_edit_complete.current_app')
    def test_invalid_data(self, current_app_mock, render_template_mock, flash_mock, request_mock):
        """Test avec des données invalides (phrases manquantes)"""
        # Configuration des mocks
        request_mock.form.getlist.side_effect = lambda key: {
            'sentences[]': [],  # Pas de phrases
            'words[]': ['simple']
        }[key]
        
        # Exécution de la fonction à tester
        success, _ = fix_fill_in_blanks_edit(self.exercise_mock, self.db_mock, self.app_mock)
        
        # Vérifications
        self.assertFalse(success)
        flash_mock.assert_called_once_with('Veuillez ajouter au moins une phrase.', 'error')
        self.db_mock.session.commit.assert_not_called()

    @patch('fix_fill_in_blanks_edit_complete.request')
    @patch('fix_fill_in_blanks_edit_complete.flash')
    @patch('fix_fill_in_blanks_edit_complete.render_template')
    @patch('fix_fill_in_blanks_edit_complete.redirect')
    @patch('fix_fill_in_blanks_edit_complete.url_for')
    @patch('fix_fill_in_blanks_edit_complete.current_app')
    def test_database_error(self, current_app_mock, url_for_mock, redirect_mock, 
                          render_template_mock, flash_mock, request_mock):
        """Test la gestion des erreurs de base de données"""
        # Configuration des mocks
        request_mock.form.getlist.side_effect = lambda key: {
            'sentences[]': ['This is a ___ test.'],
            'words[]': ['simple']
        }[key]
        request_mock.form.get.return_value = None
        request_mock.files = {}
        
        # Simuler une erreur lors du commit
        self.db_mock.session.commit.side_effect = Exception("Database error")
        
        # Exécution de la fonction à tester
        success, _ = fix_fill_in_blanks_edit(self.exercise_mock, self.db_mock, self.app_mock)
        
        # Vérifications
        self.assertFalse(success)
        self.db_mock.session.rollback.assert_called_once()
        flash_mock.assert_called_once_with('Erreur lors de la modification de l\'exercice: Database error', 'error')

if __name__ == '__main__':
    unittest.main()
