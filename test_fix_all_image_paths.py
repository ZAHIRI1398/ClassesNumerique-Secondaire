#!/usr/bin/env python3
"""
Script pour tester la correction automatique des chemins d'images
"""

import os
import sys
import json
from flask import Flask
from models import db, Exercise
from config import config

def test_fix_all_image_paths():
    """Teste la logique de correction automatique des chemins d'images"""
    
    # Créer une application Flask minimale
    app = Flask(__name__)
    app.config.from_object(config['development'])
    db.init_app(app)
    
    with app.app_context():
        print("=== TEST CORRECTION AUTOMATIQUE DES CHEMINS D'IMAGES ===\n")
        
        # Récupérer tous les exercices avec des images
        exercises = Exercise.query.filter(
            Exercise.image_path.isnot(None),
            Exercise.image_path != ""
        ).all()
        
        if not exercises:
            print("[ERROR] Aucun exercice avec image trouve")
            return
        
        print(f"[INFO] {len(exercises)} exercice(s) avec image trouve(s)\n")
        
        corrections_made = 0
        results = []
        
        for exercise in exercises:
            original_path = exercise.image_path
            needs_correction = False
            corrected_path = original_path
            
            print(f"[*] Exercice {exercise.id}: {exercise.title}")
            print(f"    Chemin actuel: {original_path}")
            
            # Vérifier si le chemin a besoin d'être corrigé
            if original_path and (not original_path.startswith('/static/uploads/') or original_path.startswith('/static/exercises/')):
                needs_correction = True
                
                if original_path.startswith('static/'):
                    # Cas: static/uploads/filename -> /static/uploads/filename
                    corrected_path = f"/{original_path}"
                elif original_path.startswith('uploads/'):
                    # Cas: uploads/filename -> /static/uploads/filename
                    corrected_path = f"/static/{original_path}"
                elif original_path.startswith('/static/exercises/'):
                    # Cas: /static/exercises/filename -> /static/uploads/filename
                    filename = os.path.basename(original_path)
                    corrected_path = f"/static/uploads/{filename}"
                elif original_path.startswith('static/exercises/'):
                    # Cas: static/exercises/filename -> /static/uploads/filename
                    filename = os.path.basename(original_path)
                    corrected_path = f"/static/uploads/{filename}"
                else:
                    # Cas: filename seul -> /static/uploads/filename
                    filename = os.path.basename(original_path)
                    corrected_path = f"/static/uploads/{filename}"
            
            if needs_correction:
                print(f"    --> Correction: {corrected_path}")
                
                # Mettre à jour exercise.image_path
                exercise.image_path = corrected_path
                
                # Mettre à jour content.image si le contenu existe
                if exercise.content:
                    try:
                        content = json.loads(exercise.content)
                        if 'image' in content:
                            old_content_image = content['image']
                            content['image'] = corrected_path
                            exercise.content = json.dumps(content)
                            print(f"    [+] Content image: {old_content_image} -> {corrected_path}")
                    except json.JSONDecodeError:
                        print(f"    [!] Erreur de parsing JSON pour le contenu")
                
                corrections_made += 1
                results.append({
                    'id': exercise.id,
                    'title': exercise.title,
                    'original': original_path,
                    'corrected': corrected_path,
                    'status': 'corrigé'
                })
            else:
                print(f"    [OK] Chemin déjà correct")
                results.append({
                    'id': exercise.id,
                    'title': exercise.title,
                    'original': original_path,
                    'corrected': original_path,
                    'status': 'déjà correct'
                })
            
            print()
        
        # Sauvegarder les changements
        if corrections_made > 0:
            db.session.commit()
            print(f"[SUCCESS] CORRECTION TERMINÉE")
            print(f"[INFO] {corrections_made} exercice(s) corrigé(s) sur {len(exercises)} total")
            print("\n[OK] Tous les chemins d'images sont maintenant cohérents avec le préfixe /static/uploads/")
            print("[OK] Les images devraient s'afficher correctement dans tous les exercices")
        else:
            print("[INFO] Aucune correction nécessaire - tous les chemins sont déjà corrects")
        
        # Afficher le résumé
        print("\n=== RESUME DES CORRECTIONS ===")
        for result in results:
            status_icon = "[OK]" if result['status'] == 'déjà correct' else "[FIX]"
            print(f"{status_icon} Exercice {result['id']}: {result['title'][:30]}... - {result['status']}")
            if result['status'] == 'corrigé':
                print(f"    {result['original']} -> {result['corrected']}")

def verify_corrections():
    """Vérifie que toutes les corrections ont été appliquées correctement"""
    
    app = Flask(__name__)
    app.config.from_object(config['development'])
    db.init_app(app)
    
    with app.app_context():
        print("\n=== VÉRIFICATION DES CORRECTIONS ===\n")
        
        exercises = Exercise.query.filter(
            Exercise.image_path.isnot(None),
            Exercise.image_path != ""
        ).all()
        
        incorrect_paths = 0
        
        for exercise in exercises:
            # Vérifier exercise.image_path
            path_correct = exercise.image_path.startswith('/static/uploads/')
            
            # Vérifier content.image
            content_correct = True
            if exercise.content:
                try:
                    content = json.loads(exercise.content)
                    if 'image' in content:
                        content_correct = content['image'].startswith('/static/uploads/')
                except:
                    content_correct = False
            
            if not path_correct or not content_correct:
                print(f"[ERROR] Exercice {exercise.id}: {exercise.title}")
                if not path_correct:
                    print(f"   - image_path incorrect: {exercise.image_path}")
                if not content_correct:
                    print(f"   - content.image incorrect")
                incorrect_paths += 1
            else:
                print(f"[OK] Exercice {exercise.id}: {exercise.title}")
        
        if incorrect_paths == 0:
            print(f"\n[SUCCESS] VERIFICATION REUSSIE: Tous les {len(exercises)} exercices ont des chemins corrects!")
        else:
            print(f"\n[WARNING] {incorrect_paths} exercice(s) ont encore des problemes")

if __name__ == "__main__":
    test_fix_all_image_paths()
    verify_corrections()
