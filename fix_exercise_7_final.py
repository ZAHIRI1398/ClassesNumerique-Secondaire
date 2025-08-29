#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour corriger l'exercice 7 avec image 0 bytes
"""

import os
import sqlite3
from PIL import Image, ImageDraw, ImageFont

def create_test_image(filepath, text="IMAGE TEST EXERCICE 7"):
    """Crée une image de test"""
    try:
        # Créer une image de test (600x400, fond bleu clair)
        img = Image.new('RGB', (600, 400), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        # Utiliser une police par défaut
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # Centrer le texte
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (600 - text_width) // 2
        y = (400 - text_height) // 2
        
        # Dessiner le texte
        draw.text((x, y), text, fill='darkblue', font=font)
        
        # Sauvegarder l'image
        img.save(filepath)
        return True
        
    except Exception as e:
        print(f"Erreur creation image: {e}")
        return False

def fix_exercise_7():
    """Corrige l'exercice 7"""
    
    db_path = "instance/classe_numerique.db"
    upload_dir = "static/uploads"
    
    print("=== CORRECTION EXERCICE 7 ===")
    
    # Créer le dossier d'upload s'il n'existe pas
    os.makedirs(upload_dir, exist_ok=True)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Récupérer l'exercice 7
        cursor.execute("SELECT id, title, image_path FROM exercise WHERE id = 7")
        exercise = cursor.fetchone()
        
        if not exercise:
            print("Exercice 7 non trouve")
            return False
        
        exercise_id, title, current_image_path = exercise
        print(f"Exercice trouve: '{title}'")
        print(f"Image actuelle: {current_image_path}")
        
        # Vérifier l'image actuelle
        if current_image_path:
            current_file = current_image_path[1:] if current_image_path.startswith('/') else current_image_path
            if os.path.exists(current_file):
                size = os.path.getsize(current_file)
                print(f"Taille actuelle: {size} bytes")
                if size == 0:
                    print("Image vide detectee - correction necessaire")
                else:
                    print("Image semble OK")
                    return True
        
        # Créer une nouvelle image
        new_filename = "exercise_7_corrected.png"
        new_filepath = os.path.join(upload_dir, new_filename)
        new_image_path = f"/static/uploads/{new_filename}"
        
        print(f"Creation nouvelle image: {new_filepath}")
        
        if create_test_image(new_filepath, "EXERCICE 7 CORRIGE\ntest des images"):
            # Mettre à jour la base de données
            cursor.execute(
                "UPDATE exercise SET image_path = ? WHERE id = ?",
                (new_image_path, exercise_id)
            )
            conn.commit()
            
            print(f"Base mise a jour: {new_image_path}")
            print(f"Taille fichier: {os.path.getsize(new_filepath)} bytes")
            
            return True
        else:
            print("Echec creation image")
            return False
            
    except Exception as e:
        print(f"Erreur: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def verify_correction():
    """Vérifie la correction"""
    print("\n=== VERIFICATION ===")
    
    try:
        conn = sqlite3.connect("instance/classe_numerique.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, title, image_path FROM exercise WHERE id = 7")
        exercise = cursor.fetchone()
        
        if exercise:
            exercise_id, title, image_path = exercise
            print(f"Exercice 7: {title}")
            print(f"Chemin: {image_path}")
            
            if image_path:
                file_path = image_path[1:] if image_path.startswith('/') else image_path
                if os.path.exists(file_path):
                    size = os.path.getsize(file_path)
                    print(f"Fichier: {file_path} ({size} bytes)")
                    if size > 0:
                        print("SUCCES - Image corrigee!")
                    else:
                        print("ECHEC - Image toujours vide")
                else:
                    print("ECHEC - Fichier manquant")
        
        conn.close()
        
    except Exception as e:
        print(f"Erreur verification: {e}")

if __name__ == "__main__":
    if fix_exercise_7():
        verify_correction()
        print("\nCorrection terminee!")
    else:
        print("\nEchec correction!")
