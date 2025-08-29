#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
from PIL import Image, ImageDraw, ImageFont
import shutil

def fix_exercise_7_with_uploaded_image():
    """
    Corriger l'exercice 7 en utilisant une image uploadée via /test_upload
    """
    print("=== CORRECTION EXERCICE 7 AVEC IMAGE UPLOADEE ===")
    
    # Chemin vers la base de données
    db_path = "instance/classe_numerique.db"
    
    if not os.path.exists(db_path):
        print(f"Base de donnees non trouvee: {db_path}")
        return
    
    # Chercher les images récemment uploadées
    uploads_dir = "static/uploads"
    uploaded_images = []
    
    if os.path.exists(uploads_dir):
        for file in os.listdir(uploads_dir):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                file_path = os.path.join(uploads_dir, file)
                file_size = os.path.getsize(file_path)
                if file_size > 0:  # Ignorer les fichiers vides
                    uploaded_images.append((file, file_path, file_size))
    
    # Trier par date de modification (plus récent en premier)
    uploaded_images.sort(key=lambda x: os.path.getmtime(x[1]), reverse=True)
    
    print(f"Images disponibles dans {uploads_dir}:")
    for i, (filename, filepath, size) in enumerate(uploaded_images[:5]):  # Afficher les 5 plus récentes
        print(f"  {i+1}. {filename} ({size} bytes)")
    
    if not uploaded_images:
        print("Aucune image valide trouvee dans static/uploads")
        return
    
    # Utiliser l'image la plus récente
    selected_image = uploaded_images[0]
    selected_filename, selected_filepath, selected_size = selected_image
    
    print(f"\nImage selectionnee: {selected_filename} ({selected_size} bytes)")
    
    # Connexion à la base de données
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Trouver l'exercice 7
        cursor.execute("SELECT id, title, image_path FROM exercise WHERE id = 7")
        exercise = cursor.fetchone()
        
        if not exercise:
            print("Exercice 7 non trouve")
            return
        
        exercise_id, title, current_image_path = exercise
        print(f"Exercice trouvé: '{title}'")
        print(f"Image actuelle: {current_image_path}")
        
        # Nouveau chemin d'image
        new_image_path = f"/static/uploads/{selected_filename}"
        
        # Mettre à jour la base de données
        cursor.execute(
            "UPDATE exercise SET image_path = ? WHERE id = ?",
            (new_image_path, exercise_id)
        )
        
        conn.commit()
        print(f"Base mise a jour: {new_image_path}")
        
        # Vérification finale
        cursor.execute("SELECT title, image_path FROM exercise WHERE id = 7")
        result = cursor.fetchone()
        if result:
            title, image_path = result
            print(f"\n=== VERIFICATION ===")
            print(f"Exercice 7: {title}")
            print(f"Chemin: {image_path}")
            print(f"Fichier: {selected_filepath} ({selected_size} bytes)")
            print("SUCCES - Image mise a jour!")
        
    except Exception as e:
        print(f"Erreur: {e}")
        conn.rollback()
    finally:
        conn.close()
    
    print("\nCorrection terminée!")

if __name__ == "__main__":
    fix_exercise_7_with_uploaded_image()
