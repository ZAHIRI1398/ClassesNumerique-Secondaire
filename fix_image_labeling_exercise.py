import os
import sys
import json
from flask import Flask
from models import db, Exercise

# Configuration minimale pour accéder à la base de données
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///classe_numerique.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def normalize_image_path(path):
    """Normalise le chemin d'image pour assurer la cohérence"""
    if not path:
        return None
    
    # Si c'est déjà un chemin relatif commençant par /static/
    if path.startswith('/static/'):
        return path
    
    # Si c'est un chemin relatif sans /static/
    if not path.startswith('/'):
        # Si c'est un chemin d'image pour les exercices d'étiquetage
        if 'exercises/image_labeling/' in path or path.startswith('exercises/image_labeling/'):
            return f'/static/uploads/{path}'
        
        # Si c'est un chemin d'image standard pour les exercices
        if 'exercises/' in path or path.startswith('exercises/'):
            return f'/static/uploads/{path}'
    
    return path

def fix_image_labeling_exercise(exercise_id):
    """Corrige l'incohérence entre exercise.image_path et content['main_image'] pour un exercice d'étiquetage d'image"""
    with app.app_context():
        exercise = Exercise.query.get(exercise_id)
        if not exercise:
            print(f"Erreur: Exercice ID {exercise_id} non trouvé")
            return False
        
        if exercise.exercise_type != 'image_labeling':
            print(f"Erreur: L'exercice ID {exercise_id} n'est pas de type 'image_labeling' mais '{exercise.exercise_type}'")
            return False
        
        print(f"Correction de l'exercice ID {exercise_id}: {exercise.title}")
        
        try:
            content = json.loads(exercise.content) if exercise.content else {}
        except:
            content = {}
        
        if not isinstance(content, dict):
            content = {}
        
        # Vérifier si l'image principale existe dans le contenu
        main_image = content.get('main_image')
        
        if main_image:
            print(f"Image principale trouvée dans content['main_image']: {main_image}")
            
            # Normaliser le chemin de l'image
            normalized_image_path = normalize_image_path(main_image)
            print(f"Chemin d'image normalisé: {normalized_image_path}")
            
            # Mettre à jour exercise.image_path avec le chemin normalisé
            exercise.image_path = normalized_image_path
            print(f"exercise.image_path mis à jour: {exercise.image_path}")
            
            # Mettre à jour content['main_image'] avec le chemin normalisé
            content['main_image'] = normalized_image_path
            exercise.content = json.dumps(content)
            print(f"content['main_image'] mis à jour: {content['main_image']}")
            
            # Sauvegarder les modifications
            db.session.commit()
            print(f"Modifications sauvegardées avec succès")
            return True
        else:
            print(f"Aucune image principale trouvée dans le contenu de l'exercice")
            return False

def fix_all_image_labeling_exercises():
    """Corrige l'incohérence pour tous les exercices de type image_labeling"""
    with app.app_context():
        exercises = Exercise.query.filter_by(exercise_type='image_labeling').all()
        print(f"Nombre d'exercices de type image_labeling trouvés: {len(exercises)}")
        
        fixed_count = 0
        for exercise in exercises:
            print(f"\nTraitement de l'exercice ID {exercise.id}: {exercise.title}")
            if fix_image_labeling_exercise(exercise.id):
                fixed_count += 1
        
        print(f"\nRésumé: {fixed_count}/{len(exercises)} exercices corrigés")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Si un ID d'exercice est fourni en argument
        try:
            exercise_id = int(sys.argv[1])
            fix_image_labeling_exercise(exercise_id)
        except ValueError:
            print("Erreur: L'ID d'exercice doit être un nombre entier")
    else:
        # Sinon, corriger tous les exercices de type image_labeling
        fix_all_image_labeling_exercises()
