"""
Script de test pour vérifier l'affichage des images dans les exercices de type "word_placement" et "flashcards".
Ce script permet de tester la correction apportée au problème d'affichage des images.
"""

import os
import sys
import json
import logging
from flask import Flask, render_template, request, jsonify
from models import db, Exercise, User
import cloud_storage
from fix_image_display_routes import register_image_display_routes

# Configuration du logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

# Configuration de l'application de test
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_word_placement_images.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app.config['TESTING'] = True

# Initialisation de la base de données
db.init_app(app)

# Enregistrement de la route pour get_cloudinary_url
register_image_display_routes(app)

@app.route('/')
def index():
    """Page d'accueil du test"""
    word_placement_exercises = Exercise.query.filter_by(exercise_type='word_placement').all()
    flashcard_exercises = Exercise.query.filter_by(exercise_type='flashcards').all()
    return render_template('test_image_exercises.html', 
                          word_placement_exercises=word_placement_exercises,
                          flashcard_exercises=flashcard_exercises)

@app.route('/test/create-sample-exercises')
def create_sample_exercises():
    """Crée des exercices de test pour word_placement et flashcards avec différentes configurations d'images"""
    try:
        # Créer un utilisateur de test si nécessaire
        user = User.query.filter_by(email='test@example.com').first()
        if not user:
            user = User(
                email='test@example.com',
                username='testuser',
                role='teacher'
            )
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
        
        # Créer des exercices de type word_placement
        word_placement1 = Exercise(
            title="Word Placement Test 1",
            description="Exercice de placement de mots avec image",
            subject="Test",
            exercise_type="word_placement",
            teacher_id=user.id,
            image_path="/static/uploads/word_placement_test1.png",
            content=json.dumps({
                "text": "Ceci est un [test] pour vérifier l'affichage des [images].",
                "words": ["test", "images"],
                "image": "/static/uploads/word_placement_test1.png"
            })
        )
        
        word_placement2 = Exercise(
            title="Word Placement Test 2",
            description="Exercice de placement de mots sans image dans content",
            subject="Test",
            exercise_type="word_placement",
            teacher_id=user.id,
            image_path="/static/uploads/word_placement_test2.png",
            content=json.dumps({
                "text": "Ceci est un autre [test] pour vérifier l'affichage des [images].",
                "words": ["test", "images"]
            })
        )
        
        # Créer des exercices de type flashcards
        flashcards1 = Exercise(
            title="Flashcards Test 1",
            description="Exercice de cartes mémoire avec images",
            subject="Test",
            exercise_type="flashcards",
            teacher_id=user.id,
            image_path="/static/uploads/flashcards_test1.png",
            content=json.dumps({
                "cards": [
                    {"front": "Carte 1", "back": "Réponse 1", "image": "/static/uploads/flashcard1_1.png"},
                    {"front": "Carte 2", "back": "Réponse 2", "image": "/static/uploads/flashcard1_2.png"}
                ]
            })
        )
        
        flashcards2 = Exercise(
            title="Flashcards Test 2",
            description="Exercice de cartes mémoire avec image principale uniquement",
            subject="Test",
            exercise_type="flashcards",
            teacher_id=user.id,
            image_path="/static/uploads/flashcards_test2.png",
            content=json.dumps({
                "cards": [
                    {"front": "Carte 1", "back": "Réponse 1"},
                    {"front": "Carte 2", "back": "Réponse 2"}
                ]
            })
        )
        
        # Ajouter les exercices à la base de données
        db.session.add_all([word_placement1, word_placement2, flashcards1, flashcards2])
        db.session.commit()
        
        # Créer des images de test si elles n'existent pas
        uploads_dir = os.path.join(app.static_folder, 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Créer des images pour word_placement
        for i in range(1, 3):
            filename = f"word_placement_test{i}.png"
            filepath = os.path.join(uploads_dir, filename)
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    f.write(f"""<svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
                        <rect width="100%" height="100%" fill="#f0f0f0"/>
                        <text x="200" y="100" font-family="Arial" font-size="24" text-anchor="middle" fill="#333">
                            Word Placement Test Image {i}
                        </text>
                    </svg>""")
        
        # Créer des images pour flashcards
        for i in range(1, 3):
            filename = f"flashcards_test{i}.png"
            filepath = os.path.join(uploads_dir, filename)
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    f.write(f"""<svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
                        <rect width="100%" height="100%" fill="#e0f0e0"/>
                        <text x="200" y="100" font-family="Arial" font-size="24" text-anchor="middle" fill="#333">
                            Flashcards Test Image {i}
                        </text>
                    </svg>""")
            
            # Créer des images pour les cartes individuelles
            for j in range(1, 3):
                filename = f"flashcard{i}_{j}.png"
                filepath = os.path.join(uploads_dir, filename)
                if not os.path.exists(filepath):
                    with open(filepath, 'w') as f:
                        f.write(f"""<svg width="300" height="150" xmlns="http://www.w3.org/2000/svg">
                            <rect width="100%" height="100%" fill="#e0e0f0"/>
                            <text x="150" y="75" font-family="Arial" font-size="18" text-anchor="middle" fill="#333">
                                Flashcard {i}.{j}
                            </text>
                        </svg>""")
        
        return "Exercices de test créés avec succès!"
    except Exception as e:
        logger.error(f"Erreur lors de la création des exercices de test: {str(e)}")
        return f"Erreur lors de la création des exercices de test: {str(e)}"

@app.route('/test/view-word-placement/<int:exercise_id>')
def view_word_placement(exercise_id):
    """Affiche un exercice de type word_placement pour vérifier l'affichage des images"""
    exercise = Exercise.query.get_or_404(exercise_id)
    if exercise.exercise_type != 'word_placement':
        return "Cet exercice n'est pas de type word_placement"
    
    content = json.loads(exercise.content) if exercise.content else {}
    return render_template('exercise_types/word_placement.html', exercise=exercise, content=content)

@app.route('/test/view-flashcards/<int:exercise_id>')
def view_flashcards(exercise_id):
    """Affiche un exercice de type flashcards pour vérifier l'affichage des images"""
    exercise = Exercise.query.get_or_404(exercise_id)
    if exercise.exercise_type != 'flashcards':
        return "Cet exercice n'est pas de type flashcards"
    
    content = json.loads(exercise.content) if exercise.content else {}
    return render_template('exercise_types/flashcards.html', exercise=exercise, content=content)

@app.route('/test/check-image-url')
def check_image_url():
    """Vérifie la génération d'URL d'image avec cloud_storage.get_cloudinary_url"""
    image_path = request.args.get('path', '')
    if not image_path:
        return jsonify({"error": "Aucun chemin d'image fourni"}), 400
    
    try:
        url = cloud_storage.get_cloudinary_url(image_path)
        return jsonify({
            "original_path": image_path,
            "cloudinary_url": url,
            "success": True
        })
    except Exception as e:
        logger.error(f"Erreur lors de la génération de l'URL Cloudinary: {str(e)}")
        return jsonify({
            "original_path": image_path,
            "error": str(e),
            "success": False
        }), 500

@app.route('/test/reset-db')
def reset_db():
    """Réinitialise la base de données de test"""
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    if os.path.exists(db_path):
        os.remove(db_path)
    
    with app.app_context():
        db.create_all()
    
    return "Base de données réinitialisée!"

@app.route('/test/get-cloudinary-url')
def test_get_cloudinary_url():
    """Page de test pour la route /get_cloudinary_url"""
    return render_template('test_get_cloudinary_url.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5002)
