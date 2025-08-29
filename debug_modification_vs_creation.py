#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour diagnostiquer les différences entre création et modification d'exercices
"""

import os
import sqlite3
import json

def debug_modification_vs_creation():
    """Analyser les différences entre création et modification"""
    
    # Chemin vers la base de données
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')
    exercises_dir = os.path.join(os.path.dirname(__file__), 'static', 'exercises')
    
    if not os.path.exists(db_path):
        print(f"Base de donnees non trouvee: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Récupérer tous les exercices QCM avec leurs détails
        cursor.execute("""
            SELECT id, title, image_path, content
            FROM exercise 
            WHERE exercise_type = 'qcm'
            ORDER BY id DESC
            LIMIT 10
        """)
        
        exercises = cursor.fetchall()
        
        print("DIAGNOSTIC CREATION VS MODIFICATION")
        print("=" * 50)
        
        for exercise in exercises:
            exercise_id, title, image_path, content = exercise
            
            print(f"\nExercice ID {exercise_id}: {title}")
            print(f"Image path (DB): {image_path}")
            
            # Vérifier l'existence du fichier
            if image_path:
                filename = os.path.basename(image_path)
                full_path = os.path.join(exercises_dir, filename)
                
                if os.path.exists(full_path):
                    file_size = os.path.getsize(full_path)
                    print(f"Fichier physique: OK ({file_size} octets)")
                else:
                    print(f"Fichier physique: MANQUANT ({filename})")
            else:
                print("Aucune image")
            
            # Analyser le contenu JSON
            if content:
                try:
                    content_data = json.loads(content)
                    content_image = content_data.get('image')
                    
                    if content_image:
                        print(f"Content.image: {content_image}")
                        
                        # Vérifier la cohérence
                        if image_path == content_image:
                            print("Coherence: OK (image_path == content.image)")
                        else:
                            print("Coherence: PROBLEME (image_path != content.image)")
                    else:
                        print("Content.image: MANQUANT")
                        
                except json.JSONDecodeError:
                    print("Content JSON: ERREUR DE DECODAGE")
            else:
                print("Content: VIDE")
            
            print("-" * 40)
        
        conn.close()
        
        # Lister les derniers fichiers créés
        print("\nDERNIERS FICHIERS CREES:")
        print("=" * 30)
        
        files = []
        for file in os.listdir(exercises_dir):
            if file.endswith('.png') and os.path.isfile(os.path.join(exercises_dir, file)):
                file_path = os.path.join(exercises_dir, file)
                mtime = os.path.getmtime(file_path)
                size = os.path.getsize(file_path)
                files.append((file, mtime, size))
        
        # Trier par date de modification (plus récent en premier)
        files.sort(key=lambda x: x[1], reverse=True)
        
        for i, (file, mtime, size) in enumerate(files[:10]):
            import datetime
            date_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            print(f"{i+1}. {file} ({size} octets) - {date_str}")
        
        return True
        
    except Exception as e:
        print(f"Erreur: {str(e)}")
        return False

if __name__ == "__main__":
    debug_modification_vs_creation()
