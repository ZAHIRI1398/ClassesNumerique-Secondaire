#!/usr/bin/env python3
"""
Script pour créer un exercice "texte à trous" avec la bonne structure
"""

from models import Exercise, db
from extensions import init_extensions
from flask import Flask
import json

def create_fill_in_blanks_exercise():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    init_extensions(app)
    
    with app.app_context():
        # Structure correcte pour "texte à trous"
        content = {
            "sentences": [
                "Le chat ___ sur le tapis",
                "La voiture est de couleur ___",
                "En mathématiques, 2 + 2 = ___"
            ],
            "words": [
                "dort",
                "rouge", 
                "4",
                "mange",
                "bleue",
                "5"
            ]
        }
        
        # Créer l'exercice
        exercise = Exercise(
            title="Test Texte à Trous - Structure Correcte",
            description="Exercice de test avec la bonne structure JSON pour texte à trous",
            exercise_type="fill_in_blanks",
            content=json.dumps(content, ensure_ascii=False),
            teacher_id=1  # Assuming teacher with ID 1 exists
        )
        
        try:
            db.session.add(exercise)
            db.session.commit()
            print(f"[OK] Exercice 'texte a trous' cree avec succes !")
            print(f"   ID: {exercise.id}")
            print(f"   Titre: {exercise.title}")
            print(f"   Type: {exercise.exercise_type}")
            print(f"   Structure: {content}")
            
            # Vérifier que l'exercice est bien sauvé
            saved_exercise = Exercise.query.filter_by(id=exercise.id).first()
            if saved_exercise:
                saved_content = saved_exercise.get_content()
                print(f"[OK] Verification - Contenu sauve: {saved_content}")
                
                # Vérifier les clés attendues
                if 'sentences' in saved_content and 'words' in saved_content:
                    print("[OK] Structure correcte confirmee !")
                else:
                    print("[ERROR] Structure incorrecte !")
                    
        except Exception as e:
            print(f"[ERROR] Erreur lors de la creation: {e}")
            db.session.rollback()

if __name__ == "__main__":
    create_fill_in_blanks_exercise()
