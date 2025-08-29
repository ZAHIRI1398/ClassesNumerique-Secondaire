"""
Script de test pour vérifier la correction des chemins d'images des flashcards
"""

import os
import json
import sqlite3
import requests
from urllib.parse import quote

# Configuration
DB_PATH = "instance/app.db"  # Chemin vers la base de données SQLite
BASE_URL = "http://localhost:5000"  # URL de base de l'application Flask

def get_flashcard_exercises():
    """
    Récupère tous les exercices de type flashcards depuis la base de données
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Requête pour récupérer les exercices de type flashcards
        query = """
        SELECT id, title, content, image_path
        FROM exercise
        WHERE exercise_type = 'flashcards'
        """
        
        cursor.execute(query)
        exercises = cursor.fetchall()
        
        result = []
        for exercise in exercises:
            exercise_id, title, content_json, image_path = exercise
            
            # Convertir le contenu JSON en dictionnaire Python
            try:
                content = json.loads(content_json) if content_json else {}
            except:
                content = {}
            
            # Extraire les chemins d'images des cartes
            cards = content.get('cards', [])
            card_images = []
            
            for i, card in enumerate(cards):
                if isinstance(card, dict) and 'image' in card and card['image']:
                    card_images.append({
                        'index': i,
                        'path': card['image']
                    })
            
            result.append({
                'id': exercise_id,
                'title': title,
                'image_path': image_path,
                'card_images': card_images
            })
        
        conn.close()
        return result
        
    except Exception as e:
        print(f"Erreur lors de la récupération des exercices: {str(e)}")
        return []

def check_image_url(image_path):
    """
    Vérifie si une URL d'image est accessible via la route /get_cloudinary_url
    """
    if not image_path:
        return {
            'original_path': image_path,
            'status': 'error',
            'message': 'Chemin d\'image vide'
        }
    
    try:
        # Encoder le chemin d'image pour l'URL
        encoded_path = quote(image_path)
        url = f"{BASE_URL}/get_cloudinary_url?image_path={encoded_path}"
        
        # Faire une requête GET à la route /get_cloudinary_url
        response = requests.get(url)
        
        if response.status_code == 200:
            # Récupérer l'URL générée
            data = response.json()
            cloudinary_url = data.get('url')
            
            # Vérifier si l'URL générée est accessible
            if cloudinary_url:
                # Faire une requête GET à l'URL générée
                image_response = requests.get(cloudinary_url)
                
                if image_response.status_code == 200:
                    return {
                        'original_path': image_path,
                        'cloudinary_url': cloudinary_url,
                        'status': 'success',
                        'message': 'URL accessible'
                    }
                else:
                    return {
                        'original_path': image_path,
                        'cloudinary_url': cloudinary_url,
                        'status': 'error',
                        'message': f'URL inaccessible (code {image_response.status_code})'
                    }
            else:
                return {
                    'original_path': image_path,
                    'status': 'error',
                    'message': 'URL générée vide'
                }
        else:
            return {
                'original_path': image_path,
                'status': 'error',
                'message': f'Erreur lors de la génération de l\'URL (code {response.status_code})'
            }
            
    except Exception as e:
        return {
            'original_path': image_path,
            'status': 'error',
            'message': f'Erreur: {str(e)}'
        }

def test_flashcard_images():
    """
    Teste l'accessibilité des images des flashcards
    """
    print("=== Test des images des flashcards ===")
    
    # Récupérer les exercices de type flashcards
    exercises = get_flashcard_exercises()
    print(f"Nombre d'exercices de type flashcards: {len(exercises)}")
    
    # Tester les images des exercices
    for exercise in exercises:
        exercise_id = exercise['id']
        title = exercise['title']
        image_path = exercise['image_path']
        card_images = exercise['card_images']
        
        print(f"\nExercice {exercise_id}: {title}")
        
        # Tester l'image de l'exercice
        if image_path:
            print(f"  Image de l'exercice: {image_path}")
            result = check_image_url(image_path)
            status = "✓" if result['status'] == 'success' else "✗"
            print(f"    {status} {result['message']}")
            if 'cloudinary_url' in result:
                print(f"    URL: {result['cloudinary_url']}")
        
        # Tester les images des cartes
        for card_image in card_images:
            card_index = card_image['index']
            card_path = card_image['path']
            
            print(f"  Carte {card_index + 1}: {card_path}")
            result = check_image_url(card_path)
            status = "✓" if result['status'] == 'success' else "✗"
            print(f"    {status} {result['message']}")
            if 'cloudinary_url' in result:
                print(f"    URL: {result['cloudinary_url']}")

def test_fix_flashcard_images_api():
    """
    Teste l'API de correction des chemins d'images des flashcards
    """
    print("\n=== Test de l'API de correction des chemins d'images ===")
    
    try:
        # Faire une requête POST à l'API
        url = f"{BASE_URL}/api/fix-flashcard-images"
        response = requests.post(url)
        
        if response.status_code == 200:
            data = response.json()
            success = data.get('success', False)
            results = data.get('results', [])
            
            if success:
                print(f"API de correction exécutée avec succès: {len(results)} chemins corrigés")
                
                # Afficher les résultats
                for result in results:
                    status = "✓" if result['success'] else "✗"
                    if result['type'] == 'exercise_image':
                        print(f"{status} Exercice {result['exercise_id']} ({result['title']}): {result['old_path']} → {result['new_path']}")
                    else:
                        print(f"{status} Carte {result['card_index']} de l'exercice {result['exercise_id']} ({result['title']}): {result['old_path']} → {result['new_path']}")
            else:
                print("Échec de l'API de correction")
        else:
            print(f"Erreur lors de l'appel à l'API: code {response.status_code}")
            
    except Exception as e:
        print(f"Erreur lors du test de l'API: {str(e)}")

if __name__ == "__main__":
    # Tester les images des flashcards
    test_flashcard_images()
    
    # Tester l'API de correction des chemins d'images
    test_fix_flashcard_images_api()
    
    # Tester à nouveau les images des flashcards après correction
    print("\n=== Test des images des flashcards après correction ===")
    test_flashcard_images()
