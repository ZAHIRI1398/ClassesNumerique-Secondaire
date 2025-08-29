#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test d'upload d'image sans normalize_image_path
"""

import os
import sys
from PIL import Image
from io import BytesIO
from werkzeug.datastructures import FileStorage

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_upload_no_normalize():
    """Test l'upload d'image sans normalisation"""
    
    # Créer une image de test
    img = Image.new('RGB', (200, 200), color='blue')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    # Créer un FileStorage simulé avec nom contenant espaces et apostrophes
    file = FileStorage(
        stream=img_bytes,
        filename="Capture d'écran test 2025.png",
        content_type='image/png'
    )
    
    print("TEST UPLOAD SANS NORMALISATION")
    print("=" * 40)
    print(f"Fichier test: {file.filename}")
    print(f"Taille: {len(img_bytes.getvalue())} octets")
    
    # Simuler l'environnement Flask minimal
    class MockApp:
        def __init__(self):
            self.root_path = os.path.dirname(os.path.abspath(__file__))
    
    # Importer et tester le module sans normalisation
    try:
        import cloud_storage_no_cloudinary as cloud_storage
        
        # Simuler current_app
        import cloud_storage_no_cloudinary
        cloud_storage_no_cloudinary.current_app = MockApp()
        
        # Test d'upload
        result = cloud_storage.upload_file(file, exercise_type='qcm')
        
        print(f"\nResultat upload: {result}")
        
        if result:
            # Vérifier que le fichier existe
            file_path = os.path.join(MockApp().root_path, 'static', 'exercises', os.path.basename(result))
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"Fichier cree: {file_path}")
                print(f"Taille sur disque: {file_size} octets")
                print("SUCCES - Upload sans normalisation fonctionne")
                
                # Vérifier que le nom contient bien les espaces et apostrophes
                if "d'écran" in os.path.basename(result) and " " in os.path.basename(result):
                    print("SUCCES - Nom de fichier preserve avec espaces et apostrophes")
                else:
                    print("INFO - Nom de fichier modifie par le systeme")
                
                # Nettoyer le fichier de test
                os.remove(file_path)
                print("Fichier de test supprime")
            else:
                print("ECHEC - Fichier non trouve sur disque")
        else:
            print("ECHEC - Upload a retourne None")
            
    except Exception as e:
        print(f"ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_upload_no_normalize()
