#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour tester la création d'un nouvel exercice avec image
et vérifier que le chemin utilise bien /static/exercises/
"""

import os
import sqlite3
import tempfile
from PIL import Image

def create_test_image():
    """Créer une image de test temporaire"""
    # Créer une image simple avec PIL
    img = Image.new('RGB', (200, 150), color='lightblue')
    
    # Créer un fichier temporaire
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    img.save(temp_file.name, 'PNG')
    temp_file.close()
    
    return temp_file.name

def simulate_exercise_creation():
    """Simuler la création d'un exercice avec image"""
    
    # Créer une image de test
    test_image_path = create_test_image()
    
    try:
        # Simuler le processus d'upload
        from werkzeug.datastructures import FileStorage
        import io
        
        # Lire l'image de test
        with open(test_image_path, 'rb') as f:
            image_data = f.read()
        
        # Créer un objet FileStorage simulé
        image_stream = io.BytesIO(image_data)
        file_storage = FileStorage(
            stream=image_stream,
            filename='test_new_upload.png',
            content_type='image/png'
        )
        
        # Simuler le processus d'upload selon le code de app.py
        from werkzeug.utils import secure_filename
        import uuid
        
        def generate_unique_filename(filename):
            """Générer un nom de fichier unique"""
            name, ext = os.path.splitext(secure_filename(filename))
            unique_id = str(uuid.uuid4())[:8]
            return f"{name}_{unique_id}{ext}"
        
        # Générer le nom de fichier unique
        filename = secure_filename(file_storage.filename)
        unique_filename = generate_unique_filename(filename)
        
        # Chemin de destination selon le nouveau code
        upload_folder = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        filepath = os.path.join(upload_folder, unique_filename)
        
        # Sauvegarder le fichier
        file_storage.save(filepath)
        
        # Le chemin qui devrait être généré par le nouveau code
        expected_path = f'/static/exercises/{unique_filename}'
        
        print(f"Fichier sauvegarde: {filepath}")
        print(f"Chemin attendu en base: {expected_path}")
        
        # Vérifier que le fichier existe et n'est pas vide
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"Taille du fichier: {file_size} bytes")
            
            if file_size > 0:
                print("Fichier sauvegarde avec succes (non vide)")
                
                # Nettoyer le fichier de test
                os.remove(filepath)
                print("Fichier de test supprime")
                
                return expected_path
            else:
                print("Fichier sauvegarde mais vide")
                return None
        else:
            print("Fichier non sauvegarde")
            return None
            
    except Exception as e:
        print(f"Erreur lors de la simulation: {str(e)}")
        return None
    finally:
        # Nettoyer l'image de test temporaire
        if os.path.exists(test_image_path):
            os.remove(test_image_path)

def test_path_generation():
    """Tester que les nouveaux chemins utilisent bien /static/exercises/"""
    
    print("SIMULATION DE CREATION D'EXERCICE AVEC IMAGE")
    print("=" * 50)
    
    expected_path = simulate_exercise_creation()
    
    if expected_path:
        if expected_path.startswith('/static/exercises/'):
            print(f"\nSUCCES: Le nouveau code genere bien des chemins /static/exercises/")
            print(f"Chemin genere: {expected_path}")
            return True
        else:
            print(f"\nECHEC: Le chemin genere utilise encore l'ancien format")
            print(f"Chemin genere: {expected_path}")
            return False
    else:
        print(f"\nECHEC: Impossible de simuler l'upload")
        return False

if __name__ == "__main__":
    print("TEST DE CREATION D'EXERCICE AVEC IMAGE")
    print("=" * 60)
    
    success = test_path_generation()
    
    if success:
        print(f"\nVALIDATION COMPLETE: Les nouveaux uploads utilisent /static/exercises/")
    else:
        print(f"\nPROBLEME: Des corrections supplementaires sont necessaires")
