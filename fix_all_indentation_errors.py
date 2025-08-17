#!/usr/bin/env python3
"""
Script pour corriger toutes les erreurs d'indentation dans app.py
"""

import os
import shutil
from datetime import datetime
import re

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

def fix_all_indentation_errors():
    """Corrige toutes les erreurs d'indentation dans app.py"""
    try:
        # Lire le contenu du fichier
        with open('app.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Liste des lignes modifiées
        modified_lines = []
        
        # Parcourir toutes les lignes pour trouver les blocs elif sans indentation correcte
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Vérifier si c'est une ligne elif pour fill_in_blanks
            if re.match(r'\s+elif exercise\.exercise_type == \'fill_in_blanks\':', line):
                # Vérifier si les lignes suivantes sont correctement indentées
                current_indent = re.match(r'(\s+)', line).group(1)
                expected_indent = current_indent + '    '  # 4 espaces supplémentaires
                
                # Stocker la ligne actuelle
                modified_lines.append(line)
                i += 1
                
                # Vérifier les lignes suivantes
                while i < len(lines) and (lines[i].strip().startswith('#') or lines[i].strip() == 'pass'):
                    # Corriger l'indentation si nécessaire
                    if not lines[i].startswith(expected_indent):
                        # Supprimer toute indentation existante
                        stripped_line = lines[i].strip()
                        # Ajouter la bonne indentation
                        lines[i] = expected_indent + stripped_line + '\n'
                        print(f"Ligne {i+1} corrigée: {lines[i].rstrip()}")
                    
                    modified_lines.append(lines[i])
                    i += 1
            else:
                # Conserver la ligne telle quelle
                modified_lines.append(line)
                i += 1
        
        # Écrire le contenu corrigé
        with open('app.py', 'w', encoding='utf-8') as f:
            f.writelines(modified_lines)
        
        print("Correction des erreurs d'indentation terminée avec succès.")
        return True
    except Exception as e:
        print(f"Erreur lors de la correction des erreurs d'indentation: {str(e)}")
        return False

def main():
    """Fonction principale"""
    print("Correction de toutes les erreurs d'indentation dans app.py...")
    
    # Créer une sauvegarde
    if not backup_app_py():
        print("Impossible de continuer sans créer de sauvegarde.")
        return
    
    # Corriger toutes les erreurs d'indentation
    if fix_all_indentation_errors():
        print("\nIMPORTANT: N'oubliez pas de redémarrer l'application Flask pour que les modifications prennent effet.")
    else:
        print("La correction des erreurs d'indentation a échoué.")

if __name__ == "__main__":
    main()
