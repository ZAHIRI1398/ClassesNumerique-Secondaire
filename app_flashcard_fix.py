"""
Version simplifiée de l'application Flask pour tester la correction des images des flashcards
Sans dépendance aux modules problématiques
"""

import os
import json
import sqlite3
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Import des modules de correction des flashcards
from fix_flashcard_images import register_fix_flashcard_images_routes
from diagnose_flashcard_images import register_diagnose_flashcard_routes
from image_url_service import get_cloudinary_url, ImageUrlService

# Création de l'application Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'flashcard_fix_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['DATABASE'] = 'instance/app.db'

# Configuration des routes pour la correction des flashcards
register_fix_flashcard_images_routes(app)
register_diagnose_flashcard_routes(app)

# Route pour la page d'accueil
@app.route('/')
def home():
    return render_template('admin/dashboard.html')

# Route améliorée pour récupérer l'URL d'une image
@app.route('/get_cloudinary_url', methods=['GET'])
def get_cloudinary_url_route():
    """
    Route améliorée pour récupérer l'URL d'une image
    Avec logs de débogage détaillés pour diagnostiquer les problèmes d'affichage
    """
    image_path = request.args.get('image_path')
    logger.debug(f"[DEBUG] Route /get_cloudinary_url appelée avec image_path={image_path}")
    
    if not image_path:
        logger.error("[ERROR] Aucun chemin d'image fourni à /get_cloudinary_url")
        return jsonify({'error': 'Aucun chemin d\'image fourni'}), 400
    
    try:
        # Utiliser notre service d'URL d'images
        url = get_cloudinary_url(image_path)
        logger.debug(f"[DEBUG] URL générée: {url}")
        
        # Vérifier si l'URL générée pointe vers un fichier existant
        if url and url.startswith('/'):
            url_path = url[1:]
            url_exists = os.path.exists(url_path)
            logger.debug(f"[DEBUG] Le fichier à l'URL générée existe: {url_exists}")
        
        # Retourner l'URL finale
        logger.info(f"[INFO] URL finale retournée: {url}")
        return jsonify({'url': url})
        
    except Exception as e:
        logger.error(f"[ERROR] Erreur lors de la génération de l'URL pour {image_path}: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Route de diagnostic pour vérifier les chemins d'images
@app.route('/debug-image-paths', methods=['GET'])
def debug_image_paths():
    """
    Route de diagnostic pour vérifier les chemins d'images
    """
    image_path = request.args.get('image_path')
    if not image_path:
        return jsonify({'error': 'Aucun chemin d\'image fourni'}), 400
    
    result = {
        'original_path': image_path,
        'paths_checked': []
    }
    
    # Extraire le nom de fichier
    filename = os.path.basename(image_path)
    result['filename'] = filename
    
    # Vérifier les chemins possibles
    possible_paths = [
        os.path.join("static", "exercises", "general", filename),
        os.path.join("static", "exercises", "flashcards", filename),
        os.path.join("static", "uploads", "flashcards", filename),
        os.path.join("static", "uploads", "general", filename),
        os.path.join("static", "uploads", filename),
        os.path.join("static", "exercises", filename),
        os.path.join("uploads", filename),
        os.path.join("exercises", filename),
        image_path
    ]
    
    for path in possible_paths:
        exists = os.path.exists(path)
        size = os.path.getsize(path) if exists else None
        result['paths_checked'].append({
            'path': path,
            'exists': exists,
            'size': size
        })
    
    # Utiliser notre service d'URL d'images
    try:
        url = get_cloudinary_url(image_path)
        result['cloudinary_url'] = url
        
        # Vérifier si l'URL générée pointe vers un fichier existant
        if url and url.startswith('/'):
            url_path = url[1:]
            url_exists = os.path.exists(url_path)
            result['url_exists'] = url_exists
    except Exception as e:
        result['cloudinary_error'] = str(e)
    
    return jsonify(result)

# Route pour tester la correction des images des flashcards
@app.route('/test-flashcard-fix')
def test_flashcard_fix():
    """
    Route pour tester la correction des images des flashcards
    """
    # Connexion à la base de données
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Récupération des exercices de type flashcard
    cursor.execute("SELECT id, title, content FROM exercise WHERE exercise_type = 'flashcards' LIMIT 5")
    exercises = cursor.fetchall()
    
    results = []
    for exercise in exercises:
        exercise_id = exercise['id']
        title = exercise['title']
        content = json.loads(exercise['content']) if exercise['content'] else {}
        
        # Récupération des chemins d'images
        main_image = content.get('main_image', '')
        cards = content.get('cards', [])
        card_images = [card.get('image', '') for card in cards if 'image' in card]
        
        # Test des URLs d'images
        main_image_url = get_cloudinary_url(main_image) if main_image else None
        card_image_urls = [get_cloudinary_url(img) for img in card_images]
        
        results.append({
            'exercise_id': exercise_id,
            'title': title,
            'main_image': main_image,
            'main_image_url': main_image_url,
            'card_images': card_images,
            'card_image_urls': card_image_urls
        })
    
    conn.close()
    return jsonify(results)

if __name__ == '__main__':
    # Création du répertoire d'upload s'il n'existe pas
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Lancement de l'application
    app.run(debug=True, port=5001)
