#!/usr/bin/env python3
"""
Script pour vérifier et créer le dossier static/uploads/ en production
"""

import os
import sys

def check_and_create_uploads_folder():
    """Vérifier et créer le dossier uploads si nécessaire"""
    
    print("=== VERIFICATION DOSSIER UPLOADS ===")
    
    # Chemins à vérifier
    static_dir = "static"
    uploads_dir = os.path.join(static_dir, "uploads")
    
    print(f"Répertoire de travail actuel: {os.getcwd()}")
    print(f"Vérification du dossier: {uploads_dir}")
    
    # Vérifier si le dossier static existe
    if not os.path.exists(static_dir):
        print(f"PROBLEME: Le dossier {static_dir} n'existe pas !")
        print("Creation du dossier static...")
        try:
            os.makedirs(static_dir)
            print(f"OK Dossier {static_dir} cree avec succes")
        except Exception as e:
            print(f"ERREUR lors de la creation de {static_dir}: {e}")
            return False
    else:
        print(f"OK Dossier {static_dir} existe")
    
    # Vérifier si le dossier uploads existe
    if not os.path.exists(uploads_dir):
        print(f"PROBLEME: Le dossier {uploads_dir} n'existe pas !")
        print("Creation du dossier uploads...")
        try:
            os.makedirs(uploads_dir, exist_ok=True)
            print(f"OK Dossier {uploads_dir} cree avec succes")
            
            # Créer un fichier .gitkeep pour s'assurer que le dossier est versionné
            gitkeep_path = os.path.join(uploads_dir, ".gitkeep")
            with open(gitkeep_path, 'w') as f:
                f.write("# Ce fichier garantit que le dossier uploads est versionne dans Git\n")
            print(f"OK Fichier .gitkeep cree: {gitkeep_path}")
            
        except Exception as e:
            print(f"ERREUR lors de la creation de {uploads_dir}: {e}")
            return False
    else:
        print(f"OK Dossier {uploads_dir} existe deja")
    
    # Vérifier les permissions
    try:
        test_file = os.path.join(uploads_dir, "test_write.txt")
        with open(test_file, 'w') as f:
            f.write("Test d'écriture")
        
        # Lire le fichier
        with open(test_file, 'r') as f:
            content = f.read()
        
        # Supprimer le fichier de test
        os.remove(test_file)
        
        print(f"OK Permissions d'ecriture OK dans {uploads_dir}")
        
    except Exception as e:
        print(f"ERREUR Probleme de permissions dans {uploads_dir}: {e}")
        return False
    
    # Lister le contenu du dossier
    try:
        files = os.listdir(uploads_dir)
        print(f"Contenu du dossier uploads ({len(files)} fichiers):")
        for file in files[:10]:  # Afficher max 10 fichiers
            file_path = os.path.join(uploads_dir, file)
            size = os.path.getsize(file_path) if os.path.isfile(file_path) else 0
            print(f"  - {file} ({size} bytes)")
        
        if len(files) > 10:
            print(f"  ... et {len(files) - 10} autres fichiers")
            
    except Exception as e:
        print(f"ERREUR lors de la lecture du dossier: {e}")
    
    print("\n=== RÉSULTAT ===")
    print("OK Dossier uploads verifie et pret pour les images")
    return True

if __name__ == "__main__":
    success = check_and_create_uploads_folder()
    if success:
        print("SUCCES: Le dossier uploads est operationnel")
        sys.exit(0)
    else:
        print("ECHEC: Probleme avec le dossier uploads")
        sys.exit(1)
