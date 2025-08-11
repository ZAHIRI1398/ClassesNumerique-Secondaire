#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour vérifier les types d'exercices dans le modèle
"""

from models import Exercise

def test_exercise_types():
    print("=== TEST DES TYPES D'EXERCICES ===")
    print(f"Liste des types d'exercices dans le modèle :")
    
    for i, (type_id, type_name) in enumerate(Exercise.EXERCISE_TYPES, 1):
        print(f"{i:2d}. {type_id:20s} -> {type_name}")
    
    print(f"\nTotal : {len(Exercise.EXERCISE_TYPES)} types d'exercices")
    
    # Vérifier si "Mots à placer" est présent
    word_placement_found = any(type_id == 'word_placement' for type_id, type_name in Exercise.EXERCISE_TYPES)
    print(f"\n'Mots à placer' (word_placement) trouvé : {'✅ OUI' if word_placement_found else '❌ NON'}")
    
    # Vérifier si "QCM Multichoix" est présent
    qcm_multichoix_found = any(type_id == 'qcm_multichoix' for type_id, type_name in Exercise.EXERCISE_TYPES)
    print(f"'QCM Multichoix' (qcm_multichoix) trouvé : {'✅ OUI' if qcm_multichoix_found else '❌ NON'}")

if __name__ == "__main__":
    test_exercise_types()
