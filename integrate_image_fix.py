"""
Script d'intégration des routes de diagnostic et correction d'images dans app.py
"""

import os
import re

def integrate_image_fix():
    """Intègre les routes de diagnostic et correction d'images dans app.py"""
    
    # Chemin vers app.py
    app_path = 'app.py'
    
    # Vérifier si le fichier existe
    if not os.path.isfile(app_path):
        print(f"Erreur: {app_path} introuvable")
        return False
    
    # Lire le contenu du fichier
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si l'intégration a déjà été faite
    if 'from fix_image_display import register_image_fix_routes' in content:
        print("Les routes de diagnostic d'images sont déjà intégrées")
        return True
    
    # Ajouter l'import en haut du fichier
    import_pattern = r'(from flask import .*?\n)'
    import_statement = r'\1from fix_image_display import register_image_fix_routes\n'
    content = re.sub(import_pattern, import_statement, content, count=1)
    
    # Trouver où ajouter l'appel à register_image_fix_routes
    # Chercher après la création de l'application Flask
    app_creation_pattern = r'(app = Flask\(.*?\).*?\n)'
    if not re.search(app_creation_pattern, content):
        print("Erreur: Impossible de trouver la création de l'application Flask")
        return False
    
    # Chercher la section d'initialisation des extensions
    init_pattern = r'(# Initialiser les extensions.*?\n)'
    if re.search(init_pattern, content):
        # Ajouter après l'initialisation des extensions
        register_call = r'\1\n# Enregistrer les routes de diagnostic et correction d\'images\nregister_image_fix_routes(app)\n'
        content = re.sub(init_pattern, register_call, content, count=1)
    else:
        # Ajouter après la création de l'application
        register_call = r'\1\n# Enregistrer les routes de diagnostic et correction d\'images\nregister_image_fix_routes(app)\n'
        content = re.sub(app_creation_pattern, register_call, content, count=1)
    
    # Sauvegarder le fichier modifié
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Routes de diagnostic d'images intégrées avec succès")
    return True

if __name__ == '__main__':
    integrate_image_fix()
