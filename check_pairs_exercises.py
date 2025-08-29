from flask import Flask
from models import db, Exercise
import json
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    exercises = Exercise.query.filter_by(exercise_type='pairs').all()
    print(f'Nombre d\'exercices pairs: {len(exercises)}')
    
    for ex in exercises:
        print(f'ID: {ex.id}, Titre: {ex.title}')
        print(f'Image path: {ex.image_path}')
        
        try:
            content = json.loads(ex.content)
            print('Structure du contenu:')
            
            # Vérifier la structure des éléments
            if 'left_items' in content:
                print(f"left_items: {len(content['left_items'])} éléments")
                for i, item in enumerate(content['left_items']):
                    if isinstance(item, dict):
                        print(f"  - Item {i}: type={item.get('type', 'non spécifié')}, content={item.get('content', 'non spécifié')}")
                    else:
                        print(f"  - Item {i}: {item} (format simple)")
            
            if 'right_items' in content:
                print(f"right_items: {len(content['right_items'])} éléments")
                for i, item in enumerate(content['right_items']):
                    if isinstance(item, dict):
                        print(f"  - Item {i}: type={item.get('type', 'non spécifié')}, content={item.get('content', 'non spécifié')}")
                    else:
                        print(f"  - Item {i}: {item} (format simple)")
            
            # Vérifier si les images existent
            if 'image' in content:
                image_path = content['image']
                print(f"Image principale: {image_path}")
                if image_path:
                    file_path = os.path.join(app.root_path, image_path.lstrip('/'))
                    if os.path.exists(file_path):
                        print(f"  ✓ L'image existe: {file_path}")
                    else:
                        print(f"  ✗ L'image n'existe pas: {file_path}")
            
            print("\nContenu JSON complet:")
            print(json.dumps(content, indent=2))
            
        except json.JSONDecodeError as e:
            print(f"Erreur de décodage JSON: {e}")
        
        print("\n" + "-"*80 + "\n")
