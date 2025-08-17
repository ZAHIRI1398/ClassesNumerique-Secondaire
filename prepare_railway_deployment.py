#!/usr/bin/env python3
"""
Script pour préparer le déploiement sur Railway des corrections pour l'affichage
du feedback des exercices fill_in_blanks avec plusieurs mots par ligne
"""

import os
import sys
import json
import shutil
import subprocess
from datetime import datetime

def create_backup():
    """Crée une sauvegarde des fichiers modifiés"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backup_avant_deploiement_{timestamp}"
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Fichiers à sauvegarder
    files_to_backup = [
        "app.py",
        "templates/feedback.html"
    ]
    
    for file_path in files_to_backup:
        if os.path.exists(file_path):
            dest_path = os.path.join(backup_dir, os.path.basename(file_path))
            shutil.copy2(file_path, dest_path)
            print(f"[INFO] Sauvegarde de {file_path} vers {dest_path}")
    
    print(f"[OK] Sauvegarde créée dans le dossier {backup_dir}")
    return True

def check_git_status():
    """Vérifie le statut Git"""
    try:
        # Vérifier si le dossier .git existe
        if not os.path.exists(".git"):
            print("[ERREUR] Ce n'est pas un dépôt Git. Impossible de déployer sur Railway.")
            return False
        
        # Vérifier les modifications en attente
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        modified_files = result.stdout.strip().split("\n")
        modified_files = [f for f in modified_files if f]
        
        if modified_files:
            print("[INFO] Fichiers modifiés détectés:")
            for file in modified_files:
                print(f"  - {file}")
        else:
            print("[INFO] Aucun fichier modifié détecté.")
        
        return True
    except Exception as e:
        print(f"[ERREUR] Erreur lors de la vérification du statut Git: {e}")
        return False

def create_commit_message():
    """Crée un message de commit détaillé"""
    commit_message = """Fix: Amélioration de l'affichage du feedback pour les exercices fill_in_blanks

Cette correction améliore l'affichage du feedback pour les exercices de type "Texte à trous" (fill_in_blanks) 
qui contiennent plusieurs blancs par ligne.

Modifications:
1. Ajout d'informations sur la phrase à laquelle appartient chaque blanc dans app.py
2. Modification du template feedback.html pour regrouper les blancs par phrase
3. Amélioration de l'expérience utilisateur pour les exercices avec plusieurs blancs par ligne

Cette correction complète les précédentes corrections du problème de double comptage des blancs
et de conflit entre les deux implémentations de scoring.

Documentation: DOCUMENTATION_FILL_IN_BLANKS_FIX_FINAL_UPDATE.md"""
    
    with open("commit_message.txt", "w", encoding="utf-8") as f:
        f.write(commit_message)
    
    print("[OK] Message de commit créé dans commit_message.txt")
    return True

def prepare_git_commands():
    """Prépare les commandes Git pour le déploiement"""
    commands = [
        "git add app.py templates/feedback.html DOCUMENTATION_FILL_IN_BLANKS_FIX_FINAL_UPDATE.md",
        "git commit -F commit_message.txt",
        "git push"
    ]
    
    print("[INFO] Commandes Git à exécuter pour déployer sur Railway:")
    for cmd in commands:
        print(f"  $ {cmd}")
    
    return True

def main():
    """Fonction principale"""
    print("[INFO] Préparation du déploiement sur Railway des corrections pour l'affichage du feedback")
    
    # Créer une sauvegarde
    if not create_backup():
        print("[ERREUR] Échec de la création de sauvegarde")
        return
    
    # Vérifier le statut Git
    if not check_git_status():
        print("[ERREUR] Échec de la vérification du statut Git")
        return
    
    # Créer un message de commit
    if not create_commit_message():
        print("[ERREUR] Échec de la création du message de commit")
        return
    
    # Préparer les commandes Git
    if not prepare_git_commands():
        print("[ERREUR] Échec de la préparation des commandes Git")
        return
    
    print("\n[OK] Préparation du déploiement terminée")
    print("[INFO] Pour déployer sur Railway, exécutez les commandes Git listées ci-dessus")
    print("[INFO] Une fois le déploiement effectué, vérifiez le bon fonctionnement sur Railway")

if __name__ == "__main__":
    main()
