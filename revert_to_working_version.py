#!/usr/bin/env python3
"""
Script pour revenir à la dernière version fonctionnelle sur Railway
"""
import os
import subprocess
import sys
import argparse

def run_command(command):
    """Exécute une commande et affiche le résultat"""
    print(f"\n>>> Exécution: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                               capture_output=True, text=True)
        print(f"[OK] Succès: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERREUR] Échec: {e}")
        print(f"Sortie d'erreur: {e.stderr}")
        return False

def get_last_commits(count=5):
    """Récupère les derniers commits pour aider à identifier le problème"""
    print(f"\n[INFO] Récupération des {count} derniers commits...")
    try:
        result = subprocess.run(
            f"git log -{count} --oneline", 
            shell=True, check=True, capture_output=True, text=True
        )
        commits = result.stdout.strip().split('\n')
        print("\nDerniers commits:")
        for commit in commits:
            print(f"  {commit}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERREUR] Impossible de récupérer l'historique des commits: {e}")
        return False

def revert_to_working_version(commit_id=None, force=False):
    """Revient à la dernière version fonctionnelle sur Railway"""
    print("[INFO] Début du processus de retour à la version fonctionnelle...")
    
    # 1. Vérifier l'état actuel
    if not run_command("git status"):
        print("[ERREUR] Impossible de vérifier l'état Git. Abandon.")
        return False
    
    # Afficher les derniers commits pour aider à identifier le problème
    get_last_commits()
    
    # 2. Déterminer le commit à annuler
    if not commit_id:
        commit_id = "4352b64"  # ID du dernier commit qui a causé le crash (route de diagnostic)
        print(f"\n[INFO] Aucun commit ID spécifié, utilisation du commit par défaut: {commit_id}")
    
    # Demander confirmation sauf si --force est utilisé
    if not force:
        try:
            confirm = input(f"\nÊtes-vous sûr de vouloir annuler le commit {commit_id} ? (o/n): ")
            if confirm.lower() != 'o':
                print("[INFO] Opération annulée par l'utilisateur.")
                return False
        except EOFError:
            print("\n[ERREUR] Mode interactif non disponible. Utilisez --force pour continuer sans confirmation.")
            return False
    else:
        print(f"\n[INFO] Mode force activé, annulation du commit {commit_id} sans confirmation...")
    
    # 3. Créer un revert du commit problématique
    commit_message = "Revert: Annulation des modifications qui causent le crash sur Railway"
    
    if not run_command(f'git revert {commit_id} --no-edit'):
        print(f"[ERREUR] Échec du revert du commit {commit_id}.")
        print("[INFO] Tentative de revert avec --strategy=recursive -X theirs...")
        if not run_command(f'git revert {commit_id} --strategy=recursive -X theirs --no-edit'):
            print(f"[ERREUR] Échec du revert du commit {commit_id} même avec stratégie alternative. Abandon.")
            return False
    
    # 4. Pousser les modifications sur GitHub
    if not run_command("git push origin main"):
        print("[ERREUR] Échec du push sur GitHub. Abandon.")
        return False
    
    print("\n[SUCCÈS] Retour à la version fonctionnelle effectué!")
    print("[INFO] Un nouveau déploiement devrait se déclencher automatiquement sur Railway.")
    print("[INFO] Veuillez vérifier votre tableau de bord Railway pour suivre le déploiement.")
    print("[INFO] Une fois terminé, vérifiez que votre application fonctionne à l'URL Railway.")
    
    return True

def main():
    """Fonction principale avec parsing des arguments"""
    parser = argparse.ArgumentParser(description="Revenir à une version fonctionnelle sur Railway")
    parser.add_argument(
        "--commit", 
        help="ID du commit à annuler (par défaut: dernier commit qui a causé le crash)"
    )
    parser.add_argument(
        "--force", 
        action="store_true",
        help="Exécuter sans demander de confirmation"
    )
    args = parser.parse_args()
    
    try:
        revert_to_working_version(args.commit, args.force)
    except Exception as e:
        print(f"[ERREUR] Erreur inattendue: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
