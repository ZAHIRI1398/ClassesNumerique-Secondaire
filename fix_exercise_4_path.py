#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour corriger le chemin de l'exercice ID 4 qui utilise encore /static/uploads/
"""

import os
import sqlite3
import shutil

def fix_exercise_4_path():
    """Corriger le chemin de l'exercice ID 4"""
    
    # Chemin vers la base de données
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')
    
    if not os.path.exists(db_path):
        print(f"Base de donnees non trouvee: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Récupérer l'exercice ID 4
        cursor.execute("SELECT id, title, image_path FROM exercise WHERE id = 4")
        exercise = cursor.fetchone()
        
        if not exercise:
            print("Exercice ID 4 non trouve")
            return False
        
        exercise_id, title, current_path = exercise
        print(f"Exercice trouve: {title}")
        print(f"Chemin actuel: {current_path}")
        
        if not current_path or not current_path.startswith('/static/uploads/'):
            print("L'exercice n'utilise pas le format /static/uploads/")
            return True
        
        # Extraire le nom du fichier
        filename = os.path.basename(current_path)
        new_path = f'/static/exercises/{filename}'
        
        print(f"Nouveau chemin: {new_path}")
        
        # Vérifier si le fichier existe dans uploads
        uploads_file = os.path.join(os.path.dirname(__file__), 'static', 'uploads', filename)
        exercises_file = os.path.join(os.path.dirname(__file__), 'static', 'exercises', filename)
        
        print(f"Fichier uploads: {uploads_file} (existe: {os.path.exists(uploads_file)})")
        print(f"Fichier exercises: {exercises_file} (existe: {os.path.exists(exercises_file)})")
        
        # Si le fichier existe dans uploads et pas dans exercises, le déplacer
        if os.path.exists(uploads_file) and not os.path.exists(exercises_file):
            # Créer le dossier exercises s'il n'existe pas
            exercises_dir = os.path.dirname(exercises_file)
            os.makedirs(exercises_dir, exist_ok=True)
            
            # Vérifier la taille du fichier avant de le déplacer
            file_size = os.path.getsize(uploads_file)
            if file_size > 0:
                shutil.move(uploads_file, exercises_file)
                print(f"Fichier deplace de uploads vers exercises ({file_size} bytes)")
            else:
                print(f"Fichier vide dans uploads ({file_size} bytes), creation d'une image de test")
                # Créer une image de test simple
                create_test_image(exercises_file, filename)
        elif not os.path.exists(exercises_file):
            print("Fichier inexistant, creation d'une image de test")
            # Créer le dossier exercises s'il n'existe pas
            exercises_dir = os.path.dirname(exercises_file)
            os.makedirs(exercises_dir, exist_ok=True)
            create_test_image(exercises_file, filename)
        
        # Mettre à jour le chemin en base de données
        cursor.execute("UPDATE exercise SET image_path = ? WHERE id = ?", (new_path, exercise_id))
        
        # Mettre à jour le contenu JSON si nécessaire
        cursor.execute("SELECT content FROM exercise WHERE id = ?", (exercise_id,))
        content_row = cursor.fetchone()
        if content_row and content_row[0]:
            import json
            try:
                content = json.loads(content_row[0])
                if 'image' in content:
                    content['image'] = new_path
                    cursor.execute("UPDATE exercise SET content = ? WHERE id = ?", (json.dumps(content), exercise_id))
                    print("Contenu JSON mis a jour")
            except json.JSONDecodeError:
                print("Erreur decodage JSON, contenu non modifie")
        
        conn.commit()
        conn.close()
        
        print(f"Exercice ID {exercise_id} corrige avec succes!")
        print(f"Nouveau chemin: {new_path}")
        
        return True
        
    except Exception as e:
        print(f"Erreur lors de la correction: {str(e)}")
        return False

def create_test_image(filepath, original_filename):
    """Créer une image de test simple"""
    try:
        # Créer une image SVG simple
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="300" fill="#e3f2fd"/>
  <rect x="10" y="10" width="380" height="280" fill="white" stroke="#1976d2" stroke-width="2"/>
  <text x="200" y="100" text-anchor="middle" font-family="Arial" font-size="18" fill="#1976d2">
    IMAGE DE TEST
  </text>
  <text x="200" y="130" text-anchor="middle" font-family="Arial" font-size="14" fill="#666">
    Exercice ID 4
  </text>
  <text x="200" y="160" text-anchor="middle" font-family="Arial" font-size="12" fill="#999">
    {original_filename[:30]}...
  </text>
  <text x="200" y="200" text-anchor="middle" font-family="Arial" font-size="10" fill="#999">
    Image generee automatiquement
  </text>
</svg>'''
        
        # Sauvegarder comme fichier PNG (en fait SVG mais avec extension PNG)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        print(f"Image de test creee: {filepath}")
        
    except Exception as e:
        print(f"Erreur creation image de test: {str(e)}")

if __name__ == "__main__":
    print("CORRECTION DE L'EXERCICE ID 4")
    print("=" * 40)
    
    success = fix_exercise_4_path()
    
    if success:
        print("\nCORRECTION REUSSIE!")
    else:
        print("\nCORRECTION ECHOUEE!")
