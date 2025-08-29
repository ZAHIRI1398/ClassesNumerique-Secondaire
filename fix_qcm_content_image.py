#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour synchroniser les images dans le contenu JSON des exercices QCM
"""

import os
import sqlite3
import json

def fix_qcm_content_images():
    """Synchroniser les images dans le contenu JSON"""
    
    # Chemin vers la base de données
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')
    
    if not os.path.exists(db_path):
        print(f"Base de donnees non trouvee: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Récupérer les exercices QCM avec image_path mais sans image dans le contenu
        cursor.execute("""
            SELECT id, title, image_path, content 
            FROM exercise 
            WHERE exercise_type = 'qcm' AND image_path IS NOT NULL AND image_path != ''
        """)
        
        exercises = cursor.fetchall()
        
        print("SYNCHRONISATION DES IMAGES DANS LE CONTENU JSON")
        print("=" * 60)
        
        fixed_count = 0
        
        for exercise in exercises:
            exercise_id, title, image_path, content = exercise
            
            print(f"\nExercice ID {exercise_id}: {title}")
            print(f"Image path: {image_path}")
            
            if content:
                try:
                    content_data = json.loads(content)
                    
                    # Vérifier si l'image est manquante ou différente
                    needs_update = False
                    
                    if 'image' not in content_data:
                        print("Status: Image manquante dans JSON - ajout en cours")
                        content_data['image'] = image_path
                        needs_update = True
                    elif content_data['image'] != image_path:
                        print(f"Status: Image incoherente - mise a jour en cours")
                        print(f"  Ancien: {content_data['image']}")
                        print(f"  Nouveau: {image_path}")
                        content_data['image'] = image_path
                        needs_update = True
                    else:
                        print("Status: Image deja coherente")
                    
                    if needs_update:
                        # Mettre à jour le contenu en base
                        new_content = json.dumps(content_data)
                        cursor.execute("UPDATE exercise SET content = ? WHERE id = ?", (new_content, exercise_id))
                        print("Contenu mis a jour avec succes")
                        fixed_count += 1
                        
                except json.JSONDecodeError as e:
                    print(f"Erreur decodage JSON: {str(e)}")
            else:
                print("Contenu vide - creation du contenu avec image")
                # Créer un contenu minimal avec l'image
                content_data = {
                    'image': image_path,
                    'questions': []
                }
                new_content = json.dumps(content_data)
                cursor.execute("UPDATE exercise SET content = ? WHERE id = ?", (new_content, exercise_id))
                print("Contenu cree avec succes")
                fixed_count += 1
            
            print("-" * 40)
        
        # Valider les changements
        conn.commit()
        conn.close()
        
        print(f"\nRESUME:")
        print(f"Exercices corriges: {fixed_count}")
        print("Synchronisation terminee!")
        
        return True
        
    except Exception as e:
        print(f"Erreur lors de la synchronisation: {str(e)}")
        return False

if __name__ == "__main__":
    fix_qcm_content_images()
