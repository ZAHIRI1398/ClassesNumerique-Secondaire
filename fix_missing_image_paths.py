from flask import Flask
from models import db, Exercise
import json
import os
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def create_image(path, text, width=600, height=300, bg_color=(240, 240, 240), text_color=(0, 0, 0)):
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
    # Récupérer l'exercice problématique
    exercise = Exercise.query.get(37)  # ID de l'exercice problématique
    
    if not exercise:
        print("Exercice non trouvé.")
        exit(1)
    
    print(f"Correction de l'exercice #{exercise.id}: {exercise.title}")
    
    # Définir le chemin d'image
    image_path = f"/static/uploads/pairs/pairs_exercise_{exercise.id}.png"
    
    # Mettre à jour l'exercice
    exercise.image_path = image_path
    
    # Mettre à jour le contenu JSON
    content = json.loads(exercise.content) if exercise.content else {}
    content['image'] = image_path
    exercise.content = json.dumps(content)
    
    # Créer l'image
    full_path = os.path.join(app.root_path, image_path.lstrip('/'))
    create_image(full_path, f"EXERCICE D'APPARIEMENT #{exercise.id}", bg_color=(255, 240, 200))
    
    # Sauvegarder les modifications
    db.session.commit()
    
    print(f"Exercice corrigé avec succès!")
    print(f"Nouveau chemin d'image: {exercise.image_path}")
