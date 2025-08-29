#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test d'upload d'image sans Cloudinary
"""

import os
import sys
from PIL import Image
from io import BytesIO
from werkzeug.datastructures import FileStorage

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_upload_no_cloudinary():
    """Test l'upload d'image sans Cloudinary"""
    
    # Créer une image de test
    img = Image.new('RGB', (200, 200), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    # Créer un FileStorage simulé
    file = FileStorage(
        stream=img_bytes,
        filename='test_image.png',
        content_type='image/png'
    )
    
    print("TEST UPLOAD SANS CLOUDINARY")
    print("=" * 40)
    print(f"Fichier test: {file.filename}")
    print(f"Taille: {len(img_bytes.getvalue())} octets")
    
    # Simuler l'environnement Flask minimal
    class MockApp:
        def __init__(self):
            self.root_path = os.path.dirname(os.path.abspath(__file__))
    
    # Importer et tester le module sans Cloudinary
    try:
        import cloud_storage_no_cloudinary as cloud_storage
        
        # Simuler current_app
        import cloud_storage_no_cloudinary
        cloud_storage_no_cloudinary.current_app = MockApp()
        
        # Test d'upload
        result = cloud_storage.upload_file(file, exercise_type='qcm')
        
        print(f"\nRésultat upload: {result}")
        
        if result:
            # Vérifier que le fichier existe
            file_path = os.path.join(MockApp().root_path, 'static', 'exercises', os.path.basename(result))
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"Fichier créé: {file_path}")
                print(f"Taille sur disque: {file_size} octets")
                print("✅ SUCCÈS - Upload sans Cloudinary fonctionne")
                
                # Nettoyer le fichier de test
                os.remove(file_path)
                print("Fichier de test supprimé")
            else:
                print("❌ ÉCHEC - Fichier non trouvé sur disque")
        else:
            print("❌ ÉCHEC - Upload a retourné None")
            
    except Exception as e:
        print(f"❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_upload_no_cloudinary()
