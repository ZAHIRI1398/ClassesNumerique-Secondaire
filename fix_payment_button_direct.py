import os
import sys
import re
from flask import Flask, render_template, url_for

# Configuration minimale pour tester les routes
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test_key'

# Fonction pour vérifier si le blueprint de paiement est correctement importé et enregistré
def check_payment_blueprint():
    print("=== VÉRIFICATION DU BLUEPRINT DE PAIEMENT ===")
    
    # Lire le contenu du fichier app.py
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Erreur lors de la lecture de app.py: {str(e)}")
        return False
    
    # Vérifier les imports du blueprint de paiement
    import_pattern = r'from\s+payment_routes\s+import\s+payment_bp'
    imports = re.findall(import_pattern, content)
    print(f"Nombre d'imports du blueprint de paiement: {len(imports)}")
    
    # Vérifier les enregistrements du blueprint
    register_pattern = r'app\.register_blueprint\s*\(\s*payment_bp\s*(?:,\s*url_prefix\s*=\s*[\'"]/payment[\'"]\s*)?\)'
    registrations = re.findall(register_pattern, content)
    print(f"Nombre d'enregistrements du blueprint de paiement: {len(registrations)}")
    
    # Vérifier si le blueprint est correctement importé et enregistré
    if len(imports) == 1 and len(registrations) == 1:
        print("✓ Le blueprint de paiement est correctement importé et enregistré.")
        return True
    else:
        print("✗ Problème détecté avec le blueprint de paiement.")
        return False

# Fonction pour corriger le blueprint de paiement
def fix_payment_blueprint():
    print("=== CORRECTION DU BLUEPRINT DE PAIEMENT ===")
    
    # Lire le contenu du fichier app.py
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Erreur lors de la lecture de app.py: {str(e)}")
        return False
    
    # Créer une sauvegarde
    backup_dir = "backup_payment_button_fix_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(backup_dir, exist_ok=True)
    
    try:
        with open(os.path.join(backup_dir, 'app.py'), 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Sauvegarde de app.py créée dans {backup_dir}")
    except Exception as e:
        print(f"Erreur lors de la création de la sauvegarde: {str(e)}")
    
    # Vérifier les imports du blueprint de paiement
    import_pattern = r'from\s+payment_routes\s+import\s+payment_bp'
    imports = re.findall(import_pattern, content)
    
    # Vérifier les enregistrements du blueprint
    register_pattern = r'app\.register_blueprint\s*\(\s*payment_bp\s*(?:,\s*url_prefix\s*=\s*[\'"]/payment[\'"]\s*)?\)'
    registrations = re.findall(register_pattern, content)
    
    # Corriger les duplications si nécessaire
    if len(imports) > 1:
        # Supprimer toutes les occurrences sauf la première
        content = re.sub(import_pattern, '', content, count=len(imports)-1)
        print("Imports dupliqués supprimés.")
    
    if len(registrations) > 1:
        # Supprimer toutes les occurrences sauf la première
        content = re.sub(register_pattern, '', content, count=len(registrations)-1)
        print("Enregistrements dupliqués supprimés.")
    
    # S'assurer qu'il y a au moins un import et un enregistrement
    if len(imports) == 0:
        # Ajouter l'import après les autres imports
        import_section = re.search(r'import.*?\n\n', content, re.DOTALL)
        if import_section:
            position = import_section.end()
            content = content[:position] + "from payment_routes import payment_bp\n" + content[position:]
            print("Import du blueprint de paiement ajouté.")
    
    if len(registrations) == 0:
        # Ajouter l'enregistrement après les autres enregistrements de blueprint
        last_register = re.search(r'app\.register_blueprint\([^)]*\)[^\n]*\n', content)
        if last_register:
            position = last_register.end()
            content = content[:position] + "app.register_blueprint(payment_bp, url_prefix='/payment')\n" + content[position:]
            print("Enregistrement du blueprint de paiement ajouté.")
    
    # Écrire le contenu corrigé
    try:
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("✓ Corrections appliquées avec succès à app.py")
        return True
    except Exception as e:
        print(f"Erreur lors de l'écriture des corrections: {str(e)}")
        return False

# Fonction pour vérifier la route du bouton d'abonnement
def test_payment_button():
    print("=== TEST DU BOUTON D'ABONNEMENT ÉCOLE ===")
    
    # Vérifier si le fichier payment_routes.py existe
    if not os.path.exists('payment_routes.py'):
        print("✗ Le fichier payment_routes.py n'existe pas.")
        return False
    
    # Lire le contenu du fichier payment_routes.py
    try:
        with open('payment_routes.py', 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Erreur lors de la lecture de payment_routes.py: {str(e)}")
        return False
    
    # Vérifier si la route subscribe existe
    subscribe_pattern = r'@payment_bp\.route\s*\(\s*[\'"]\/subscribe\/(?:<.*?>|[^\'"])*[\'"]\s*(?:,\s*methods\s*=\s*\[[^\]]*\])?\s*\)'
    subscribe_routes = re.findall(subscribe_pattern, content)
    
    if not subscribe_routes:
        print("✗ La route subscribe n'a pas été trouvée dans payment_routes.py")
        return False
    
    print(f"Route subscribe trouvée: {subscribe_routes[0]}")
    
    # Vérifier si la fonction subscribe existe
    subscribe_func_pattern = r'def\s+subscribe\s*\('
    subscribe_funcs = re.findall(subscribe_func_pattern, content)
    
    if not subscribe_funcs:
        print("✗ La fonction subscribe n'a pas été trouvée dans payment_routes.py")
        return False
    
    print("✓ La fonction subscribe existe dans payment_routes.py")
    
    # Vérifier le template select_school.html
    if not os.path.exists('templates/payment/select_school.html'):
        print("✗ Le template select_school.html n'existe pas.")
        return False
    
    # Lire le contenu du template
    try:
        with open('templates/payment/select_school.html', 'r', encoding='utf-8') as f:
            template_content = f.read()
    except Exception as e:
        print(f"Erreur lors de la lecture du template: {str(e)}")
        return False
    
    # Vérifier si le bouton d'abonnement existe
    button_pattern = r'href\s*=\s*[\'"]{{ url_for\s*\(\s*[\'"]payment\.subscribe[\'"]\s*,\s*subscription_type\s*=\s*[\'"]school[\'"]\s*\) }}[\'"]'
    buttons = re.findall(button_pattern, template_content)
    
    if not buttons:
        print("✗ Le bouton d'abonnement n'a pas été trouvé dans le template.")
        return False
    
    print("✓ Le bouton d'abonnement existe dans le template.")
    
    # Créer un script de test pour vérifier la route
    test_script = """
from flask import Flask
from payment_routes import payment_bp
import requests

app = Flask(__name__)
app.register_blueprint(payment_bp, url_prefix='/payment')

with app.test_request_context():
    url = url_for('payment.subscribe', subscription_type='school')
    print(f"URL générée pour payment.subscribe: {url}")

# Tester la route avec requests
try:
    response = requests.get('http://localhost' + url)
    print(f"Statut de la réponse: {response.status_code}")
    if response.status_code == 200 or response.status_code == 302:
        print("✓ La route payment.subscribe fonctionne correctement.")
    else:
        print(f"✗ La route payment.subscribe a retourné un statut {response.status_code}")
except Exception as e:
    print(f"Erreur lors du test de la route: {str(e)}")
"""
    
    # Écrire le script de test
    try:
        with open('test_payment_button.py', 'w', encoding='utf-8') as f:
            f.write(test_script)
        print("✓ Script de test créé: test_payment_button.py")
    except Exception as e:
        print(f"Erreur lors de la création du script de test: {str(e)}")
    
    return True

# Fonction principale
def main():
    from datetime import datetime
    
    print("=== CORRECTION DU PROBLÈME DU BOUTON D'ABONNEMENT ÉCOLE ===")
    print(f"Date et heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Vérifier le blueprint de paiement
    if not check_payment_blueprint():
        # Corriger le blueprint de paiement
        fix_payment_blueprint()
    
    # Tester le bouton d'abonnement
    test_payment_button()
    
    print("\n=== RECOMMANDATIONS ===")
    print("1. Exécutez le script de test: python test_payment_button.py")
    print("2. Redémarrez l'application Flask")
    print("3. Testez le bouton 'Souscrire un nouvel abonnement école' dans l'interface")
    print("4. Vérifiez les logs de l'application pour détecter d'éventuelles erreurs")

if __name__ == "__main__":
    main()
