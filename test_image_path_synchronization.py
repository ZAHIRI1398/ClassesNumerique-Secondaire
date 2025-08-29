import os
import sys
import json
from flask import Flask, current_app
from models import db, Exercise
from utils.image_path_synchronizer import synchronize_all_exercises

# Créer une application Flask minimale pour le test
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def test_image_paths():
    """
    Teste la synchronisation des chemins d'images pour tous les exercices.
    Affiche les statistiques et les détails des modifications.
    """
    with app.app_context():
        print("=== ÉTAT INITIAL DES CHEMINS D'IMAGES ===")
        exercises = Exercise.query.all()
        for exercise in exercises:
            content = json.loads(exercise.content) if exercise.content else {}
            content_image = content.get('image', 'Non défini')
            print(f"Exercice {exercise.id} - {exercise.title}")
            print(f"  - exercise.image_path: {exercise.image_path}")
            print(f"  - content['image']: {content_image}")
            print("-" * 50)
        
        print("\n=== SYNCHRONISATION DES CHEMINS D'IMAGES ===")
        stats = synchronize_all_exercises(db, Exercise)
        
        print(f"\nTotal d'exercices traités: {stats['total']}")
        print(f"Exercices modifiés: {stats['modified']}")
        print(f"Erreurs rencontrées: {stats['errors']}")
        
        if stats['modified'] > 0:
            print("\n=== DÉTAILS DES MODIFICATIONS ===")
            for detail in stats['details']:
                print(f"Exercice {detail['id']} - {detail['title']}")
                print(f"  - Nouveau chemin: {detail['image_path']}")
        
        print("\n=== ÉTAT FINAL DES CHEMINS D'IMAGES ===")
        exercises = Exercise.query.all()
        for exercise in exercises:
            content = json.loads(exercise.content) if exercise.content else {}
            content_image = content.get('image', 'Non défini')
            print(f"Exercice {exercise.id} - {exercise.title}")
            print(f"  - exercise.image_path: {exercise.image_path}")
            print(f"  - content['image']: {content_image}")
            print("-" * 50)

def test_specific_cases():
    """
    Teste la synchronisation avec des cas spécifiques problématiques.
    """
    with app.app_context():
        print("=== TEST DE CAS SPÉCIFIQUES ===")
        
        # Cas 1: Chemin avec espaces et caractères spéciaux
        test_path = "uploads/Capture d'écran 2025-08-14 145027.png"
        normalized = test_path.replace(' ', '_').replace("'", '')
        print(f"Original: {test_path}")
        print(f"Normalisé: {normalized}")
        print(f"Attendu: /static/uploads/Capture_decran_2025-08-14_145027.png")
        
        # Cas 2: Chemin avec duplication de segments
        test_path = "/static/uploads/static/uploads/image.png"
        from utils.image_path_handler import clean_duplicated_path_segments
        cleaned = clean_duplicated_path_segments(test_path)
        print(f"\nOriginal: {test_path}")
        print(f"Nettoyé: {cleaned}")
        print(f"Attendu: /static/uploads/image.png")
        
        # Cas 3: Chemin sans préfixe /static/
        test_path = "uploads/image.png"
        if not test_path.startswith('/static/'):
            fixed = f'/static/{test_path}' if not test_path.startswith('static/') else f'/{test_path}'
        print(f"\nOriginal: {test_path}")
        print(f"Corrigé: {fixed}")
        print(f"Attendu: /static/uploads/image.png")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--specific":
        test_specific_cases()
    else:
        test_image_paths()
