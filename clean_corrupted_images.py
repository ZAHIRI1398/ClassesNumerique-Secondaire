import os
import sqlite3
import json
import shutil
from PIL import Image

# Script pour nettoyer toutes les images corrompues (0 octets)
def find_corrupted_images():
    """Trouve toutes les images corrompues dans le dossier uploads"""
    uploads_dir = "static/uploads"
    corrupted_files = []
    
    if not os.path.exists(uploads_dir):
        print(f"Dossier {uploads_dir} non trouvé")
        return corrupted_files
    
    print("=== SCAN DES IMAGES CORROMPUES ===")
    
    for filename in os.listdir(uploads_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            filepath = os.path.join(uploads_dir, filename)
            size = os.path.getsize(filepath)
            
            if size == 0:
                corrupted_files.append(filepath)
                print(f"CORROMPU: {filename} (0 octets)")
            else:
                # Vérifier si l'image est lisible
                try:
                    with Image.open(filepath) as img:
                        pass  # Image valide
                except Exception as e:
                    corrupted_files.append(filepath)
                    print(f"CORROMPU: {filename} ({size} octets) - {e}")
    
    print(f"\nTotal images corrompues: {len(corrupted_files)}")
    return corrupted_files

def get_valid_replacement_image():
    """Trouve une image valide à utiliser comme remplacement"""
    uploads_dir = "static/uploads"
    
    # Chercher l'image de test que nous avons créée
    test_image = os.path.join(uploads_dir, "qcm_digestive_system_test.png")
    if os.path.exists(test_image) and os.path.getsize(test_image) > 0:
        return test_image
    
    # Chercher d'autres images valides
    for filename in os.listdir(uploads_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            filepath = os.path.join(uploads_dir, filename)
            size = os.path.getsize(filepath)
            
            if size > 0:
                try:
                    with Image.open(filepath) as img:
                        print(f"Image de remplacement trouvée: {filename} ({size} octets)")
                        return filepath
                except:
                    continue
    
    return None

def clean_corrupted_images():
    """Nettoie toutes les images corrompues"""
    corrupted_files = find_corrupted_images()
    
    if not corrupted_files:
        print("Aucune image corrompue trouvée!")
        return
    
    replacement_image = get_valid_replacement_image()
    if not replacement_image:
        print("ERREUR: Aucune image valide trouvée pour le remplacement!")
        return
    
    print(f"\n=== NETTOYAGE DES IMAGES CORROMPUES ===")
    print(f"Image de remplacement: {replacement_image}")
    
    cleaned_count = 0
    for corrupted_file in corrupted_files:
        try:
            # Remplacer l'image corrompue par l'image valide
            shutil.copy2(replacement_image, corrupted_file)
            new_size = os.path.getsize(corrupted_file)
            
            if new_size > 0:
                print(f"CORRIGÉ: {os.path.basename(corrupted_file)} ({new_size} octets)")
                cleaned_count += 1
            else:
                print(f"ÉCHEC: {os.path.basename(corrupted_file)} (toujours 0 octets)")
        except Exception as e:
            print(f"ERREUR: {os.path.basename(corrupted_file)} - {e}")
    
    print(f"\n=== RÉSULTATS ===")
    print(f"Images corrompues trouvées: {len(corrupted_files)}")
    print(f"Images corrigées: {cleaned_count}")
    print(f"Échecs: {len(corrupted_files) - cleaned_count}")

def update_database_references():
    """Met à jour les références d'images dans la base de données"""
    print("\n=== MISE À JOUR BASE DE DONNÉES ===")
    
    conn = sqlite3.connect('instance/app.db')
    cursor = conn.cursor()
    
    # Récupérer tous les exercices avec des images
    cursor.execute('SELECT id, title, content, image_path FROM exercise WHERE content LIKE "%image%" OR image_path IS NOT NULL')
    exercises = cursor.fetchall()
    
    updated_count = 0
    for exercise_id, title, content_json, image_path in exercises:
        try:
            content = json.loads(content_json) if content_json else {}
            updated = False
            
            # Vérifier l'image dans le contenu JSON
            if 'image' in content:
                image_file = content['image']
                if image_file.startswith('/static/'):
                    file_path = image_file[1:]  # Enlever le / initial
                    if os.path.exists(file_path):
                        size = os.path.getsize(file_path)
                        if size > 0:
                            try:
                                with Image.open(file_path) as img:
                                    pass  # Image valide
                            except:
                                print(f"Image corrompue dans exercice {exercise_id}: {image_file}")
                        else:
                            print(f"Image vide dans exercice {exercise_id}: {image_file}")
                    else:
                        print(f"Image manquante dans exercice {exercise_id}: {image_file}")
            
            # Vérifier l'image_path
            if image_path:
                if image_path.startswith('/static/'):
                    file_path = image_path[1:]
                    if os.path.exists(file_path):
                        size = os.path.getsize(file_path)
                        if size == 0:
                            print(f"Image_path vide dans exercice {exercise_id}: {image_path}")
                    else:
                        print(f"Image_path manquante dans exercice {exercise_id}: {image_path}")
            
        except Exception as e:
            print(f"Erreur exercice {exercise_id}: {e}")
    
    conn.close()

if __name__ == "__main__":
    clean_corrupted_images()
    update_database_references()
    print("\n=== NETTOYAGE TERMINÉ ===")
    print("Actualisez votre navigateur pour voir les images corrigées.")
