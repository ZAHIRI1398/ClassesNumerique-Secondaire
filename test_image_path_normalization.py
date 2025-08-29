"""
Script de test pour vérifier la normalisation des chemins d'images
avec support du paramètre exercise_type
"""
import os
import sys
from utils.image_utils_no_normalize import normalize_image_path

def test_normalize_image_path_with_exercise_type():
    """Test la fonction normalize_image_path avec le paramètre exercise_type"""
    test_cases = [
        # Format: (input_path, exercise_type, expected_output)
        
        # Tests sans exercise_type (comportement par défaut)
        ("uploads/image.jpg", None, "/static/uploads/image.jpg"),
        ("image.jpg", None, "/static/uploads/image.jpg"),
        
        # Tests avec exercise_type spécifié
        ("uploads/image.jpg", "qcm", "/static/uploads/qcm/image.jpg"),
        ("image.jpg", "fill_in_blanks", "/static/uploads/fill_in_blanks/image.jpg"),
        ("image.jpg", "pairs", "/static/uploads/pairs/image.jpg"),
        ("image.jpg", "flashcards", "/static/uploads/flashcards/image.jpg"),
        
        # Tests avec chemins déjà préfixés
        ("/static/uploads/image.jpg", "qcm", "/static/uploads/qcm/image.jpg"),
        ("/static/uploads/general/image.jpg", "pairs", "/static/uploads/pairs/image.jpg"),
        
        # URLs externes (ne devraient pas être modifiées)
        ("https://example.com/image.jpg", "qcm", "https://example.com/image.jpg"),
        
        # Chemins avec espaces et caractères spéciaux
        ("uploads/image with spaces.jpg", "legend", "/static/uploads/legend/image_with_spaces.jpg"),
        
        # Cas vide
        (None, "qcm", None),
        ("", "qcm", ""),
        
        # Cas spécifique: /static/uploads/general/general_TIMESTAMP_...
        ("/static/uploads/general/general_20250828_214402_abc123.jpg", "pairs", "/static/uploads/pairs/pairs_20250828_214402_abc123.jpg"),
        ("/static/uploads/general/general_20250828_214402_abc123.jpg", None, "/static/uploads/general_20250828_214402_abc123.jpg"),
        ("/static/uploads/general/general_20250828_214402_abc123.jpg", "general", "/static/uploads/general_20250828_214402_abc123.jpg"),
        ("/static/uploads/general/general_20250828_214402_abc123.jpg", "qcm", "/static/uploads/qcm/qcm_20250828_214402_abc123.jpg"),
        ("/static/uploads/general/image_without_general_prefix.jpg", "qcm", "/static/uploads/qcm/image_without_general_prefix.jpg"),
    ]
    
    print("Test de normalize_image_path avec exercise_type:")
    print("-" * 80)
    
    for input_path, exercise_type, expected_output in test_cases:
        actual_output = normalize_image_path(input_path, exercise_type=exercise_type)
        result = "OK" if actual_output == expected_output else "FAIL"
        
        print(f"{result} Input: {input_path}, Type: {exercise_type}")
        print(f"  Expected: {expected_output}")
        print(f"  Actual:   {actual_output}")
        print()

if __name__ == "__main__":
    test_normalize_image_path_with_exercise_type()
