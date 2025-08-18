"""
Script pour vérifier la structure de la table Exercise et les chemins d'images
"""

import os
import sys
from flask import Flask
from models import db, Exercise
from config import config
from sqlalchemy import inspect

def check_exercise_table():
    """Vérifie la structure de la table Exercise et les chemins d'images"""
    # Créer une application Flask minimale
    app = Flask(__name__)
    app.config.from_object(config['development'])
    db.init_app(app)
    
    with app.app_context():
        # Obtenir l'inspecteur SQLAlchemy
        inspector = inspect(db.engine)
        
        # Vérifier si la table Exercise existe
        if 'exercise' not in inspector.get_table_names():
            print("La table 'exercise' n'existe pas dans la base de données.")
            return
        
        # Obtenir les colonnes de la table Exercise
        columns = inspector.get_columns('exercise')
        print("Structure de la table Exercise:")
        for column in columns:
            print(f"- {column['name']} ({column['type']})")
        
        # Compter le nombre total d'exercices
        total_exercises = Exercise.query.count()
        print(f"\nNombre total d'exercices: {total_exercises}")
        
        # Compter les exercices avec image_path non NULL
        with_image = Exercise.query.filter(Exercise.image_path.isnot(None)).count()
        print(f"Exercices avec image_path non NULL: {with_image}")
        
        # Compter les exercices avec image_path NULL
        without_image = Exercise.query.filter(Exercise.image_path.is_(None)).count()
        print(f"Exercices avec image_path NULL: {without_image}")
        
        # Vérifier si d'autres champs pourraient contenir des chemins d'images
        # Par exemple, dans le contenu JSON
        print("\nRecherche d'images dans d'autres champs:")
        
        # Vérifier le champ content pour des références à des images
        image_in_content = 0
        for ex in Exercise.query.limit(100).all():  # Limiter à 100 pour éviter de surcharger
            if ex.content and isinstance(ex.content, dict):
                # Chercher des clés qui pourraient contenir des chemins d'images
                for key in ['image', 'image_path', 'main_image', 'background_image']:
                    if key in ex.content and ex.content[key]:
                        image_in_content += 1
                        print(f"- Exercice #{ex.id}: Image trouvée dans content['{key}']: {ex.content[key]}")
                        break
        
        print(f"\nExercices avec images dans le champ content: {image_in_content} (sur 100 analysés)")
        
        # Suggérer des actions
        print("\nSuggestions:")
        if with_image == 0 and image_in_content > 0:
            print("- Les images semblent être stockées dans le champ 'content' plutôt que 'image_path'")
            print("- Modifier le script de migration pour extraire les images du champ 'content'")
        elif with_image == 0 and image_in_content == 0:
            print("- Aucune image trouvée dans la base de données")
            print("- Vérifier si les images dans static/uploads sont référencées ailleurs")
        else:
            print("- Vérifier le format des chemins d'images dans image_path")

if __name__ == "__main__":
    check_exercise_table()
