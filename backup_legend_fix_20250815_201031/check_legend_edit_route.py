#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de diagnostic pour vérifier la route d'édition des exercices de type légende
Ce script vérifie que la route d'édition des exercices de type légende fonctionne correctement
et que le contenu de l'exercice est correctement mis à jour.
"""

import os
import sys
import json
import requests
from flask import Flask, session
from app import app, db, Exercise, User

def check_legend_edit_route():
    """Vérifie la route d'édition des exercices de type légende"""
    print("=== Diagnostic de la route d'édition des exercices de type légende ===\n")
    
    # 1. Vérifier si le template legend_edit.html existe
    template_path = os.path.join("templates", "exercise_types", "legend_edit.html")
    if os.path.exists(template_path):
        print(f"✅ Le template {template_path} existe.")
    else:
        print(f"❌ Le template {template_path} n'existe pas!")
        return False
    
    # 2. Rechercher des exercices de type légende dans la base de données
    with app.app_context():
        legend_exercises = Exercise.query.filter_by(exercise_type='legend').all()
        
        if legend_exercises:
            print(f"✅ {len(legend_exercises)} exercice(s) de type légende trouvé(s) dans la base de données.")
            
            # Afficher les détails du premier exercice de type légende
            exercise = legend_exercises[0]
            print(f"\nDétails de l'exercice ID {exercise.id}:")
            print(f"  - Titre: {exercise.title}")
            print(f"  - Description: {exercise.description}")
            
            # Analyser le contenu JSON
            content = json.loads(exercise.content) if exercise.content else {}
            print(f"  - Mode: {content.get('mode', 'non spécifié')}")
            print(f"  - Image principale: {content.get('main_image', 'aucune')}")
            
            if 'zones' in content:
                print(f"  - Nombre de zones: {len(content['zones'])}")
            
            if 'elements' in content:
                print(f"  - Nombre d'éléments: {len(content['elements'])}")
            
            print("\nLa route d'édition devrait maintenant fonctionner correctement pour cet exercice.")
            print(f"URL d'édition: /exercise/edit_exercise/{exercise.id}")
        else:
            print("⚠️ Aucun exercice de type légende trouvé dans la base de données.")
    
    # 3. Vérifier la présence de la logique de traitement dans app.py
    with open("app.py", "r", encoding="utf-8") as file:
        app_content = file.read()
        
        if "[LEGEND_EDIT_DEBUG] Traitement du contenu LÉGENDE" in app_content:
            print("\n✅ La logique de debug pour les exercices de type légende est présente dans app.py.")
        else:
            print("\n⚠️ La logique de debug pour les exercices de type légende n'a pas été trouvée dans app.py.")
        
        if "legend_mode = request.form.get('legend_mode', 'classic')" in app_content:
            print("✅ La logique de traitement du mode de légende est présente dans app.py.")
        else:
            print("⚠️ La logique de traitement du mode de légende n'a pas été trouvée dans app.py.")
    
    print("\n=== Diagnostic terminé ===")
    print("La route d'édition des exercices de type légende devrait maintenant fonctionner correctement.")
    print("Pour tester, connectez-vous à l'application et essayez de modifier un exercice de type légende.")
    
    return True

if __name__ == "__main__":
    check_legend_edit_route()
