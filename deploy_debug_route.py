#!/usr/bin/env python3
"""
Script pour déployer la route de diagnostic des données de formulaire
"""

import os
import subprocess
import sys

def deploy_debug_route():
    """Déploie la route de diagnostic sur Railway"""
    
    print("Déploiement de la route de diagnostic pour les données de formulaire...")
    
    # Vérifier si git est installé
    try:
        subprocess.run(["git", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Erreur: Git n'est pas installé ou n'est pas dans le PATH.")
        return False
    
    # Vérifier si nous sommes dans un dépôt git
    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], 
                      check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.SubprocessError:
        print("Erreur: Ce répertoire n'est pas un dépôt git.")
        return False
    
    # Vérifier les modifications
    result = subprocess.run(["git", "status", "--porcelain"], 
                           check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if not result.stdout:
        print("Aucune modification à déployer.")
        return False
    
    # Afficher les fichiers modifiés
    print("Fichiers modifiés:")
    modified_files = result.stdout.decode('utf-8').strip().split('\n')
    for file in modified_files:
        print(f"  {file}")
    
    # Ajouter les fichiers modifiés
    try:
        subprocess.run(["git", "add", "app.py", "templates/debug/form_data.html"], 
                      check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Fichiers ajoutés au commit.")
    except subprocess.SubprocessError as e:
        print(f"Erreur lors de l'ajout des fichiers: {e}")
        return False
    
    # Créer un commit
    commit_message = "Ajout de la route de diagnostic pour les données de formulaire"
    try:
        subprocess.run(["git", "commit", "-m", commit_message], 
                      check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Commit créé: {commit_message}")
    except subprocess.SubprocessError as e:
        print(f"Erreur lors de la création du commit: {e}")
        return False
    
    # Pousser les modifications
    try:
        subprocess.run(["git", "push"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Modifications poussées avec succès.")
    except subprocess.SubprocessError as e:
        print(f"Erreur lors du push: {e}")
        return False
    
    print("\nDéploiement terminé avec succès!")
    print("La route de diagnostic sera disponible à l'adresse: https://votre-app.railway.app/debug-form-data")
    print("N'oubliez pas que vous devez être connecté en tant qu'administrateur pour y accéder.")
    
    return True

if __name__ == "__main__":
    deploy_debug_route()
