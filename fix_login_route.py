"""
Script pour déplacer la route /login avant app.run() dans app.py
"""
import os
import re

def fix_login_route():
    """
    Déplace la route /login avant app.run() dans app.py
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
    
    # Extraire la route login
    login_route_pattern = r'@app\.route\([\'\"]/login[\'\"].*?def login\(\):.*?return render_template\([\'\"](login|auth/login)\.html[\'\"](?:,\s*form=form)?\)\s*\n'
    login_route_match = re.search(login_route_pattern, content, re.DOTALL)
    
    if not login_route_match:
        # Si le pattern spécifique n'est pas trouvé, essayons un pattern plus général
        login_route_pattern = r'@app\.route\([\'\"]/login[\'\"].*?def login\(\):.*?(?=@app\.route|if __name__)'
        login_route_match = re.search(login_route_pattern, content, re.DOTALL)
    
    if login_route_match:
        login_route = login_route_match.group(0)
        
        # Supprimer la route login de son emplacement actuel
        content = content.replace(login_route, '')
        
        # Trouver un bon endroit pour ajouter la route login (avant app.run)
        app_run_pattern = r'if __name__ == [\'"]__main__[\'"]:.*?app\.run\(debug=True\)'
        app_run_match = re.search(app_run_pattern, content, re.DOTALL)
        
        if app_run_match:
            position = app_run_match.start()
            
            # Insérer la route login avant app.run
            new_content = content[:position] + login_route + '\n' + content[position:]
            
            # Écrire le contenu modifié dans le fichier
            with open(app_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            
            print("La route /login a été déplacée avec succès avant app.run() dans app.py.")
            return True
        else:
            print("Impossible de trouver l'instruction app.run() dans app.py.")
            return False
    else:
        print("Impossible de trouver la route /login dans app.py.")
        return False

if __name__ == "__main__":
    fix_login_route()
