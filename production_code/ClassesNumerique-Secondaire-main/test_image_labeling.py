#!/usr/bin/env python3
"""
Script de test pour créer un exercice d'étiquetage d'image
"""

import json
from app import app, db
from models import Exercise, User

def create_test_image_labeling():
    with app.app_context():
        # Trouver un enseignant existant
        teacher = User.query.filter_by(role='teacher').first()
        if not teacher:
            print("Aucun enseignant trouvé dans la base de données")
            return
        
        # Contenu de l'exercice d'étiquetage d'image
        content = {
            "main_image": "static/uploads/corps_humain_exemple.jpg",  # Image d'exemple
            "labels": [
                "Le cœur",
                "Les poumons", 
                "L'estomac",
                "Le foie",
                "Les reins"
            ],
            "zones": [
                {"x": 150, "y": 120, "label": "Le cœur"},
                {"x": 100, "y": 100, "label": "Les poumons"},
                {"x": 180, "y": 180, "label": "L'estomac"},
                {"x": 200, "y": 140, "label": "Le foie"},
                {"x": 120, "y": 200, "label": "Les reins"}
            ]
        }
        
        # Créer l'exercice
        exercise = Exercise(
            title="Test Étiquetage d'Image - Corps Humain",
            description="Placez les étiquettes des organes aux bons endroits sur le schéma du corps humain.",
            exercise_type="image_labeling",
            content=json.dumps(content),
            subject="Sciences",
            max_attempts=3,
            teacher_id=teacher.id
        )
        
        db.session.add(exercise)
        db.session.commit()
        
        print(f"[OK] Exercice d'etiquetage d'image cree avec succes (ID: {exercise.id})")
        print(f"Titre: {exercise.title}")
        print(f"Type: {exercise.exercise_type}")
        print(f"Enseignant: {teacher.username}")
        print(f"Etiquettes: {len(content['labels'])} etiquettes")
        print(f"Zones: {len(content['zones'])} zones de placement")
        
        return exercise.id

if __name__ == "__main__":
    exercise_id = create_test_image_labeling()
    if exercise_id:
        print(f"\nVous pouvez tester l'exercice a l'URL: http://127.0.0.1:5000/exercise/{exercise_id}")
