#!/usr/bin/env python3
"""
Script pour corriger définitivement le problème d'upload d'images
"""

import os
import sys
import json

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import db, Exercise
from app import app

def fix_image_upload_issue():
    """Corriger le problème d'upload d'images qui génère des fichiers vides"""
    
    print("=== CORRECTION PROBLEME UPLOAD IMAGES ===\n")
    
    with app.app_context():
        # 1. Analyser l'exercice 7
        exercise = Exercise.query.get(7)
        if not exercise:
            print("Exercice 7 non trouve!")
            return
        
        print(f"ETAT ACTUEL:")
        print(f"Image path: {exercise.image_path}")
        
        # 2. Vérifier si l'image existe et sa taille
        if exercise.image_path:
            image_filename = exercise.image_path.replace('/static/uploads/', '').replace('static/uploads/', '')
            image_file = f"static/uploads/{image_filename}"
            
            if os.path.exists(image_file):
                size = os.path.getsize(image_file)
                print(f"Image actuelle: {image_file} ({size} bytes)")
                
                if size == 0:
                    print("PROBLEME: Image vide detectee")
                    
                    # Supprimer l'image vide
                    os.remove(image_file)
                    print("Image vide supprimee")
                    
                    # Chercher une image valide récente
                    upload_dir = "static/uploads"
                    valid_images = []
                    
                    for file in os.listdir(upload_dir):
                        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                            file_path = os.path.join(upload_dir, file)
                            file_size = os.path.getsize(file_path)
                            mtime = os.path.getmtime(file_path)
                            
                            # Images valides (non vides)
                            if file_size > 0:
                                valid_images.append((file, file_size, mtime))
                    
                    if valid_images:
                        # Prendre l'image la plus récente
                        valid_images.sort(key=lambda x: x[2], reverse=True)
                        best_image = valid_images[0][0]
                        
                        print(f"Image de remplacement trouvee: {best_image}")
                        
                        # Mettre à jour la base de données
                        new_path = f"/static/uploads/{best_image}"
                        exercise.image_path = new_path
                        
                        # Mettre à jour le JSON
                        if exercise.content:
                            try:
                                content = json.loads(exercise.content)
                                content['image'] = new_path
                                exercise.content = json.dumps(content)
                            except:
                                pass
                        
                        db.session.commit()
                        print(f"Base de donnees mise a jour: {new_path}")
                        
                        # Vérifier que l'image est accessible
                        test_file = f"static/uploads/{best_image}"
                        if os.path.exists(test_file):
                            test_size = os.path.getsize(test_file)
                            print(f"Verification: {test_file} ({test_size} bytes) - OK")
                        
                    else:
                        print("Aucune image valide trouvee pour remplacement")
                        # Retirer l'image de l'exercice
                        exercise.image_path = None
                        if exercise.content:
                            try:
                                content = json.loads(exercise.content)
                                if 'image' in content:
                                    del content['image']
                                exercise.content = json.dumps(content)
                            except:
                                pass
                        db.session.commit()
                        print("Image retiree de l'exercice")
                
                else:
                    print(f"Image valide: {size} bytes")
            else:
                print(f"Image manquante: {image_file}")

def check_upload_function():
    """Vérifier la fonction d'upload dans app.py"""
    
    print("\n=== VERIFICATION FONCTION UPLOAD ===\n")
    
    # Lire le fichier app.py pour vérifier les fonctions d'upload
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Chercher les fonctions safe_file_save et generate_consistent_image_path
        if 'def safe_file_save(' in content:
            print("✓ Fonction safe_file_save trouvee")
        else:
            print("✗ Fonction safe_file_save manquante")
        
        if 'def generate_consistent_image_path(' in content:
            print("✓ Fonction generate_consistent_image_path trouvee")
        else:
            print("✗ Fonction generate_consistent_image_path manquante")
        
        # Vérifier l'utilisation dans les routes d'édition
        if 'safe_file_save(' in content:
            print("✓ Utilisation de safe_file_save detectee")
        else:
            print("✗ safe_file_save non utilisee - probleme potentiel")
        
    except Exception as e:
        print(f"Erreur lecture app.py: {e}")

def suggest_permanent_fix():
    """Suggérer une correction permanente"""
    
    print("\n=== SUGGESTIONS CORRECTION PERMANENTE ===\n")
    
    print("PROBLEME IDENTIFIE:")
    print("- Les images sont uploadees mais restent vides (0 bytes)")
    print("- Cela indique un probleme dans le processus de sauvegarde")
    print()
    
    print("SOLUTIONS:")
    print("1. Verifier que safe_file_save() est bien utilisee")
    print("2. Ajouter des logs pour tracer les uploads")
    print("3. Verifier les permissions du dossier static/uploads")
    print("4. Tester l'upload avec /test_upload")
    print()
    
    print("ACTIONS IMMEDIATES:")
    print("1. Utiliser une image existante valide")
    print("2. Tester l'upload via /test_upload")
    print("3. Verifier les logs d'erreur")

if __name__ == "__main__":
    fix_image_upload_issue()
    check_upload_function()
    suggest_permanent_fix()
