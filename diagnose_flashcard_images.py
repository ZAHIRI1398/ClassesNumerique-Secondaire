"""
Script de diagnostic pour les images des flashcards
Ce script analyse les problèmes d'affichage des images dans les flashcards
"""

import os
import json
import sqlite3
import logging
from flask import Flask, render_template, jsonify, request, redirect, url_for

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('flashcard_images_diagnosis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('flashcard_diagnosis')

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
            except Exception as e:
                logger.error(f"Erreur lors de la conversion JSON pour l'exercice {exercise_id}: {str(e)}")
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
                'card_images': card_images,
                'content': content
            })
        
        conn.close()
        return result
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des exercices: {str(e)}")
        return []

def check_image_exists(image_path):
    """
    Vérifie si une image existe à un chemin donné ou à des chemins alternatifs
    Retourne un dictionnaire avec les résultats de la vérification
    """
    if not image_path:
        logger.warning("Chemin d'image vide")
        return {
            'original_path': None,
            'exists': False,
            'found_at': None,
            'message': "Chemin d'image vide"
        }
    
    logger.debug(f"Vérification de l'existence de l'image: {image_path}")
    
    # Extraire le nom de fichier
    filename = os.path.basename(image_path)
    logger.debug(f"Nom de fichier extrait: {filename}")
    
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
        logger.debug(f"Vérification du chemin: {path}")
        if os.path.exists(path):
            logger.info(f"Image trouvée à: {path}")
            # Normaliser le chemin pour le retour
            normalized_path = path
            if not normalized_path.startswith('/'):
                normalized_path = f"/{normalized_path}"
            return {
                'original_path': image_path,
                'exists': True,
                'found_at': normalized_path.replace('\\', '/'),
                'message': f"Image trouvée à: {normalized_path}"
            }
    
    # Si l'image n'existe nulle part
    logger.warning(f"Image non trouvée: {image_path}")
    return {
        'original_path': image_path,
        'exists': False,
        'found_at': None,
        'message': f"Image non trouvée: {image_path}"
    }

def diagnose_flashcard_images():
    """
    Diagnostique les problèmes d'affichage des images dans les flashcards
    """
    logger.info("=== Diagnostic des images des flashcards ===")
    
    # Récupérer les exercices de type flashcards
    exercises = get_flashcard_exercises()
    logger.info(f"Nombre d'exercices de type flashcards: {len(exercises)}")
    
    results = []
    
    # Analyser les images des exercices
    for exercise in exercises:
        exercise_id = exercise['id']
        title = exercise['title']
        image_path = exercise['image_path']
        card_images = exercise['card_images']
        
        logger.info(f"Exercice {exercise_id}: {title}")
        
        exercise_result = {
            'id': exercise_id,
            'title': title,
            'main_image': None,
            'cards': []
        }
        
        # Vérifier l'image principale de l'exercice
        if image_path:
            logger.info(f"Image principale: {image_path}")
            check_result = check_image_exists(image_path)
            exercise_result['main_image'] = check_result
        
        # Vérifier les images des cartes
        for card_image in card_images:
            card_index = card_image['index']
            card_path = card_image['path']
            
            logger.info(f"Carte {card_index + 1}: {card_path}")
            check_result = check_image_exists(card_path)
            exercise_result['cards'].append({
                'index': card_index,
                'image': check_result
            })
        
        results.append(exercise_result)
    
    return results

def register_diagnose_flashcard_routes(app):
    """
    Enregistre les routes pour diagnostiquer les problèmes d'affichage des images dans les flashcards
    """
    @app.route('/diagnose-flashcard-images')
    def diagnose_flashcard_images_route():
        """
        Route pour diagnostiquer les problèmes d'affichage des images dans les flashcards
        """
        results = diagnose_flashcard_images()
        
        return render_template(
            'admin/simple_diagnose_flashcard_images.html',
            results=results
        )
    
    @app.route('/api/diagnose-flashcard-images', methods=['GET'])
    def diagnose_flashcard_images_api():
        """
        API pour diagnostiquer les problèmes d'affichage des images dans les flashcards
        """
        results = diagnose_flashcard_images()
        
        return jsonify({
            'success': True,
            'results': results
        })

# Si le script est exécuté directement, diagnostiquer les problèmes d'affichage des images
if __name__ == "__main__":
    print("=== Diagnostic des images des flashcards ===")
    results = diagnose_flashcard_images()
    
    # Afficher les résultats
    print(f"\n{len(results)} exercices analysés:")
    
    # Compter les problèmes
    total_cards = 0
    missing_cards = 0
    
    for exercise in results:
        exercise_id = exercise['id']
        title = exercise['title']
        main_image = exercise['main_image']
        cards = exercise['cards']
        
        print(f"\nExercice {exercise_id}: {title}")
        
        # Afficher le résultat pour l'image principale
        if main_image:
            status = "✓" if main_image['exists'] else "✗"
            print(f"  Image principale: {status} {main_image['message']}")
        
        # Afficher les résultats pour les images des cartes
        for card in cards:
            card_index = card['index']
            image = card['image']
            
            total_cards += 1
            if not image['exists']:
                missing_cards += 1
            
            status = "✓" if image['exists'] else "✗"
            print(f"  Carte {card_index + 1}: {status} {image['message']}")
    
    # Afficher le résumé
    print(f"\nRésumé: {missing_cards}/{total_cards} images de cartes manquantes")
