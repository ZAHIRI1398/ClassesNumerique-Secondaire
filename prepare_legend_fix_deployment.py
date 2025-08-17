import os
import shutil
import datetime
import subprocess
from pathlib import Path

def create_backup():
    """Crée une sauvegarde des fichiers modifiés"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backup_legend_fix_{timestamp}"
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Fichiers à sauvegarder
    files_to_backup = [
        "templates/exercise_types/legend_edit.html",
        "check_legend_edit_route.py",
        "DOCUMENTATION_LEGEND_EXERCISE_FIX.md",
        "fix_legend_edit_route_final.py",
        "app.py"
    ]
    
    for file_path in files_to_backup:
        if os.path.exists(file_path):
            dest_path = os.path.join(backup_dir, os.path.basename(file_path))
            shutil.copy2(file_path, dest_path)
            print(f"Sauvegarde de {file_path} vers {dest_path}")
    
    return backup_dir

def check_git_status():
    """Vérifie le statut Git et retourne les fichiers modifiés"""
    try:
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if result.returncode != 0:
            print("Erreur lors de la vérification du statut Git.")
            return []
        
        modified_files = []
        for line in result.stdout.splitlines():
            if line.strip():
                status = line[:2].strip()
                file_path = line[3:].strip()
                modified_files.append((status, file_path))
        
        return modified_files
    except Exception as e:
        print(f"Exception lors de la vérification du statut Git: {str(e)}")
        return []

def create_commit_message():
    """Crée un message de commit pour la correction des exercices de type légende"""
    commit_message = """Fix: Correction des erreurs sur les exercices de type légende

- Ajout du template manquant legend_edit.html
- Implémentation de trois modes de légende (classique, quadrillage, spatial)
- Ajout d'un script de diagnostic pour vérifier la route d'édition
- Correction de l'erreur d'indentation dans app.py
- Ajout du return manquant dans la section GET pour les exercices de type légende
- Documentation complète de la solution

Cette correction résout l'erreur de serveur interne (500) qui se produisait
lors de la modification d'un exercice de type légende.
"""
    return commit_message

def main():
    print("=== Préparation du déploiement pour la correction des exercices de type légende ===\n")
    
    # 1. Créer une sauvegarde
    backup_dir = create_backup()
    print(f"\nSauvegarde créée dans le dossier: {backup_dir}\n")
    
    # 2. Vérifier les fichiers modifiés avec Git
    print("Vérification des fichiers modifiés avec Git...\n")
    modified_files = check_git_status()
    
    if modified_files:
        print("Fichiers modifiés détectés:")
        for status, file_path in modified_files:
            print(f"  {status} {file_path}")
    else:
        print("Aucun fichier modifié détecté.")
    
    # 3. Créer un message de commit
    commit_message = create_commit_message()
    print("\nMessage de commit préparé:")
    print("-" * 50)
    print(commit_message)
    print("-" * 50)
    
    # 4. Afficher les commandes Git pour le déploiement
    print("\nCommandes Git pour déployer les modifications sur Railway:")
    print("-" * 50)
    print("git add templates/exercise_types/legend_edit.html")
    print("git add check_legend_edit_route.py")
    print("git add DOCUMENTATION_LEGEND_EXERCISE_FIX.md")
    print("git add prepare_legend_fix_deployment.py")
    print("git add fix_legend_edit_route_final.py")
    print("git add app.py")
    print(f'git commit -m "{commit_message.splitlines()[0]}"')
    print("git push")
    print("-" * 50)
    
    # 5. Instructions finales
    print("\nInstructions:")
    print("1. Exécutez les commandes Git ci-dessus pour déployer les modifications.")
    print("2. Une fois le déploiement terminé, vérifiez que les exercices de type légende peuvent être modifiés sans erreur.")
    print("3. Si nécessaire, exécutez le script de diagnostic pour confirmer que tout fonctionne correctement:")
    print("   python check_legend_edit_route.py")

if __name__ == "__main__":
    main()
