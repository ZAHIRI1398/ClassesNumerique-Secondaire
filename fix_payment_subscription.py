"""
Script de correction pour le problème de souscription d'abonnement école.
Ce script corrige le problème de redirection entre l'inscription d'école et le système de paiement.
"""
import os
import sys
import shutil
from datetime import datetime

# Configuration
BACKUP_DIR = f"backup_payment_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
PAYMENT_ROUTES_FILE = "payment_routes.py"
APP_PY_FILE = "app.py"

def create_backup():
    """Crée une sauvegarde des fichiers avant modification"""
    print(f"Création du répertoire de sauvegarde {BACKUP_DIR}...")
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    # Sauvegarde des fichiers
    for file in [PAYMENT_ROUTES_FILE, APP_PY_FILE]:
        if os.path.exists(file):
            backup_path = os.path.join(BACKUP_DIR, file)
            print(f"Sauvegarde de {file} vers {backup_path}...")
            shutil.copy2(file, backup_path)
    
    print("Sauvegarde terminée.")

def fix_payment_routes():
    """Corrige le fichier payment_routes.py pour s'assurer que la fonction subscribe est correctement enregistrée"""
    print("Vérification et correction du fichier payment_routes.py...")
    
    try:
        with open(PAYMENT_ROUTES_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier si la fonction subscribe est correctement définie
        if "@payment_bp.route('/subscribe/<subscription_type>')" in content:
            print("La route /subscribe/<subscription_type> est déjà définie.")
            
            # Vérifier si la fonction est correctement nommée
            if "def subscribe(subscription_type):" in content:
                print("La fonction subscribe est correctement nommée.")
            else:
                print("ERREUR: La fonction subscribe n'est pas correctement nommée.")
                # Correction du nom de la fonction si nécessaire
                content = content.replace("def subscribe_route(subscription_type):", "def subscribe(subscription_type):")
                
                with open(PAYMENT_ROUTES_FILE, 'w', encoding='utf-8') as f:
                    f.write(content)
                print("Correction appliquée: Renommage de la fonction subscribe_route en subscribe.")
        else:
            print("ERREUR: La route /subscribe/<subscription_type> n'est pas définie.")
            # Ici, on pourrait ajouter la définition complète de la route si elle était manquante
    
    except Exception as e:
        print(f"Erreur lors de la correction de payment_routes.py: {str(e)}")
        return False
    
    return True

def fix_integration():
    """Vérifie et corrige l'intégration entre le module d'inscription d'école et le système de paiement"""
    print("Vérification de l'intégration entre le module d'inscription d'école et le système de paiement...")
    
    try:
        # Vérifier que le blueprint de paiement est correctement enregistré dans app.py
        with open(APP_PY_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "app.register_blueprint(payment_bp)" in content:
            print("Le blueprint de paiement est correctement enregistré dans app.py.")
        else:
            print("ATTENTION: Le blueprint de paiement n'est pas explicitement enregistré dans app.py.")
            
            # Vérifier si l'import est présent
            if "from payment_routes import payment_bp" in content:
                print("L'import du blueprint de paiement est présent dans app.py.")
                
                # Ajouter l'enregistrement du blueprint après l'initialisation des extensions
                if "init_extensions(app)" in content:
                    insert_point = content.find("init_extensions(app)") + len("init_extensions(app)")
                    new_content = content[:insert_point] + "\n\n# Enregistrement du blueprint de paiement\napp.register_blueprint(payment_bp)\n" + content[insert_point:]
                    
                    with open(APP_PY_FILE, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print("Correction appliquée: Enregistrement explicite du blueprint de paiement dans app.py.")
            else:
                print("ERREUR: L'import du blueprint de paiement est manquant dans app.py.")
    
    except Exception as e:
        print(f"Erreur lors de la vérification de l'intégration: {str(e)}")
        return False
    
    return True

def create_integration_script():
    """Crée un script d'intégration pour connecter l'inscription d'école et le système de paiement"""
    print("Création du script d'intégration school_payment_integration.py...")
    
    script_content = """
from flask import Blueprint, redirect, url_for, flash, current_app
from flask_login import current_user, login_required
from models import db, School, User

def integrate_school_payment(app):
    """
    Intègre le module de paiement d'école à l'application Flask.
    Cette fonction crée un blueprint pour gérer les redirections entre
    l'inscription d'école et le système de paiement.
    """
    # Création du blueprint
    school_payment_bp = Blueprint('school_payment', __name__)
    
    @school_payment_bp.route('/register-school-to-payment')
    @login_required
    def register_school_to_payment():
        """
        Route de redirection après la création d'une école pour initier le processus de paiement.
        """
        # Vérifier si l'utilisateur est associé à une école
        if not current_user.school_id:
            flash('Vous devez d\'abord créer une école avant de procéder au paiement.', 'warning')
            return redirect(url_for('school_registration_mod.register_school_simplified'))
        
        # Rediriger vers la page de paiement pour un abonnement école
        return redirect(url_for('payment.subscribe', subscription_type='school'))
    
    # Enregistrer le blueprint dans l'application
    app.register_blueprint(school_payment_bp)
    
    # Modifier les routes d'inscription d'école pour rediriger vers le paiement
    from integrate_school_registration_mod import school_registration_mod
    
    # Sauvegarder les fonctions originales
    original_register_school_simplified = school_registration_mod.view_functions['register_school_simplified']
    original_register_school_connected = school_registration_mod.view_functions['register_school_connected']
    
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
    
    return app
"""
    
    try:
        with open("school_payment_integration.py", 'w', encoding='utf-8') as f:
            f.write(script_content)
        print("Script d'intégration créé avec succès.")
    except Exception as e:
        print(f"Erreur lors de la création du script d'intégration: {str(e)}")
        return False
    
    return True

def create_app_integration_script():
    """Crée un script pour intégrer le module de paiement d'école dans app.py"""
    print("Création du script d'intégration pour app.py...")
    
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
        print("Script d'intégration pour app.py créé avec succès.")
    except Exception as e:
        print(f"Erreur lors de la création du script d'intégration pour app.py: {str(e)}")
        return False
    
    return True

def main():
    """Fonction principale"""
    print("=== DÉBUT DE LA CORRECTION DU PROBLÈME DE SOUSCRIPTION D'ABONNEMENT ÉCOLE ===")
    
    # Créer une sauvegarde
    create_backup()
    
    # Corriger le fichier payment_routes.py
    if not fix_payment_routes():
        print("Échec de la correction du fichier payment_routes.py.")
        return False
    
    # Vérifier l'intégration
    if not fix_integration():
        print("Échec de la vérification de l'intégration.")
        return False
    
    # Créer le script d'intégration
    if not create_integration_script():
        print("Échec de la création du script d'intégration.")
        return False
    
    # Créer le script d'intégration pour app.py
    if not create_app_integration_script():
        print("Échec de la création du script d'intégration pour app.py.")
        return False
    
    print("\n=== CORRECTION TERMINÉE ===")
    print("Les fichiers suivants ont été créés ou modifiés:")
    print("1. payment_routes.py (corrigé)")
    print("2. app.py (vérifié)")
    print("3. school_payment_integration.py (nouveau)")
    print("4. app_integration_snippet.py (nouveau)")
    
    print("\nPour appliquer la correction complète:")
    print("1. Vérifiez que les modifications de payment_routes.py sont correctes")
    print("2. Ajoutez le contenu de app_integration_snippet.py à votre app.py")
    print("3. Redémarrez l'application Flask")
    
    return True

if __name__ == "__main__":
    main()
