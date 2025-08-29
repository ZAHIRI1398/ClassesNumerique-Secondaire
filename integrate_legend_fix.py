"""
Script d'intégration de la correction pour les exercices de type légende.
Ce script ajoute le blueprint de création d'exercices de type légende à l'application Flask.
"""

import os
import sys
from flask import Flask
from legend_creation_fix import register_legend_blueprint

def integrate_legend_fix(app_file_path):
    """
    Intègre la correction pour les exercices de type légende dans l'application Flask.
    
    Args:
        app_file_path: Chemin vers le fichier app.py
    """
    # Vérifier si le fichier app.py existe
    if not os.path.exists(app_file_path):
        print(f"Erreur: Le fichier {app_file_path} n'existe pas.")
        return False
    
    # Lire le contenu du fichier app.py
    with open(app_file_path, 'r', encoding='utf-8') as file:
        app_content = file.read()
    
    # Vérifier si la correction a déjà été intégrée
    if "from legend_creation_fix import register_legend_blueprint" in app_content:
        print("La correction pour les exercices de type légende est déjà intégrée.")
        return True
    
    # Ajouter l'import du module legend_creation_fix
    import_line = "from legend_creation_fix import register_legend_blueprint"
    if "import os" in app_content:
        app_content = app_content.replace("import os", "import os\n" + import_line)
    else:
        # Ajouter l'import au début du fichier
        app_content = import_line + "\n" + app_content
    
    # Ajouter l'enregistrement du blueprint
    register_line = "    app = register_legend_blueprint(app)"
    if "def create_app(" in app_content:
        # Trouver la fonction create_app
        create_app_start = app_content.find("def create_app(")
        if create_app_start != -1:
            # Trouver la ligne où les autres blueprints sont enregistrés
            blueprint_register_pos = app_content.find("register_blueprint", create_app_start)
            if blueprint_register_pos != -1:
                # Trouver la fin de la ligne
                line_end = app_content.find("\n", blueprint_register_pos)
                if line_end != -1:
                    # Insérer notre ligne après l'enregistrement d'un autre blueprint
                    app_content = app_content[:line_end+1] + register_line + "\n" + app_content[line_end+1:]
            else:
                # Si aucun blueprint n'est trouvé, ajouter avant le return app
                return_pos = app_content.find("return app", create_app_start)
                if return_pos != -1:
                    # Insérer notre ligne avant le return app
                    app_content = app_content[:return_pos] + register_line + "\n    " + app_content[return_pos:]
    else:
        # Si create_app n'existe pas, ajouter à la fin du fichier
        app_content += "\n\n# Intégration de la correction pour les exercices de type légende\napp = register_legend_blueprint(app)\n"
    
    # Sauvegarder le fichier modifié
    with open(app_file_path, 'w', encoding='utf-8') as file:
        file.write(app_content)
    
    print(f"La correction pour les exercices de type légende a été intégrée dans {app_file_path}.")
    return True

if __name__ == "__main__":
    # Si le script est exécuté directement, utiliser le chemin par défaut
    app_path = "app.py"
    if len(sys.argv) > 1:
        app_path = sys.argv[1]
    
    success = integrate_legend_fix(app_path)
    if success:
        print("Intégration réussie!")
    else:
        print("Échec de l'intégration.")
