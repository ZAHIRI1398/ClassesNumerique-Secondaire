"""
Script pour ajouter une route racine (/) qui redirige vers la page de connexion
"""
import os
import re

def add_root_route():
    """
    Ajoute une route racine (/) qui redirige vers la page de connexion
    """
    # Chemin vers le fichier app.py
    app_path = 'app.py'
    
    # Vérifier si le fichier existe
    if not os.path.exists(app_path):
        print(f"Le fichier {app_path} n'existe pas.")
        return False
    
    # Lire le contenu du fichier
    with open(app_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Vérifier si la route racine existe déjà
    if re.search(r'@app\.route\([\'"]\/[\'"]\)', content):
        print("La route racine (/) existe déjà dans app.py.")
        return False
    
    # Trouver un bon endroit pour ajouter la route racine
    # Chercher après les imports et avant les autres routes
    import_section_end = re.search(r'(^.*?import.*?\n\n)', content, re.DOTALL)
    
    if import_section_end:
        position = import_section_end.end()
        
        # Code de la route racine à ajouter
        root_route = """@app.route('/')
def index():
    # Route racine qui redirige vers la page de connexion
    from flask import redirect, url_for
    return redirect(url_for('login'))

"""
        
        # Insérer la route racine
        new_content = content[:position] + root_route + content[position:]
        
        # Écrire le contenu modifié dans le fichier
        with open(app_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        print("La route racine (/) a été ajoutée avec succès à app.py.")
        return True
    else:
        print("Impossible de trouver un bon endroit pour ajouter la route racine.")
        return False

if __name__ == "__main__":
    add_root_route()
