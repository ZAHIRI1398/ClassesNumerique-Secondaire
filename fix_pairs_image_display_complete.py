from flask import Flask, render_template_string, current_app
from models import db, Exercise, User
import json
import os
from PIL import Image, ImageDraw, ImageFont
import sys
import shutil
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def normalize_image_path(path):
    """Normalise le chemin d'image pour qu'il commence par /static/uploads/"""
    if not path:
        return None
    
    # Convertir les chemins /static/exercises/ en /static/uploads/
    if '/static/exercises/' in path:
        path = path.replace('/static/exercises/', '/static/uploads/')
    
    # Normaliser le chemin pour qu'il commence par /static/
    if not path.startswith('/static/'):
        if path.startswith('static/'):
            path = '/' + path
        elif not path.startswith('/'):
            path = '/static/uploads/' + path
    
    return path

def fix_pairs_exercise(exercise, create_missing_images=True):
    """Corrige l'affichage des images pour un exercice d'association de paires"""
    if exercise.exercise_type != 'pairs':
        return False, "L'exercice n'est pas de type 'pairs'"
    
    try:
        content = json.loads(exercise.content)
    except json.JSONDecodeError:
        return False, "Contenu JSON invalide"
    
    changes_made = []
    
    # Normaliser l'image principale
    if exercise.image_path:
        old_path = exercise.image_path
        new_path = normalize_image_path(exercise.image_path)
        if old_path != new_path:
            exercise.image_path = new_path
            changes_made.append(f"Image principale: {old_path} -> {new_path}")
    
    # Normaliser l'image dans le contenu JSON
    if 'image' in content:
        old_path = content['image']
        new_path = normalize_image_path(content['image'])
        if old_path != new_path:
            content['image'] = new_path
            changes_made.append(f"Image JSON: {old_path} -> {new_path}")
    
    # Vérifier si l'image principale existe
    if exercise.image_path:
        file_path = os.path.join(app.root_path, exercise.image_path.lstrip('/'))
        if not os.path.exists(file_path):
            if create_missing_images:
                # Créer le répertoire si nécessaire
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                # Créer une image de remplacement
                create_test_image(file_path, f"IMAGE EXERCICE PAIRES #{exercise.id}", bg_color=(230, 240, 255))
                changes_made.append(f"Image principale créée: {file_path}")
            else:
                changes_made.append(f"Image principale manquante: {file_path}")
    
    # Traiter les deux formats possibles d'exercices de paires
    if 'left_items' in content and 'right_items' in content:
        # Format 1: left_items et right_items
        # Convertir les éléments simples en objets avec type et contenu
        if isinstance(content['left_items'], list):
            new_left_items = []
            for item in content['left_items']:
                if isinstance(item, str):
                    # Si c'est un chemin d'image, le convertir en objet image
                    if item.endswith('.png') or item.endswith('.jpg') or item.endswith('.jpeg') or item.endswith('.gif'):
                        normalized_path = normalize_image_path(item)
                        new_left_items.append({"type": "image", "content": normalized_path})
                        changes_made.append(f"Élément gauche converti en objet image: {item} -> {normalized_path}")
                        
                        # Créer l'image si elle n'existe pas
                        if create_missing_images:
                            file_path = os.path.join(app.root_path, normalized_path.lstrip('/'))
                            if not os.path.exists(file_path):
                                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                                create_test_image(file_path, f"IMAGE GAUCHE #{len(new_left_items)}", bg_color=(200, 230, 255))
                                changes_made.append(f"Image gauche créée: {file_path}")
                    else:
                        new_left_items.append({"type": "text", "content": item})
                        changes_made.append(f"Élément gauche converti en objet texte: {item}")
                elif isinstance(item, dict) and 'content' in item:
                    # Si c'est déjà un objet avec content, normaliser le chemin si c'est une image
                    if item.get('type') == 'image' and item['content']:
                        old_path = item['content']
                        new_path = normalize_image_path(item['content'])
                        if old_path != new_path:
                            item['content'] = new_path
                            changes_made.append(f"Chemin image gauche normalisé: {old_path} -> {new_path}")
                        
                        # Créer l'image si elle n'existe pas
                        if create_missing_images:
                            file_path = os.path.join(app.root_path, new_path.lstrip('/'))
                            if not os.path.exists(file_path):
                                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                                create_test_image(file_path, f"IMAGE GAUCHE #{len(new_left_items)}", bg_color=(200, 230, 255))
                                changes_made.append(f"Image gauche créée: {file_path}")
                    new_left_items.append(item)
                else:
                    new_left_items.append({"type": "text", "content": str(item)})
                    changes_made.append(f"Élément gauche converti en objet texte: {item}")
            content['left_items'] = new_left_items
        
        # Faire de même pour les éléments de droite
        if isinstance(content['right_items'], list):
            new_right_items = []
            for item in content['right_items']:
                if isinstance(item, str):
                    # Si c'est un chemin d'image, le convertir en objet image
                    if item.endswith('.png') or item.endswith('.jpg') or item.endswith('.jpeg') or item.endswith('.gif'):
                        normalized_path = normalize_image_path(item)
                        new_right_items.append({"type": "image", "content": normalized_path})
                        changes_made.append(f"Élément droite converti en objet image: {item} -> {normalized_path}")
                        
                        # Créer l'image si elle n'existe pas
                        if create_missing_images:
                            file_path = os.path.join(app.root_path, normalized_path.lstrip('/'))
                            if not os.path.exists(file_path):
                                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                                create_test_image(file_path, f"IMAGE DROITE #{len(new_right_items)}", bg_color=(255, 230, 200))
                                changes_made.append(f"Image droite créée: {file_path}")
                    else:
                        new_right_items.append({"type": "text", "content": item})
                        changes_made.append(f"Élément droite converti en objet texte: {item}")
                elif isinstance(item, dict) and 'content' in item:
                    # Si c'est déjà un objet avec content, normaliser le chemin si c'est une image
                    if item.get('type') == 'image' and item['content']:
                        old_path = item['content']
                        new_path = normalize_image_path(item['content'])
                        if old_path != new_path:
                            item['content'] = new_path
                            changes_made.append(f"Chemin image droite normalisé: {old_path} -> {new_path}")
                        
                        # Créer l'image si elle n'existe pas
                        if create_missing_images:
                            file_path = os.path.join(app.root_path, new_path.lstrip('/'))
                            if not os.path.exists(file_path):
                                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                                create_test_image(file_path, f"IMAGE DROITE #{len(new_right_items)}", bg_color=(255, 230, 200))
                                changes_made.append(f"Image droite créée: {file_path}")
                    new_right_items.append(item)
                else:
                    new_right_items.append({"type": "text", "content": str(item)})
                    changes_made.append(f"Élément droite converti en objet texte: {item}")
            content['right_items'] = new_right_items
            
    elif 'pairs' in content:
        # Format 2: liste de paires
        for pair in content['pairs']:
            # Traiter l'élément gauche
            if 'left' in pair and isinstance(pair['left'], dict):
                if pair['left'].get('type') == 'image' and pair['left'].get('content'):
                    old_path = pair['left']['content']
                    new_path = normalize_image_path(old_path)
                    if old_path != new_path:
                        pair['left']['content'] = new_path
                        changes_made.append(f"Chemin image gauche normalisé: {old_path} -> {new_path}")
                    
                    # Créer l'image si elle n'existe pas
                    if create_missing_images:
                        file_path = os.path.join(app.root_path, new_path.lstrip('/'))
                        if not os.path.exists(file_path):
                            os.makedirs(os.path.dirname(file_path), exist_ok=True)
                            create_test_image(file_path, f"IMAGE PAIRE {pair.get('id', 'X')}", bg_color=(200, 230, 255))
                            changes_made.append(f"Image gauche créée: {file_path}")
            
            # Traiter l'élément droit
            if 'right' in pair and isinstance(pair['right'], dict):
                if pair['right'].get('type') == 'image' and pair['right'].get('content'):
                    old_path = pair['right']['content']
                    new_path = normalize_image_path(old_path)
                    if old_path != new_path:
                        pair['right']['content'] = new_path
                        changes_made.append(f"Chemin image droite normalisé: {old_path} -> {new_path}")
                    
                    # Créer l'image si elle n'existe pas
                    if create_missing_images:
                        file_path = os.path.join(app.root_path, new_path.lstrip('/'))
                        if not os.path.exists(file_path):
                            os.makedirs(os.path.dirname(file_path), exist_ok=True)
                            create_test_image(file_path, f"IMAGE PAIRE {pair.get('id', 'X')}", bg_color=(255, 230, 200))
                            changes_made.append(f"Image droite créée: {file_path}")
    
    # Mettre à jour le contenu de l'exercice
    exercise.content = json.dumps(content)
    
    return len(changes_made) > 0, changes_made

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
    text_width, text_height = 200, 30  # Valeurs par défaut
    try:
        if hasattr(draw, 'textsize'):
            text_width, text_height = draw.textsize(text, font=font)
        elif hasattr(draw, 'textbbox'):
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    except Exception:
        pass  # Utiliser les valeurs par défaut
    
    position = ((width - text_width) // 2, (height - text_height) // 2)
    draw.text(position, text, fill=text_color, font=font)
    
    # Sauvegarder l'image
    img.save(path)
    print(f"Image créée: {path}")

def create_cloud_storage_helper():
    """Crée un module cloud_storage.py avec une fonction get_cloudinary_url simplifiée"""
    cloud_storage_path = os.path.join(app.root_path, 'cloud_storage.py')
    
    if not os.path.exists(cloud_storage_path):
        with open(cloud_storage_path, 'w') as f:
            f.write("""
def get_cloudinary_url(path):
    \"\"\"Fonction simplifiée pour obtenir l'URL d'une image\"\"\"
    if not path:
        return None
    
    # Pour les chemins locaux, retourner le chemin tel quel
    if path.startswith('/static/'):
        return path
    
    # Pour les URLs Cloudinary, retourner l'URL telle quelle
    if path.startswith('http'):
        return path
    
    # Sinon, considérer comme un chemin local et ajouter /static/
    if not path.startswith('/'):
        path = '/static/' + path
    
    return path
""")
        print(f"Module cloud_storage.py créé: {cloud_storage_path}")
    else:
        print(f"Module cloud_storage.py existe déjà: {cloud_storage_path}")

def create_backup(exercise):
    """Crée une sauvegarde de l'exercice avant modification"""
    backup_dir = os.path.join(app.root_path, 'backups', 'pairs')
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'exercise_{exercise.id}_{timestamp}.json')
    
    with open(backup_file, 'w') as f:
        backup_data = {
            'id': exercise.id,
            'title': exercise.title,
            'description': exercise.description,
            'exercise_type': exercise.exercise_type,
            'image_path': exercise.image_path,
            'content': json.loads(exercise.content) if exercise.content else None
        }
        json.dump(backup_data, f, indent=2)
    
    print(f"Sauvegarde créée: {backup_file}")
    return backup_file

def main():
    with app.app_context():
        # Créer le module cloud_storage.py si nécessaire
        create_cloud_storage_helper()
        
        # Option 1: Corriger tous les exercices d'association de paires existants
        if len(sys.argv) > 1 and sys.argv[1] == '--fix-all':
            exercises = Exercise.query.filter_by(exercise_type='pairs').all()
            print(f"Correction de {len(exercises)} exercices d'association de paires...")
            
            for exercise in exercises:
                # Créer une sauvegarde avant modification
                backup_file = create_backup(exercise)
                
                # Corriger l'exercice
                success, changes = fix_pairs_exercise(exercise, create_missing_images=True)
                
                if success:
                    print(f"Exercice #{exercise.id} ({exercise.title}) corrigé avec {len(changes)} modifications:")
                    for change in changes:
                        print(f"  - {change}")
                else:
                    print(f"Exercice #{exercise.id} ({exercise.title}): Aucune modification nécessaire")
            
            db.session.commit()
            print("Modifications enregistrées dans la base de données.")
        
        # Option 2: Corriger un exercice spécifique
        elif len(sys.argv) > 2 and sys.argv[1] == '--fix':
            try:
                exercise_id = int(sys.argv[2])
                exercise = Exercise.query.get(exercise_id)
                
                if not exercise:
                    print(f"Erreur: Exercice #{exercise_id} non trouvé")
                    return
                
                if exercise.exercise_type != 'pairs':
                    print(f"Erreur: L'exercice #{exercise_id} n'est pas de type 'pairs' mais '{exercise.exercise_type}'")
                    return
                
                # Créer une sauvegarde avant modification
                backup_file = create_backup(exercise)
                
                # Corriger l'exercice
                success, changes = fix_pairs_exercise(exercise, create_missing_images=True)
                
                if success:
                    print(f"Exercice #{exercise.id} ({exercise.title}) corrigé avec {len(changes)} modifications:")
                    for change in changes:
                        print(f"  - {change}")
                    
                    db.session.commit()
                    print("Modifications enregistrées dans la base de données.")
                else:
                    print(f"Exercice #{exercise.id} ({exercise.title}): Aucune modification nécessaire")
            
            except ValueError:
                print(f"Erreur: ID d'exercice invalide '{sys.argv[2]}'")
        
        # Option 3: Créer un nouvel exercice d'association avec des images
        elif len(sys.argv) > 1 and sys.argv[1] == '--create-test':
            success, message = create_test_pairs_with_images()
            if success:
                db.session.commit()
                print(message)
            else:
                print(f"Erreur: {message}")
        
        # Option 4: Afficher l'aide
        else:
            print("Usage:")
            print("  python fix_pairs_image_display_complete.py --fix-all    # Corrige tous les exercices d'association de paires")
            print("  python fix_pairs_image_display_complete.py --fix ID     # Corrige l'exercice d'association de paires avec l'ID spécifié")
            print("  python fix_pairs_image_display_complete.py --create-test # Crée un exercice d'association avec des images")

if __name__ == "__main__":
    main()
