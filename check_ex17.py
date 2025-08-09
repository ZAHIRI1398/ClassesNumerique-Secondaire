#!/usr/bin/env python3
"""Script simple pour vérifier le contenu de l'exercice 17"""

from app import app, Exercise, db
import json

def check_exercise_17():
    with app.app_context():
        exercise = Exercise.query.get(17)
        if not exercise:
            print("❌ ERREUR : Exercice 17 non trouvé en base")
            return
        
        print("=== DIAGNOSTIC EXERCICE 17 ===")
        print(f"Titre: {exercise.title}")
        print(f"Type: {exercise.exercise_type}")
        print(f"Contenu brut: {exercise.content}")
        print()
        
        try:
            content = json.loads(exercise.content)
            print("=== CONTENU PARSÉ ===")
            print(f"Instructions: {content.get('instructions', 'N/A')}")
            print(f"Image principale: {content.get('main_image', 'N/A')}")
            print(f"Mode: {content.get('mode', 'classic')}")
            
            zones = content.get('zones', [])
            print(f"Nombre de zones: {len(zones)}")
            
            for i, zone in enumerate(zones):
                print(f"  Zone {i+1}: '{zone.get('legend', 'N/A')}' (x:{zone.get('x')}, y:{zone.get('y')})")
            
            elements = content.get('elements', [])
            if elements:
                print(f"Éléments: {elements}")
                
        except json.JSONDecodeError as e:
            print(f"❌ ERREUR JSON: {e}")
        
        print("=== FIN DIAGNOSTIC ===")

if __name__ == "__main__":
    check_exercise_17()
