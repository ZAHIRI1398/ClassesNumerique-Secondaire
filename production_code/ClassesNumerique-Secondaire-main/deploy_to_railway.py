#!/usr/bin/env python3
"""
Script de déploiement pour Railway
- Pousse les modifications sur GitHub
- Déclenche le redéploiement sur Railway
- Exécute l'initialisation de la base de données
"""

import subprocess
import sys
import time

def run_command(cmd, description):
    """Exécuter une commande et afficher le résultat"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} réussi!")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} échoué!")
            if result.stderr.strip():
                print(f"   Erreur: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Erreur lors de {description}: {e}")
        return False

def deploy_to_railway():
    """Déployer sur Railway avec initialisation"""
    
    print("=== DÉPLOIEMENT SUR RAILWAY ===")
    
    # 1. Ajouter tous les fichiers
    if not run_command("git add .", "Ajout des fichiers"):
        return False
    
    # 2. Commit
    commit_msg = "Ajout initialisation production Railway avec compte admin"
    if not run_command(f'git commit -m "{commit_msg}"', "Commit des modifications"):
        print("ℹ️ Aucune modification à committer ou commit déjà fait")
    
    # 3. Push vers GitHub
    if not run_command("git push origin main", "Push vers GitHub"):
        return False
    
    print("\n🚀 Code poussé sur GitHub!")
    print("Railway va automatiquement redéployer...")
    
    # 4. Instructions pour l'utilisateur
    print("\n" + "="*50)
    print("📋 ÉTAPES SUIVANTES:")
    print("="*50)
    print("1. Attendez que Railway termine le redéploiement (2-3 minutes)")
    print("2. Allez sur: https://web-production-9a047.up.railway.app/init-production")
    print("3. Ou connectez-vous directement avec:")
    print("   📧 Email: admin@admin.com")
    print("   🔑 Mot de passe: admin")
    print("4. Accédez au dashboard admin pour gérer les utilisateurs")
    
    print("\n🎯 URL de production: https://web-production-9a047.up.railway.app")
    print("🎯 URL admin: https://web-production-9a047.up.railway.app/admin/dashboard")
    
    return True

if __name__ == "__main__":
    success = deploy_to_railway()
    if success:
        print("\n🎉 DÉPLOIEMENT LANCÉ AVEC SUCCÈS!")
    else:
        print("\n❌ ÉCHEC DU DÉPLOIEMENT!")
        sys.exit(1)
