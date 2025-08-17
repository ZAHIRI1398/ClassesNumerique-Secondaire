import os
import re
import sys
import requests
from urllib.parse import urljoin

def check_app_py_integration(app_py_path):
    """Vérifie si les blueprints sont correctement intégrés dans app.py"""
    print(f"Vérification de l'intégration dans {app_py_path}...")
    
    try:
        with open(app_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier les imports
        has_diagnose_import = "from diagnose_select_school_route import diagnose_select_school_bp" in content
        has_fix_import = "from fix_payment_select_school import fix_payment_select_school_bp" in content
        has_integrate_import = "from integrate_select_school_fix import integrate_select_school_fix" in content
        
        # Vérifier l'enregistrement des blueprints
        has_diagnose_register = "app.register_blueprint(diagnose_select_school_bp)" in content
        has_fix_register = "app.register_blueprint(fix_payment_select_school_bp)" in content
        has_integrate_call = "integrate_select_school_fix(app)" in content
        
        print(f"Import diagnose_select_school_bp: {'OK' if has_diagnose_import else 'NON TROUVE'}")
        print(f"Import fix_payment_select_school_bp: {'OK' if has_fix_import else 'NON TROUVE'}")
        print(f"Import integrate_select_school_fix: {'OK' if has_integrate_import else 'NON TROUVE'}")
        print(f"Enregistrement diagnose_select_school_bp: {'OK' if has_diagnose_register else 'NON TROUVE'}")
        print(f"Enregistrement fix_payment_select_school_bp: {'OK' if has_fix_register else 'NON TROUVE'}")
        print(f"Appel integrate_select_school_fix: {'OK' if has_integrate_call else 'NON TROUVE'}")
        
        return has_diagnose_import and has_fix_import and (has_diagnose_register and has_fix_register or has_integrate_call)
    
    except Exception as e:
        print(f"Erreur lors de la vérification de {app_py_path}: {e}")
        return False

def check_blueprint_files(base_path):
    """Vérifie si les fichiers de blueprint existent"""
    print(f"Vérification des fichiers de blueprint dans {base_path}...")
    
    diagnose_path = os.path.join(base_path, "diagnose_select_school_route.py")
    fix_path = os.path.join(base_path, "fix_payment_select_school.py")
    integrate_path = os.path.join(base_path, "integrate_select_school_fix.py")
    
    has_diagnose = os.path.exists(diagnose_path)
    has_fix = os.path.exists(fix_path)
    has_integrate = os.path.exists(integrate_path)
    
    print(f"diagnose_select_school_route.py: {'OK' if has_diagnose else 'NON TROUVE'}")
    print(f"fix_payment_select_school.py: {'OK' if has_fix else 'NON TROUVE'}")
    print(f"integrate_select_school_fix.py: {'OK' if has_integrate else 'NON TROUVE'}")
    
    return has_diagnose and has_fix and has_integrate

def check_template_files(base_path):
    """Vérifie si les fichiers de template existent"""
    print(f"Vérification des fichiers de template dans {base_path}...")
    
    template_path = os.path.join(base_path, "templates", "payment", "fix_payment_select_school.html")
    has_template = os.path.exists(template_path)
    
    print(f"templates/payment/fix_payment_select_school.html: {'OK' if has_template else 'NON TROUVE'}")
    
    return has_template

def check_production_routes(base_url):
    """Vérifie si les routes sont accessibles en production"""
    print(f"Vérification des routes en production sur {base_url}...")
    
    diagnose_url = urljoin(base_url, "/diagnose/select-school-route")
    fix_url = urljoin(base_url, "/fix-payment/select-school")
    
    try:
        diagnose_response = requests.get(diagnose_url)
        diagnose_ok = diagnose_response.status_code == 200
    except:
        diagnose_ok = False
    
    try:
        fix_response = requests.get(fix_url)
        fix_ok = fix_response.status_code == 200
    except:
        fix_ok = False
    
    print(f"Route /diagnose/select-school-route: {'OK' if diagnose_ok else 'NON ACCESSIBLE'}")
    print(f"Route /fix-payment/select-school: {'OK' if fix_ok else 'NON ACCESSIBLE'}")
    
    return diagnose_ok and fix_ok

def fix_integration_issues(app_py_path):
    """Tente de corriger les problèmes d'intégration dans app.py"""
    print(f"Tentative de correction de l'intégration dans {app_py_path}...")
    
    try:
        with open(app_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Créer une sauvegarde
        backup_path = f"{app_py_path}.bak.{os.path.basename(os.path.dirname(app_py_path))}"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
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
            else:
                # Si on ne trouve pas if __name__ == '__main__', ajouter à la fin
                content += "\n\n# Enregistrement des blueprints pour la correction select-school\n" + "\n".join(registers_to_add) + "\n"
        
        # Écrire le contenu modifié
        with open(app_py_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Intégration corrigée dans {app_py_path}")
        print(f"Sauvegarde créée: {backup_path}")
        return True
    
    except Exception as e:
        print(f"Erreur lors de la correction de {app_py_path}: {e}")
        return False

def main():
    base_path = os.path.dirname(os.path.abspath(__file__))
    production_path = os.path.join(base_path, "production_code", "ClassesNumerique-Secondaire-main")
    app_py_path = os.path.join(production_path, "app.py")
    
    print("=== Vérification de l'intégration des blueprints ===")
    print()
    
    # Vérifier les fichiers
    files_ok = check_blueprint_files(production_path)
    print()
    
    # Vérifier les templates
    templates_ok = check_template_files(production_path)
    print()
    
    # Vérifier l'intégration dans app.py
    integration_ok = check_app_py_integration(app_py_path)
    print()
    
    if not files_ok:
        print("ERREUR: Les fichiers de blueprint sont manquants.")
        print("Solution: Copiez les fichiers diagnose_select_school_route.py, fix_payment_select_school.py et integrate_select_school_fix.py vers le répertoire de production.")
    
    if not templates_ok:
        print("ERREUR: Les fichiers de template sont manquants.")
        print("Solution: Copiez le fichier fix_payment_select_school.html vers le répertoire templates/payment/ de production.")
    
    if not integration_ok:
        print("ERREUR: L'intégration dans app.py est incorrecte.")
        
        fix = input("Voulez-vous tenter de corriger automatiquement l'intégration? (o/n): ")
        if fix.lower() == 'o':
            fixed = fix_integration_issues(app_py_path)
            if fixed:
                print("SUCCES: Intégration corrigée. Veuillez redéployer l'application.")
            else:
                print("ERREUR: Échec de la correction automatique.")
                print("Solution manuelle: Ajoutez les imports et enregistrements des blueprints dans app.py:")
                print("```python")
                print("from diagnose_select_school_route import diagnose_select_school_bp")
                print("from fix_payment_select_school import fix_payment_select_school_bp")
                print("# Avant if __name__ == '__main__':")
                print("app.register_blueprint(diagnose_select_school_bp)")
                print("app.register_blueprint(fix_payment_select_school_bp)")
                print("```")
        else:
            print("Solution manuelle: Ajoutez les imports et enregistrements des blueprints dans app.py:")
            print("```python")
            print("from diagnose_select_school_route import diagnose_select_school_bp")
            print("from fix_payment_select_school import fix_payment_select_school_bp")
            print("# Avant if __name__ == '__main__':")
            print("app.register_blueprint(diagnose_select_school_bp)")
            print("app.register_blueprint(fix_payment_select_school_bp)")
            print("```")
    
    if files_ok and templates_ok and integration_ok:
        print("SUCCES: Tous les fichiers et l'intégration semblent corrects.")
        print("Si les routes ne sont toujours pas accessibles, vérifiez que l'application a bien été redémarrée après le déploiement.")
        
        check_prod = input("Voulez-vous vérifier les routes en production? (o/n): ")
        if check_prod.lower() == 'o':
            base_url = input("Entrez l'URL de base de l'application (ex: https://classesnumeriques.be): ")
            check_production_routes(base_url)
    
    print()
    print("=== Fin de la vérification ===")

if __name__ == "__main__":
    main()
