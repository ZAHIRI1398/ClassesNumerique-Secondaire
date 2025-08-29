"""
Test complet pour la fonction normalize_pairs_exercise_content
Ce script vérifie le comportement de la fonction avec différents types de chemins d'images
"""

import os
import json
import sys
from flask import Flask
from normalize_pairs_exercise_paths import normalize_pairs_exercise_content

# Configuration de l'application Flask pour le contexte
app = Flask(__name__)

def create_test_directory_structure():
    """Crée une structure de répertoires de test avec des fichiers factices"""
    # Créer les répertoires nécessaires
    os.makedirs('static/uploads/pairs', exist_ok=True)
    os.makedirs('static/exercises/pairs', exist_ok=True)
    os.makedirs('static/uploads/general', exist_ok=True)
    os.makedirs('static/exercises/general', exist_ok=True)
    
    # Créer des fichiers factices
    test_files = [
        'static/uploads/pairs/test_upload_pairs.png',
        'static/exercises/pairs/test_exercise_pairs.png',
        'static/uploads/general/test_upload_general.png',
        'static/exercises/general/test_exercise_general.png'
    ]
    
    for file_path in test_files:
        with open(file_path, 'w') as f:
            f.write('Test file')
    
    return test_files

def run_tests():
    """Exécute les tests sur la fonction normalize_pairs_exercise_content"""
    with app.app_context():
        print("=== Test de normalize_pairs_exercise_content ===\n")
        
        # Créer la structure de répertoires de test
        test_files = create_test_directory_structure()
        print(f"Fichiers de test créés: {test_files}\n")
        
        # Cas de test 1: Chemin /static/exercises/ -> /static/uploads/
        test_case_1 = {
            "pairs": [
                {
                    "id": "1",
                    "left": {
                        "content": "/static/exercises/pairs/test_exercise_pairs.png",
                        "type": "image"
                    },
                    "right": {
                        "content": "Texte test",
                        "type": "text"
                    }
                }
            ]
        }
        
        print("Cas de test 1: Chemin /static/exercises/ -> /static/uploads/")
        print(f"Avant: {json.dumps(test_case_1, indent=2)}")
        result_1 = normalize_pairs_exercise_content(test_case_1)
        print(f"Après: {json.dumps(result_1, indent=2)}")
        print(f"Changement détecté: {result_1 != test_case_1}\n")
        
        # Cas de test 2: Chemin /static/uploads/ (fichier existe dans exercises)
        test_case_2 = {
            "pairs": [
                {
                    "id": "1",
                    "left": {
                        "content": "/static/uploads/pairs/test_exercise_pairs.png",
                        "type": "image"
                    },
                    "right": {
                        "content": "Texte test",
                        "type": "text"
                    }
                }
            ]
        }
        
        print("Cas de test 2: Chemin /static/uploads/ (fichier existe dans exercises)")
        print(f"Avant: {json.dumps(test_case_2, indent=2)}")
        result_2 = normalize_pairs_exercise_content(test_case_2)
        print(f"Après: {json.dumps(result_2, indent=2)}")
        print(f"Changement détecté: {result_2 != test_case_2}\n")
        
        # Cas de test 3: Chemin /static/uploads/ (fichier existe dans uploads)
        test_case_3 = {
            "pairs": [
                {
                    "id": "1",
                    "left": {
                        "content": "/static/uploads/pairs/test_upload_pairs.png",
                        "type": "image"
                    },
                    "right": {
                        "content": "Texte test",
                        "type": "text"
                    }
                }
            ]
        }
        
        print("Cas de test 3: Chemin /static/uploads/ (fichier existe dans uploads)")
        print(f"Avant: {json.dumps(test_case_3, indent=2)}")
        result_3 = normalize_pairs_exercise_content(test_case_3)
        print(f"Après: {json.dumps(result_3, indent=2)}")
        print(f"Changement détecté: {result_3 != test_case_3}\n")
        
        # Cas de test 4: Chemin inexistant
        test_case_4 = {
            "pairs": [
                {
                    "id": "1",
                    "left": {
                        "content": "/static/uploads/pairs/fichier_inexistant.png",
                        "type": "image"
                    },
                    "right": {
                        "content": "Texte test",
                        "type": "text"
                    }
                }
            ]
        }
        
        print("Cas de test 4: Chemin inexistant")
        print(f"Avant: {json.dumps(test_case_4, indent=2)}")
        result_4 = normalize_pairs_exercise_content(test_case_4)
        print(f"Après: {json.dumps(result_4, indent=2)}")
        print(f"Changement détecté: {result_4 != test_case_4}\n")
        
        # Cas de test 5: Format ancien avec listes left_items et right_items
        test_case_5 = {
            "left_items": [
                {
                    "content": "/static/exercises/general/test_exercise_general.png",
                    "type": "image"
                },
                "Texte simple"
            ],
            "right_items": [
                "Texte réponse",
                "/static/uploads/general/test_upload_general.png"
            ]
        }
        
        print("Cas de test 5: Format ancien avec listes left_items et right_items")
        print(f"Avant: {json.dumps(test_case_5, indent=2)}")
        result_5 = normalize_pairs_exercise_content(test_case_5)
        print(f"Après: {json.dumps(result_5, indent=2)}")
        print(f"Changement détecté: {result_5 != test_case_5}\n")
        
        # Nettoyer les fichiers de test
        for file_path in test_files:
            try:
                os.remove(file_path)
            except:
                pass

if __name__ == "__main__":
    try:
        run_tests()
        print("Tests terminés avec succès!")
    except Exception as e:
        print(f"Erreur lors des tests: {str(e)}")
        sys.exit(1)
