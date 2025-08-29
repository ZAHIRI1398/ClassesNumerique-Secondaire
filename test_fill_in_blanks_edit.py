"""
Script de test pour valider la correction de l'édition des exercices fill_in_blanks

Ce script simule une requête POST pour l'édition d'un exercice fill_in_blanks
et vérifie que le contenu JSON est correctement mis à jour.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Ajouter le répertoire parent au chemin de recherche des modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import de la fonction de correction
from fix_fill_in_blanks_edit import fix_fill_in_blanks_edit

class TestFillInBlanksEdit(unittest.TestCase):
    """Tests pour la correction de l'édition des exercices fill_in_blanks"""

    @patch('flask.request')
    def test_valid_data(self, mock_request):
        """Test avec des données valides"""
        # Simuler les données du formulaire
        mock_request.form.getlist.side_effect = lambda key: {
            'sentences[]': ['Voici une ___ avec un trou.', 'Une autre ___ avec ___ trous.'],
            'words[]': ['phrase', 'phrase', 'deux']
        }[key]

        # Créer un mock pour l'exercice
        mock_exercise = MagicMock()
        mock_exercise.get_content.return_value = {
            'sentences': ['Ancienne phrase avec ___.'],
            'words': ['trou']
        }

        # Appeler la fonction de correction
        content = {'sentences': ['Ancienne phrase avec ___.'], 'words': ['trou']}
        success, _ = fix_fill_in_blanks_edit(mock_exercise, content)

        # Vérifier que le contenu a été mis à jour correctement
        self.assertTrue(success)
        self.assertEqual(content['sentences'], ['Voici une ___ avec un trou.', 'Une autre ___ avec ___ trous.'])
        self.assertEqual(content['words'], ['phrase', 'phrase', 'deux'])
        self.assertEqual(mock_exercise.content, json.dumps(content))

    @patch('flask.request')
    @patch('flask.flash')
    @patch('flask.render_template')
    def test_missing_sentences(self, mock_render, mock_flash, mock_request):
        """Test avec des phrases manquantes"""
        # Simuler les données du formulaire
        mock_request.form.getlist.side_effect = lambda key: {
            'sentences[]': [],
            'words[]': ['mot1', 'mot2']
        }[key]

        # Créer un mock pour l'exercice
        mock_exercise = MagicMock()
        mock_exercise.get_content.return_value = {}

        # Appeler la fonction de correction
        content = {}
        success, _ = fix_fill_in_blanks_edit(mock_exercise, content)

        # Vérifier que l'erreur a été détectée
        self.assertFalse(success)
        mock_flash.assert_called_with('Veuillez ajouter au moins une phrase.', 'error')

    @patch('flask.request')
    @patch('flask.flash')
    @patch('flask.render_template')
    def test_missing_words(self, mock_render, mock_flash, mock_request):
        """Test avec des mots manquants"""
        # Simuler les données du formulaire
        mock_request.form.getlist.side_effect = lambda key: {
            'sentences[]': ['Phrase avec ___.'],
            'words[]': []
        }[key]

        # Créer un mock pour l'exercice
        mock_exercise = MagicMock()
        mock_exercise.get_content.return_value = {}

        # Appeler la fonction de correction
        content = {}
        success, _ = fix_fill_in_blanks_edit(mock_exercise, content)

        # Vérifier que l'erreur a été détectée
        self.assertFalse(success)
        mock_flash.assert_called_with('Veuillez ajouter au moins un mot.', 'error')

    @patch('flask.request')
    @patch('flask.flash')
    @patch('flask.render_template')
    def test_sentence_without_blanks(self, mock_render, mock_flash, mock_request):
        """Test avec une phrase sans trous"""
        # Simuler les données du formulaire
        mock_request.form.getlist.side_effect = lambda key: {
            'sentences[]': ['Phrase avec un trou.', 'Phrase sans trou'],
            'words[]': ['mot1']
        }[key]

        # Créer un mock pour l'exercice
        mock_exercise = MagicMock()
        mock_exercise.get_content.return_value = {}

        # Appeler la fonction de correction
        content = {}
        success, _ = fix_fill_in_blanks_edit(mock_exercise, content)

        # Vérifier que l'erreur a été détectée
        self.assertFalse(success)
        mock_flash.assert_called_with('La phrase 2 ne contient pas de trous (utilisez ___ pour marquer les trous).', 'error')

    @patch('flask.request')
    @patch('flask.flash')
    @patch('flask.render_template')
    def test_not_enough_words(self, mock_render, mock_flash, mock_request):
        """Test avec pas assez de mots pour tous les trous"""
        # Simuler les données du formulaire
        mock_request.form.getlist.side_effect = lambda key: {
            'sentences[]': ['Phrase avec ___.', 'Phrase avec ___ et ___.'],
            'words[]': ['mot1', 'mot2']
        }[key]

        # Créer un mock pour l'exercice
        mock_exercise = MagicMock()
        mock_exercise.get_content.return_value = {}

        # Appeler la fonction de correction
        content = {}
        success, _ = fix_fill_in_blanks_edit(mock_exercise, content)

        # Vérifier que l'erreur a été détectée
        self.assertFalse(success)
        mock_flash.assert_called_with('Il n\'y a pas assez de mots (2) pour remplir tous les trous (3).', 'error')

if __name__ == '__main__':
    unittest.main()
