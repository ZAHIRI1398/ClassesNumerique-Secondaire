#!/usr/bin/env python3
"""
Script pour télécharger directement la version fonctionnelle de production depuis GitHub
"""
import os
import requests
import zipfile
import shutil
import sys
from datetime import datetime

def create_backup(backup_dir="backup_avant_recuperation"):
    """Crée une sauvegarde des fichiers importants"""
    print(f"[INFO] Création d'une sauvegarde des fichiers importants...")
    
    # Créer le dossier de sauvegarde avec horodatage
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"{backup_dir}_{timestamp}"
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Liste des fichiers importants à sauvegarder
    important_files = ["app.py", "config.py", "models.py", "modified_submit.py"]
    
    for file in important_files:
        if os.path.exists(file):
            print(f"  - Sauvegarde de {file}")
            shutil.copy2(file, os.path.join(backup_dir, file))
    
    print(f"[OK] Sauvegarde créée dans le dossier: {backup_dir}")
    return backup_dir

def download_production_code(repo="ZAHIRI1398/ClassesNumerique-Secondaire", branch="main"):
    """Télécharge le code de production depuis GitHub"""
    print(f"[INFO] Téléchargement du code de production depuis GitHub...")
    
    # URL de l'archive ZIP du dépôt
    zip_url = f"https://github.com/{repo}/archive/refs/heads/{branch}.zip"
    zip_file = "production_code.zip"
    
    try:
        # Télécharger l'archive
        print(f"  - Téléchargement depuis {zip_url}")
        response = requests.get(zip_url, stream=True)
        response.raise_for_status()
        
        with open(zip_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"[OK] Code téléchargé avec succès: {zip_file}")
        return zip_file
    
    except requests.exceptions.RequestException as e:
        print(f"[ERREUR] Échec du téléchargement: {e}")
        return None

def extract_production_code(zip_file, extract_dir="production_code"):
    """Extrait l'archive ZIP téléchargée"""
    print(f"[INFO] Extraction du code de production...")
    
    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir)
    
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Trouver le dossier racine dans l'archive (généralement repo-branch)
        root_dir = None
        for item in os.listdir(extract_dir):
            if os.path.isdir(os.path.join(extract_dir, item)):
                root_dir = os.path.join(extract_dir, item)
                break
        
        print(f"[OK] Code extrait dans: {root_dir}")
        return root_dir
    
    except zipfile.BadZipFile as e:
        print(f"[ERREUR] Échec de l'extraction: {e}")
        return None

def copy_production_files(source_dir, target_files=None):
    """Copie les fichiers de production vers le répertoire de travail"""
    print(f"[INFO] Copie des fichiers de production vers le répertoire de travail...")
    
    if target_files is None:
        target_files = ["app.py", "config.py", "models.py", "modified_submit.py"]
    
    for file in target_files:
        source_file = os.path.join(source_dir, file)
        if os.path.exists(source_file):
            print(f"  - Copie de {file}")
            shutil.copy2(source_file, file)
        else:
            print(f"  - [AVERTISSEMENT] Fichier non trouvé: {source_file}")
    
    print(f"[OK] Fichiers de production copiés avec succès")
    return True

def cleanup(zip_file, extract_dir):
    """Nettoie les fichiers temporaires"""
    print(f"[INFO] Nettoyage des fichiers temporaires...")
    
    if os.path.exists(zip_file):
        os.remove(zip_file)
    
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    
    print(f"[OK] Nettoyage terminé")

def main():
    """Fonction principale"""
    print("=" * 60)
    print("RÉCUPÉRATION DE LA VERSION FONCTIONNELLE DE PRODUCTION")
    print("=" * 60)
    
    # 1. Créer une sauvegarde
    backup_dir = create_backup()
    
    # 2. Télécharger le code de production
    zip_file = download_production_code()
    if not zip_file:
        print("[ERREUR] Impossible de continuer sans le code de production. Abandon.")
        return False
    
    # 3. Extraire l'archive
    extract_dir = "production_code"
    source_dir = extract_production_code(zip_file, extract_dir)
    if not source_dir:
        print("[ERREUR] Impossible d'extraire le code de production. Abandon.")
        return False
    
    # 4. Copier les fichiers de production
    success = copy_production_files(source_dir)
    if not success:
        print("[ERREUR] Échec de la copie des fichiers de production. Abandon.")
        return False
    
    # 5. Nettoyer les fichiers temporaires
    cleanup(zip_file, extract_dir)
    
    print("\n" + "=" * 60)
    print("[SUCCÈS] Version fonctionnelle de production récupérée avec succès!")
    print(f"[INFO] Une sauvegarde de vos fichiers originaux a été créée dans: {backup_dir}")
    print("[INFO] Vous pouvez maintenant exécuter l'application avec: python app.py")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"[ERREUR] Une erreur inattendue s'est produite: {e}")
        sys.exit(1)
