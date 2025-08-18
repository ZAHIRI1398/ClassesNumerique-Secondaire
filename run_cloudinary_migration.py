"""
Script pour exécuter la migration des images vers Cloudinary
en chargeant les variables d'environnement depuis .env.cloudinary
"""

import os
import sys
import subprocess
import argparse

def load_env_file(env_file):
    """Charge les variables d'environnement depuis un fichier .env"""
    if not os.path.exists(env_file):
        print(f"Erreur: Le fichier {env_file} n'existe pas")
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

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Exécute la migration des images vers Cloudinary")
    parser.add_argument('--no-dry-run', action='store_true', help="Exécute la migration réelle (sans simulation)")
    parser.add_argument('--batch-size', type=int, default=10, help="Nombre d'images à traiter par lot")
    parser.add_argument('--sleep-time', type=int, default=1, help="Temps d'attente entre les lots (secondes)")
    args = parser.parse_args()
    
    # Charger les variables d'environnement
    if not load_env_file('.env.cloudinary'):
        sys.exit(1)
    
    # Vérifier que les variables Cloudinary sont définies
    required_vars = ['CLOUDINARY_CLOUD_NAME', 'CLOUDINARY_API_KEY', 'CLOUDINARY_API_SECRET']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print("Erreur: Variables d'environnement Cloudinary manquantes:")
        for var in missing_vars:
            print(f"  - {var}")
        sys.exit(1)
    
    # Construire la commande pour exécuter le script de migration
    cmd = [sys.executable, 'migrate_images_to_cloudinary.py']
    if args.no_dry_run:
        cmd.append('--no-dry-run')
    if args.batch_size != 10:
        cmd.extend(['--batch-size', str(args.batch_size)])
    if args.sleep_time != 1:
        cmd.extend(['--sleep-time', str(args.sleep_time)])
    
    # Exécuter le script de migration
    print("\nExécution de la commande:", ' '.join(cmd))
    result = subprocess.run(cmd)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
