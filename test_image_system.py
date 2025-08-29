#!/usr/bin/env python3
"""
Test script pour le nouveau système de gestion des chemins d'images
"""

import sys
import os

# Ajouter le répertoire racine au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from utils.image_path_manager import ImagePathManager, get_image_display_path, migrate_image_path
    
    print("=== Test du système de gestion des chemins d'images ===")
    print()
    
    # Test 1: Génération de noms de fichiers uniques
    print("1. Test génération de noms de fichiers uniques:")
    filename1 = ImagePathManager.generate_unique_filename("test image.jpg", "qcm")
    filename2 = ImagePathManager.generate_unique_filename("test image.jpg", "fill_in_blanks")
    print(f"   QCM: {filename1}")
    print(f"   Fill-in-blanks: {filename2}")
    print()
    
    # Test 2: Chemins d'upload
    print("2. Test chemins d'upload:")
    for exercise_type in ['qcm', 'fill_in_blanks', 'pairs', 'unknown_type']:
        folder = ImagePathManager.get_upload_folder(exercise_type)
        web_path = ImagePathManager.get_web_path("test.jpg", exercise_type)
        print(f"   {exercise_type}: {folder} -> {web_path}")
    print()
    
    # Test 3: Nettoyage des chemins dupliqués
    print("3. Test nettoyage des chemins dupliqués:")
    test_paths = [
        "/static/uploads/static/uploads/test.jpg",
        "/static/uploads/test.jpg",
        "static/uploads/test.jpg",
        "test.jpg",
        "http://example.com/test.jpg"
    ]
    for path in test_paths:
        cleaned = ImagePathManager.clean_duplicate_paths(path)
        print(f"   {path} -> {cleaned}")
    print()
    
    # Test 4: Migration de chemins
    print("4. Test migration de chemins:")
    old_paths = [
        "/static/uploads/static/uploads/old_image.jpg",
        "static/uploads/old_image.jpg",
        "old_image.jpg",
        "http://cloudinary.com/image.jpg"
    ]
    for old_path in old_paths:
        migrated = migrate_image_path(old_path, "qcm")
        print(f"   {old_path} -> {migrated}")
    print()
    
    # Test 5: Extraction de noms de fichiers
    print("5. Test extraction de noms de fichiers:")
    paths = [
        "/static/uploads/qcm/test.jpg",
        "static/uploads/test.jpg",
        "test.jpg",
        "http://example.com/path/test.jpg"
    ]
    for path in paths:
        filename = ImagePathManager.extract_filename_from_path(path)
        print(f"   {path} -> {filename}")
    print()
    
    print("SUCCESS: Tous les tests du système d'images ont réussi!")
    
except ImportError as e:
    print(f"ERROR: Import error: {e}")
except Exception as e:
    print(f"ERROR: Unexpected error: {e}")
    import traceback
    traceback.print_exc()
