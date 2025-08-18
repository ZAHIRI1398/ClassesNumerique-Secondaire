"""
Script pour corriger le problème d'indentation dans le bloc if __name__ == '__main__' de app.py
"""
import os
from datetime import datetime

def fix_indentation_main():
    """
    Corrige le problème d'indentation dans le bloc if __name__ == '__main__' de app.py
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
    
    # Chercher la ligne if __name__ == '__main__':
    main_line_index = None
    for i, line in enumerate(lines):
        if "if __name__ == '__main__':" in line:
            main_line_index = i
            break
    
    if main_line_index is None:
        print("Le bloc if __name__ == '__main__': n'a pas été trouvé dans app.py.")
        return False
    
    # Corriger l'indentation des lignes suivantes
    for i in range(main_line_index + 1, len(lines)):
        # Si la ligne n'est pas vide et n'est pas déjà indentée
        if lines[i].strip() and not lines[i].startswith('    '):
            lines[i] = '    ' + lines[i]
    
    # Écrire le contenu modifié dans le fichier
    with open(app_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)
    
    print("L'indentation du bloc if __name__ == '__main__': a été corrigée avec succès.")
    return True

if __name__ == "__main__":
    fix_indentation_main()
