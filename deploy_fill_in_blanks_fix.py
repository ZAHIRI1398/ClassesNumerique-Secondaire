#!/usr/bin/env python3
"""
Script pour déployer la correction du problème de scoring des exercices fill_in_blanks
"""

import os
import sys
import subprocess
import time
import requests

def check_git_status():
    """Vérifie si le dépôt Git est propre"""
    result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
    if result.stdout.strip():
        print("Des modifications non commitées sont présentes:")
        print(result.stdout)
        return False
    return True

def commit_changes():
    """Commit les modifications"""
    # Ajouter les fichiers modifiés
    subprocess.run(['git', 'add', 'app.py'])
    
    # Créer le commit
    commit_message = "Fix: Correction du problème de scoring des exercices texte à trous (fill_in_blanks)"
    result = subprocess.run(['git', 'commit', '-m', commit_message], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Erreur lors du commit:")
        print(result.stderr)
        return False
    
    print("Commit créé avec succès:")
    print(result.stdout)
    return True

def push_to_remote():
    """Push les modifications vers le dépôt distant"""
    result = subprocess.run(['git', 'push'], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Erreur lors du push:")
        print(result.stderr)
        return False
    
    print("Push effectué avec succès:")
    print(result.stdout)
    return True

def check_deployment(url, max_retries=10, delay=30):
    """Vérifie que le déploiement est accessible"""
    print(f"Vérification du déploiement à l'URL: {url}")
    
    for i in range(max_retries):
        try:
            print(f"Tentative {i+1}/{max_retries}...")
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"[SUCCÈS] Déploiement accessible (HTTP {response.status_code})")
                return True
            else:
                print(f"[ATTENTE] Le déploiement a répondu avec le code HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"[ATTENTE] Erreur de connexion: {e}")
        
        if i < max_retries - 1:
            print(f"Nouvelle tentative dans {delay} secondes...")
            time.sleep(delay)
    
    print("[ÉCHEC] Le déploiement n'est pas accessible après plusieurs tentatives")
    return False

def main():
    """Fonction principale"""
    print("Déploiement de la correction du problème de scoring des exercices fill_in_blanks")
    
    # Vérifier si le dépôt Git est propre
    if not check_git_status():
        response = input("Des modifications non commitées sont présentes. Voulez-vous continuer? (o/n): ")
        if response.lower() != 'o':
            print("Déploiement annulé")
            return
    
    # Commit les modifications
    if not commit_changes():
        print("Erreur lors du commit. Déploiement annulé")
        return
    
    # Push les modifications
    if not push_to_remote():
        print("Erreur lors du push. Déploiement annulé")
        return
    
    print("\nLes modifications ont été pushées avec succès!")
    print("Railway va automatiquement déployer les changements.")
    
    # Demander l'URL de déploiement
    deployment_url = input("\nEntrez l'URL de déploiement Railway (ou appuyez sur Entrée pour utiliser https://web-production-9a047.up.railway.app): ")
    if not deployment_url:
        deployment_url = "https://web-production-9a047.up.railway.app"
    
    # Vérifier le déploiement
    print("\nVérification du déploiement dans 60 secondes...")
    time.sleep(60)  # Attendre que Railway démarre le déploiement
    
    if check_deployment(deployment_url):
        print("\n[SUCCÈS] La correction a été déployée avec succès!")
    else:
        print("\n[AVERTISSEMENT] Le déploiement n'est pas accessible, mais les modifications ont été pushées.")
        print("Vérifiez manuellement l'état du déploiement sur Railway.")

if __name__ == '__main__':
    main()
