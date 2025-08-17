#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour corriger le problème de retour dans la route d'édition d'exercice
Ce script ajoute un return manquant à la fin de la fonction edit_exercise dans app.py
"""

import os
import sys
import re
from datetime import datetime

def backup_file(file_path):
    """Crée une sauvegarde du fichier"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.bak.{timestamp}"
    
    try:
        with open(file_path, "r", encoding="utf-8") as source:
            content = source.read()
        
        with open(backup_path, "w", encoding="utf-8") as target:
            target.write(content)
        
        print(f"Sauvegarde créée: {backup_path}")
        return True
    except Exception as e:
        print(f"Erreur lors de la création de la sauvegarde: {e}")
        return False

def fix_edit_exercise_return():
    """Ajoute un return manquant à la fin de la fonction edit_exercise"""
    file_path = "app.py"
    
    # Créer une sauvegarde
    if not backup_file(file_path):
        print("Impossible de créer une sauvegarde. Opération annulée.")
        return False
    
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        
        # Trouver la route d'édition d'exercice
        pattern = r"(@app\.route\('/exercise/(\d+)/edit', methods=\['GET', 'POST'\])\s+@login_required\s+def edit_exercise\(exercise_id\):.*?)((?=@app\.route)|$)"
        
        # Rechercher le motif dans le contenu
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            print("La route d'édition d'exercice n'a pas été trouvée dans app.py")
            return False
        
        # Extraire la route complète
        route_content = match.group(1)
        
        # Vérifier si la route se termine par un return
        if not re.search(r"return\s+[^None]", route_content.split("if request.method == 'POST':")[-1]):
            # Ajouter le return manquant à la fin de la route
            if "if exercise.exercise_type == 'legend':" in route_content:
                # Cas où il y a une condition pour les exercices de type légende
                new_route = route_content.replace(
                    "    return render_template('exercise_types/legend_edit.html', exercise=exercise)",
                    "    return render_template('exercise_types/legend_edit.html', exercise=exercise)\n"
                )
            else:
                # Cas général
                new_route = route_content + "\n    return render_template('exercise_edit.html', exercise=exercise)\n"
            
            # Remplacer l'ancienne route par la nouvelle
            new_content = content.replace(route_content, new_route)
            
            # Écrire le contenu modifié
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(new_content)
            
            print("[OK] Le return manquant a été ajouté à la fonction edit_exercise dans app.py")
            return True
        else:
            print("La fonction edit_exercise semble déjà avoir un return. Vérification plus approfondie nécessaire.")
            return False
    
    except Exception as e:
        print(f"[ERREUR] Erreur lors de la modification de app.py: {e}")
        return False

if __name__ == "__main__":
    print("=== Correction du problème de retour dans la route d'édition d'exercice ===\n")
    success = fix_edit_exercise_return()
    
    if success:
        print("\nLa correction a été appliquée avec succès.")
        print("Vous pouvez maintenant démarrer l'application avec 'python app.py'")
    else:
        print("\nLa correction a échoué. Une analyse plus approfondie est nécessaire.")
