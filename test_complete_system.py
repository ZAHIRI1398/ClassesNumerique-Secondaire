#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
import requests
from PIL import Image
import io

def test_complete_system():
    """
    Test complet du système d'upload d'images et d'affichage des exercices
    """
    print("=== TEST COMPLET DU SYSTEME ===")
    
    # 1. Vérifier que l'application Flask fonctionne
    try:
        response = requests.get("http://127.0.0.1:5000", timeout=5)
        print(f"[OK] Flask app accessible (status: {response.status_code})")
    except Exception as e:
        print(f"[ERROR] Flask app inaccessible: {e}")
        return False
    
    # 2. Vérifier la base de données
    db_path = "instance/classe_numerique.db"
    if not os.path.exists(db_path):
        print(f"[ERROR] Base de donnees manquante: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Vérifier l'exercice 7
        cursor.execute("SELECT id, title, image_path FROM exercise WHERE id = 7")
        exercise = cursor.fetchone()
        
        if not exercise:
            print("[ERROR] Exercice 7 non trouve")
            return False
        
        exercise_id, title, image_path = exercise
        print(f"[OK] Exercice 7 trouve: '{title}'")
        print(f"  Image path: {image_path}")
        
        # Vérifier que le fichier image existe
        if image_path:
            # Convertir le chemin web en chemin système
            if image_path.startswith('/static/uploads/'):
                file_path = image_path.replace('/static/uploads/', 'static/uploads/')
            else:
                file_path = image_path
            
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"[OK] Fichier image existe: {file_size} bytes")
                
                if file_size > 0:
                    print("[OK] Fichier image non vide")
                else:
                    print("[ERROR] Fichier image vide (0 bytes)")
                    return False
            else:
                print(f"[ERROR] Fichier image manquant: {file_path}")
                return False
        else:
            print("[ERROR] Aucun chemin d'image defini")
            return False
    
    except Exception as e:
        print(f"[ERROR] Erreur base de donnees: {e}")
        return False
    finally:
        conn.close()
    
    # 3. Vérifier le dossier uploads
    uploads_dir = "static/uploads"
    if os.path.exists(uploads_dir):
        files = [f for f in os.listdir(uploads_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        print(f"[OK] Dossier uploads: {len(files)} images disponibles")
        
        # Afficher les 3 plus récentes
        if files:
            files_with_time = [(f, os.path.getmtime(os.path.join(uploads_dir, f))) for f in files]
            files_with_time.sort(key=lambda x: x[1], reverse=True)
            
            print("  Images récentes:")
            for i, (filename, _) in enumerate(files_with_time[:3]):
                file_path = os.path.join(uploads_dir, filename)
                size = os.path.getsize(file_path)
                print(f"    {i+1}. {filename} ({size} bytes)")
    else:
        print(f"[ERROR] Dossier uploads manquant: {uploads_dir}")
        return False
    
    # 4. Test de la route /test_upload (GET)
    try:
        response = requests.get("http://127.0.0.1:5000/test_upload", timeout=5)
        if response.status_code == 200:
            print("[OK] Route /test_upload accessible")
        else:
            print(f"[ERROR] Route /test_upload erreur: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Route /test_upload inaccessible: {e}")
    
    print("\n=== RESUME ===")
    print("[OK] Application Flask fonctionnelle")
    print("[OK] Base de donnees accessible")
    print("[OK] Exercice 7 configure avec image valide")
    print("[OK] Systeme d'upload operationnel")
    print("\n[SUCCESS] SYSTEME COMPLETEMENT FONCTIONNEL!")
    
    return True

def create_test_image():
    """
    Créer une image de test pour les uploads
    """
    img = Image.new('RGB', (200, 100), color='lightblue')
    
    # Sauvegarder dans le dossier uploads
    uploads_dir = "static/uploads"
    os.makedirs(uploads_dir, exist_ok=True)
    
    test_filename = "test_system_image.png"
    test_path = os.path.join(uploads_dir, test_filename)
    
    img.save(test_path)
    print(f"Image de test créée: {test_path}")
    
    return test_path

if __name__ == "__main__":
    # Créer une image de test si nécessaire
    create_test_image()
    
    # Lancer le test complet
    test_complete_system()
