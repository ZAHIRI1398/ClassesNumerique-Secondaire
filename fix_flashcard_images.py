"""
Script de correction automatique des chemins d'images pour les flashcards
Ce script corrige les chemins d'images dans la base de données et vérifie leur existence
"""

import os
import json
import sqlite3
from flask import Flask, render_template, jsonify, request, redirect, url_for
from utils.image_path_manager import ImagePathManager

# Configuration
DB_PATH = "instance/app.db"  # Chemin vers la base de données SQLite

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

def check_image_exists(image_path):
    """
    Vérifie si une image existe à un chemin donné ou à des chemins alternatifs
    Retourne le chemin correct si l'image existe, sinon None
    """
    if not image_path:
        return None
    
    # Extraire le nom de fichier
    filename = os.path.basename(image_path)
    
    # Liste des chemins possibles à vérifier
    possible_paths = [
        image_path,  # Chemin original
        image_path[1:] if image_path.startswith('/') else image_path,  # Sans le slash initial
        f"/static/uploads/{filename}",  # Dans /static/uploads/
        f"static/uploads/{filename}",  # Dans static/uploads/ sans slash initial
        f"/static/exercises/{filename}",  # Dans /static/exercises/
        f"static/exercises/{filename}",  # Dans static/exercises/ sans slash initial
        f"/static/uploads/flashcards/{filename}",  # Dans /static/uploads/flashcards/
        f"static/uploads/flashcards/{filename}",  # Dans static/uploads/flashcards/ sans slash initial
        f"/static/exercises/flashcards/{filename}",  # Dans /static/exercises/flashcards/
        f"static/exercises/flashcards/{filename}"  # Dans static/exercises/flashcards/ sans slash initial
    ]
    
    # Vérifier chaque chemin possible
    for path in possible_paths:
        if os.path.exists(path):
            # Normaliser le chemin pour le retour
            normalized_path = path
            if not normalized_path.startswith('/'):
                normalized_path = f"/{normalized_path}"
            return normalized_path.replace('\\', '/')
    
    # Si l'image n'existe nulle part, retourner None
    return None

def fix_image_path(image_path):
    """
    Corrige un chemin d'image en vérifiant son existence
    Si l'image n'existe pas, retourne un chemin par défaut
    """
    if not image_path:
        return None
    
    # Vérifier si l'image existe
    correct_path = check_image_exists(image_path)
    
    if correct_path:
        return correct_path
    
    # Si l'image n'existe pas, extraire le nom de fichier et construire un chemin par défaut
    filename = os.path.basename(image_path)
    default_path = f"/static/uploads/{filename}"
    
    return default_path

def update_exercise_image_path(exercise_id, new_path):
    """
    Met à jour le chemin d'image d'un exercice dans la base de données
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Mettre à jour le chemin d'image
        query = """
        UPDATE exercise
        SET image_path = ?
        WHERE id = ?
        """
        
        cursor.execute(query, (new_path, exercise_id))
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Erreur lors de la mise à jour du chemin d'image: {str(e)}")
        return False

def update_card_image_path(exercise_id, card_index, new_path):
    """
    Met à jour le chemin d'image d'une carte dans la base de données
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Récupérer le contenu actuel
        query = """
        SELECT content
        FROM exercise
        WHERE id = ?
        """
        
        cursor.execute(query, (exercise_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return False
        
        content_json = result[0]
        
        # Convertir le contenu JSON en dictionnaire Python
        try:
            content = json.loads(content_json) if content_json else {}
        except:
            content = {}
        
        # Mettre à jour le chemin d'image de la carte
        cards = content.get('cards', [])
        if 0 <= card_index < len(cards) and isinstance(cards[card_index], dict):
            cards[card_index]['image'] = new_path
            content['cards'] = cards
            
            # Mettre à jour le contenu dans la base de données
            update_query = """
            UPDATE exercise
            SET content = ?
            WHERE id = ?
            """
            
            cursor.execute(update_query, (json.dumps(content), exercise_id))
            conn.commit()
            conn.close()
            
            return True
        
        conn.close()
        return False
        
    except Exception as e:
        print(f"Erreur lors de la mise à jour du chemin d'image de la carte: {str(e)}")
        return False

def fix_all_flashcard_images():
    """
    Corrige tous les chemins d'images des flashcards dans la base de données
    """
    exercises = get_flashcard_exercises()
    results = []
    
    for exercise in exercises:
        exercise_id = exercise['id']
        title = exercise['title']
        image_path = exercise['image_path']
        card_images = exercise['card_images']
        
        # Corriger le chemin d'image de l'exercice
        if image_path:
            new_path = fix_image_path(image_path)
            if new_path != image_path:
                success = update_exercise_image_path(exercise_id, new_path)
                results.append({
                    'type': 'exercise_image',
                    'exercise_id': exercise_id,
                    'title': title,
                    'old_path': image_path,
                    'new_path': new_path,
                    'success': success
                })
        
        # Corriger les chemins d'images des cartes
        for card_image in card_images:
            card_index = card_image['index']
            card_path = card_image['path']
            
            new_path = fix_image_path(card_path)
            if new_path != card_path:
                success = update_card_image_path(exercise_id, card_index, new_path)
                results.append({
                    'type': 'card_image',
                    'exercise_id': exercise_id,
                    'title': title,
                    'card_index': card_index,
                    'old_path': card_path,
                    'new_path': new_path,
                    'success': success
                })
    
    return results

def register_fix_flashcard_images_routes(app):
    """
    Enregistre les routes pour corriger les chemins d'images des flashcards
    """
    @app.route('/fix-flashcard-images', methods=['GET'])
    def fix_flashcard_images_route():
        """
        Route pour corriger les chemins d'images des flashcards
        """
        results = fix_all_flashcard_images()
        
        return render_template(
            'admin/simple_fix_flashcard_images.html',
            results=results
        )
    
    @app.route('/api/fix-flashcard-images', methods=['POST'])
    def fix_flashcard_images_api():
        """
        API pour corriger les chemins d'images des flashcards
        """
        results = fix_all_flashcard_images()
        
        return jsonify({
            'success': True,
            'results': results
        })

# Si le script est exécuté directement, corriger les chemins d'images
if __name__ == "__main__":
    print("=== Correction des chemins d'images des flashcards ===")
    results = fix_all_flashcard_images()
    
    print(f"\n{len(results)} chemins d'images corrigés:")
    for result in results:
        status = "✓" if result['success'] else "✗"
        if result['type'] == 'exercise_image':
            print(f"{status} Exercice {result['exercise_id']} ({result['title']}): {result['old_path']} → {result['new_path']}")
        else:
            print(f"{status} Carte {result['card_index']} de l'exercice {result['exercise_id']} ({result['title']}): {result['old_path']} → {result['new_path']}")
