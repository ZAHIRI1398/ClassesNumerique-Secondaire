"""
Script d'intégration de la correction pour la route /payment/select-school
Ce script modifie le fichier app.py pour intégrer les blueprints de diagnostic et correction
"""
import os
import sys
import re
from datetime import datetime

def integrate_select_school_fix(app_file_path):
    """
    Intègre les blueprints de diagnostic et correction dans le fichier app.py
    
    Args:
        app_file_path: Chemin vers le fichier app.py
    
    Returns:
        bool: True si l'intégration a réussi, False sinon
    """
    print(f"Intégration de la correction pour la route /payment/select-school dans {app_file_path}")
    
    # Vérifier que les fichiers nécessaires existent
    required_files = [
        'diagnose_select_school_route.py',
        'fix_payment_select_school.py',
        'integrate_select_school_fix.py',
        'templates/fix_payment_select_school.html'
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"Erreur: Le fichier {file_path} est manquant!")
            return False
    
    # Vérifier que le fichier app.py existe
    if not os.path.exists(app_file_path):
        print(f"Erreur: Le fichier {app_file_path} n'existe pas!")
        return False
    
    # Créer une sauvegarde du fichier app.py
    backup_path = f"{app_file_path}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        with open(app_file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        
        print(f"Sauvegarde créée: {backup_path}")
    except Exception as e:
        print(f"Erreur lors de la création de la sauvegarde: {str(e)}")
        return False
    
    # Ajouter les imports nécessaires
    import_pattern = re.compile(r'from flask import .*?\n', re.DOTALL)
    import_statement = """from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, abort, send_from_directory, current_app
from integrate_select_school_fix import integrate_select_school_fix
"""
    
    # Modifier le contenu du fichier app.py
    modified_content = original_content
    
    # Remplacer l'import Flask
    if import_pattern.search(modified_content):
        modified_content = import_pattern.sub(import_statement, modified_content, 1)
    else:
        print("Avertissement: Import Flask non trouvé, ajout manuel nécessaire")
        # Ajouter l'import au début du fichier
        modified_content = import_statement + modified_content
    
    # Trouver l'endroit où enregistrer les blueprints
    blueprint_pattern = re.compile(r'# Enregistrer les blueprints.*?app\.register_blueprint\(.*?\)', re.DOTALL)
    integration_code = """
# Intégration de la correction pour la route /payment/select-school
try:
    from integrate_select_school_fix import integrate_select_school_fix
    integrate_select_school_fix(app)
    print("✓ Correction de la route /payment/select-school intégrée avec succès")
except Exception as e:
    print(f"✗ Erreur lors de l'intégration de la correction pour /payment/select-school: {str(e)}")
"""
    
    # Chercher le bloc "if __name__ == '__main__':"
    main_pattern = re.compile(r'if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:', re.DOTALL)
    main_match = main_pattern.search(modified_content)
    
    if main_match:
        # Insérer le code d'intégration juste avant le bloc if __name__ == '__main__':
        insert_pos = main_match.start()
        modified_content = modified_content[:insert_pos] + integration_code + modified_content[insert_pos:]
        print("Code d'intégration ajouté avant le bloc if __name__ == '__main__':")
    else:
        # Si le bloc if __name__ == '__main__': n'est pas trouvé, ajouter à la fin du fichier
        modified_content += "\n" + integration_code
        print("Code d'intégration ajouté à la fin du fichier")
    
    # Écrire le contenu modifié dans le fichier app.py
    try:
        with open(app_file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        print(f"Fichier {app_file_path} modifié avec succès")
    except Exception as e:
        print(f"Erreur lors de la modification du fichier: {str(e)}")
        # Restaurer la sauvegarde
        with open(backup_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        with open(app_file_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"Restauration de la sauvegarde effectuée")
        return False
    
    print("\nIntégration terminée avec succès!")
    print("Pour vérifier l'intégration:")
    print("1. Redémarrez l'application Flask")
    print("2. Accédez à la route /diagnose/select-school-route pour le diagnostic")
    print("3. Accédez à la route /fix-payment/select-school pour tester la version corrigée")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        app_path = sys.argv[1]
    else:
        app_path = "app.py"  # Chemin par défaut
    
    integrate_select_school_fix(app_path)
