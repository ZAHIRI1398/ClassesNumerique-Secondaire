from flask import Flask
from models import db, Exercise
import json
import os
from PIL import Image, ImageDraw, ImageFont
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def get_image_url(path):
    """Fonction simplifiée pour obtenir l'URL d'une image"""
    if not path:
        return None
    
    # Normaliser le chemin pour qu'il commence par /static/
    if not path.startswith('/static/'):
        if path.startswith('static/'):
            path = '/' + path
        else:
            path = '/static/' + path.lstrip('/')
    
    return path

def fix_pairs_exercise(exercise):
    """Corrige l'affichage des images pour un exercice d'association de paires"""
    if exercise.exercise_type != 'pairs':
        return False, "L'exercice n'est pas de type 'pairs'"
    
    try:
        content = json.loads(exercise.content)
    except json.JSONDecodeError:
        return False, "Contenu JSON invalide"
    
    # Vérifier si l'image principale existe
    image_path = exercise.image_path
    if image_path:
        file_path = os.path.join(app.root_path, image_path.lstrip('/'))
        if not os.path.exists(file_path):
            print(f"Attention: L'image principale n'existe pas: {file_path}")
    
    # Convertir les éléments simples en objets avec type et contenu
    if 'left_items' in content and isinstance(content['left_items'], list):
        new_left_items = []
        for item in content['left_items']:
            if isinstance(item, str):
                new_left_items.append({"type": "text", "content": item})
            elif isinstance(item, dict) and 'content' in item:
                # Déjà au bon format
                new_left_items.append(item)
            else:
                new_left_items.append({"type": "text", "content": str(item)})
        content['left_items'] = new_left_items
    
    if 'right_items' in content and isinstance(content['right_items'], list):
        new_right_items = []
        for item in content['right_items']:
            if isinstance(item, str):
                new_right_items.append({"type": "text", "content": item})
            elif isinstance(item, dict) and 'content' in item:
                # Déjà au bon format
                new_right_items.append(item)
            else:
                new_right_items.append({"type": "text", "content": str(item)})
        content['right_items'] = new_right_items
    
    # Mettre à jour le contenu de l'exercice
    exercise.content = json.dumps(content)
    return True, "Exercice mis à jour avec succès"

def create_test_pairs_with_images():
    """Crée un exercice d'association de paires avec des images"""
    # Vérifier si l'enseignant existe
    teacher = User.query.filter_by(email='mr.zahiri@gmail.com').first()
    if not teacher:
        return False, "Enseignant non trouvé"
    
    # Créer les dossiers pour les images
    upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'pairs')
    os.makedirs(upload_dir, exist_ok=True)
    
    # Créer des images pour le test
    image_paths = []
    for i in range(1, 5):
        img_path = os.path.join(upload_dir, f'animal_{i}.png')
        create_test_image(img_path, f"Animal {i}", bg_color=(200, 230, 255))
        image_paths.append(f'/static/uploads/pairs/animal_{i}.png')
    
    # Créer l'exercice
    pairs_with_images = Exercise(
        title="Test d'association avec images",
        description="Associez chaque animal à son nom.",
        exercise_type="pairs",
        image_path="/static/uploads/pairs/animals_pairs.png",
        content=json.dumps({
            "image": "/static/uploads/pairs/animals_pairs.png",
            "left_items": [
                {"type": "image", "content": image_paths[0]},
                {"type": "image", "content": image_paths[1]},
                {"type": "image", "content": image_paths[2]},
                {"type": "image", "content": image_paths[3]}
            ],
            "right_items": [
                {"type": "text", "content": "Chat"},
                {"type": "text", "content": "Chien"},
                {"type": "text", "content": "Oiseau"},
                {"type": "text", "content": "Poisson"}
            ],
            "correct_pairs": [[0, 0], [1, 1], [2, 2], [3, 3]]
        }),
        teacher_id=teacher.id
    )
    db.session.add(pairs_with_images)
    
    # Créer l'image principale
    create_test_image(
        os.path.join(app.root_path, 'static', 'uploads', 'pairs', 'animals_pairs.png'),
        "ASSOCIATION D'ANIMAUX",
        bg_color=(230, 255, 200)
    )
    
    return True, "Exercice d'association avec images créé avec succès"

def create_test_image(path, text, width=600, height=300, bg_color=(240, 240, 240), text_color=(0, 0, 0)):
    """Crée une image avec du texte pour les exercices"""
    # Vérifier si le répertoire existe, sinon le créer
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    # Créer une image
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Essayer de charger une police, sinon utiliser la police par défaut
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except IOError:
        font = ImageFont.load_default()
    
    # Ajouter du texte au centre de l'image
    text_width, text_height = draw.textsize(text, font=font) if hasattr(draw, 'textsize') else (200, 30)
    position = ((width - text_width) // 2, (height - text_height) // 2)
    draw.text(position, text, fill=text_color, font=font)
    
    # Sauvegarder l'image
    img.save(path)
    print(f"Image créée: {path}")

with app.app_context():
    # Option 1: Corriger tous les exercices d'association de paires existants
    if len(sys.argv) > 1 and sys.argv[1] == '--fix-all':
        exercises = Exercise.query.filter_by(exercise_type='pairs').all()
        print(f"Correction de {len(exercises)} exercices d'association de paires...")
        
        for exercise in exercises:
            success, message = fix_pairs_exercise(exercise)
            print(f"Exercice #{exercise.id} ({exercise.title}): {message}")
        
        db.session.commit()
        print("Modifications enregistrées dans la base de données.")
    
    # Option 2: Créer un nouvel exercice d'association avec des images
    elif len(sys.argv) > 1 and sys.argv[1] == '--create-test':
        from models import User
        success, message = create_test_pairs_with_images()
        if success:
            db.session.commit()
            print(message)
        else:
            print(f"Erreur: {message}")
    
    # Option 3: Afficher l'aide
    else:
        print("Usage:")
        print("  python fix_pairs_image_display.py --fix-all    # Corrige tous les exercices d'association de paires")
        print("  python fix_pairs_image_display.py --create-test # Crée un exercice d'association avec des images")
