#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour corriger directement les images de l'exercice 7
sans passer par la route /test_upload
"""

import os
import sqlite3
from PIL import Image, ImageDraw, ImageFont
import shutil

def create_test_image(filepath, text="IMAGE TEST EXERCICE 7"):
    """Crée une image de test"""
    try:
        # Créer une image de test (600x400, fond bleu)
        img = Image.new('RGB', (600, 400), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        # Essayer d'utiliser une police système
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # Calculer la position du texte pour le centrer
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (600 - text_width) // 2
        y = (400 - text_height) // 2
        
        # Dessiner le texte
        draw.text((x, y), text, fill='darkblue', font=font)
        
        # Sauvegarder l'image
        img.save(filepath)
        print(f"Image créée: {filepath} ({os.path.getsize(filepath)} bytes)")
        return True
        
    except Exception as e:
        print(f"Erreur lors de la création de l'image: {e}")
        return False

def fix_exercise_7_images():
    """Corrige les images de l'exercice 7"""
    
    # Chemin vers la base de données
    db_path = "instance/app.db"
    if not os.path.exists(db_path):
        print(f"Base de données non trouvée: {db_path}")
        return False
    
    # Dossier d'upload
    upload_dir = "static/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    print("=== CORRECTION DES IMAGES EXERCICE 7 ===")
    
    try:
        # Connexion à la base de données
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Récupérer l'exercice 7
        cursor.execute("SELECT id, title, image_path FROM exercise WHERE id = 7")
        exercise = cursor.fetchone()
        
        if not exercise:
            print("Exercice 7 non trouvé dans la base de données")
            return False
        
        exercise_id, title, current_image_path = exercise
        print(f"Exercice trouvé: ID={exercise_id}, Titre='{title}'")
        print(f"Chemin image actuel: {current_image_path}")
        
        # Créer une nouvelle image de test
        new_filename = "exercise_7_test_image.png"
        new_filepath = os.path.join(upload_dir, new_filename)
        new_image_path = f"/static/uploads/{new_filename}"
        
        if create_test_image(new_filepath, f"IMAGE EXERCICE 7\n{title}"):
            # Mettre à jour la base de données
            cursor.execute(
                "UPDATE exercise SET image_path = ? WHERE id = ?",
                (new_image_path, exercise_id)
            )
            conn.commit()
            
            print(f"✅ Image mise à jour avec succès:")
            print(f"   Nouveau chemin: {new_image_path}")
            print(f"   Fichier: {new_filepath}")
            print(f"   Taille: {os.path.getsize(new_filepath)} bytes")
            
            # Vérifier la mise à jour
            cursor.execute("SELECT image_path FROM exercise WHERE id = 7")
            updated_path = cursor.fetchone()[0]
            print(f"   Vérification BDD: {updated_path}")
            
            return True
        else:
            print("❌ Échec de la création de l'image")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def verify_fix():
    """Vérifie que la correction a fonctionné"""
    print("\n=== VÉRIFICATION ===")
    
    db_path = "instance/app.db"
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, title, image_path FROM exercise WHERE id = 7")
        exercise = cursor.fetchone()
        
        if exercise:
            exercise_id, title, image_path = exercise
            print(f"Exercice 7: {title}")
            print(f"Chemin image: {image_path}")
            
            if image_path:
                # Vérifier si le fichier existe
                if image_path.startswith('/static/'):
                    file_path = image_path[1:]  # Enlever le / du début
                else:
                    file_path = image_path
                
                if os.path.exists(file_path):
                    size = os.path.getsize(file_path)
                    print(f"✅ Fichier existe: {file_path} ({size} bytes)")
                    if size > 0:
                        print("✅ Fichier non vide - Correction réussie!")
                    else:
                        print("❌ Fichier vide (0 bytes)")
                else:
                    print(f"❌ Fichier n'existe pas: {file_path}")
            else:
                print("❌ Aucun chemin d'image défini")
        else:
            print("❌ Exercice 7 non trouvé")
            
    except Exception as e:
        print(f"❌ Erreur de vérification: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    if fix_exercise_7_images():
        verify_fix()
        print("\n🎉 Correction terminée! Vous pouvez maintenant tester l'exercice 7.")
    else:
        print("\n❌ Échec de la correction.")
