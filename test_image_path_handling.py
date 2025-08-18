"""
Script de test pour vérifier la correction de la fonction get_cloudinary_url
Ce script teste différents cas de chemins d'images pour s'assurer que la normalisation fonctionne correctement
"""

import sys
import os
from flask import Flask

# Créer une application Flask minimale pour le contexte
app = Flask(__name__)
app.logger.setLevel('DEBUG')

# Importer le module cloud_storage
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import cloud_storage

def test_get_cloudinary_url():
    """
    Teste la fonction get_cloudinary_url avec différents types de chemins d'images
    """
    print("\n=== TEST DE LA FONCTION get_cloudinary_url ===\n")
    
    # Liste des cas de test avec description et valeur attendue
    test_cases = [
        {
            "description": "URL Cloudinary",
            "input": "https://res.cloudinary.com/demo/image/upload/v1234567890/sample.jpg",
            "expected": "https://res.cloudinary.com/demo/image/upload/v1234567890/sample.jpg"
        },
        {
            "description": "URL externe",
            "input": "https://example.com/images/photo.jpg",
            "expected": "https://example.com/images/photo.jpg"
        },
        {
            "description": "Chemin avec /static/uploads/ dupliqué",
            "input": "/static/uploads/static/uploads/image.jpg",
            "expected": "/static/uploads/image.jpg"
        },
        {
            "description": "Chemin avec /static/uploads/ simple",
            "input": "/static/uploads/image.jpg",
            "expected": "/static/uploads/image.jpg"
        },
        {
            "description": "Chemin commençant par /static/",
            "input": "/static/images/photo.png",
            "expected": "/static/images/photo.png"
        },
        {
            "description": "Chemin commençant par static/ (sans slash)",
            "input": "static/uploads/image.jpg",
            "expected": "/static/uploads/image.jpg"
        },
        {
            "description": "Nom de fichier simple",
            "input": "image.jpg",
            "expected": "/static/uploads/image.jpg"
        },
        {
            "description": "Chemin relatif",
            "input": "uploads/image.jpg",
            "expected": "/static/uploads/image.jpg"
        },
        {
            "description": "Chemin avec sous-dossiers",
            "input": "dossier1/dossier2/image.jpg",
            "expected": "/static/uploads/image.jpg"
        },
        {
            "description": "Valeur None",
            "input": None,
            "expected": None
        }
    ]
    
    # Exécuter les tests
    for i, test in enumerate(test_cases, 1):
        with app.app_context():
            result = cloud_storage.get_cloudinary_url(test["input"])
            status = "SUCCES" if result == test["expected"] else "ECHEC"
            
            print(f"Test {i}: {test['description']}")
            print(f"  Entrée:    {test['input']}")
            print(f"  Attendu:   {test['expected']}")
            print(f"  Résultat:  {result}")
            print(f"  Statut:    {status}")
            print()

def test_with_real_examples():
    """
    Teste la fonction avec des exemples réels de chemins d'images provenant de la base de données
    """
    print("\n=== TEST AVEC DES EXEMPLES RÉELS ===\n")
    
    real_examples = [
        "/static/uploads/1738345030_image5.jpeg",
        "static/uploads/triangle.png",
        "/static/uploads/static/uploads/corps_humain_exemple.jpg",
        "https://res.cloudinary.com/demo/image/upload/v1234567890/clopepe.png"
    ]
    
    for i, example in enumerate(real_examples, 1):
        with app.app_context():
            result = cloud_storage.get_cloudinary_url(example)
            print(f"Exemple {i}:")
            print(f"  Original:  {example}")
            print(f"  Normalisé: {result}")
            print()

if __name__ == "__main__":
    test_get_cloudinary_url()
    test_with_real_examples()
    print("Tests terminés.")
