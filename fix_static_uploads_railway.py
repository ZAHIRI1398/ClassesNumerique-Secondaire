#!/usr/bin/env python3
"""
Script pour créer le répertoire static/uploads en production Railway
et corriger les problèmes d'affichage d'images
"""

import os
import sys
from pathlib import Path

def create_static_uploads_directory():
    """Crée le répertoire static/uploads s'il n'existe pas"""
    try:
        # Créer le répertoire static/uploads
        uploads_dir = Path('static/uploads')
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Repertoire {uploads_dir} cree avec succes")
        
        # Créer un fichier .gitkeep pour que le répertoire soit conservé dans Git
        gitkeep_file = uploads_dir / '.gitkeep'
        gitkeep_file.touch()
        
        print(f"Fichier .gitkeep cree dans {uploads_dir}")
        
        # Vérifier les permissions
        if uploads_dir.exists():
            print(f"Repertoire {uploads_dir} existe et est accessible")
            return True
        else:
            print(f"Erreur: Le repertoire {uploads_dir} n'a pas pu etre cree")
            return False
            
    except Exception as e:
        print(f"Erreur lors de la creation du repertoire: {e}")
        return False

def main():
    print("Correction des problemes d'affichage d'images Railway")
    print("=" * 60)
    
    success = create_static_uploads_directory()
    
    if success:
        print("\nSUCCES: Repertoire static/uploads cree")
        print("Les images pourront maintenant etre uploadees et affichees")
        print("Redeployez l'application pour appliquer les changements")
    else:
        print("\nECHEC: Impossible de creer le repertoire")
        sys.exit(1)

if __name__ == "__main__":
    main()
