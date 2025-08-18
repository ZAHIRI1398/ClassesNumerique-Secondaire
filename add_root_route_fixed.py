"""
Script pour ajouter une route racine (/) qui redirige vers la page de connexion
en la plaçant au bon endroit dans app.py
"""
import os
import re

def add_root_route_fixed():
    """
    Ajoute une route racine (/) qui redirige vers la page de connexion
    en la plaçant après la définition de l'application Flask
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
    if re.search(r'@app\.route\([\'\"]/[\'\"]', content):
        # Supprimer la route racine existante qui pourrait être mal placée
        content = re.sub(r'@app\.route\([\'\"]/[\'\"].*?def index\(\):.*?return redirect\(url_for\(\'login\'\)\)\n\n', '', content, flags=re.DOTALL)
    
    # Trouver un bon endroit pour ajouter la route racine
    # Chercher après la définition de l'application Flask
    app_definition = re.search(r'app = Flask\(__name__\).*?\n', content)
    
    if app_definition:
        position = app_definition.end()
        
        # Code de la route racine à ajouter
        root_route = """
@app.route('/')
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
        print("Impossible de trouver la définition de l'application Flask.")
        return False

if __name__ == "__main__":
    add_root_route_fixed()
