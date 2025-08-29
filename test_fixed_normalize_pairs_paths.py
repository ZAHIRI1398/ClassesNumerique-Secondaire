"""
Test complet pour la fonction normalize_pairs_exercise_content améliorée
Ce script vérifie le comportement de la fonction avec différents types de chemins d'images,
en particulier le cas problématique des chemins avec /static/uploads/general/general_
"""

import os
import json
import sys
from flask import Flask
from fixed_normalize_pairs_exercise_paths import normalize_pairs_exercise_content

# Configuration de l'application Flask pour le contexte
app = Flask(__name__)

def create_test_directory_structure():
    """Crée une structure de répertoires de test avec des fichiers factices"""
    # Créer les répertoires nécessaires
    os.makedirs('static/uploads/pairs', exist_ok=True)
    os.makedirs('static/uploads/general', exist_ok=True)
    
    # Créer des fichiers factices
    test_files = [
        'static/uploads/pairs/pairs_20250828_21.png',
        'static/uploads/general/general_20250828_21.png',
        'static/uploads/general/general_20250828_22.png',
        'static/uploads/general/image_sans_prefixe.png'
    ]
    
    for file_path in test_files:
        with open(file_path, 'w') as f:
            f.write('Test file')
    
    return test_files

def run_tests():
    """Exécute les tests sur la fonction normalize_pairs_exercise_content améliorée"""
    with app.app_context():
        print("=== Test de normalize_pairs_exercise_content améliorée ===\n")
        
        # Créer la structure de répertoires de test
        test_files = create_test_directory_structure()
        print(f"Fichiers de test créés: {test_files}\n")
        
        # Cas de test 1: Chemin problématique /static/uploads/general/general_
        test_case_1 = {
            "pairs": [
                {
                    "id": "1",
                    "left": {
                        "content": "/static/uploads/general/general_20250828_21.png",
                        "type": "image"
                    },
                    "right": {
                        "content": "Texte test",
                        "type": "text"
                    }
                }
            ]
        }
        
        print("Cas de test 1: Chemin problématique /static/uploads/general/general_")
        print(f"Avant: {json.dumps(test_case_1, indent=2)}")
        result_1 = normalize_pairs_exercise_content(test_case_1, exercise_type='pairs')
        print(f"Après: {json.dumps(result_1, indent=2)}")
        print(f"Changement détecté: {result_1 != test_case_1}")
        
        # Vérifier que le chemin a été correctement normalisé
        expected_path = "/static/uploads/pairs/pairs_20250828_21.png"
        actual_path = result_1["pairs"][0]["left"]["content"]
        print(f"Chemin attendu: {expected_path}")
        print(f"Chemin obtenu: {actual_path}")
        print(f"Test réussi: {expected_path == actual_path}\n")
        
        # Cas de test 2: Plusieurs chemins problématiques
        test_case_2 = {
            "pairs": [
                {
                    "id": "1",
                    "left": {
                        "content": "/static/uploads/general/general_20250828_21.png",
                        "type": "image"
                    },
                    "right": {
                        "content": "/static/uploads/general/general_20250828_22.png",
                        "type": "image"
                    }
                },
                {
                    "id": "2",
                    "left": {
                        "content": "Texte gauche",
                        "type": "text"
                    },
                    "right": {
                        "content": "/static/uploads/general/general_20250828_21.png",
                        "type": "image"
                    }
                }
            ]
        }
        
        print("Cas de test 2: Plusieurs chemins problématiques")
        print(f"Avant: {json.dumps(test_case_2, indent=2)}")
        result_2 = normalize_pairs_exercise_content(test_case_2, exercise_type='pairs')
        print(f"Après: {json.dumps(result_2, indent=2)}")
        print(f"Changement détecté: {result_2 != test_case_2}")
        
        # Vérifier que tous les chemins ont été correctement normalisés
        expected_paths = [
            "/static/uploads/pairs/pairs_20250828_21.png",
            "/static/uploads/pairs/pairs_20250828_22.png",
            "/static/uploads/pairs/pairs_20250828_21.png"
        ]
        
        actual_paths = [
            result_2["pairs"][0]["left"]["content"],
            result_2["pairs"][0]["right"]["content"],
            result_2["pairs"][1]["right"]["content"]
        ]
        
        all_correct = all(expected == actual for expected, actual in zip(expected_paths, actual_paths))
        print(f"Test réussi: {all_correct}\n")
        
        # Cas de test 3: Format ancien avec listes left_items et right_items
        test_case_3 = {
            "left_items": [
                {
                    "content": "/static/uploads/general/general_20250828_21.png",
                    "type": "image"
                },
                "Texte simple"
            ],
            "right_items": [
                "Texte réponse",
                "/static/uploads/general/general_20250828_22.png"
            ]
        }
        
        print("Cas de test 3: Format ancien avec listes left_items et right_items")
        print(f"Avant: {json.dumps(test_case_3, indent=2)}")
        result_3 = normalize_pairs_exercise_content(test_case_3, exercise_type='pairs')
        print(f"Après: {json.dumps(result_3, indent=2)}")
        print(f"Changement détecté: {result_3 != test_case_3}")
        
        # Vérifier que les chemins ont été correctement normalisés
        expected_left_path = "/static/uploads/pairs/pairs_20250828_21.png"
        actual_left_path = result_3["left_items"][0]["content"]
        
        expected_right_path = "/static/uploads/pairs/pairs_20250828_22.png"
        actual_right_path = result_3["right_items"][1]["content"]
        
        left_correct = expected_left_path == actual_left_path
        right_correct = isinstance(result_3["right_items"][1], dict) and result_3["right_items"][1].get("content") == expected_right_path
        
        print(f"Test chemin gauche réussi: {left_correct}")
        print(f"Test chemin droite réussi: {right_correct}\n")
        
        # Cas de test 4: Chemin sans préfixe general_
        test_case_4 = {
            "pairs": [
                {
                    "id": "1",
                    "left": {
                        "content": "/static/uploads/general/image_sans_prefixe.png",
                        "type": "image"
                    },
                    "right": {
                        "content": "Texte test",
                        "type": "text"
                    }
                }
            ]
        }
        
        print("Cas de test 4: Chemin sans préfixe general_")
        print(f"Avant: {json.dumps(test_case_4, indent=2)}")
        result_4 = normalize_pairs_exercise_content(test_case_4, exercise_type='pairs')
        print(f"Après: {json.dumps(result_4, indent=2)}")
        print(f"Changement détecté: {result_4 != test_case_4}")
        
        # Vérifier que le chemin a été correctement normalisé
        expected_path = "/static/uploads/pairs/image_sans_prefixe.png"
        actual_path = result_4["pairs"][0]["left"]["content"]
        print(f"Chemin attendu: {expected_path}")
        print(f"Chemin obtenu: {actual_path}")
        print(f"Test réussi: {expected_path == actual_path}\n")
        
        # Nettoyer les fichiers de test
        for file_path in test_files:
            try:
                os.remove(file_path)
            except:
                pass
        
        # Nettoyer les répertoires
        try:
            os.rmdir('static/uploads/pairs')
            os.rmdir('static/uploads/general')
            os.rmdir('static/uploads')
            os.rmdir('static')
        except:
            pass

if __name__ == "__main__":
    try:
        run_tests()
        print("Tests terminés avec succès!")
    except Exception as e:
        print(f"Erreur lors des tests: {str(e)}")
        sys.exit(1)
