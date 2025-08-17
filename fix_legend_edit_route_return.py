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
    """Ajoute un return manquant pour le cas GET de la route d'édition d'exercice de type légende"""
    file_path = "app.py"
    
    # Créer une sauvegarde
    if not backup_file(file_path):
        print("Impossible de créer une sauvegarde. Opération annulée.")
        return False
    
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        
        # Trouver la partie GET de la route d'édition d'exercice
        pattern = r"(if request\.method == 'GET':.+?)(elif exercise\.exercise_type == 'legend':.+?)(elif request\.method == 'POST')"
        
        # Rechercher le motif dans le contenu avec le flag DOTALL pour matcher les sauts de ligne
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            print("La structure attendue de la route d'édition d'exercice n'a pas été trouvée dans app.py")
            return False
        
        # Extraire les parties correspondantes
        get_part = match.group(1)
        legend_part = match.group(2)
        post_part = match.group(3)
        
        # Vérifier si la partie legend se termine par un return
        if not re.search(r"return\s+[^None]", legend_part):
            # Ajouter le return manquant à la fin de la partie legend
            modified_legend_part = legend_part.rstrip() + "\n            return render_template('exercise_types/legend_edit.html', exercise=exercise, content=content)\n        "
            
            # Reconstruire le contenu modifié
            new_content = content.replace(get_part + legend_part + post_part, 
                                         get_part + modified_legend_part + post_part)
            
            # Écrire le contenu modifié
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(new_content)
            
            print("[OK] Le return manquant a été ajouté à la fonction edit_exercise pour les exercices de type légende")
            return True
        else:
            print("La fonction edit_exercise pour les exercices de type légende semble déjà avoir un return.")
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
