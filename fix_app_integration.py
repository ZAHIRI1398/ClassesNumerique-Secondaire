import os
import re
import sys
import shutil
from datetime import datetime

def fix_app_integration(app_py_path):
    """Corrige l'intégration des blueprints dans app.py"""
    print(f"Correction de l'intégration dans {app_py_path}...")
    
    try:
        # Créer une sauvegarde
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{app_py_path}.bak.{timestamp}"
        shutil.copy2(app_py_path, backup_path)
        print(f"Sauvegarde créée: {backup_path}")
        
        # Lire le contenu du fichier
        with open(app_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier si l'intégration est déjà faite
        if "from diagnose_select_school_route import diagnose_select_school_bp" in content and \
           "from fix_payment_select_school import fix_payment_select_school_bp" in content and \
           "app.register_blueprint(diagnose_select_school_bp)" in content and \
           "app.register_blueprint(fix_payment_select_school_bp)" in content:
            print("L'intégration est déjà faite correctement.")
            return True
        
        # Ajouter les imports s'ils n'existent pas
        imports_to_add = []
        if "from diagnose_select_school_route import diagnose_select_school_bp" not in content:
            imports_to_add.append("from diagnose_select_school_route import diagnose_select_school_bp")
        if "from fix_payment_select_school import fix_payment_select_school_bp" not in content:
            imports_to_add.append("from fix_payment_select_school import fix_payment_select_school_bp")
        
        if imports_to_add:
            # Trouver la dernière ligne d'import
            import_pattern = r'^import\s+.*$|^from\s+.*\s+import\s+.*$'
            import_lines = re.finditer(import_pattern, content, re.MULTILINE)
            last_import_pos = 0
            for match in import_lines:
                last_import_pos = match.end()
            
            # Insérer les nouveaux imports après le dernier import
            new_content = content[:last_import_pos] + "\n" + "\n".join(imports_to_add) + "\n" + content[last_import_pos:]
            content = new_content
            print("Imports ajoutés.")
        
        # Ajouter l'enregistrement des blueprints s'il n'existe pas
        registers_to_add = []
        if "app.register_blueprint(diagnose_select_school_bp)" not in content:
            registers_to_add.append("app.register_blueprint(diagnose_select_school_bp)")
        if "app.register_blueprint(fix_payment_select_school_bp)" not in content:
            registers_to_add.append("app.register_blueprint(fix_payment_select_school_bp)")
        
        if registers_to_add:
            # Trouver la position avant if __name__ == '__main__'
            main_pattern = r'if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:'
            main_match = re.search(main_pattern, content)
            
            if main_match:
                main_pos = main_match.start()
                # Insérer les enregistrements avant if __name__ == '__main__'
                new_content = content[:main_pos] + "\n# Enregistrement des blueprints pour la correction select-school\n" + "\n".join(registers_to_add) + "\n\n" + content[main_pos:]
                content = new_content
                print("Enregistrements des blueprints ajoutés.")
            else:
                # Si on ne trouve pas if __name__ == '__main__', ajouter à la fin
                content += "\n\n# Enregistrement des blueprints pour la correction select-school\n" + "\n".join(registers_to_add) + "\n"
                print("Enregistrements des blueprints ajoutés à la fin du fichier.")
        
        # Écrire le contenu modifié
        with open(app_py_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Intégration corrigée avec succès!")
        return True
    
    except Exception as e:
        print(f"Erreur lors de la correction: {e}")
        return False

def main():
    if len(sys.argv) > 1:
        app_py_path = sys.argv[1]
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        app_py_path = os.path.join(base_path, "production_code", "ClassesNumerique-Secondaire-main", "app.py")
    
    print("=== Correction de l'intégration des blueprints ===")
    print()
    
    if not os.path.exists(app_py_path):
        print(f"Erreur: Le fichier {app_py_path} n'existe pas.")
        return
    
    success = fix_app_integration(app_py_path)
    
    if success:
        print()
        print("=== Correction terminée avec succès! ===")
        print()
        print("Pour déployer la correction:")
        print("1. Exécutez: git add " + app_py_path)
        print("2. Exécutez: git commit -m \"Fix: Correction de l'intégration des blueprints select-school\"")
        print("3. Exécutez: git push")
        print("4. Vérifiez le déploiement sur Railway")
    else:
        print()
        print("=== Échec de la correction ===")
        print()
        print("Veuillez corriger manuellement le fichier app.py en ajoutant:")
        print("```python")
        print("from diagnose_select_school_route import diagnose_select_school_bp")
        print("from fix_payment_select_school import fix_payment_select_school_bp")
        print("# Avant if __name__ == '__main__':")
        print("app.register_blueprint(diagnose_select_school_bp)")
        print("app.register_blueprint(fix_payment_select_school_bp)")
        print("```")

if __name__ == "__main__":
    main()
