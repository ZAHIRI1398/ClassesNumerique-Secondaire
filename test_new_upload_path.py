#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour vérifier que les nouveaux uploads utilisent le bon chemin /static/exercises/
"""

import os
import sys
import sqlite3
from datetime import datetime

def test_upload_path():
    """Test pour vérifier les chemins d'upload après correction"""
    
    # Chemin vers la base de données
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Base de données non trouvée: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Récupérer tous les exercices avec images
        cursor.execute("""
            SELECT id, title, exercise_type, image_path, created_at 
            FROM exercise 
            WHERE image_path IS NOT NULL AND image_path != ''
            ORDER BY created_at DESC
        """)
        
        exercises = cursor.fetchall()
        
        print(f"Exercices avec images trouves: {len(exercises)}")
        print("=" * 80)
        
        correct_path_count = 0
        incorrect_path_count = 0
        
        for exercise in exercises:
            exercise_id, title, exercise_type, image_path, created_at = exercise
            
            # Vérifier le format du chemin
            if image_path.startswith('/static/exercises/'):
                status = "CORRECT"
                correct_path_count += 1
            elif image_path.startswith('/static/uploads/'):
                status = "ANCIEN FORMAT"
                incorrect_path_count += 1
            else:
                status = "FORMAT INCONNU"
                incorrect_path_count += 1
            
            print(f"ID {exercise_id}: {title}")
            print(f"  Type: {exercise_type}")
            print(f"  Chemin: {image_path}")
            print(f"  Statut: {status}")
            print(f"  Créé: {created_at}")
            print("-" * 40)
        
        conn.close()
        
        print(f"\nRESUME:")
        print(f"Chemins corrects (/static/exercises/): {correct_path_count}")
        print(f"Anciens chemins (/static/uploads/): {incorrect_path_count}")
        
        if incorrect_path_count == 0:
            print(f"\nSUCCES: Tous les chemins utilisent le bon format!")
            return True
        else:
            print(f"\nATTENTION: {incorrect_path_count} exercices utilisent encore l'ancien format")
            return False
            
    except Exception as e:
        print(f"Erreur lors du test: {str(e)}")
        return False

def check_physical_files():
    """Vérifier que les fichiers existent physiquement"""
    
    uploads_dir = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    exercises_dir = os.path.join(os.path.dirname(__file__), 'static', 'exercises')
    
    print(f"\nVERIFICATION DES FICHIERS PHYSIQUES:")
    print("=" * 50)
    
    # Vérifier le dossier uploads
    if os.path.exists(uploads_dir):
        uploads_files = [f for f in os.listdir(uploads_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        print(f"static/uploads/: {len(uploads_files)} fichiers")
        for f in uploads_files[:5]:  # Afficher les 5 premiers
            file_path = os.path.join(uploads_dir, f)
            size = os.path.getsize(file_path)
            print(f"  - {f} ({size} bytes)")
        if len(uploads_files) > 5:
            print(f"  ... et {len(uploads_files) - 5} autres fichiers")
    else:
        print(f"static/uploads/: Dossier non trouve")
    
    # Vérifier le dossier exercises
    if os.path.exists(exercises_dir):
        exercises_files = [f for f in os.listdir(exercises_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        print(f"static/exercises/: {len(exercises_files)} fichiers")
        for f in exercises_files[:5]:  # Afficher les 5 premiers
            file_path = os.path.join(exercises_dir, f)
            size = os.path.getsize(file_path)
            print(f"  - {f} ({size} bytes)")
        if len(exercises_files) > 5:
            print(f"  ... et {len(exercises_files) - 5} autres fichiers")
    else:
        print(f"static/exercises/: Dossier non trouve")

if __name__ == "__main__":
    print("TEST DES CHEMINS D'UPLOAD APRES CORRECTION")
    print("=" * 60)
    
    success = test_upload_path()
    check_physical_files()
    
    if success:
        print(f"\nTEST REUSSI: La correction est effective!")
    else:
        print(f"\nTEST ECHOUE: Des problemes subsistent")
