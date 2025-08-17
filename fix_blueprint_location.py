"""
Script pour corriger l'emplacement des fichiers blueprint en production.
Ce script déplace les fichiers blueprint au bon endroit et met à jour les imports.
"""

import os
import shutil
import sys
import re

def fix_blueprint_location():
    """Corrige l'emplacement des fichiers blueprint en production."""
    production_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                 "production_code", "ClassesNumerique-Secondaire-main")
    
    print("=== Correction de l'emplacement des fichiers blueprint ===")
    print(f"Répertoire de production: {production_dir}")
    
    # Vérifier si les fichiers blueprint existent
    blueprint_files = [
        "diagnose_select_school_route.py",
        "fix_payment_select_school.py"
    ]
    
    # 1. Créer une copie des fichiers blueprint avec imports relatifs
    for file in blueprint_files:
        source_path = os.path.join(production_dir, file)
        if os.path.isfile(source_path):
            print(f"[INFO] Fichier {file} trouvé à {source_path}")
            
            # Lire le contenu du fichier
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Créer un fichier temporaire avec imports relatifs
            temp_path = os.path.join(production_dir, f"temp_{file}")
            with open(temp_path, 'w', encoding='utf-8') as f:
                # Remplacer les imports absolus par des imports relatifs
                modified_content = content
                modified_content = re.sub(r'from models import', r'from .models import', modified_content)
                modified_content = re.sub(r'from config import', r'from .config import', modified_content)
                modified_content = re.sub(r'from utils import', r'from .utils import', modified_content)
                
                f.write(modified_content)
            
            print(f"[INFO] Fichier temporaire créé à {temp_path}")
        else:
            print(f"[ERREUR] Fichier {file} non trouvé à {source_path}")
    
    # 2. Créer un package pour les blueprints
    blueprints_dir = os.path.join(production_dir, "blueprints")
    if not os.path.exists(blueprints_dir):
        os.makedirs(blueprints_dir)
        print(f"[INFO] Répertoire blueprints créé à {blueprints_dir}")
    
    # Créer un fichier __init__.py dans le package blueprints
    init_path = os.path.join(blueprints_dir, "__init__.py")
    with open(init_path, 'w', encoding='utf-8') as f:
        f.write('"""Package pour les blueprints de l\'application."""\n')
    print(f"[INFO] Fichier __init__.py créé à {init_path}")
    
    # 3. Déplacer les fichiers temporaires vers le package blueprints
    for file in blueprint_files:
        temp_path = os.path.join(production_dir, f"temp_{file}")
        if os.path.isfile(temp_path):
            dest_path = os.path.join(blueprints_dir, file)
            shutil.copy(temp_path, dest_path)
            print(f"[INFO] Fichier {file} copié vers {dest_path}")
            
            # Supprimer le fichier temporaire
            os.remove(temp_path)
            print(f"[INFO] Fichier temporaire {temp_path} supprimé")
    
    # 4. Mettre à jour app.py pour utiliser les blueprints depuis le package
    app_py_path = os.path.join(production_dir, "app.py")
    if os.path.isfile(app_py_path):
        # Faire une sauvegarde de app.py
        backup_path = f"{app_py_path}.bak.{os.path.basename(__file__).split('.')[0]}"
        shutil.copy(app_py_path, backup_path)
        print(f"[INFO] Sauvegarde de app.py créée à {backup_path}")
        
        # Lire le contenu de app.py
        with open(app_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remplacer les imports des blueprints
        modified_content = content
        modified_content = modified_content.replace(
            "from diagnose_select_school_route import diagnose_select_school_bp",
            "from blueprints.diagnose_select_school_route import diagnose_select_school_bp"
        )
        modified_content = modified_content.replace(
            "from fix_payment_select_school import fix_payment_select_school_bp",
            "from blueprints.fix_payment_select_school import fix_payment_select_school_bp"
        )
        
        # Écrire le contenu modifié dans app.py
        with open(app_py_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        print(f"[INFO] Fichier app.py mis à jour avec les imports depuis le package blueprints")
    else:
        print(f"[ERREUR] Fichier app.py non trouvé à {app_py_path}")
    
    print("\n=== Correction terminée ===")
    print("Pour déployer la correction:")
    print("1. Exécutez: git add production_code/ClassesNumerique-Secondaire-main/app.py production_code/ClassesNumerique-Secondaire-main/blueprints/")
    print("2. Exécutez: git commit -m \"Fix: Correction de l'emplacement des blueprints\"")
    print("3. Exécutez: git push")
    print("4. Vérifiez le déploiement sur Railway")

if __name__ == "__main__":
    fix_blueprint_location()
