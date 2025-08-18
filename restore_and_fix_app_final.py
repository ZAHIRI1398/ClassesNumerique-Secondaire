"""
Script pour restaurer app.py à partir d'une sauvegarde et ajouter les routes nécessaires
"""
import os
import shutil
from datetime import datetime

def restore_and_fix_app():
    """
    Restaure app.py à partir d'une sauvegarde et ajoute les routes nécessaires
    """
    # Chemin vers le fichier app.py
    app_path = 'app.py'
    
    # Chemin vers la sauvegarde la plus ancienne
    backup_path = 'app.py.bak_20250818_105625'
    
    # Vérifier si la sauvegarde existe
    if not os.path.exists(backup_path):
        print(f"La sauvegarde {backup_path} n'existe pas.")
        return False
    
    # Créer une sauvegarde du fichier app.py actuel
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    current_backup_path = f'app.py.current_{timestamp}'
    shutil.copy2(app_path, current_backup_path)
    print(f"Sauvegarde du fichier actuel créée : {current_backup_path}")
    
    # Restaurer app.py à partir de la sauvegarde
    shutil.copy2(backup_path, app_path)
    print(f"app.py restauré à partir de {backup_path}")
    
    # Lire le contenu du fichier restauré
    with open(app_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Ajouter la route racine juste après la définition de l'application Flask
    app_definition = 'app = Flask(__name__)'
    if app_definition in content:
        position = content.find(app_definition) + len(app_definition)
        
        # Code des routes à ajouter
        routes_code = """

@app.route('/')
def index():
    # Route racine qui redirige vers la page de connexion
    return redirect('/login')

"""
        
        # Insérer les routes
        new_content = content[:position] + routes_code + content[position:]
        
        # Écrire le contenu modifié dans le fichier
        with open(app_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        print("Les routes nécessaires ont été ajoutées avec succès dans app.py.")
        return True
    else:
        print("Impossible de trouver la définition de l'application Flask.")
        return False

if __name__ == "__main__":
    restore_and_fix_app()
