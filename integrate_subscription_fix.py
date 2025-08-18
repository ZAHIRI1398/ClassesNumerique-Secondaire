"""
Script d'intégration pour la solution du problème du bouton "Souscrire un nouvel abonnement école"
Ce script modifie app.py pour intégrer la correction
"""

import os
import sys
import re
import shutil
from datetime import datetime

# Configuration
APP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
BACKUP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                         f'backup_payment_blueprint_fix_{datetime.now().strftime("%Y%m%d_%H%M%S")}')

def create_backup():
    """Créer une sauvegarde de app.py"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    backup_path = os.path.join(BACKUP_DIR, 'app.py')
    shutil.copy2(APP_PATH, backup_path)
    print(f"[OK] Sauvegarde créée: {backup_path}")
    return backup_path

def integrate_fix():
    """Intégrer la correction dans app.py"""
    # Créer une sauvegarde
    backup_path = create_backup()
    
    # Lire le contenu de app.py
    with open(APP_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si l'import est déjà présent
    if 'from fix_school_subscription_simple import integrate_fix' in content:
        print("[ATTENTION] L'import de la correction est déjà présent dans app.py")
        return False
    
    # Trouver la position pour insérer l'import
    import_pattern = re.compile(r'# Import and register payment blueprint.*?app\.register_blueprint\(payment_bp\)', re.DOTALL)
    match = import_pattern.search(content)
    
    if not match:
        print("[ERREUR] Impossible de trouver l'emplacement pour insérer l'import")
        return False
    
    # Position après l'enregistrement du blueprint de paiement
    insert_pos = match.end()
    
    # Insérer l'import et l'intégration
    new_content = content[:insert_pos] + '\n\n# Intégration de la correction pour le bouton d\'abonnement école\nfrom fix_school_subscription_simple import integrate_fix\napp = integrate_fix(app)' + content[insert_pos:]
    
    # Écrire le contenu modifié
    with open(APP_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"[OK] Correction intégrée dans app.py")
    return True

def verify_integration():
    """Vérifier que l'intégration a été effectuée correctement"""
    with open(APP_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'from fix_school_subscription_simple import integrate_fix' in content and 'app = integrate_fix(app)' in content:
        print("[OK] Vérification réussie: La correction est bien intégrée dans app.py")
        return True
    else:
        print("[ERREUR] Vérification échouée: La correction n'est pas correctement intégrée")
        return False

def create_documentation():
    """Créer une documentation pour la solution"""
    doc_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'DOCUMENTATION_CORRECTION_BOUTON_ABONNEMENT_ECOLE.md')
    
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write("""# Correction du bouton "Souscrire un nouvel abonnement école"

## Problème initial

Le bouton "Souscrire un nouvel abonnement école" ne fonctionnait pas correctement pour les utilisateurs déjà connectés, notamment Sara. Les problèmes suivants ont été identifiés :

1. Lorsque Sara clique sur le bouton, aucune redirection visible ne se produit
2. Sara reçoit un message d'erreur lors de la création d'un compte école ("email existe déjà")
3. Le flux d'inscription et de souscription est bloqué

## Analyse technique

Après analyse approfondie, nous avons identifié les causes suivantes :

1. **Redirection incorrecte** : Sara, en tant qu'enseignante sans école ni abonnement, devrait être redirigée vers la page de sélection d'école (`payment.select_school`), mais cette redirection ne fonctionnait pas correctement.

2. **Type d'abonnement manquant** : Sara n'avait pas de type d'abonnement défini (`subscription_type: None`), ce qui pouvait causer des problèmes dans la logique de redirection.

3. **Flux d'inscription bloqué** : Le message d'erreur "email existe déjà" apparaît car Sara essaie de créer un nouveau compte alors qu'elle est déjà connectée.

## Solution implémentée

Nous avons créé un script de correction (`fix_school_subscription_simple.py`) qui :

1. **Corrige le type d'abonnement** : Définit `subscription_type='pending'` pour Sara si ce champ est vide.

2. **Ajoute une route de diagnostic** : `/fix/school-subscription` qui analyse l'état de l'utilisateur et applique les corrections nécessaires.

3. **Implémente une redirection correcte** : Redirige les enseignants sans abonnement approuvé vers la page de sélection d'école.

Le script d'intégration (`integrate_subscription_fix.py`) modifie `app.py` pour intégrer cette correction dans l'application Flask.

## Comment utiliser la solution

1. **Accéder à la page de diagnostic** : Visiter `/fix/school-subscription` lorsque vous êtes connecté en tant que Sara.

2. **Suivre le flux normal** : Après la correction, le bouton "Souscrire un nouvel abonnement école" redirigera correctement vers la page de sélection d'école.

## Vérification

Pour vérifier que la correction fonctionne :

1. Connectez-vous en tant que Sara (sara@gmail.com)
2. Accédez à la page de sélection d'école via `/fix/school-subscription`
3. Vérifiez que vous pouvez voir la liste des écoles avec abonnement actif
4. Sélectionnez une école ou souscrivez un nouvel abonnement école

## Déploiement

La correction a été intégrée dans l'application Flask et est prête à être déployée en production.
""")
    
    print(f"[OK] Documentation créée: {doc_path}")
    return doc_path

if __name__ == '__main__':
    print("=== INTÉGRATION DE LA CORRECTION POUR LE BOUTON D'ABONNEMENT ÉCOLE ===")
    
    # Intégrer la correction
    if integrate_fix():
        # Vérifier l'intégration
        if verify_integration():
            # Créer la documentation
            doc_path = create_documentation()
            
            print("""
=== INSTRUCTIONS D'UTILISATION ===

1. Redémarrer l'application Flask pour appliquer les modifications.

2. Accéder à la page de diagnostic :
   http://localhost:5000/fix/school-subscription

3. Se connecter en tant que Sara (sara@gmail.com) et tester le bouton d'abonnement école.

4. Consulter la documentation pour plus de détails sur la correction.
""")
        else:
            print("❌ L'intégration a échoué. Veuillez vérifier manuellement app.py.")
    else:
        print("❌ L'intégration a été annulée.")
