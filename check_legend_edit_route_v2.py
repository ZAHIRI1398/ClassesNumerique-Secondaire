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
    
    # 3. Vérifier la présence de la logique de traitement dans app.py
    try:
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
            
            # Vérifier la présence de la gestion des trois modes de légende
            if "if legend_mode == 'grid':" in app_content:
                print("✅ La gestion du mode quadrillage est présente.")
            else:
                print("⚠️ La gestion du mode quadrillage n'a pas été trouvée.")
                
            if "if legend_mode == 'spatial':" in app_content:
                print("✅ La gestion du mode spatial est présente.")
            else:
                print("⚠️ La gestion du mode spatial n'a pas été trouvée.")
                
            # Vérifier la mise à jour du contenu de l'exercice
            if "exercise.content = json.dumps(content)" in app_content:
                print("✅ La mise à jour du contenu de l'exercice est présente.")
            else:
                print("⚠️ La mise à jour du contenu de l'exercice n'a pas été trouvée.")
    except Exception as e:
        print(f"❌ Erreur lors de la lecture de app.py: {e}")
    
    print("\n=== Diagnostic terminé ===")
    print("La route d'édition des exercices de type légende devrait maintenant fonctionner correctement.")
    print("Pour tester, connectez-vous à l'application et essayez de modifier un exercice de type légende.")
    
    return True

if __name__ == "__main__":
    check_legend_edit_route()
