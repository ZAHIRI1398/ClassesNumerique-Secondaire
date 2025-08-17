#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour corriger le problème de retour manquant dans la route d'édition d'exercice de type légende
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

def fix_legend_edit_route_return():
    """Ajoute une condition pour les exercices de type légende dans la section GET de la route edit_exercise"""
    file_path = "app.py"
    
    # Créer une sauvegarde
    if not backup_file(file_path):
        print("Impossible de créer une sauvegarde. Opération annulée.")
        return False
    
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
        
        # Trouver la section GET de la route edit_exercise
        in_edit_exercise = False
        in_get_section = False
        last_elif_line = -1
        
        for i, line in enumerate(lines):
            if "def edit_exercise(exercise_id):" in line:
                in_edit_exercise = True
            
            if in_edit_exercise and "if request.method == 'GET':" in line:
                in_get_section = True
            
            if in_get_section and "elif exercise.exercise_type ==" in line:
                last_elif_line = i
            
            if in_get_section and "elif request.method == 'POST':" in line:
                # Nous avons trouvé la fin de la section GET
                break
        
        if last_elif_line == -1:
            print("Structure de code non reconnue. Impossible de trouver la section GET ou les conditions elif.")
            return False
        
        # Chercher s'il y a déjà une condition pour les exercices de type légende
        legend_condition_exists = False
        for i in range(last_elif_line - 5, last_elif_line + 5):
            if i >= 0 and i < len(lines) and "exercise.exercise_type == 'legend'" in lines[i]:
                legend_condition_exists = True
                break
        
        if legend_condition_exists:
            print("Une condition pour les exercices de type légende existe déjà.")
        else:
            # Ajouter la condition pour les exercices de type légende après la dernière condition elif
            indent = re.match(r'^(\s*)', lines[last_elif_line]).group(1)
            legend_condition = f"{indent}elif exercise.exercise_type == 'legend':\n"
            legend_condition += f"{indent}    return render_template('exercise_types/legend_edit.html', exercise=exercise, content=content)\n"
            
            lines.insert(last_elif_line + 1, legend_condition)
            
            # Écrire le contenu modifié
            with open(file_path, "w", encoding="utf-8") as file:
                file.writelines(lines)
            
            print("[OK] La condition pour les exercices de type légende a été ajoutée à la fonction edit_exercise")
            return True
    
    except Exception as e:
        print(f"[ERREUR] Erreur lors de la modification de app.py: {e}")
        return False

if __name__ == "__main__":
    print("=== Correction du problème de retour dans la route d'édition d'exercice de type légende ===\n")
    success = fix_legend_edit_route_return()
    
    if success:
        print("\nLa correction a été appliquée avec succès.")
        print("Vous pouvez maintenant démarrer l'application avec 'python app.py'")
    else:
        print("\nLa correction a échoué. Une approche manuelle est nécessaire.")
