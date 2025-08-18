"""
Script pour corriger la route racine (/) qui redirige vers la page de connexion
"""
import os
import re

def fix_root_route():
    """
    Corrige la route racine (/) pour qu'elle redirige correctement vers la page de connexion
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
    
    # Supprimer la route racine existante qui pourrait être mal configurée
    content = re.sub(r'@app\.route\([\'\"]/[\'\"].*?def index\(\):.*?return redirect\(url_for\(\'login\'\)\)\n\n', '', content, flags=re.DOTALL)
    
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
        
        print("La route racine (/) a été corrigée avec succès dans app.py.")
        return True
    else:
        print("Impossible de trouver la définition de l'application Flask.")
        return False

if __name__ == "__main__":
    fix_root_route()
