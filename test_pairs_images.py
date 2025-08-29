"""
Script de test pour vérifier l'affichage des images dans les exercices de type pairs
"""
import os
import json
import requests
from bs4 import BeautifulSoup
from app import app, db, Exercise, cloud_storage
from flask import url_for

def test_pairs_exercise_images():
    """Teste l'affichage des images dans un exercice de type pairs"""
    with app.app_context():
        # Récupérer l'exercice #92
        exercise = Exercise.query.get(92)
        if not exercise:
            print("Exercice #92 non trouvé")
            return
        
        print(f"Exercice trouvé: {exercise.title} (ID: {exercise.id})")
        
        # Analyser le contenu JSON
        content = json.loads(exercise.content)
        
        # Vérifier si le contenu contient des paires avec des images
        if 'pairs' in content:
            print(f"Nombre de paires: {len(content['pairs'])}")
            
            # Vérifier chaque paire
            for i, pair in enumerate(content['pairs']):
                print(f"\nPaire #{i+1}:")
                
                # Vérifier l'élément de gauche
                if pair['left']['type'] == 'image':
                    image_path = pair['left']['content']
                    print(f"  Image gauche: {image_path}")
                    
                    # Tester la fonction get_cloudinary_url avec exercise_type='pairs'
                    normalized_path = cloud_storage.get_cloudinary_url(image_path, 'pairs')
                    print(f"  URL normalisée: {normalized_path}")
                    
                    # Vérifier si le fichier existe
                    if image_path.startswith('/static/'):
                        file_path = os.path.join(app.root_path, image_path[1:])
                        exists = os.path.exists(file_path)
                        print(f"  Le fichier existe: {exists}")
                        if not exists:
                            print(f"  Chemin complet: {file_path}")
                
                # Vérifier l'élément de droite
                if pair['right']['type'] == 'image':
                    image_path = pair['right']['content']
                    print(f"  Image droite: {image_path}")
                    
                    # Tester la fonction get_cloudinary_url avec exercise_type='pairs'
                    normalized_path = cloud_storage.get_cloudinary_url(image_path, 'pairs')
                    print(f"  URL normalisée: {normalized_path}")
                    
                    # Vérifier si le fichier existe
                    if image_path.startswith('/static/'):
                        file_path = os.path.join(app.root_path, image_path[1:])
                        exists = os.path.exists(file_path)
                        print(f"  Le fichier existe: {exists}")
                        if not exists:
                            print(f"  Chemin complet: {file_path}")

if __name__ == "__main__":
    test_pairs_exercise_images()
