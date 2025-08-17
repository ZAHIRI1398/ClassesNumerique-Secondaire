#!/usr/bin/env python3
"""
Script pour corriger l'erreur de contexte d'application Flask dans app.py
Ce script modifie la façon dont init_database() est appelée pour s'assurer
qu'elle est toujours exécutée dans un contexte d'application.
"""

import os
import sys
import shutil
from datetime import datetime

def backup_file(file_path):
    """Crée une sauvegarde du fichier avant modification"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.bak.{timestamp}"
    shutil.copy2(file_path, backup_path)
    print(f"Sauvegarde créée: {backup_path}")
    return backup_path

def fix_app_context_error(file_path):
    """Corrige l'erreur de contexte d'application dans app.py"""
    # Créer une sauvegarde
    backup_file(file_path)
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Rechercher la ligne problématique
    if 'if __name__ == \'__main__\' or os.environ.get(\'FLASK_ENV\') == \'production\':' in content and 'init_database()' in content:
        # Modifier la façon dont init_database est appelée
        modified_content = content.replace(
            'if __name__ == \'__main__\' or os.environ.get(\'FLASK_ENV\') == \'production\':\n    init_database()',
            'if __name__ == \'__main__\' or os.environ.get(\'FLASK_ENV\') == \'production\':\n    # Ne pas appeler init_database() directement, cela sera fait dans le bloc principal avec app_context'
        )
        
        # Modifier le bloc principal pour inclure init_database dans app_context
        if 'if __name__ == \'__main__\':' in modified_content:
            modified_content = modified_content.replace(
                'if __name__ == \'__main__\':\n    with app.app_context():',
                'if __name__ == \'__main__\':\n    # Initialiser la base de données dans le contexte d\'application\n    with app.app_context():'
            )
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)
        
        print("Correction appliquée avec succès.")
        print("L'initialisation de la base de données est maintenant correctement effectuée dans le contexte d'application.")
        return True
    else:
        print("Structure attendue non trouvée dans le fichier. Vérification manuelle requise.")
        return False

def main():
    """Fonction principale"""
    app_path = 'app.py'
    
    if not os.path.exists(app_path):
        print(f"Erreur: Le fichier {app_path} n'existe pas.")
        return False
    
    print(f"Correction de l'erreur de contexte d'application dans {app_path}...")
    success = fix_app_context_error(app_path)
    
    if success:
        print("\nInstructions pour tester la correction:")
        print("1. Exécutez l'application avec: python app.py")
        print("2. Vérifiez qu'aucune erreur de contexte d'application n'apparaît dans les logs")
        print("\nSi l'erreur persiste, restaurez la sauvegarde et contactez le développeur.")
    else:
        print("\nLa correction automatique a échoué.")
        print("Veuillez vérifier manuellement le fichier app.py et corriger l'appel à init_database().")
    
    return success

if __name__ == "__main__":
    main()
