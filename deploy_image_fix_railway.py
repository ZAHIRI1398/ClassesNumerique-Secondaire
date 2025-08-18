"""
Script de déploiement des corrections d'affichage d'images pour Railway
"""
import os
import sys
import shutil
import datetime
import subprocess

def create_backup(file_path):
    """Crée une sauvegarde d'un fichier"""
    if os.path.exists(file_path):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{file_path}.bak_{timestamp}"
        shutil.copy2(file_path, backup_path)
        print(f"Sauvegarde créée: {backup_path}")
        return backup_path
    return None

def check_cloudinary_config():
    """Vérifie si les variables d'environnement Cloudinary sont configurées"""
    required_vars = ['CLOUDINARY_CLOUD_NAME', 'CLOUDINARY_API_KEY', 'CLOUDINARY_API_SECRET']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"ATTENTION: Variables d'environnement Cloudinary manquantes: {', '.join(missing_vars)}")
        print("Les images seront stockées localement en développement.")
        return False
    
    print("Configuration Cloudinary détectée.")
    return True

def deploy_image_fix():
    """Déploie les corrections d'affichage d'images"""
    print("=== Déploiement des corrections d'affichage d'images ===")
    
    # 1. Vérifier si les fichiers nécessaires existent
    required_files = ['fix_image_paths.py', 'integrate_image_sync.py']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"ERREUR: Fichiers manquants: {', '.join(missing_files)}")
        return False
    
    # 2. Créer des sauvegardes
    print("\n--- Création des sauvegardes ---")
    create_backup('app.py')
    
    # 3. Vérifier la configuration Cloudinary
    print("\n--- Vérification de la configuration Cloudinary ---")
    check_cloudinary_config()
    
    # 4. Intégrer le blueprint dans app.py
    print("\n--- Intégration du blueprint ---")
    try:
        result = subprocess.run(['python', 'integrate_image_sync.py'], 
                               capture_output=True, text=True, check=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"ERREUR lors de l'intégration du blueprint: {e}")
        print(f"Sortie: {e.stdout}")
        print(f"Erreur: {e.stderr}")
        return False
    
    # 5. Vérifier l'intégration
    print("\n--- Vérification de l'intégration ---")
    try:
        check_cmd = "from app import app; print('Blueprint intégré avec succès' if hasattr(app, 'blueprints') and 'image_sync' in app.blueprints else 'Blueprint non intégré')"
        result = subprocess.run(['python', '-c', check_cmd], 
                               capture_output=True, text=True, check=True)
        print(result.stdout)
        
        if "Blueprint non intégré" in result.stdout:
            print("ERREUR: Le blueprint n'a pas été intégré correctement.")
            return False
    except subprocess.CalledProcessError as e:
        print(f"ERREUR lors de la vérification: {e}")
        print(f"Sortie: {e.stdout}")
        print(f"Erreur: {e.stderr}")
        return False
    
    # 6. Préparer les fichiers pour Railway
    print("\n--- Préparation des fichiers pour Railway ---")
    railway_files = ['fix_image_paths.py', 'DOCUMENTATION_CORRECTION_AFFICHAGE_IMAGES_COMPLETE.md', 
                    'GUIDE_DEPLOIEMENT_CORRECTION_IMAGES_COMPLET.md']
    
    for file in railway_files:
        if os.path.exists(file):
            print(f"Fichier prêt pour le déploiement: {file}")
        else:
            print(f"ATTENTION: Fichier manquant pour le déploiement: {file}")
    
    print("\n=== Déploiement terminé avec succès ===")
    print("\nÉtapes suivantes pour Railway:")
    print("1. Commiter les modifications:")
    print("   git add fix_image_paths.py app.py")
    print("   git commit -m \"Correction de l'affichage des images\"")
    print("2. Pousser vers Railway:")
    print("   git push railway main")
    print("\nAprès le déploiement, accéder aux routes suivantes:")
    print("- /fix-template-paths - Correction des templates")
    print("- /sync-image-paths - Synchronisation des chemins d'images")
    print("- /check-image-consistency - Vérification de la cohérence")
    print("- /create-simple-placeholders - Création d'images placeholder")
    
    return True

if __name__ == "__main__":
    deploy_image_fix()
