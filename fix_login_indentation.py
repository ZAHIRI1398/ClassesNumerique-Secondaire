"""
Script pour corriger les problèmes d'indentation dans la route /login de app.py
"""
import os
import re
from datetime import datetime

def fix_login_indentation():
    """
    Corrige les problèmes d'indentation dans la route /login de app.py
    """
    # Chemin vers le fichier app.py
    app_path = 'app.py'
    
    # Vérifier si le fichier existe
    if not os.path.exists(app_path):
        print(f"Le fichier {app_path} n'existe pas.")
        return False
    
    # Créer une sauvegarde du fichier app.py
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f'app.py.bak_{timestamp}'
    with open(app_path, 'r', encoding='utf-8') as src, open(backup_path, 'w', encoding='utf-8') as dst:
        dst.write(src.read())
    print(f"Sauvegarde créée : {backup_path}")
    
    # Lire le contenu du fichier ligne par ligne
    with open(app_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Chercher la route /login et corriger l'indentation
    login_route_start = None
    login_route_end = None
    
    for i, line in enumerate(lines):
        if "@app.route('/login')" in line or '@app.route("/login")' in line:
            login_route_start = i
            break
    
    if login_route_start is None:
        print("La route /login n'a pas été trouvée dans app.py.")
        return False
    
    # Trouver la fin de la fonction login
    for i in range(login_route_start + 1, len(lines)):
        # Chercher une ligne qui commence par une définition de fonction ou de route
        # et qui n'est pas indentée (niveau 0)
        if (re.match(r'^def\s+\w+\(', lines[i]) or 
            re.match(r'^@app\.route', lines[i]) or 
            re.match(r'^@login_required', lines[i])):
            login_route_end = i
            break
    
    # Si on n'a pas trouvé la fin, prendre jusqu'à la fin du fichier
    if login_route_end is None:
        login_route_end = len(lines)
    
    # Extraire la fonction login
    login_function = lines[login_route_start:login_route_end]
    
    # Corriger l'indentation de la fonction login
    corrected_login = []
    
    # Ajouter la ligne de décorateur
    corrected_login.append(login_function[0])
    
    # Ajouter la définition de fonction sans indentation
    if len(login_function) > 1:
        corrected_login.append(login_function[1].lstrip())
    
    # Ajouter le reste de la fonction avec une indentation de 4 espaces
    for i in range(2, len(login_function)):
        # Supprimer l'indentation existante et ajouter 4 espaces
        corrected_login.append("    " + login_function[i].lstrip())
    
    # Remplacer la fonction login dans le fichier
    new_lines = lines[:login_route_start] + corrected_login + lines[login_route_end:]
    
    # Écrire le contenu modifié dans le fichier
    with open(app_path, 'w', encoding='utf-8') as file:
        file.writelines(new_lines)
    
    print("L'indentation de la route /login a été corrigée avec succès.")
    return True

if __name__ == "__main__":
    fix_login_indentation()
