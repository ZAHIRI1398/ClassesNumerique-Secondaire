"""
Script de test pour la route /get_cloudinary_url
Ce script permet de tester la route avec différents chemins d'images
et d'analyser les résultats pour diagnostiquer les problèmes d'affichage
"""

import os
import sys
import requests
import json
import sqlite3
from urllib.parse import quote

# Configuration
BASE_URL = "http://127.0.0.1:5000"  # URL de base de l'application Flask
DB_PATH = "instance/app.db"  # Chemin vers la base de données SQLite

def get_flashcard_image_paths():
    """
    Récupère tous les chemins d'images des flashcards depuis la base de données
    """
    print("Récupération des chemins d'images des flashcards depuis la base de données...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Requête pour récupérer les chemins d'images des flashcards
        query = """
        SELECT e.id, e.title, e.image_path, json_extract(e.content, '$.cards[0].image') as card_image
        FROM exercise e
        WHERE e.exercise_type = 'flashcards'
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        image_paths = []
        for row in results:
            exercise_id, title, exercise_image, card_image = row
            
            # Ajouter l'image de l'exercice si elle existe
            if exercise_image:
                image_paths.append({
                    'exercise_id': exercise_id,
                    'title': title,
                    'type': 'exercise_image',
                    'path': exercise_image
                })
            
            # Ajouter l'image de la carte si elle existe
            if card_image and card_image != 'null':
                # Enlever les guillemets si présents
                if card_image.startswith('"') and card_image.endswith('"'):
                    card_image = card_image[1:-1]
                
                image_paths.append({
                    'exercise_id': exercise_id,
                    'title': title,
                    'type': 'card_image',
                    'path': card_image
                })
        
        conn.close()
        print(f"Trouvé {len(image_paths)} chemins d'images dans les flashcards.")
        return image_paths
        
    except Exception as e:
        print(f"Erreur lors de la récupération des chemins d'images: {str(e)}")
        return []

def test_cloudinary_url(image_path):
    """
    Teste la route /get_cloudinary_url avec un chemin d'image spécifique
    """
    try:
        # Encoder le chemin d'image pour l'URL
        encoded_path = quote(image_path)
        url = f"{BASE_URL}/get_cloudinary_url?image_path={encoded_path}"
        
        # Faire la requête
        response = requests.get(url)
        
        # Vérifier si la requête a réussi
        if response.status_code == 200:
            data = response.json()
            return {
                'status': 'success',
                'url': data.get('url'),
                'response': data
            }
        else:
            return {
                'status': 'error',
                'code': response.status_code,
                'response': response.text
            }
    except Exception as e:
        return {
            'status': 'exception',
            'error': str(e)
        }

def test_debug_image_paths(image_path):
    """
    Teste la route /debug-image-paths avec un chemin d'image spécifique
    """
    try:
        # Encoder le chemin d'image pour l'URL
        encoded_path = quote(image_path)
        url = f"{BASE_URL}/debug-image-paths?image_path={encoded_path}"
        
        # Faire la requête
        response = requests.get(url)
        
        # Vérifier si la requête a réussi
        if response.status_code == 200:
            data = response.json()
            return {
                'status': 'success',
                'data': data
            }
        else:
            return {
                'status': 'error',
                'code': response.status_code,
                'response': response.text
            }
    except Exception as e:
        return {
            'status': 'exception',
            'error': str(e)
        }

def check_file_exists(path):
    """
    Vérifie si un fichier existe à un chemin donné
    """
    if not path:
        return False
    
    # Essayer le chemin tel quel
    if os.path.exists(path):
        return True
    
    # Essayer sans le slash initial
    if path.startswith('/'):
        if os.path.exists(path[1:]):
            return True
    
    # Essayer avec un slash initial
    if not path.startswith('/'):
        if os.path.exists('/' + path):
            return True
    
    return False

def main():
    """
    Fonction principale
    """
    print("=== Test de la route /get_cloudinary_url ===")
    
    # Vérifier si un chemin d'image spécifique est fourni en argument
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        print(f"Test avec le chemin d'image spécifié: {image_path}")
        
        # Tester la route /get_cloudinary_url
        result = test_cloudinary_url(image_path)
        print("\nRésultat du test /get_cloudinary_url:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Tester la route /debug-image-paths
        debug_result = test_debug_image_paths(image_path)
        print("\nRésultat du test /debug-image-paths:")
        print(json.dumps(debug_result, indent=2, ensure_ascii=False))
        
    else:
        # Récupérer tous les chemins d'images des flashcards
        image_paths = get_flashcard_image_paths()
        
        if not image_paths:
            print("Aucun chemin d'image trouvé dans les flashcards.")
            return
        
        print("\n=== Résultats des tests ===")
        
        # Tester chaque chemin d'image
        for i, image_info in enumerate(image_paths):
            image_path = image_info['path']
            print(f"\n--- Test {i+1}/{len(image_paths)}: {image_path} ---")
            print(f"Exercise ID: {image_info['exercise_id']}, Titre: {image_info['title']}")
            print(f"Type: {image_info['type']}")
            
            # Vérifier si le fichier existe
            exists = check_file_exists(image_path)
            print(f"Le fichier existe: {exists}")
            
            # Tester la route /get_cloudinary_url
            result = test_cloudinary_url(image_path)
            print("Résultat du test /get_cloudinary_url:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # Tester la route /debug-image-paths
            debug_result = test_debug_image_paths(image_path)
            print("Résultat du test /debug-image-paths:")
            print(json.dumps(debug_result, indent=2, ensure_ascii=False))
            
            print("-" * 50)

if __name__ == "__main__":
    main()
