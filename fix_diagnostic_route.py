#!/usr/bin/env python3
"""
Script pour corriger la route de diagnostic en ajoutant l'import json manquant
"""

import os
import re
import sys

def fix_diagnostic_route():
    """Corrige la route de diagnostic en ajoutant l'import json manquant"""
    app_path = 'app.py'
    
    # Vérifier que le fichier existe
    if not os.path.exists(app_path):
        print(f"Erreur: {app_path} n'existe pas!")
        return False
    
    # Lire le contenu du fichier
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si la route existe
    if '@app.route(\'/diagnostic-fill-in-blanks\')' not in content:
        print("La route de diagnostic n'existe pas dans le fichier!")
        return False
    
    # Vérifier si l'import json existe déjà
    if 'import json' in content:
        # Vérifier s'il est importé seul ou avec d'autres modules
        if re.search(r'import\s+json\s*($|,|\n)', content) or re.search(r'import\s+.*?,\s*json\s*($|,|\n)', content):
            print("L'import json existe déjà!")
            
            # Vérifier s'il y a d'autres problèmes potentiels
            if 'json.loads' in content and 'json' not in content.split('def diagnostic_fill_in_blanks')[0]:
                print("ATTENTION: json est importé mais peut-être pas accessible dans la fonction diagnostic_fill_in_blanks")
                
                # Ajouter l'import dans la fonction
                modified_content = content.replace(
                    'def diagnostic_fill_in_blanks():',
                    'def diagnostic_fill_in_blanks():\n    import json'
                )
                
                # Écrire le contenu modifié
                with open(app_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                
                print(f"Import json ajouté dans la fonction diagnostic_fill_in_blanks dans {app_path}")
                return True
            
            return True
    
    # Ajouter l'import json au début du fichier
    import_line = 'import json\n'
    
    # Trouver un bon endroit pour insérer l'import
    # Chercher après les autres imports
    import_section_end = content.find("# Configuration")
    if import_section_end == -1:
        import_section_end = content.find("@app.route")
    
    if import_section_end == -1:
        # Si on ne trouve pas de bon endroit, insérer au début
        modified_content = import_line + content
    else:
        # Chercher le dernier import
        last_import_pos = 0
        for match in re.finditer(r'^import\s+.*$|^from\s+.*\s+import\s+.*$', content, re.MULTILINE):
            last_import_pos = max(last_import_pos, match.end())
        
        if last_import_pos > 0:
            # Insérer après le dernier import
            modified_content = content[:last_import_pos] + '\n' + import_line + content[last_import_pos:]
        else:
            # Insérer au début du fichier
            modified_content = import_line + content
    
    # Écrire le contenu modifié
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print(f"Import json ajouté avec succès dans {app_path}!")
    return True

if __name__ == '__main__':
    fix_diagnostic_route()
