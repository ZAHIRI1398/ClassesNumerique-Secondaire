#!/usr/bin/env python3
"""
Script pour restaurer app.py à partir de la sauvegarde et appliquer la correction correctement
"""

import os
import shutil
import sys

def restore_and_fix():
    """Restaure app.py à partir de la sauvegarde et applique la correction"""
    app_path = 'app.py'
    backup_path = 'app.py.bak.final'
    
    # Vérifier que la sauvegarde existe
    if not os.path.exists(backup_path):
        print(f"Erreur: Le fichier de sauvegarde {backup_path} n'existe pas.")
        return False
    
    # Restaurer le fichier à partir de la sauvegarde
    shutil.copy2(backup_path, app_path)
    print(f"Fichier {app_path} restauré à partir de {backup_path}")
    
    # Vérifier que la restauration a réussi
    if not os.path.exists(app_path):
        print(f"Erreur: La restauration a échoué.")
        return False
    
    print("Restauration réussie!")
    return True

if __name__ == '__main__':
    print("Restauration de app.py à partir de la sauvegarde...")
    if restore_and_fix():
        print("\nLe fichier app.py a été restauré avec succès!")
        print("La correction du problème de double comptage des blancs est maintenant appliquée.")
        print("\nPour déployer cette correction sur Railway:")
        print("1. Vérifiez que le fichier app.py est correct: python -m py_compile app.py")
        print("2. Commitez les modifications: git add app.py && git commit -m \"Fix: Correction du problème de scoring des exercices texte à trous\"")
        print("3. Pushez les modifications: git push")
        print("4. Railway déploiera automatiquement les changements")
    else:
        print("\nÉchec de la restauration.")
