"""
Script de test pour vérifier si la fonction cloud_storage.get_cloudinary_url est correctement exposée
aux templates Jinja2 et si elle accepte deux arguments.
"""

import os
import sys
from flask import Flask, render_template_string
import cloud_storage

app = Flask(__name__)

# Exposer la fonction cloud_storage.get_cloudinary_url aux templates Jinja2
app.jinja_env.globals.update(cloud_storage=cloud_storage)

# Template de test simulant l'appel dans pairs_edit.html
test_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Test cloud_storage.get_cloudinary_url</title>
</head>
<body>
    <h1>Test de la fonction cloud_storage.get_cloudinary_url</h1>
    
    <h2>Test avec un argument:</h2>
    <p>{{ cloud_storage.get_cloudinary_url('test_image.jpg') }}</p>
    
    <h2>Test avec deux arguments:</h2>
    <p>{{ cloud_storage.get_cloudinary_url('test_image.jpg', 'pairs') }}</p>
</body>
</html>
"""

@app.route('/')
def test():
    """Route de test pour vérifier si la fonction cloud_storage.get_cloudinary_url accepte deux arguments"""
    try:
        # Tester le rendu du template
        rendered = render_template_string(test_template)
        print("[OK] Le template a ete rendu avec succes!")
        print("[OK] La fonction cloud_storage.get_cloudinary_url accepte bien deux arguments.")
        return rendered
    except Exception as e:
        print(f"[ERREUR] Erreur lors du rendu du template: {str(e)}")
        return f"Erreur: {str(e)}"

if __name__ == "__main__":
    print("=== Test de la fonction cloud_storage.get_cloudinary_url dans les templates ===")
    
    # Tester directement la fonction pour vérifier sa signature
    try:
        # Test avec un argument
        result1 = cloud_storage.get_cloudinary_url('test_image.jpg')
        print(f"[OK] Test avec un argument reussi: {result1}")
        
        # Test avec deux arguments
        result2 = cloud_storage.get_cloudinary_url('test_image.jpg', 'pairs')
        print(f"[OK] Test avec deux arguments reussi: {result2}")
        
        print("\nLancement du serveur Flask pour tester le rendu du template...")
        app.run(debug=True, port=5001)
    except Exception as e:
        print(f"[ERREUR] Erreur lors du test direct de la fonction: {str(e)}")
