#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour corriger définitivement le décalage entre noms générés et noms en base
"""

import os
import sqlite3
import json

def fix_file_name_mismatch():
    """Corriger les exercices avec fichiers manquants en utilisant les fichiers réels"""
    
    # Chemin vers la base de données
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')
    exercises_dir = os.path.join(os.path.dirname(__file__), 'static', 'exercises')
    
    if not os.path.exists(db_path):
        print(f"Base de donnees non trouvee: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("CORRECTION DECALAGE NOMS DE FICHIERS")
        print("=" * 45)
        
        # Récupérer les exercices avec fichiers manquants
        problematic_exercises = [
            (5, "Capture d'écran 2025-08-19 222708_20250824_000202_uBW0Yx.png", "qcm_20250824_000202_8536a204.png"),
            (4, "Capture d'écran 2025-08-19 222831_20250823_235038_CYM0Zh.png", "qcm_20250823_235038_3da85263.png")
        ]
        
        fixed_count = 0
        
        for exercise_id, expected_file, actual_file in problematic_exercises:
            print(f"\nExercice ID {exercise_id}:")
            print(f"Fichier attendu: {expected_file}")
            print(f"Fichier reel: {actual_file}")
            
            # Vérifier que le fichier réel existe
            actual_path = os.path.join(exercises_dir, actual_file)
            if os.path.exists(actual_path):
                file_size = os.path.getsize(actual_path)
                print(f"Fichier reel confirme: {file_size} octets")
                
                # Nouveau chemin web
                new_web_path = f"/static/exercises/{actual_file}"
                
                # Mettre à jour la base de données
                cursor.execute("UPDATE exercise SET image_path = ? WHERE id = ?", (new_web_path, exercise_id))
                
                # Mettre à jour le contenu JSON
                cursor.execute("SELECT content FROM exercise WHERE id = ?", (exercise_id,))
                result = cursor.fetchone()
                
                if result and result[0]:
                    try:
                        content_data = json.loads(result[0])
                        content_data['image'] = new_web_path
                        new_content = json.dumps(content_data)
                        cursor.execute("UPDATE exercise SET content = ? WHERE id = ?", (new_content, exercise_id))
                        print(f"Base mise a jour: {new_web_path}")
                        fixed_count += 1
                    except json.JSONDecodeError:
                        print("Erreur decodage JSON")
                else:
                    print("Contenu vide")
            else:
                print(f"Fichier reel non trouve: {actual_file}")
            
            print("-" * 30)
        
        # Valider les changements
        conn.commit()
        conn.close()
        
        print(f"\nRESUME:")
        print(f"Exercices corriges: {fixed_count}")
        print("Correction terminee!")
        
        return True
        
    except Exception as e:
        print(f"Erreur: {str(e)}")
        return False

if __name__ == "__main__":
    fix_file_name_mismatch()
