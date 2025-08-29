#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour déterminer quel fichier app.py est utilisé par Flask
"""

import os
import sys

def check_app_files():
    """Vérifie les différents fichiers app.py et leur contenu"""
    
    root_app = r"c:\Users\JeMat\OneDrive\classenumerique20250801\app.py"
    prod_app = r"c:\Users\JeMat\OneDrive\classenumerique20250801\production_code\ClassesNumerique-Secondaire-main\app.py"
    
    print("=== VERIFICATION DES FICHIERS APP.PY ===")
    print()
    
    # Vérifier le fichier racine
    print("1. FICHIER RACINE:")
    print(f"   Chemin: {root_app}")
    if os.path.exists(root_app):
        print("   ✅ Existe")
        with open(root_app, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'test_upload' in content:
                print("   ✅ Contient la route /test_upload")
            else:
                print("   ❌ Ne contient PAS la route /test_upload")
        
        # Vérifier la dernière ligne pour voir comment Flask est démarré
        lines = content.split('\n')
        for line in reversed(lines):
            if line.strip() and not line.strip().startswith('#'):
                print(f"   Dernière ligne: {line.strip()}")
                break
    else:
        print("   ❌ N'existe pas")
    
    print()
    
    # Vérifier le fichier production
    print("2. FICHIER PRODUCTION:")
    print(f"   Chemin: {prod_app}")
    if os.path.exists(prod_app):
        print("   ✅ Existe")
        with open(prod_app, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'test_upload' in content:
                print("   ✅ Contient la route /test_upload")
            else:
                print("   ❌ Ne contient PAS la route /test_upload")
    else:
        print("   ❌ N'existe pas")
    
    print()
    print("=== RECOMMANDATION ===")
    print("Flask utilise probablement le fichier RACINE (app.py)")
    print("Si la route /test_upload n'y est pas, il faut l'ajouter.")

if __name__ == "__main__":
    check_app_files()
