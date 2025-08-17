import os
import re
import shutil
import datetime

def backup_file(file_path):
    """Crée une sauvegarde du fichier avec un timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.bak.{timestamp}"
    shutil.copy2(file_path, backup_path)
    print(f"Sauvegarde créée: {backup_path}")
    return backup_path

def fix_indentation(file_path):
    """Corrige l'indentation dans le fichier app.py."""
    # Créer une sauvegarde
    backup_path = backup_file(file_path)
    
    # Lire le contenu du fichier
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Corriger l'indentation du bloc fill_in_blanks
    # Rechercher le bloc avec une indentation incorrecte et le corriger
    pattern = r'(\n\s{8})elif exercise\.exercise_type == \'fill_in_blanks\':(.*?)(\n\s{8})# Créer une nouvelle tentative'
    replacement = r'\n    elif exercise.exercise_type == \'fill_in_blanks\':\2\n    # Créer une nouvelle tentative'
    
    # Utiliser re.DOTALL pour que le point corresponde également aux sauts de ligne
    corrected_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Écrire le contenu corrigé dans le fichier
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(corrected_content)
    
    print(f"Indentation corrigée dans {file_path}")
    return True

if __name__ == "__main__":
    app_path = "app.py"
    if os.path.exists(app_path):
        fix_indentation(app_path)
        print("Correction terminée. Veuillez redémarrer l'application.")
    else:
        print(f"Erreur: Le fichier {app_path} n'existe pas.")
