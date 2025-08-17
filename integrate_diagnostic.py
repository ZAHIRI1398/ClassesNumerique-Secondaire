import os
import sys
import shutil
from datetime import datetime

def backup_app_file():
    """Crée une sauvegarde du fichier app.py"""
    app_path = "app.py"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"app.py.bak.{timestamp}"
    
    try:
        shutil.copy2(app_path, backup_path)
        print(f"Sauvegarde créée: {backup_path}")
        return True
    except Exception as e:
        print(f"Erreur lors de la création de la sauvegarde: {str(e)}")
        return False

def integrate_diagnostic_blueprint():
    """Intègre le blueprint de diagnostic dans app.py"""
    app_path = "app.py"
    
    try:
        # Lire le contenu du fichier app.py
        with open(app_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Vérifier si le blueprint est déjà importé
        if "from diagnostic_school_choice import diagnostic_bp" in content:
            print("Le blueprint de diagnostic est déjà importé.")
            return False
        
        # Trouver l'endroit où ajouter l'import
        import_section = content.find("# Import des blueprints")
        if import_section == -1:
            # Chercher une autre section d'import
            import_section = content.find("from admin_routes import admin_bp")
            if import_section == -1:
                print("Impossible de trouver l'endroit où ajouter l'import.")
                return False
        
        # Trouver la fin de la section d'import
        end_of_imports = content.find("\n\n", import_section)
        if end_of_imports == -1:
            end_of_imports = content.find("\n# ", import_section)
            if end_of_imports == -1:
                print("Impossible de trouver la fin de la section d'import.")
                return False
        
        # Ajouter l'import du blueprint
        new_import = "\nfrom diagnostic_school_choice import diagnostic_bp"
        content = content[:end_of_imports] + new_import + content[end_of_imports:]
        
        # Trouver l'endroit où enregistrer le blueprint
        register_section = content.find("app.register_blueprint(admin_bp)")
        if register_section == -1:
            register_section = content.find("app.register_blueprint")
            if register_section == -1:
                print("Impossible de trouver l'endroit où enregistrer le blueprint.")
                return False
        
        # Trouver la fin de la section d'enregistrement
        end_of_register = content.find("\n\n", register_section)
        if end_of_register == -1:
            end_of_register = content.find("\n# ", register_section)
            if end_of_register == -1:
                # Chercher la ligne suivante
                end_of_register = content.find("\n", register_section)
                if end_of_register == -1:
                    print("Impossible de trouver la fin de la section d'enregistrement.")
                    return False
        
        # Ajouter l'enregistrement du blueprint
        new_register = "\napp.register_blueprint(diagnostic_bp)"
        content = content[:end_of_register] + new_register + content[end_of_register:]
        
        # Écrire le contenu modifié dans le fichier
        with open(app_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        print("Blueprint de diagnostic intégré avec succès dans app.py")
        return True
    
    except Exception as e:
        print(f"Erreur lors de l'intégration du blueprint: {str(e)}")
        return False

def main():
    """Fonction principale"""
    print("=== INTÉGRATION DU DIAGNOSTIC DE CHOIX D'ÉCOLE ===")
    
    # Vérifier que les fichiers nécessaires existent
    if not os.path.exists("app.py"):
        print("Erreur: Le fichier app.py n'existe pas dans le répertoire courant.")
        return
    
    if not os.path.exists("diagnostic_school_choice.py"):
        print("Erreur: Le fichier diagnostic_school_choice.py n'existe pas dans le répertoire courant.")
        return
    
    # Créer une sauvegarde
    if not backup_app_file():
        print("Abandon de l'intégration en raison d'une erreur de sauvegarde.")
        return
    
    # Intégrer le blueprint
    if integrate_diagnostic_blueprint():
        print("\nIntégration réussie!")
        print("Vous pouvez maintenant accéder à /diagnostic/school-choice pour diagnostiquer le problème de choix d'école.")
        print("Note: Cette route est protégée et nécessite des droits d'administrateur.")
    else:
        print("\nL'intégration a échoué. Veuillez vérifier les erreurs ci-dessus.")

if __name__ == "__main__":
    main()
