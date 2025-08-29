"""
Script de test pour vérifier la normalisation des chemins d'images avec structures de dossiers intermédiaires
"""
import os
import sys
from utils.image_path_handler import normalize_image_path

def test_normalize_nested_image_paths():
    """Test la fonction normalize_image_path avec différents types de chemins imbriqués"""
    test_cases = [
        # Chemins simples (référence)
        ("uploads/image.jpg", "/static/uploads/image.jpg"),
        ("image.jpg", "/static/uploads/image.jpg"),
        
        # Chemins avec sous-dossiers
        ("uploads/exercises/qcm/image.jpg", "/static/uploads/exercises/qcm/image.jpg"),
        ("exercises/qcm/image.jpg", "/static/exercises/qcm/image.jpg"),
        
        # Chemins avec /static/ et sous-dossiers
        ("/static/uploads/exercises/qcm/image.jpg", "/static/uploads/exercises/qcm/image.jpg"),
        ("/static/exercises/qcm/image.jpg", "/static/exercises/qcm/image.jpg"),
        
        # Chemins avec caractères spéciaux et sous-dossiers
        ("uploads/exercises/qcm/image test.jpg", "/static/uploads/exercises/qcm/image_test.jpg"),
        ("exercises/qcm/image-spécial.jpg", "/static/exercises/qcm/image-special.jpg"),
        
        # Cas spécifiques mentionnés dans le problème
        ("/static/uploads/exercises/qcm/imagetest_20250828_151642_CMruYw.png", 
         "/static/uploads/exercises/qcm/imagetest_20250828_151642_CMruYw.png"),
    ]
    
    print("Test de normalize_image_path avec chemins imbriqués:")
    print("-" * 80)
    
    for input_path, expected_output in test_cases:
        actual_output = normalize_image_path(input_path)
        result = "OK" if actual_output == expected_output else "FAIL"
        
        print(f"{result} Input: {input_path}")
        print(f"  Expected: {expected_output}")
        print(f"  Actual:   {actual_output}")
        print()

if __name__ == "__main__":
    test_normalize_nested_image_paths()
