"""
Script de correction automatique pour les chemins d'images dans les exercices de paires
Ce script corrige automatiquement les chemins d'images dans les exercices de paires
et crée une sauvegarde de la base de données avant modification
"""

import os
import json
import sys
import shutil
import datetime
import pathlib
from flask import Flask, current_app
from models import db, Exercise
from improved_normalize_pairs_exercise_paths import normalize_pairs_exercise_content

# Fonction pour trouver le chemin de la base de données
def find_database_path():
    """Trouve le chemin de la base de données SQLite
    
    Returns:
        str: URI SQLAlchemy pour la base de données
    """
    # Vérifier d'abord dans le répertoire instance
    instance_db_path = os.path.abspath('instance/app.db')
    root_db_path = os.path.abspath('app.db')
    
    if os.path.exists(instance_db_path):
        print(f"[INFO] Base de données trouvée: {instance_db_path}")
        return f'sqlite:///{instance_db_path}'
    elif os.path.exists(root_db_path):
        print(f"[INFO] Base de données trouvée: {root_db_path}")
        return f'sqlite:///{root_db_path}'
    else:
        # Recherche récursive dans le répertoire courant
        for db_file in pathlib.Path('.').glob('**/app.db'):
            db_path = os.path.abspath(db_file)
            print(f"[INFO] Base de données trouvée: {db_path}")
            return f'sqlite:///{db_path}'
    
    print("[ERREUR] Aucune base de données trouvée")
    return None

# Configuration de l'application Flask
app = Flask(__name__)
db_uri = find_database_path()
if not db_uri:
    print("[ERREUR] Impossible de trouver la base de données. Vérifiez que le fichier app.db existe.")
    sys.exit(1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def backup_database():
    """
    Crée une sauvegarde de la base de données avant modification
    
    Returns:
        str: Chemin de la sauvegarde
    """
    # Obtenir le chemin de la base de données
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    
    # Vérifier que le chemin existe
    if not os.path.exists(db_path):
        print(f"[ERREUR] Le fichier de base de données n'existe pas: {db_path}")
        return None
    
    # Créer un nom de fichier pour la sauvegarde avec timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}_backup_{timestamp}"
    
    # Copier le fichier de base de données
    try:
        shutil.copy2(db_path, backup_path)
        print(f"[INFO] Sauvegarde de la base de données créée: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"[ERREUR] Impossible de créer une sauvegarde de la base de données: {str(e)}")
        return None

def ensure_static_directories():
    """
    S'assure que les répertoires static/uploads et static/exercises existent
    """
    directories = ['static/uploads', 'static/exercises', 'static/uploads/pairs', 'static/exercises/pairs']
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"[INFO] Répertoire {directory} vérifié/créé")

def normalize_image_path(path):
    """
    Normalise un chemin d'image pour assurer la cohérence
    
    Args:
        path (str): Chemin d'image à normaliser
        
    Returns:
        str: Chemin normalisé
    """
    if not path or not isinstance(path, str):
        return path
        
    # Cas 1: URL externe (http://, https://, etc.)
    if path.startswith(('http://', 'https://', 'data:')):
        return path
        
    # Cas 2: Chemin avec /static/exercises/
    if '/static/exercises/' in path:
        return path.replace('/static/exercises/', '/static/uploads/')
        
    # Cas 3: Chemin absolu avec /static/
    if path.startswith('/static/'):
        # Déjà normalisé, conserver la structure de répertoires existante
        return path
        
    # Cas 4: Chemin relatif commençant par static/
    if path.startswith('static/'):
        return '/' + path
        
    # Cas 5: Chemin avec sous-répertoire spécifique (comme general/)
    if '/' in path and not path.startswith('/'):
        # Vérifier si c'est un chemin d'image avec sous-répertoire
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        is_image = any(path.lower().endswith(ext) for ext in image_extensions)
        
        if is_image:
            # Conserver la structure de sous-répertoire
            return f'/static/{path}'
    
    # Cas 6: Chemin relatif sans préfixe ni sous-répertoire
    # Vérifier si c'est un chemin d'image (extensions communes)
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    is_image = any(path.lower().endswith(ext) for ext in image_extensions)
    
    if is_image:
        # Ajouter le préfixe /static/uploads/ par défaut
        return f'/static/uploads/{path}'
    
    # Cas par défaut: retourner le chemin tel quel
    return path

def fix_pair_image_path(pair_item):
    """
    Corrige le chemin d'image d'un élément de paire
    
    Args:
        pair_item (dict): L'élément de paire (left ou right)
        
    Returns:
        bool: True si des modifications ont été apportées, False sinon
    """
    if not pair_item or not isinstance(pair_item, dict):
        return False
        
    if pair_item.get('type') != 'image' or not pair_item.get('content'):
        return False
        
    old_path = pair_item['content']
    new_path = normalize_image_path(old_path)
    
    if new_path != old_path:
        pair_item['content'] = new_path
        return True
        
    return False

def fix_pairs_exercise_content(content):
    """
    Corrige les chemins d'images dans un exercice de paires
    
    Args:
        content (dict): Le contenu JSON de l'exercice
        
    Returns:
        tuple: (content modifié, booléen indiquant si des modifications ont été apportées)
    """
    if not isinstance(content, dict):
        return content, False
        
    modified = False
    
    # Corriger les chemins dans les paires
    if 'pairs' in content and isinstance(content['pairs'], list):
        for pair in content['pairs']:
            # Corriger l'élément gauche s'il s'agit d'une image
            if 'left' in pair and isinstance(pair['left'], dict):
                if fix_pair_image_path(pair['left']):
                    modified = True
            
            # Corriger l'élément droit s'il s'agit d'une image
            if 'right' in pair and isinstance(pair['right'], dict):
                if fix_pair_image_path(pair['right']):
                    modified = True
    
    # Corriger les chemins dans les éléments gauches et droits (format utilisé dans le template)
    for item_list in ['left_items', 'right_items', 'shuffled_right_items']:
        if item_list in content and isinstance(content[item_list], list):
            for i, item in enumerate(content[item_list]):
                # Si l'élément est un dictionnaire avec type='image'
                if isinstance(item, dict) and item.get('type') == 'image':
                    if fix_pair_image_path(item):
                        modified = True
                # Si l'élément est une chaîne et semble être un chemin d'image
                elif isinstance(item, str) and (
                    item.startswith('/static/') or 
                    item.startswith('static/') or
                    any(item.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif'])
                ):
                    # Convertir en format objet
                    normalized_path = normalize_image_path(item)
                    if normalized_path != item:
                        content[item_list][i] = {
                            'type': 'image',
                            'content': normalized_path
                        }
                        modified = True
    
    return content, modified

def fix_pairs_exercises():
    """Corrige les chemins d'images dans tous les exercices de paires"""
    with app.app_context():
        # S'assurer que les répertoires existent
        ensure_static_directories()
        
        # Créer une sauvegarde de la base de données
        backup_path = backup_database()
        if not backup_path:
            print("[ERREUR] Impossible de continuer sans sauvegarde de la base de données")
            return
        
        # Récupérer tous les exercices de type 'pairs'
        pairs_exercises = Exercise.query.filter_by(exercise_type='pairs').all()
        
        print(f"Nombre d'exercices de paires trouvés: {len(pairs_exercises)}")
        
        fixed_count = 0
        
        for exercise in pairs_exercises:
            print(f"\n--- Exercice ID: {exercise.id}, Titre: {exercise.title} ---")
            
            if not exercise.content:
                print("  Pas de contenu JSON")
                continue
                
            try:
                content = json.loads(exercise.content)
                
                # Vérifier si le contenu a des paires
                if 'pairs' not in content or not isinstance(content['pairs'], list):
                    print("  Pas de paires dans le contenu")
                    continue
                    
                print(f"  Nombre de paires: {len(content['pairs'])}")
                
                # Corriger les chemins d'images
                fixed_content, modified = fix_pairs_exercise_content(content)
                
                if modified:
                    # Mettre à jour le contenu dans la base de données
                    exercise.content = json.dumps(fixed_content)
                    db.session.commit()
                    fixed_count += 1
                    print(f"  [OK] Chemins d'images corrigés pour l'exercice {exercise.id}")
                else:
                    print(f"  [INFO] Aucune correction nécessaire pour l'exercice {exercise.id}")
                    
            except Exception as e:
                print(f"  [ERREUR] Erreur lors de la correction de l'exercice {exercise.id}: {str(e)}")
        
        print(f"\nRésumé: {fixed_count}/{len(pairs_exercises)} exercices corrigés")
        print(f"Sauvegarde de la base de données: {backup_path}")

def create_flask_route():
    """
    Génère le code pour une route Flask qui peut être ajoutée à app.py
    pour corriger les chemins d'images via une interface web
    """
    route_code = """
@app.route('/fix-pairs-images', methods=['GET'])
@login_required
@admin_required
def fix_pairs_images():
    \"\"\"
    Route pour corriger les chemins d'images dans les exercices de paires
    Accessible uniquement aux administrateurs
    \"\"\"
    # S'assurer que les répertoires existent
    ensure_static_directories()
    
    # Récupérer tous les exercices de type 'pairs'
    pairs_exercises = Exercise.query.filter_by(exercise_type='pairs').all()
    
    fixed_count = 0
    total_count = len(pairs_exercises)
    results = []
    
    for exercise in pairs_exercises:
        result = {
            'id': exercise.id,
            'title': exercise.title,
            'status': 'skipped',
            'message': ''
        }
        
        if not exercise.content:
            result['message'] = "Pas de contenu JSON"
            results.append(result)
            continue
            
        try:
            content = json.loads(exercise.content)
            
            # Vérifier si le contenu a des paires
            if 'pairs' not in content or not isinstance(content['pairs'], list):
                result['message'] = "Pas de paires dans le contenu"
                results.append(result)
                continue
                
            # Corriger les chemins d'images
            fixed_content, modified = fix_pairs_exercise_content(content)
            
            if modified:
                # Mettre à jour le contenu dans la base de données
                exercise.content = json.dumps(fixed_content)
                db.session.commit()
                fixed_count += 1
                result['status'] = 'fixed'
                result['message'] = f"Chemins d'images corrigés ({len(content['pairs'])} paires)"
            else:
                result['status'] = 'ok'
                result['message'] = "Aucune correction nécessaire"
                
        except Exception as e:
            result['status'] = 'error'
            result['message'] = f"Erreur: {str(e)}"
            
        results.append(result)
    
    return render_template(
        'admin/fix_pairs_images.html',
        results=results,
        fixed_count=fixed_count,
        total_count=total_count
    )
"""
    
    print("\n=== CODE DE ROUTE FLASK ===")
    print("Ajoutez ce code à app.py pour créer une route web de correction:")
    print(route_code)

def main():
    """Fonction principale"""
    try:
        fix_pairs_exercises()
        create_flask_route()
        print("\nCorrection des chemins d'images terminée avec succès!")
    except Exception as e:
        print(f"\nErreur lors de la correction des chemins d'images: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
