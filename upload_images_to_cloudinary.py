"""
Script pour uploader les images du répertoire static/uploads vers Cloudinary
sans nécessiter de référence dans la base de données
"""

import os
import sys
import json
import time
import argparse
from flask import Flask
import cloudinary
import cloudinary.uploader
import cloudinary.api
from tabulate import tabulate
from config import config

def create_app():
    """Crée une instance minimale de l'application Flask"""
    app = Flask(__name__)
    
    # Charger la configuration depuis config.py
    try:
        app.config.from_object(config['development'])
        print("[OK] Configuration chargée avec succès")
    except Exception as e:
        print(f"[ERREUR] Impossible de charger la configuration: {str(e)}")
        sys.exit(1)
    
    return app

def configure_cloudinary():
    """Configure Cloudinary avec les variables d'environnement"""
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
    api_key = os.environ.get('CLOUDINARY_API_KEY')
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')
    
    if not all([cloud_name, api_key, api_secret]):
        print("[ERREUR] Variables d'environnement Cloudinary manquantes:")
        print(f"  - CLOUDINARY_CLOUD_NAME: {'Présent' if cloud_name else 'Manquant'}")
        print(f"  - CLOUDINARY_API_KEY: {'Présent' if api_key else 'Manquant'}")
        print(f"  - CLOUDINARY_API_SECRET: {'Présent' if api_secret else 'Manquant'}")
        return False
    
    # Configurer Cloudinary
    try:
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )
        print("[OK] Cloudinary configuré avec succès")
        return True
    except Exception as e:
        print(f"[ERREUR] Impossible de configurer Cloudinary: {str(e)}")
        return False

def upload_to_cloudinary(file_path, folder='uploads'):
    """
    Upload un fichier vers Cloudinary
    
    Args:
        file_path: Chemin du fichier à uploader
        folder: Dossier de destination sur Cloudinary
        
    Returns:
        str: URL Cloudinary du fichier uploadé ou None en cas d'erreur
    """
    try:
        # Extraire le nom du fichier
        filename = os.path.basename(file_path)
        
        # Upload vers Cloudinary
        result = cloudinary.uploader.upload(
            file_path,
            folder=folder,
            public_id=os.path.splitext(filename)[0],  # Utiliser le nom du fichier sans extension
            resource_type="auto"
        )
        
        return result['secure_url']
    except Exception as e:
        print(f"[ERREUR] Erreur lors de l'upload de {file_path}: {str(e)}")
        return None

def upload_images_to_cloudinary(dry_run=True, batch_size=10, sleep_time=1):
    """
    Upload toutes les images du répertoire static/uploads vers Cloudinary
    
    Args:
        dry_run: Si True, n'effectue pas réellement l'upload
        batch_size: Nombre d'images à uploader par lot
        sleep_time: Temps d'attente entre chaque lot (en secondes)
    """
    app = create_app()
    
    with app.app_context():
        # Configurer Cloudinary
        if not configure_cloudinary():
            print("[ERREUR] Impossible de configurer Cloudinary")
            print("Vérifiez vos variables d'environnement CLOUDINARY_*")
            sys.exit(1)
        
        # Chemin du répertoire static/uploads
        uploads_dir = os.path.join(app.static_folder, 'uploads')
        
        if not os.path.exists(uploads_dir):
            print(f"[ERREUR] Le répertoire {uploads_dir} n'existe pas")
            sys.exit(1)
        
        # Récupérer la liste des fichiers
        files = []
        for root, _, filenames in os.walk(uploads_dir):
            for filename in filenames:
                # Ignorer les fichiers cachés et .gitkeep
                if filename.startswith('.') or filename == '.gitkeep':
                    continue
                
                # Ignorer les répertoires
                file_path = os.path.join(root, filename)
                if os.path.isdir(file_path):
                    continue
                
                # Ignorer les fichiers vides
                if os.path.getsize(file_path) == 0:
                    continue
                
                # Ajouter à la liste
                files.append({
                    'path': file_path,
                    'name': filename,
                    'size': os.path.getsize(file_path)
                })
        
        print(f"Trouvé {len(files)} fichiers à uploader vers Cloudinary")
        
        if not files:
            print("Aucun fichier à uploader")
            return
        
        # Afficher un tableau des fichiers à uploader
        table_data = []
        for file in files[:10]:  # Limiter à 10 pour l'affichage
            table_data.append([
                file['name'],
                f"{file['size'] / 1024:.1f} KB",
                file['path']
            ])
        
        print("\nAperçu des fichiers à uploader:")
        print(tabulate(table_data, headers=["Nom", "Taille", "Chemin"], tablefmt="grid"))
        
        if len(files) > 10:
            print(f"... et {len(files) - 10} autres fichiers")
        
        if dry_run:
            print("\n[SIMULATION] Mode simulation activé, aucun upload ne sera effectué")
            print("Pour effectuer l'upload réel, exécutez avec --no-dry-run")
            return
        
        # Confirmer l'upload
        if input("\nConfirmer l'upload vers Cloudinary ? (o/N) ").lower() != 'o':
            print("Upload annulé")
            return
        
        # Uploader les fichiers par lots
        successful = 0
        failed = 0
        results = []
        
        for i in range(0, len(files), batch_size):
            batch = files[i:i+batch_size]
            print(f"\nUpload du lot {i//batch_size + 1}/{(len(files) + batch_size - 1)//batch_size}...")
            
            for file in batch:
                try:
                    # Uploader vers Cloudinary
                    cloudinary_url = upload_to_cloudinary(file['path'])
                    
                    if not cloudinary_url:
                        print(f"[ERREUR] Échec d'upload pour {file['name']}")
                        failed += 1
                        results.append({
                            'name': file['name'],
                            'status': 'failed',
                            'error': 'Échec d\'upload vers Cloudinary'
                        })
                        continue
                    
                    print(f"[OK] {file['name']} uploadé: {cloudinary_url}")
                    successful += 1
                    results.append({
                        'name': file['name'],
                        'status': 'success',
                        'url': cloudinary_url
                    })
                    
                except Exception as e:
                    print(f"[ERREUR] Erreur pour {file['name']}: {str(e)}")
                    failed += 1
                    results.append({
                        'name': file['name'],
                        'status': 'failed',
                        'error': str(e)
                    })
            
            # Attendre entre les lots pour éviter de surcharger l'API Cloudinary
            if i + batch_size < len(files):
                print(f"Attente de {sleep_time} secondes avant le prochain lot...")
                time.sleep(sleep_time)
        
        # Afficher un résumé
        print("\n=== Résumé de l'upload ===")
        print(f"Total: {len(files)} fichiers")
        print(f"Réussis: {successful} fichiers")
        print(f"Échoués: {failed} fichiers")
        
        # Sauvegarder les résultats dans un fichier JSON
        with open('cloudinary_upload_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print("\nRésultats détaillés sauvegardés dans cloudinary_upload_results.json")
        print("\nCes URLs Cloudinary pourront être utilisées pour les nouveaux exercices.")

def load_env_file(env_file):
    """Charge les variables d'environnement depuis un fichier .env"""
    if not os.path.exists(env_file):
        print(f"[ERREUR] Le fichier {env_file} n'existe pas")
        return False
    
    print(f"Chargement des variables depuis {env_file}...")
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            key, value = line.split('=', 1)
            os.environ[key] = value
            # Afficher les variables (masquer les secrets)
            if 'SECRET' in key or 'KEY' in key:
                masked_value = value[:4] + '*' * (len(value) - 4) if len(value) > 4 else '****'
                print(f"  {key}={masked_value}")
            else:
                print(f"  {key}={value}")
    
    return True

if __name__ == "__main__":
    # Charger les variables d'environnement depuis .env.cloudinary
    if not load_env_file('.env.cloudinary'):
        sys.exit(1)
    
    parser = argparse.ArgumentParser(description="Uploader les images vers Cloudinary")
    parser.add_argument("--no-dry-run", action="store_true", help="Effectuer réellement l'upload")
    parser.add_argument("--batch-size", type=int, default=10, help="Nombre d'images à uploader par lot")
    parser.add_argument("--sleep-time", type=int, default=1, help="Temps d'attente entre chaque lot (en secondes)")
    args = parser.parse_args()
    
    upload_images_to_cloudinary(
        dry_run=not args.no_dry_run,
        batch_size=args.batch_size,
        sleep_time=args.sleep_time
    )
