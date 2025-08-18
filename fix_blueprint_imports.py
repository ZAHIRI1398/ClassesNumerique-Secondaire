"""
Script pour corriger les problèmes d'importation dans les blueprints sans dupliquer les modèles
"""

import os
import sys

def fix_blueprint_imports():
    """Corrige les problèmes d'importation dans les blueprints"""
    try:
        # Chemin vers le répertoire des blueprints
        blueprints_dir = os.path.join('production_code', 'ClassesNumerique-Secondaire-main', 'blueprints')
        
        # Liste des fichiers blueprint à corriger
        blueprint_files = [
            'diagnose_select_school_route.py',
            'fix_payment_select_school.py',
            'school_registration_mod.py'
        ]
        
        for file_name in blueprint_files:
            file_path = os.path.join(blueprints_dir, file_name)
            if os.path.exists(file_path):
                # Lire le contenu du fichier
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Remplacer les importations relatives par des importations absolues
                content = content.replace('from .models import', 'from models import')
                
                # Écrire le contenu modifié
                with open(file_path, 'w') as f:
                    f.write(content)
                
                print(f"[INFO] Importations corrigées dans {file_path}")
        
        # Supprimer le fichier models.py du répertoire blueprints s'il existe
        models_link = os.path.join(blueprints_dir, 'models.py')
        if os.path.exists(models_link):
            os.remove(models_link)
            print(f"[INFO] Fichier {models_link} supprimé pour éviter les duplications")
        
        print("[SUCCÈS] Problèmes d'importation corrigés sans duplication de modèles")
        return True
    except Exception as e:
        print(f"[ERREUR] Échec de la correction des importations: {str(e)}")
        return False

if __name__ == "__main__":
    fix_blueprint_imports()
