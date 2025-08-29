#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour créer les fichiers images manquants pour les exercices
"""

import os
import sqlite3

def create_missing_exercise_images():
    """Créer les fichiers images manquants"""
    
    # Chemin vers la base de données
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')
    
    if not os.path.exists(db_path):
        print(f"Base de donnees non trouvee: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Récupérer tous les exercices avec images
        cursor.execute("""
            SELECT id, title, image_path 
            FROM exercise 
            WHERE image_path IS NOT NULL AND image_path != ''
        """)
        
        exercises = cursor.fetchall()
        
        print("CREATION DES IMAGES MANQUANTES")
        print("=" * 50)
        
        created_count = 0
        
        for exercise in exercises:
            exercise_id, title, image_path = exercise
            
            print(f"\nExercice ID {exercise_id}: {title}")
            print(f"Chemin: {image_path}")
            
            # Déterminer le chemin physique
            if image_path.startswith('/static/exercises/'):
                filename = image_path.replace('/static/exercises/', '')
                physical_path = os.path.join(os.path.dirname(__file__), 'static', 'exercises', filename)
            elif image_path.startswith('/static/uploads/'):
                filename = image_path.replace('/static/uploads/', '')
                physical_path = os.path.join(os.path.dirname(__file__), 'static', 'uploads', filename)
            else:
                print(f"  Format de chemin non reconnu")
                continue
            
            # Vérifier si le fichier existe
            if os.path.exists(physical_path):
                file_size = os.path.getsize(physical_path)
                print(f"  Fichier existe ({file_size} bytes)")
            else:
                print(f"  Fichier manquant - creation en cours...")
                
                # Créer le dossier parent s'il n'existe pas
                os.makedirs(os.path.dirname(physical_path), exist_ok=True)
                
                # Créer une image SVG de test
                create_test_image(physical_path, title, exercise_id)
                
                if os.path.exists(physical_path):
                    file_size = os.path.getsize(physical_path)
                    print(f"  Image creee avec succes ({file_size} bytes)")
                    created_count += 1
                else:
                    print(f"  Echec creation image")
        
        conn.close()
        
        print(f"\nRESUME:")
        print(f"Images creees: {created_count}")
        print("Correction terminee!")
        
        return True
        
    except Exception as e:
        print(f"Erreur lors de la correction: {str(e)}")
        return False

def create_test_image(filepath, title, exercise_id):
    """Créer une image de test SVG"""
    try:
        # Créer une image SVG simple
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="300" fill="#f8f9fa"/>
  <rect x="10" y="10" width="380" height="280" fill="white" stroke="#007bff" stroke-width="2"/>
  <text x="200" y="80" text-anchor="middle" font-family="Arial" font-size="18" fill="#007bff" font-weight="bold">
    IMAGE D'EXERCICE
  </text>
  <text x="200" y="120" text-anchor="middle" font-family="Arial" font-size="14" fill="#333">
    {title[:40]}
  </text>
  <text x="200" y="150" text-anchor="middle" font-family="Arial" font-size="12" fill="#666">
    Exercice ID: {exercise_id}
  </text>
  <text x="200" y="180" text-anchor="middle" font-family="Arial" font-size="10" fill="#999">
    Image generee automatiquement
  </text>
  <circle cx="200" cy="220" r="30" fill="#e3f2fd" stroke="#2196f3" stroke-width="2"/>
  <text x="200" y="225" text-anchor="middle" font-family="Arial" font-size="12" fill="#1976d2">
    QCM
  </text>
</svg>'''
        
        # Sauvegarder le fichier SVG avec extension PNG (Flask servira le SVG comme image)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
    except Exception as e:
        print(f"Erreur creation image: {str(e)}")

if __name__ == "__main__":
    create_missing_exercise_images()
