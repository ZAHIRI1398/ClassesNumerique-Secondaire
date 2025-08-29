#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour diagnostiquer l'affichage d'image dans l'interface d'édition
"""

import os
import sqlite3

def debug_exercise_image():
    """Diagnostiquer l'affichage d'image pour l'exercice modifié"""
    
    # Chemin vers la base de données
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')
    
    if not os.path.exists(db_path):
        print(f"Base de donnees non trouvee: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Récupérer l'exercice "Test QCM Complet" qui a été modifié
        cursor.execute("""
            SELECT id, title, image_path, content, created_at 
            FROM exercise 
            WHERE title LIKE '%Test QCM Complet%'
            ORDER BY created_at DESC
        """)
        
        exercises = cursor.fetchall()
        
        print("DIAGNOSTIC AFFICHAGE IMAGE APRES MODIFICATION")
        print("=" * 60)
        
        for exercise in exercises:
            exercise_id, title, image_path, content, created_at = exercise
            
            print(f"\nExercice ID {exercise_id}: {title}")
            print(f"Cree: {created_at}")
            print(f"Chemin image: {image_path}")
            
            # Vérifier si le fichier existe physiquement
            if image_path:
                # Construire le chemin physique du fichier
                if image_path.startswith('/static/exercises/'):
                    filename = image_path.replace('/static/exercises/', '')
                    physical_path = os.path.join(os.path.dirname(__file__), 'static', 'exercises', filename)
                elif image_path.startswith('/static/uploads/'):
                    filename = image_path.replace('/static/uploads/', '')
                    physical_path = os.path.join(os.path.dirname(__file__), 'static', 'uploads', filename)
                else:
                    physical_path = None
                
                if physical_path:
                    exists = os.path.exists(physical_path)
                    if exists:
                        size = os.path.getsize(physical_path)
                        print(f"Fichier physique: EXISTE ({size} bytes)")
                        print(f"Chemin physique: {physical_path}")
                    else:
                        print(f"Fichier physique: MANQUANT")
                        print(f"Chemin physique attendu: {physical_path}")
                else:
                    print(f"Impossible de determiner le chemin physique")
            else:
                print(f"Aucun chemin d'image defini")
            
            # Vérifier le contenu JSON
            if content:
                import json
                try:
                    content_data = json.loads(content)
                    if 'image' in content_data:
                        print(f"Image dans JSON: {content_data['image']}")
                    else:
                        print(f"Pas d'image dans le JSON")
                except json.JSONDecodeError:
                    print(f"Erreur decodage JSON")
            else:
                print(f"Pas de contenu JSON")
            
            print("-" * 40)
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Erreur lors du diagnostic: {str(e)}")
        return False

def check_template_logic():
    """Vérifier la logique du template"""
    
    print(f"\nVERIFICATION LOGIQUE TEMPLATE:")
    print("=" * 40)
    
    # Simuler la condition du template
    test_cases = [
        "/static/exercises/test.png",
        "/static/uploads/test.png", 
        "",
        None
    ]
    
    for image_path in test_cases:
        print(f"\nCas: image_path = {repr(image_path)}")
        
        # Condition du template: {% if exercise.image_path %}
        if image_path:
            print(f"  Template affichera: OUI (condition vraie)")
            print(f"  URL src sera: {image_path}")
        else:
            print(f"  Template affichera: NON (condition fausse)")

if __name__ == "__main__":
    debug_exercise_image()
    check_template_logic()
