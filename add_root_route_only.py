"""
Script pour ajouter uniquement la route racine (/) dans app.py
"""
import os
import re
from datetime import datetime

def add_root_route_only():
    """
    Ajoute uniquement la route racine (/) dans app.py
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
    
    # Lire le contenu du fichier
    with open(app_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Vérifier si la route racine existe déjà
    if "@app.route('/')" in content or '@app.route("/")' in content:
        print("La route racine (/) existe déjà dans app.py.")
        # Supprimer la route racine existante
        content = re.sub(r'@app\.route\([\'\"]/[\'\"].*?def index\(\):.*?return redirect\(.*?\)\n', '', content, flags=re.DOTALL)
        print("La route racine existante a été supprimée.")
    
    # Trouver un bon endroit pour ajouter la route racine
    # Chercher après la définition de l'application Flask
    app_definition = re.search(r'app = Flask\(__name__\).*?\n', content)
    
    if app_definition:
        position = app_definition.end()
        
        # Code de la route racine à ajouter avec la bonne redirection
        root_route = """
@app.route('/')
def index():
    # Route racine qui redirige vers la page de connexion
    return redirect('/login')

"""
        
        # Insérer la route racine
        new_content = content[:position] + root_route + content[position:]
        
        # Écrire le contenu modifié dans le fichier
        with open(app_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        print("La route racine (/) a été ajoutée avec succès dans app.py.")
        return True
    else:
        print("Impossible de trouver la définition de l'application Flask.")
        return False

if __name__ == "__main__":
    add_root_route_only()
