"""
Script pour corriger les problèmes d'importation dans les blueprints
"""

import os
import sys

def fix_imports():
    """Corrige les problèmes d'importation dans les blueprints"""
    try:
        # Chemin vers le répertoire des blueprints
        blueprints_dir = os.path.join('production_code', 'ClassesNumerique-Secondaire-main', 'blueprints')
        
        # Créer un fichier __init__.py dans le répertoire blueprints s'il n'existe pas
        init_file = os.path.join(blueprints_dir, '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('# Ce fichier permet de traiter le répertoire comme un package Python\n')
            print(f"[INFO] Fichier {init_file} créé")
        
        # Créer un lien symbolique vers les modèles dans le répertoire blueprints
        models_link = os.path.join(blueprints_dir, 'models.py')
        if not os.path.exists(models_link):
            # Copier le contenu du fichier models.py dans le répertoire blueprints
            models_file = os.path.join('production_code', 'ClassesNumerique-Secondaire-main', 'models.py')
            if os.path.exists(models_file):
                with open(models_file, 'r') as src, open(models_link, 'w') as dst:
                    dst.write('# Ce fichier est une copie de models.py pour résoudre les problèmes d\'importation\n')
                    dst.write('# Il est recommandé de restructurer l\'application pour éviter cette duplication\n\n')
                    dst.write(src.read())
                print(f"[INFO] Fichier models.py copié dans {blueprints_dir}")
            else:
                print(f"[ERREUR] Le fichier {models_file} n'existe pas")
                return False
        
        print("[SUCCÈS] Problèmes d'importation corrigés")
        return True
    except Exception as e:
        print(f"[ERREUR] Échec de la correction des importations: {str(e)}")
        return False

if __name__ == "__main__":
    fix_imports()
