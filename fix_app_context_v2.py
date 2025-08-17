#!/usr/bin/env python3
"""
Script pour corriger l'erreur de contexte d'application Flask dans app.py
Version 2 - Correction de l'erreur de syntaxe
"""

import os
import sys
import shutil
from datetime import datetime

def backup_file(file_path):
    """Crée une sauvegarde du fichier avant modification"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.bak.{timestamp}"
    shutil.copy2(file_path, backup_path)
    print(f"Sauvegarde créée: {backup_path}")
    return backup_path

def fix_app_context_error(file_path):
    """Corrige l'erreur de contexte d'application dans app.py"""
    # Créer une sauvegarde
    backup_file(file_path)
    
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Trouver la ligne problématique
    for i, line in enumerate(lines):
        if "if __name__ == '__main__' or os.environ.get('FLASK_ENV') == 'production':" in line:
            # Vérifier si la ligne suivante est un commentaire sans code
            if i+1 < len(lines) and lines[i+1].strip().startswith('#'):
                # Remplacer le commentaire par un appel à pass pour éviter l'erreur de syntaxe
                lines[i+1] = "    pass  # L'initialisation sera faite dans le bloc principal\n"
                
                # Écrire le fichier modifié
                with open(file_path, 'w', encoding='utf-8') as outfile:
                    outfile.writelines(lines)
                
                print("Correction de l'erreur de syntaxe appliquée avec succès.")
                return True
    
    print("Structure attendue non trouvée dans le fichier. Vérification manuelle requise.")
    return False

def main():
    """Fonction principale"""
    app_path = 'app.py'
    
    if not os.path.exists(app_path):
        print(f"Erreur: Le fichier {app_path} n'existe pas.")
        return False
    
    print(f"Correction de l'erreur de syntaxe dans {app_path}...")
    success = fix_app_context_error(app_path)
    
    if success:
        print("\nInstructions pour tester la correction:")
        print("1. Exécutez l'application avec: python app.py")
        print("2. Vérifiez qu'aucune erreur de syntaxe ou de contexte d'application n'apparaît dans les logs")
    else:
        print("\nLa correction automatique a échoué.")
        print("Veuillez vérifier manuellement le fichier app.py et corriger l'erreur de syntaxe.")
    
    return success

if __name__ == "__main__":
    main()
