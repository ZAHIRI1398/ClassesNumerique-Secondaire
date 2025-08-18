"""
Script pour intégrer le blueprint de synchronisation d'images dans app.py
"""
import re

def integrate_image_sync_blueprint():
    # Lire le contenu du fichier app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si le blueprint est déjà importé
    if 'from fix_image_paths import register_image_sync_routes' in content:
        print("Le blueprint est déjà importé dans app.py")
        return False
    
    # Ajouter l'import du blueprint après les autres imports
    import_pattern = r'(from flask import .*?\n)'
    import_statement = r'\1from fix_image_paths import register_image_sync_routes\n'
    content = re.sub(import_pattern, import_statement, content, count=1)
    
    # Trouver où initialiser le blueprint
    init_pattern = r'(if __name__ == [\'"]__main__[\'"]:\s*\n)'
    init_statement = r'# Enregistrer les routes de synchronisation d\'images\nregister_image_sync_routes(app)\n\n\1'
    content = re.sub(init_pattern, init_statement, content, count=1)
    
    # Sauvegarder les modifications
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Blueprint de synchronisation d'images intégré avec succès dans app.py")
    return True

if __name__ == "__main__":
    integrate_image_sync_blueprint()
