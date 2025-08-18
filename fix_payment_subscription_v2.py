"""
Script de correction pour le probleme de souscription d'abonnement ecole.
Ce script corrige le probleme de redirection entre l'inscription d'ecole et le systeme de paiement.
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
    """Cree une sauvegarde des fichiers avant modification"""
    print(f"Creation du repertoire de sauvegarde {BACKUP_DIR}...")
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    # Sauvegarde des fichiers
    for file in [PAYMENT_ROUTES_FILE, APP_PY_FILE]:
        if os.path.exists(file):
            backup_path = os.path.join(BACKUP_DIR, file)
            print(f"Sauvegarde de {file} vers {backup_path}...")
            shutil.copy2(file, backup_path)
    
    print("Sauvegarde terminee.")

def fix_payment_routes():
    """Corrige le fichier payment_routes.py pour s'assurer que la fonction subscribe est correctement enregistree"""
    print("Verification et correction du fichier payment_routes.py...")
    
    try:
        with open(PAYMENT_ROUTES_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifier si la fonction subscribe est correctement definie
        if "@payment_bp.route('/subscribe/<subscription_type>')" in content:
            print("La route /subscribe/<subscription_type> est deja definie.")
            
            # Verifier si la fonction est correctement nommee
            if "def subscribe(subscription_type):" in content:
                print("La fonction subscribe est correctement nommee.")
            else:
                print("ERREUR: La fonction subscribe n'est pas correctement nommee.")
                # Correction du nom de la fonction si necessaire
                content = content.replace("def subscribe_route(subscription_type):", "def subscribe(subscription_type):")
                
                with open(PAYMENT_ROUTES_FILE, 'w', encoding='utf-8') as f:
                    f.write(content)
                print("Correction appliquee: Renommage de la fonction subscribe_route en subscribe.")
        else:
            print("ERREUR: La route /subscribe/<subscription_type> n'est pas definie.")
            # Ici, on pourrait ajouter la definition complete de la route si elle etait manquante
    
    except Exception as e:
        print(f"Erreur lors de la correction de payment_routes.py: {str(e)}")
        return False
    
    return True

def fix_integration():
    """Verifie et corrige l'integration entre le module d'inscription d'ecole et le systeme de paiement"""
    print("Verification de l'integration entre le module d'inscription d'ecole et le systeme de paiement...")
    
    try:
        # Verifier que le blueprint de paiement est correctement enregistre dans app.py
        with open(APP_PY_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "app.register_blueprint(payment_bp)" in content:
            print("Le blueprint de paiement est correctement enregistre dans app.py.")
        else:
            print("ATTENTION: Le blueprint de paiement n'est pas explicitement enregistre dans app.py.")
            
            # Verifier si l'import est present
            if "from payment_routes import payment_bp" in content:
                print("L'import du blueprint de paiement est present dans app.py.")
                
                # Ajouter l'enregistrement du blueprint apres l'initialisation des extensions
                if "init_extensions(app)" in content:
                    insert_point = content.find("init_extensions(app)") + len("init_extensions(app)")
                    new_content = content[:insert_point] + "\n\n# Enregistrement du blueprint de paiement\napp.register_blueprint(payment_bp)\n" + content[insert_point:]
                    
                    with open(APP_PY_FILE, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print("Correction appliquee: Enregistrement explicite du blueprint de paiement dans app.py.")
            else:
                print("ERREUR: L'import du blueprint de paiement est manquant dans app.py.")
    
    except Exception as e:
        print(f"Erreur lors de la verification de l'integration: {str(e)}")
        return False
    
    return True

def create_integration_script():
    """Cree un script d'integration pour connecter l'inscription d'ecole et le systeme de paiement"""
    print("Creation du script d'integration school_payment_integration.py...")
    
    script_content = '''
from flask import Blueprint, redirect, url_for, flash, current_app
from flask_login import current_user, login_required
from models import db, School, User

def integrate_school_payment(app):
    """
    Integre le module de paiement d'ecole a l'application Flask.
    Cette fonction cree un blueprint pour gerer les redirections entre
    l'inscription d'ecole et le systeme de paiement.
    """
    # Creation du blueprint
    school_payment_bp = Blueprint('school_payment', __name__)
    
    @school_payment_bp.route('/register-school-to-payment')
    @login_required
    def register_school_to_payment():
        """
        Route de redirection apres la creation d'une ecole pour initier le processus de paiement.
        """
        # Verifier si l'utilisateur est associe a une ecole
        if not current_user.school_id:
            flash('Vous devez d\\'abord creer une ecole avant de proceder au paiement.', 'warning')
            return redirect(url_for('school_registration_mod.register_school_simplified'))
        
        # Rediriger vers la page de paiement pour un abonnement ecole
        return redirect(url_for('payment.subscribe', subscription_type='school'))
    
    # Enregistrer le blueprint dans l'application
    app.register_blueprint(school_payment_bp)
    
    # Modifier les routes d'inscription d'ecole pour rediriger vers le paiement
    from integrate_school_registration_mod import school_registration_mod
    
    # Sauvegarder les fonctions originales
    original_register_school_simplified = school_registration_mod.view_functions['register_school_simplified']
    original_register_school_connected = school_registration_mod.view_functions['register_school_connected']
    
    # Definir les nouvelles fonctions avec redirection vers le paiement
    @school_registration_mod.route('/register-school-simplified', methods=['GET', 'POST'])
    @login_required
    def register_school_simplified_with_payment():
        # Appeler la fonction originale
        result = original_register_school_simplified()
        
        # Si c'est une redirection (apres creation reussie), rediriger vers le paiement
        if hasattr(result, 'status_code') and result.status_code == 302:
            current_app.logger.info("Ecole creee avec succes, redirection vers le paiement...")
            return redirect(url_for('school_payment.register_school_to_payment'))
        
        # Sinon, retourner le resultat original
        return result
    
    @school_registration_mod.route('/register-school-connected', methods=['GET', 'POST'])
    @login_required
    def register_school_connected_with_payment():
        # Appeler la fonction originale
        result = original_register_school_connected()
        
        # Si c'est une redirection (apres creation reussie), rediriger vers le paiement
        if hasattr(result, 'status_code') and result.status_code == 302:
            current_app.logger.info("Ecole creee avec succes, redirection vers le paiement...")
            return redirect(url_for('school_payment.register_school_to_payment'))
        
        # Sinon, retourner le resultat original
        return result
    
    # Remplacer les fonctions originales par les nouvelles
    school_registration_mod.view_functions['register_school_simplified'] = register_school_simplified_with_payment
    school_registration_mod.view_functions['register_school_connected'] = register_school_connected_with_payment
    
    current_app.logger.info("Integration du module de paiement d'ecole terminee.")
    
    return app
'''
    
    try:
        with open("school_payment_integration.py", 'w', encoding='utf-8') as f:
            f.write(script_content)
        print("Script d'integration cree avec succes.")
    except Exception as e:
        print(f"Erreur lors de la creation du script d'integration: {str(e)}")
        return False
    
    return True

def create_app_integration_script():
    """Cree un script pour integrer le module de paiement d'ecole dans app.py"""
    print("Creation du script d'integration pour app.py...")
    
    script_content = """
# Ajoutez ces lignes a votre app.py apres l'initialisation des extensions
# et l'integration du module d'inscription d'ecole

# Integration du module de paiement d'ecole
from school_payment_integration import integrate_school_payment
integrate_school_payment(app)
"""
    
    try:
        with open("app_integration_snippet.py", 'w', encoding='utf-8') as f:
            f.write(script_content)
        print("Script d'integration pour app.py cree avec succes.")
    except Exception as e:
        print(f"Erreur lors de la creation du script d'integration pour app.py: {str(e)}")
        return False
    
    return True

def main():
    """Fonction principale"""
    print("=== DEBUT DE LA CORRECTION DU PROBLEME DE SOUSCRIPTION D'ABONNEMENT ECOLE ===")
    
    # Creer une sauvegarde
    create_backup()
    
    # Corriger le fichier payment_routes.py
    if not fix_payment_routes():
        print("Echec de la correction du fichier payment_routes.py.")
        return False
    
    # Verifier l'integration
    if not fix_integration():
        print("Echec de la verification de l'integration.")
        return False
    
    # Creer le script d'integration
    if not create_integration_script():
        print("Echec de la creation du script d'integration.")
        return False
    
    # Creer le script d'integration pour app.py
    if not create_app_integration_script():
        print("Echec de la creation du script d'integration pour app.py.")
        return False
    
    print("\n=== CORRECTION TERMINEE ===")
    print("Les fichiers suivants ont ete crees ou modifies:")
    print("1. payment_routes.py (corrige)")
    print("2. app.py (verifie)")
    print("3. school_payment_integration.py (nouveau)")
    print("4. app_integration_snippet.py (nouveau)")
    
    print("\nPour appliquer la correction complete:")
    print("1. Verifiez que les modifications de payment_routes.py sont correctes")
    print("2. Ajoutez le contenu de app_integration_snippet.py a votre app.py")
    print("3. Redemarrez l'application Flask")
    
    return True

if __name__ == "__main__":
    main()
