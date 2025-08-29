import os
import json
from utils.image_path_manager import ImagePathManager

def normalize_pairs_exercise_content(content):
    """
    Normalise les chemins d'images dans un exercice de paires pour assurer la cohérence
    entre les chemins physiques (/static/exercises/) et les chemins référencés (/static/uploads/)
    
    Args:
        content (dict): Le contenu JSON de l'exercice
        
    Returns:
        dict: Le contenu normalisé
    """
    if not isinstance(content, dict):
        return content
    
    # Fonction utilitaire pour normaliser un chemin d'image
    def normalize_path(path):
        if not path or not isinstance(path, str):
            return path
            
        # Cas 1: Chemin physique vers chemin référencé
        if '/static/exercises/' in path:
            return path.replace('/static/exercises/', '/static/uploads/')
        # Cas 2: Chemin référencé vers chemin physique (pour la cohérence)
        elif '/static/uploads/' in path:
            # Vérifier si le fichier existe avec ce chemin
            import os
            from flask import current_app
            physical_path = path.replace('/static/uploads/', '/static/exercises/')
            try:
                # Si le fichier existe avec le chemin physique, utiliser le chemin référencé
                full_path = os.path.join(current_app.root_path, physical_path.lstrip('/'))  
                if os.path.exists(full_path):
                    print(f"[PAIRS_PATH_DEBUG] Fichier trouvé avec chemin physique: {full_path}")
                    return path  # Garder le chemin référencé car le fichier existe physiquement
                else:
                    print(f"[PAIRS_PATH_DEBUG] Fichier non trouvé avec chemin physique: {full_path}")
                    # Le fichier n'existe pas, garder le chemin tel quel
                    return path
            except Exception as e:
                print(f"[PAIRS_PATH_DEBUG] Erreur lors de la vérification du chemin: {str(e)}")
                return path
        
        return path
    
    # Normaliser les chemins dans les paires
    if 'pairs' in content and isinstance(content['pairs'], list):
        for pair in content['pairs']:
            # Normaliser l'élément gauche s'il s'agit d'une image
            if 'left' in pair and isinstance(pair['left'], dict) and pair['left'].get('type') == 'image':
                pair['left']['content'] = normalize_path(pair['left']['content'])
            
            # Normaliser l'élément droit s'il s'agit d'une image
            if 'right' in pair and isinstance(pair['right'], dict) and pair['right'].get('type') == 'image':
                pair['right']['content'] = normalize_path(pair['right']['content'])
    
    # Normaliser les chemins dans les éléments gauches et droits (ancien format)
    for item_list in ['left_items', 'right_items']:
        if item_list in content and isinstance(content[item_list], list):
            for i, item in enumerate(content[item_list]):
                # Si l'élément est un dictionnaire avec type='image'
                if isinstance(item, dict) and item.get('type') == 'image':
                    item['content'] = normalize_path(item['content'])
                # Si l'élément est une chaîne et semble être un chemin d'image
                elif isinstance(item, str) and (item.startswith('/static/') or item.startswith('static/')):
                    # Convertir en format objet
                    content[item_list][i] = {
                        'type': 'image',
                        'content': normalize_path(item)
                    }
    
    # Normaliser l'image principale si elle existe
    if 'image' in content and isinstance(content['image'], str):
        content['image'] = normalize_path(content['image'])
    
    return content

# Exemple d'utilisation dans une route Flask
"""
@app.route('/create_pairs_exercise', methods=['POST'])
def create_pairs_exercise():
    # Récupérer les données du formulaire
    data = request.form
    
    # Construire le contenu de l'exercice
    content = {
        'pairs': [
            # ... données des paires ...
        ]
    }
    
    # Normaliser les chemins d'images
    content = normalize_pairs_exercise_content(content)
    
    # Sauvegarder l'exercice dans la base de données
    exercise = Exercise(
        title=data['title'],
        type='pairs',
        content=json.dumps(content),
        # ... autres champs ...
    )
    db.session.add(exercise)
    db.session.commit()
    
    return redirect(url_for('exercise.view', id=exercise.id))
"""

# Test de la fonction
if __name__ == "__main__":
    # Exemple de contenu d'exercice
    test_content = {
        "pairs": [
            {
                "id": "1",
                "left": {
                    "content": "/static/exercises/test_image.png",
                    "type": "image"
                },
                "right": {
                    "content": "Texte test",
                    "type": "text"
                }
            }
        ]
    }
    
    # Normaliser le contenu
    normalized_content = normalize_pairs_exercise_content(test_content)
    
    # Afficher le résultat
    print(json.dumps(normalized_content, indent=2))
