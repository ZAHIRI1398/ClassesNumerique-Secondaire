#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour corriger le décalage entre noms de fichiers en base et sur disque
"""

import os
import sqlite3
import json

def fix_image_name_mismatch():
    """Corriger les noms d'images incohérents entre base et disque"""
    
    # Chemin vers la base de données
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')
    exercises_dir = os.path.join(os.path.dirname(__file__), 'static', 'exercises')
    
    if not os.path.exists(db_path):
        print(f"Base de donnees non trouvee: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Récupérer les exercices avec image_path
        cursor.execute("""
            SELECT id, title, image_path, content 
            FROM exercise 
            WHERE image_path IS NOT NULL AND image_path != ''
        """)
        
        exercises = cursor.fetchall()
        
        print("CORRECTION DES NOMS D'IMAGES INCOHERENTS")
        print("=" * 50)
        
        fixed_count = 0
        
        for exercise in exercises:
            exercise_id, title, image_path, content = exercise
            
            print(f"\nExercice ID {exercise_id}: {title}")
            print(f"Image path (DB): {image_path}")
            
            if image_path:
                # Extraire le nom du fichier
                filename = os.path.basename(image_path)
                full_path = os.path.join(exercises_dir, filename)
                
                print(f"Fichier attendu: {full_path}")
                
                if not os.path.exists(full_path):
                    print("PROBLEME: Fichier non trouve sur disque")
                    
                    # Chercher un fichier similaire avec même timestamp
                    if '_2025' in filename:
                        # Extraire le timestamp
                        parts = filename.split('_')
                        if len(parts) >= 3:
                            timestamp_part = f"_{parts[-2]}_{parts[-1].split('.')[0]}"
                            
                            # Chercher tous les fichiers avec ce timestamp
                            matching_files = []
                            for file in os.listdir(exercises_dir):
                                if timestamp_part in file and os.path.isfile(os.path.join(exercises_dir, file)):
                                    matching_files.append(file)
                            
                            if matching_files:
                                # Prendre le premier fichier trouvé
                                actual_file = matching_files[0]
                                actual_path = f"/static/exercises/{actual_file}"
                                
                                print(f"Fichier trouve: {actual_file}")
                                print(f"Nouveau chemin: {actual_path}")
                                
                                # Mettre à jour la base de données
                                cursor.execute("UPDATE exercise SET image_path = ? WHERE id = ?", (actual_path, exercise_id))
                                
                                # Mettre à jour le contenu JSON si nécessaire
                                if content:
                                    try:
                                        content_data = json.loads(content)
                                        if 'image' in content_data:
                                            content_data['image'] = actual_path
                                            new_content = json.dumps(content_data)
                                            cursor.execute("UPDATE exercise SET content = ? WHERE id = ?", (new_content, exercise_id))
                                            print("Contenu JSON mis a jour")
                                    except json.JSONDecodeError:
                                        print("Erreur decodage JSON")
                                
                                fixed_count += 1
                                print("CORRIGE avec succes")
                            else:
                                print("Aucun fichier correspondant trouve")
                    else:
                        print("Format de nom non reconnu")
                else:
                    file_size = os.path.getsize(full_path)
                    print(f"Fichier OK: {file_size} octets")
            
            print("-" * 40)
        
        # Valider les changements
        conn.commit()
        conn.close()
        
        print(f"\nRESUME:")
        print(f"Exercices corriges: {fixed_count}")
        print("Correction terminee!")
        
        return True
        
    except Exception as e:
        print(f"Erreur lors de la correction: {str(e)}")
        return False

if __name__ == "__main__":
    fix_image_name_mismatch()
