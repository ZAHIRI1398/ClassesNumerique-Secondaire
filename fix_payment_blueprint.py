"""
Script de correction pour le problème de duplication du blueprint de paiement.
Ce script corrige le problème d'import et d'enregistrement du blueprint de paiement dans app.py.
"""
import os
import sys
import shutil
from datetime import datetime
import re

# Configuration
BACKUP_DIR = f"backup_payment_blueprint_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
APP_PY_FILE = "app.py"

def create_backup():
    """Crée une sauvegarde des fichiers avant modification"""
    print(f"Création du répertoire de sauvegarde {BACKUP_DIR}...")
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    # Sauvegarde des fichiers
    if os.path.exists(APP_PY_FILE):
        backup_path = os.path.join(BACKUP_DIR, APP_PY_FILE)
        print(f"Sauvegarde de {APP_PY_FILE} vers {backup_path}...")
        shutil.copy2(APP_PY_FILE, backup_path)
    
    print("Sauvegarde terminée.")

def fix_app_py():
    """Corrige le fichier app.py pour éviter la duplication du blueprint de paiement"""
    print("Vérification et correction du fichier app.py...")
    
    try:
        with open(APP_PY_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Compter les occurrences de l'import du blueprint de paiement
        import_count = content.count("from payment_routes import payment_bp")
        register_count = content.count("app.register_blueprint(payment_bp)")
        
        print(f"Nombre d'imports du blueprint de paiement: {import_count}")
        print(f"Nombre d'enregistrements du blueprint de paiement: {register_count}")
        
        if import_count > 1 or register_count > 1:
            print("Duplication détectée. Correction en cours...")
            
            # Supprimer la première occurrence de l'import
            pattern = r"from payment_routes import payment_bp\s*\n"
            match = re.search(pattern, content)
            if match:
                start_pos = match.start()
                end_pos = match.end()
                content = content[:start_pos] + content[end_pos:]
                print("Première occurrence de l'import supprimée.")
            
            # S'assurer qu'il y a un seul enregistrement du blueprint
            if register_count > 1:
                pattern = r"app\.register_blueprint\(payment_bp\)\s*\n"
                content = re.sub(pattern, "", content, count=register_count-1)
                print("Occurrences supplémentaires de l'enregistrement supprimées.")
            
            # Écrire le contenu corrigé
            with open(APP_PY_FILE, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("Correction appliquée avec succès.")
        else:
            print("Aucune duplication détectée. Aucune correction nécessaire.")
        
        # Vérifier que l'import et l'enregistrement sont présents
        if "from payment_routes import payment_bp" not in content:
            print("ERREUR: L'import du blueprint de paiement est manquant.")
            return False
        
        if "app.register_blueprint(payment_bp)" not in content:
            print("ERREUR: L'enregistrement du blueprint de paiement est manquant.")
            return False
        
        print("Le blueprint de paiement est correctement importé et enregistré.")
        return True
        
    except Exception as e:
        print(f"Erreur lors de la correction de app.py: {str(e)}")
        return False

def create_test_script():
    """Crée un script de test pour vérifier le fonctionnement du bouton d'abonnement école"""
    print("Création du script de test test_payment_button.py...")
    
    script_content = """
from flask import Flask, url_for
from werkzeug.test import Client
from werkzeug.wrappers import Response
import sys
import os

def test_payment_button():
    \"\"\"
    Test le fonctionnement du bouton 'Souscrire un nouvel abonnement école'
    en vérifiant que la route payment.subscribe est correctement générée.
    \"\"\"
    # Importer l'application Flask
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from app import app
    
    # Créer un client de test
    client = Client(app)
    
    # Tester dans un contexte d'application
    with app.test_request_context():
        # Vérifier que la route payment.subscribe est correctement générée
        url = url_for('payment.subscribe', subscription_type='school')
        print(f"URL générée pour payment.subscribe: {url}")
        
        # Vérifier que la route existe
        response = client.get(url)
        print(f"Statut de la réponse: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ La route payment.subscribe fonctionne correctement.")
        elif response.status_code == 302:
            print("⚠️ La route payment.subscribe redirige (code 302). Cela peut être normal selon la logique de l'application.")
        else:
            print(f"❌ La route payment.subscribe retourne un code d'erreur: {response.status_code}")
            
        # Vérifier que la route select_school existe
        select_school_url = url_for('payment.select_school')
        print(f"URL générée pour payment.select_school: {select_school_url}")
        
        select_school_response = client.get(select_school_url)
        print(f"Statut de la réponse: {select_school_response.status_code}")
        
        if select_school_response.status_code == 200:
            print("✅ La route payment.select_school fonctionne correctement.")
        elif select_school_response.status_code == 302:
            print("⚠️ La route payment.select_school redirige (code 302). Cela peut être normal selon la logique de l'application.")
        else:
            print(f"❌ La route payment.select_school retourne un code d'erreur: {select_school_response.status_code}")

if __name__ == "__main__":
    print("=== TEST DU BOUTON D'ABONNEMENT ÉCOLE ===")
    test_payment_button()
    print("=== FIN DU TEST ===")
"""
    
    try:
        with open("test_payment_button.py", 'w', encoding='utf-8') as f:
            f.write(script_content)
        print("Script de test créé avec succès.")
        return True
    except Exception as e:
        print(f"Erreur lors de la création du script de test: {str(e)}")
        return False

def create_integration_script():
    """Crée un script d'intégration pour connecter l'inscription d'école et le système de paiement"""
    print("Création du script d'intégration school_payment_integration.py...")
    
    script_content = """
from flask import Blueprint, redirect, url_for, flash, current_app
from flask_login import current_user, login_required

def integrate_school_payment(app):
    \"\"\"
    Intègre le module de paiement d'école à l'application Flask.
    Cette fonction crée un blueprint pour gérer les redirections entre
    l'inscription d'école et le système de paiement.
    \"\"\"
    # Création du blueprint
    school_payment_bp = Blueprint('school_payment', __name__)
    
    @school_payment_bp.route('/register-school-to-payment')
    @login_required
    def register_school_to_payment():
        \"\"\"
        Route de redirection après la création d'une école pour initier le processus de paiement.
        \"\"\"
        # Vérifier si l'utilisateur est associé à une école
        if not current_user.school_id:
            flash('Vous devez d\\'abord créer une école avant de procéder au paiement.', 'warning')
            return redirect(url_for('school_registration_mod.register_school_simplified'))
        
        # Rediriger vers la page de paiement pour un abonnement école
        return redirect(url_for('payment.subscribe', subscription_type='school'))
    
    # Enregistrer le blueprint dans l'application
    app.register_blueprint(school_payment_bp)
    
    # Modifier les routes d'inscription d'école pour rediriger vers le paiement
    try:
        from integrate_school_registration_mod import school_registration_mod
        
        # Sauvegarder les fonctions originales
        original_register_school_simplified = school_registration_mod.view_functions.get('register_school_simplified')
        original_register_school_connected = school_registration_mod.view_functions.get('register_school_connected')
        
        if original_register_school_simplified and original_register_school_connected:
            # Définir les nouvelles fonctions avec redirection vers le paiement
            @school_registration_mod.route('/register-school-simplified', methods=['GET', 'POST'])
            @login_required
            def register_school_simplified_with_payment():
                # Appeler la fonction originale
                result = original_register_school_simplified()
                
                # Si c'est une redirection (après création réussie), rediriger vers le paiement
                if hasattr(result, 'status_code') and result.status_code == 302:
                    current_app.logger.info("École créée avec succès, redirection vers le paiement...")
                    return redirect(url_for('school_payment.register_school_to_payment'))
                
                # Sinon, retourner le résultat original
                return result
            
            @school_registration_mod.route('/register-school-connected', methods=['GET', 'POST'])
            @login_required
            def register_school_connected_with_payment():
                # Appeler la fonction originale
                result = original_register_school_connected()
                
                # Si c'est une redirection (après création réussie), rediriger vers le paiement
                if hasattr(result, 'status_code') and result.status_code == 302:
                    current_app.logger.info("École créée avec succès, redirection vers le paiement...")
                    return redirect(url_for('school_payment.register_school_to_payment'))
                
                # Sinon, retourner le résultat original
                return result
            
            # Remplacer les fonctions originales par les nouvelles
            school_registration_mod.view_functions['register_school_simplified'] = register_school_simplified_with_payment
            school_registration_mod.view_functions['register_school_connected'] = register_school_connected_with_payment
            
            current_app.logger.info("Intégration du module de paiement d'école terminée.")
        else:
            current_app.logger.warning("Les fonctions d'inscription d'école n'ont pas été trouvées. L'intégration n'a pas pu être effectuée.")
    
    except ImportError:
        current_app.logger.warning("Le module d'inscription d'école n'a pas été trouvé. L'intégration n'a pas pu être effectuée.")
    
    return app
"""
    
    try:
        with open("school_payment_integration.py", 'w', encoding='utf-8') as f:
            f.write(script_content)
        print("Script d'intégration créé avec succès.")
        return True
    except Exception as e:
        print(f"Erreur lors de la création du script d'intégration: {str(e)}")
        return False

def create_app_integration_snippet():
    """Crée un snippet pour intégrer le module de paiement d'école dans app.py"""
    print("Création du snippet d'intégration pour app.py...")
    
    script_content = """
# Ajoutez ces lignes à votre app.py après l'initialisation des extensions
# et l'intégration du module d'inscription d'école

# Intégration du module de paiement d'école
from school_payment_integration import integrate_school_payment
integrate_school_payment(app)
"""
    
    try:
        with open("app_integration_snippet.py", 'w', encoding='utf-8') as f:
            f.write(script_content)
        print("Snippet d'intégration pour app.py créé avec succès.")
        return True
    except Exception as e:
        print(f"Erreur lors de la création du snippet d'intégration pour app.py: {str(e)}")
        return False

def main():
    """Fonction principale"""
    print("=== DÉBUT DE LA CORRECTION DU PROBLÈME DE BLUEPRINT DE PAIEMENT ===")
    
    # Créer une sauvegarde
    create_backup()
    
    # Corriger le fichier app.py
    if not fix_app_py():
        print("Échec de la correction du fichier app.py.")
        return False
    
    # Créer le script de test
    if not create_test_script():
        print("Échec de la création du script de test.")
        return False
    
    # Créer le script d'intégration
    if not create_integration_script():
        print("Échec de la création du script d'intégration.")
        return False
    
    # Créer le snippet d'intégration pour app.py
    if not create_app_integration_snippet():
        print("Échec de la création du snippet d'intégration pour app.py.")
        return False
    
    print("\n=== CORRECTION TERMINÉE ===")
    print("Les fichiers suivants ont été créés ou modifiés:")
    print("1. app.py (corrigé)")
    print("2. test_payment_button.py (nouveau)")
    print("3. school_payment_integration.py (nouveau)")
    print("4. app_integration_snippet.py (nouveau)")
    
    print("\nPour vérifier la correction:")
    print("1. Exécutez le script de test: python test_payment_button.py")
    print("2. Si nécessaire, intégrez le module de paiement d'école en ajoutant le contenu de app_integration_snippet.py à votre app.py")
    print("3. Redémarrez l'application Flask")
    
    return True

if __name__ == "__main__":
    main()
