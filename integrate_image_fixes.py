"""
Script d'intégration pour appliquer les correctifs d'images dans app.py
Ce script modifie app.py pour intégrer les correctifs d'images
"""

import os
import re
import sys
import shutil
import datetime

def backup_app_py():
    """
    Crée une sauvegarde de app.py avant modification
    
    Returns:
        str: Chemin du fichier de sauvegarde
    """
    # Chemin du fichier app.py
    app_py_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
    
    # Vérifier que app.py existe
    if not os.path.exists(app_py_path):
        print(f"Erreur: {app_py_path} n'existe pas")
        sys.exit(1)
    
    # Créer un nom de fichier de sauvegarde avec la date et l'heure
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(os.path.dirname(app_py_path), f'app.py.bak_{timestamp}')
    
    # Copier app.py vers le fichier de sauvegarde
    shutil.copy2(app_py_path, backup_path)
    
    print(f"Sauvegarde de app.py créée: {backup_path}")
    return backup_path

def modify_app_py():
    """
    Modifie app.py pour intégrer les correctifs d'images
    
    Returns:
        bool: True si la modification a réussi, False sinon
    """
    # Chemin du fichier app.py
    app_py_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
    
    # Lire le contenu de app.py
    with open(app_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si les imports nécessaires sont déjà présents
    imports_to_add = []
    
    if 'from utils.image_handler import handle_exercise_image' not in content:
        imports_to_add.append('from utils.image_handler import handle_exercise_image')
    
    if 'from utils.exercise_editor import process_exercise_edit' not in content:
        imports_to_add.append('from utils.exercise_editor import process_exercise_edit')
    
    if 'from apply_image_fixes import integrate_fixes_in_app' not in content:
        imports_to_add.append('from apply_image_fixes import integrate_fixes_in_app')
    
    # Ajouter les imports manquants après les autres imports
    if imports_to_add:
        import_block = '\n'.join(imports_to_add)
        # Trouver la fin du bloc d'imports
        import_pattern = r'(^import.*$|^from.*import.*$)'
        matches = list(re.finditer(import_pattern, content, re.MULTILINE))
        if matches:
            last_import = matches[-1]
            content = content[:last_import.end()] + '\n' + import_block + content[last_import.end():]
        else:
            # Si aucun import n'est trouvé, ajouter au début du fichier
            content = import_block + '\n' + content
    
    # Ajouter l'appel à integrate_fixes_in_app() avant la ligne if __name__ == '__main__':
    if 'integrate_fixes_in_app()' not in content:
        main_pattern = r'if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:'
        match = re.search(main_pattern, content)
        if match:
            integration_code = '\n# Appliquer les corrections d\'images\nintegrate_fixes_in_app()\n\n'
            content = content[:match.start()] + integration_code + content[match.start():]
        else:
            # Si if __name__ == '__main__': n'est pas trouvé, ajouter à la fin du fichier
            content += '\n\n# Appliquer les corrections d\'images\nintegrate_fixes_in_app()\n'
    
    # Écrire le contenu modifié dans app.py
    with open(app_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"app.py modifié avec succès")
    return True

def main():
    """
    Fonction principale
    """
    print("Script d'intégration des correctifs d'images")
    print("-------------------------------------------")
    
    # Créer une sauvegarde de app.py
    backup_path = backup_app_py()
    
    # Modifier app.py
    if modify_app_py():
        print("\nIntégration réussie!")
        print(f"Une sauvegarde de app.py a été créée: {backup_path}")
        print("\nPour appliquer les correctifs, redémarrez l'application Flask.")
    else:
        print("\nErreur lors de l'intégration des correctifs.")
        print(f"Vous pouvez restaurer app.py à partir de la sauvegarde: {backup_path}")

if __name__ == "__main__":
    main()
