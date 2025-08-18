"""
Script pour restaurer la version GitHub et annuler toutes les modifications récentes
"""
import os
import shutil
import requests
import zipfile
import io
from datetime import datetime

def restore_github_version():
    """
    Restaure la version GitHub et annule toutes les modifications récentes
    """
    # Créer un dossier de sauvegarde
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f'backup_avant_restauration_github_{timestamp}'
    os.makedirs(backup_dir, exist_ok=True)
    
    print(f"Création du dossier de sauvegarde : {backup_dir}")
    
    # Liste des fichiers importants à sauvegarder
    important_files = ['app.py', 'models.py', 'config.py']
    
    # Sauvegarder les fichiers importants
    for file in important_files:
        if os.path.exists(file):
            shutil.copy2(file, os.path.join(backup_dir, file))
            print(f"Sauvegarde de {file} effectuée")
    
    # URL du dépôt GitHub (branche main/master au format zip)
    github_url = "https://github.com/ZAHIRI1398/ClassesNumerique-Secondaire/archive/refs/heads/main.zip"
    
    try:
        # Télécharger le zip depuis GitHub
        print("Téléchargement de la version GitHub...")
        response = requests.get(github_url)
        response.raise_for_status()  # Vérifier si la requête a réussi
        
        # Extraire le contenu du zip
        print("Extraction du contenu...")
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            zip_ref.extractall("temp_github")
        
        # Déterminer le nom du dossier extrait
        extracted_dir = None
        for item in os.listdir("temp_github"):
            if os.path.isdir(os.path.join("temp_github", item)):
                extracted_dir = os.path.join("temp_github", item)
                break
        
        if not extracted_dir:
            print("Erreur: Impossible de trouver le dossier extrait")
            return False
        
        # Copier les fichiers importants depuis la version GitHub
        print("Remplacement des fichiers locaux par la version GitHub...")
        for file in important_files:
            github_file = os.path.join(extracted_dir, file)
            if os.path.exists(github_file):
                shutil.copy2(github_file, file)
                print(f"Fichier {file} restauré depuis GitHub")
            else:
                print(f"Attention: {file} n'existe pas dans la version GitHub")
        
        # Nettoyer les fichiers temporaires
        print("Nettoyage des fichiers temporaires...")
        shutil.rmtree("temp_github")
        
        print("\nRestauration terminée avec succès!")
        print(f"Une sauvegarde de vos fichiers a été créée dans le dossier: {backup_dir}")
        print("Vous pouvez maintenant démarrer l'application avec la version GitHub restaurée.")
        
        return True
    
    except Exception as e:
        print(f"Erreur lors de la restauration: {str(e)}")
        return False

if __name__ == "__main__":
    restore_github_version()
