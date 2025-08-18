"""
Script pour corriger les problèmes d'indentation dans la route login de app.py
"""
import os
import re

def fix_indentation():
    """
    Corrige les problèmes d'indentation dans la route login de app.py
    """
    # Chemin vers le fichier app.py
    app_path = 'app.py'
    
    # Vérifier si le fichier existe
    if not os.path.exists(app_path):
        print(f"Le fichier {app_path} n'existe pas.")
        return False
    
    # Lire le contenu du fichier
    with open(app_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Reconstruire le fichier avec les bonnes indentations
    new_lines = []
    in_login_route = False
    login_indent = 0
    
    for i, line in enumerate(lines):
        # Détecter le début de la route login
        if '@app.route(\'/login\'' in line:
            in_login_route = True
            new_lines.append(line)
            continue
        
        # Si nous sommes dans la route login
        if in_login_route:
            # Détecter la fin de la route login
            if line.strip() == '' and i < len(lines) - 1 and '@app.route' in lines[i+1]:
                in_login_route = False
                new_lines.append(line)
                continue
            
            # Corriger l'indentation des lignes dans la route login
            if line.strip().startswith('elif') or line.strip().startswith('else'):
                # Ces lignes doivent être au même niveau que le if précédent
                new_lines.append('    ' + line.lstrip())
            elif line.strip():
                # Garder l'indentation relative mais s'assurer qu'elle commence correctement
                indent_level = len(line) - len(line.lstrip())
                if indent_level > 4:  # Si l'indentation est plus profonde que le premier niveau
                    new_lines.append('    ' + ' ' * (indent_level - 4) + line.lstrip())
                else:
                    new_lines.append('    ' + line.lstrip())
            else:
                # Lignes vides
                new_lines.append(line)
        else:
            # Lignes en dehors de la route login
            new_lines.append(line)
    
    # Écrire le contenu corrigé dans le fichier
    with open(app_path, 'w', encoding='utf-8') as file:
        file.writelines(new_lines)
    
    print("Les problèmes d'indentation dans app.py ont été corrigés avec succès.")
    return True

if __name__ == "__main__":
    fix_indentation()
