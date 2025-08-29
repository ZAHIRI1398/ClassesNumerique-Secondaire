#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour nettoyer les fichiers de test créés pendant la correction des chemins d'upload
"""

import os

def cleanup_test_files():
    """Nettoyer les fichiers de test créés"""
    
    files_to_remove = [
        'test_new_upload_path.py',
        'test_new_exercise_creation.py',
        'fix_exercise_4_path.py',
        'fix_exercise_5_path.py',
        'cleanup_test_files.py'  # Ce script lui-même
    ]
    
    removed_count = 0
    
    print("NETTOYAGE DES FICHIERS DE TEST")
    print("=" * 40)
    
    for filename in files_to_remove:
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"Supprime: {filename}")
                removed_count += 1
            except Exception as e:
                print(f"Erreur suppression {filename}: {str(e)}")
        else:
            print(f"Non trouve: {filename}")
    
    print(f"\nFichiers supprimes: {removed_count}/{len(files_to_remove)}")
    print("Nettoyage termine!")

if __name__ == "__main__":
    cleanup_test_files()
