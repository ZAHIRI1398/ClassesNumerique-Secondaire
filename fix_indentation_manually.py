#!/usr/bin/env python3
"""
Script pour corriger manuellement l'erreur d'indentation dans app.py
"""

import os
import shutil
from datetime import datetime

def backup_app_py():
    """Crée une sauvegarde du fichier app.py"""
    app_path = 'app.py'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{app_path}.bak.{timestamp}"
    
    try:
        shutil.copy2(app_path, backup_path)
        print(f"Sauvegarde créée: {backup_path}")
        return True
    except Exception as e:
        print(f"Erreur lors de la création de la sauvegarde: {str(e)}")
        return False

def fix_indentation_manually():
    """Corrige manuellement l'erreur d'indentation"""
    try:
        # Lire le contenu du fichier
        with open('app.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Identifier et corriger les lignes problématiques
        for i in range(len(lines)):
            if "elif exercise.exercise_type == 'fill_in_blanks':" in lines[i]:
                # Vérifier si les lignes suivantes sont correctement indentées
                if i+1 < len(lines) and not lines[i+1].startswith('        '):
                    # Corriger l'indentation des lignes suivantes
                    j = i + 1
                    while j < len(lines) and (lines[j].strip().startswith('#') or lines[j].strip() == 'pass'):
                        if lines[j].strip().startswith('#'):
                            lines[j] = '        ' + lines[j].strip() + '\n'
                        elif lines[j].strip() == 'pass':
                            lines[j] = '        pass\n'
                        j += 1
                    
                    print(f"Indentation corrigée aux lignes {i+1}-{j}")
                    break
        
        # Écrire le contenu corrigé
        with open('app.py', 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print("Correction de l'indentation terminée avec succès.")
        return True
    except Exception as e:
        print(f"Erreur lors de la correction de l'indentation: {str(e)}")
        return False

def main():
    """Fonction principale"""
    print("Correction manuelle de l'erreur d'indentation dans app.py...")
    
    # Créer une sauvegarde
    if not backup_app_py():
        print("Impossible de continuer sans créer de sauvegarde.")
        return
    
    # Corriger l'indentation
    if fix_indentation_manually():
        print("\nIMPORTANT: N'oubliez pas de redémarrer l'application Flask pour que les modifications prennent effet.")
    else:
        print("La correction de l'indentation a échoué.")

if __name__ == "__main__":
    main()
