from flask import Flask, render_template
from models import db, Exercise
import json
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    # Récupérer l'exercice avec l'ID 5
    exercise = Exercise.query.get(5)
    
    if exercise:
        print(f"Exercice ID: {exercise.id}")
        print(f"Titre: {exercise.title}")
        print(f"Type: {exercise.exercise_type}")
        print(f"Image path: {exercise.image_path}")
        
        # Analyser le contenu JSON
        content = json.loads(exercise.content)
        
        # Vérifier le template d'édition pour ce type d'exercice
        edit_template = f"edit_{exercise.exercise_type}.html"
        template_path = os.path.join("templates", "exercise_types", edit_template)
        
        print(f"\nTemplate d'édition: {edit_template}")
        if os.path.exists(template_path):
            print(f"Le template existe: {template_path}")
            
            # Lire le template pour voir comment il gère les images
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
                
            # Chercher les sections qui gèrent l'affichage des images
            image_sections = []
            lines = template_content.split('\n')
            for i, line in enumerate(lines):
                if 'image' in line.lower() and ('src' in line.lower() or 'upload' in line.lower()):
                    start = max(0, i-5)
                    end = min(len(lines), i+5)
                    image_sections.append('\n'.join(lines[start:end]))
            
            if image_sections:
                print("\nSections du template qui gèrent les images:")
                for i, section in enumerate(image_sections):
                    print(f"\n--- Section {i+1} ---")
                    print(section)
            else:
                print("\nAucune section liée aux images trouvée dans le template")
        else:
            print(f"Le template n'existe pas: {template_path}")
            
            # Vérifier le template générique d'édition
            generic_template = "edit_exercise.html"
            generic_path = os.path.join("templates", generic_template)
            
            if os.path.exists(generic_path):
                print(f"\nTemplate générique trouvé: {generic_path}")
                # Lire le template générique
                with open(generic_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                
                # Chercher les sections qui gèrent l'affichage des images
                image_sections = []
                lines = template_content.split('\n')
                for i, line in enumerate(lines):
                    if 'image' in line.lower() and ('src' in line.lower() or 'upload' in line.lower()):
                        start = max(0, i-5)
                        end = min(len(lines), i+5)
                        image_sections.append('\n'.join(lines[start:end]))
                
                if image_sections:
                    print("\nSections du template générique qui gèrent les images:")
                    for i, section in enumerate(image_sections):
                        print(f"\n--- Section {i+1} ---")
                        print(section)
                else:
                    print("\nAucune section liée aux images trouvée dans le template générique")
    else:
        print(f"Aucun exercice trouvé avec l'ID 5")
