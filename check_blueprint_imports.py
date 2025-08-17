"""
Script pour vérifier l'importation des fichiers blueprint en production.
Ce script vérifie si les fichiers diagnose_select_school_route.py et fix_payment_select_school.py
sont correctement présents dans le répertoire de production.
"""

import os
import sys

def check_blueprint_files():
    """Vérifie la présence des fichiers blueprint dans le répertoire de production."""
    production_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                 "production_code", "ClassesNumerique-Secondaire-main")
    
    print("=== Vérification des fichiers blueprint ===")
    print(f"Répertoire de production: {production_dir}")
    
    # Liste des fichiers à vérifier
    blueprint_files = [
        "diagnose_select_school_route.py",
        "fix_payment_select_school.py"
    ]
    
    all_files_present = True
    
    # Vérifier la présence de chaque fichier
    for file in blueprint_files:
        file_path = os.path.join(production_dir, file)
        if os.path.isfile(file_path):
            print(f"[OK] {file} est present")
            # Afficher les premières lignes du fichier pour vérifier son contenu
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(500)  # Lire les 500 premiers caractères
                print(f"   Début du fichier: \n   {content[:200].replace(chr(10), chr(10)+'   ')}...")
        else:
            print(f"[ERREUR] {file} est ABSENT")
            all_files_present = False
    
    # Vérifier si app.py contient les imports nécessaires
    app_py_path = os.path.join(production_dir, "app.py")
    if os.path.isfile(app_py_path):
        print("\n=== Vérification des imports dans app.py ===")
        with open(app_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Vérifier les imports
            import_diagnose = "from diagnose_select_school_route import diagnose_select_school_bp" in content
            import_fix = "from fix_payment_select_school import fix_payment_select_school_bp" in content
            
            if import_diagnose:
                print("[OK] Import de diagnose_select_school_bp trouve")
            else:
                print("[ERREUR] Import de diagnose_select_school_bp ABSENT")
            
            if import_fix:
                print("[OK] Import de fix_payment_select_school_bp trouve")
            else:
                print("[ERREUR] Import de fix_payment_select_school_bp ABSENT")
            
            # Vérifier les enregistrements de blueprint
            register_diagnose = "app.register_blueprint(diagnose_select_school_bp)" in content
            register_fix = "app.register_blueprint(fix_payment_select_school_bp)" in content
            
            if register_diagnose:
                print("[OK] Enregistrement de diagnose_select_school_bp trouve")
            else:
                print("[ERREUR] Enregistrement de diagnose_select_school_bp ABSENT")
            
            if register_fix:
                print("[OK] Enregistrement de fix_payment_select_school_bp trouve")
            else:
                print("[ERREUR] Enregistrement de fix_payment_select_school_bp ABSENT")
            
            # Vérifier l'appel à la fonction d'intégration
            integrate_call = "integrate_select_school_fix(app)" in content
            if integrate_call:
                print("[OK] Appel a integrate_select_school_fix(app) trouve")
            else:
                print("[ERREUR] Appel a integrate_select_school_fix(app) ABSENT")
    else:
        print(f"[ERREUR] app.py est ABSENT a {app_py_path}")
    
    return all_files_present

if __name__ == "__main__":
    check_blueprint_files()
