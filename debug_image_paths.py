"""
Script de débogage pour les chemins d'images dans les flashcards
Ce script teste la route /get_cloudinary_url avec des chemins d'images réels
et vérifie si les fichiers existent physiquement sur le disque
"""

import os
import sys
import json
import sqlite3
import requests
from pathlib import Path

# Configuration
DB_PATH = "instance/app.db"
BASE_URL = "http://127.0.0.1:5000"
STATIC_DIR = "static"
EXERCISES_DIR = os.path.join(STATIC_DIR, "exercises")

def get_flashcard_image_paths():
    """Récupère tous les chemins d'images des flashcards depuis la base de données"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Récupérer tous les exercices de type flashcards
        cursor.execute("""
            SELECT id, title, content, exercise_type 
            FROM exercise 
            WHERE exercise_type = 'flashcards'
        """)
        
        exercises = cursor.fetchall()
        print(f"Trouvé {len(exercises)} exercices de type flashcards")
        
        image_paths = []
        for exercise in exercises:
            exercise_id, title, content_json, exercise_type = exercise
            
            try:
                content = json.loads(content_json)
                if 'cards' in content:
                    for i, card in enumerate(content['cards']):
                        if 'image' in card and card['image']:
                            image_paths.append({
                                'exercise_id': exercise_id,
                                'exercise_title': title,
                                'card_index': i,
                                'image_path': card['image']
                            })
            except json.JSONDecodeError:
                print(f"Erreur de décodage JSON pour l'exercice {exercise_id}")
                continue
        
        conn.close()
        return image_paths
    
    except sqlite3.Error as e:
        print(f"Erreur SQLite: {e}")
        return []

def check_file_exists(path):
    """Vérifie si un fichier existe physiquement sur le disque"""
    # Normaliser le chemin pour supprimer le / initial si présent
    if path.startswith('/'):
        path = path[1:]
    
    # Vérifier si le fichier existe
    return os.path.exists(path)

def test_get_cloudinary_url(image_path):
    """Teste la route /get_cloudinary_url avec un chemin d'image"""
    try:
        response = requests.get(f"{BASE_URL}/get_cloudinary_url", params={"image_path": image_path})
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Erreur HTTP {response.status_code}", "details": response.text}
    except requests.RequestException as e:
        return {"error": f"Erreur de requête: {str(e)}"}

def check_all_possible_paths(filename):
    """Vérifie toutes les combinaisons possibles de chemins pour un fichier"""
    possible_paths = [
        os.path.join(STATIC_DIR, "exercises", "general", filename),
        os.path.join(STATIC_DIR, "exercises", "flashcards", filename),
        os.path.join(STATIC_DIR, "uploads", "flashcards", filename),
        os.path.join(STATIC_DIR, "uploads", "general", filename),
        os.path.join(STATIC_DIR, "uploads", filename),
        os.path.join(STATIC_DIR, "exercises", filename),
        os.path.join("uploads", filename),
        os.path.join("exercises", filename),
        filename
    ]
    
    results = []
    for path in possible_paths:
        exists = check_file_exists(path)
        results.append({
            "path": path,
            "exists": exists,
            "size": os.path.getsize(path) if exists else None
        })
    
    return results

def main():
    """Fonction principale"""
    print("=== DÉBOGAGE DES CHEMINS D'IMAGES FLASHCARDS ===")
    
    # Récupérer les chemins d'images
    image_paths = get_flashcard_image_paths()
    print(f"Trouvé {len(image_paths)} chemins d'images dans les flashcards")
    
    # Vérifier chaque chemin d'image
    for i, item in enumerate(image_paths):
        print(f"\n--- Image {i+1}/{len(image_paths)} ---")
        print(f"Exercice: {item['exercise_title']} (ID: {item['exercise_id']})")
        print(f"Carte: {item['card_index']}")
        print(f"Chemin d'image: {item['image_path']}")
        
        # Vérifier si le fichier existe
        path_exists = check_file_exists(item['image_path'])
        print(f"Le fichier existe directement: {path_exists}")
        
        # Extraire le nom de fichier
        filename = os.path.basename(item['image_path'])
        print(f"Nom de fichier: {filename}")
        
        # Vérifier toutes les combinaisons possibles
        print("Vérification de toutes les combinaisons possibles:")
        possible_paths = check_all_possible_paths(filename)
        for path_info in possible_paths:
            status = "✅ EXISTE" if path_info["exists"] else "❌ N'EXISTE PAS"
            size_info = f" ({path_info['size']} octets)" if path_info["exists"] else ""
            print(f"  {status}: {path_info['path']}{size_info}")
        
        # Tester la route /get_cloudinary_url
        print("Test de la route /get_cloudinary_url:")
        result = test_get_cloudinary_url(item['image_path'])
        if 'url' in result:
            print(f"  URL générée: {result['url']}")
            # Vérifier si l'URL générée pointe vers un fichier existant
            url_path = result['url']
            if url_path.startswith('/'):
                url_path = url_path[1:]
            url_exists = check_file_exists(url_path)
            print(f"  Le fichier à l'URL générée existe: {url_exists}")
        else:
            print(f"  Erreur: {result.get('error', 'Inconnue')}")
            if 'details' in result:
                print(f"  Détails: {result['details']}")

if __name__ == "__main__":
    main()
