#!/usr/bin/env python3
"""
Test pour diagnostiquer l'erreur d'affichage de l'exercice
"""

import sys
import traceback

def test_imports():
    """Test des imports pour identifier les erreurs"""
    print("=== TEST DES IMPORTS ===")
    
    try:
        print("1. Import de Flask...")
        from flask import Flask
        print("   Flask OK")
        
        print("2. Import des modèles...")
        from models import db, Exercise, ExerciseAttempt, Course, Class
        print("   Models OK")
        
        print("3. Import de exercise_routes...")
        from exercise_routes import register_exercise_routes
        print("   exercise_routes OK")
        
        print("4. Test de création d'app Flask...")
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test'
        print("   App Flask OK")
        
        print("5. Test d'enregistrement des routes...")
        register_exercise_routes(app)
        print("   Routes enregistrees OK")
        
        print("6. Test d'accès à l'exercice 8...")
        with app.app_context():
            exercise = Exercise.query.get(8)
            if exercise:
                print(f"   Exercice 8 trouve: {exercise.title}")
                print(f"   Type: {exercise.exercise_type}")
            else:
                print("   Exercice 8 non trouve")
        
        return True
        
    except Exception as e:
        print(f"   ERREUR: {e}")
        print("   Traceback:")
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_imports()
    print(f"\n=== RESULTAT: {'SUCCES' if success else 'ECHEC'} ===")
