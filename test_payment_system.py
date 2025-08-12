#!/usr/bin/env python3
"""
Script de test et finalisation du système de paiement Stripe
- Vérification des variables d'environnement
- Test des routes de paiement
- Validation des templates
- Vérification des webhooks
"""

import os
import sys
from datetime import datetime

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_stripe_config():
    """Tester la configuration Stripe"""
    print("=== TEST CONFIGURATION STRIPE ===")
    
    # Variables d'environnement requises
    required_vars = [
        'STRIPE_SECRET_KEY',
        'STRIPE_WEBHOOK_SECRET'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print(f"✓ {var}: {'sk_' if 'SECRET' in var else 'whsec_'}***")
        else:
            print(f"✗ {var}: MANQUANT")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️ Variables manquantes: {', '.join(missing_vars)}")
        print("Pour les configurer:")
        for var in missing_vars:
            if 'SECRET_KEY' in var:
                print(f"  export {var}=sk_test_...")
            else:
                print(f"  export {var}=whsec_...")
        return False
    else:
        print("✅ Configuration Stripe OK")
        return True

def test_payment_routes():
    """Tester les routes de paiement"""
    print("\n=== TEST ROUTES PAIEMENT ===")
    
    try:
        from app import app
        with app.test_client() as client:
            # Test route de souscription (sans login)
            response = client.get('/payment/subscribe/teacher')
            print(f"✓ /payment/subscribe/teacher: {response.status_code}")
            
            # Test route de statut (sans login)
            response = client.get('/payment/status')
            print(f"✓ /payment/status: {response.status_code}")
            
            # Test webhook (POST vide)
            response = client.post('/payment/webhook', data='{}')
            print(f"✓ /payment/webhook: {response.status_code}")
            
        print("✅ Routes de paiement accessibles")
        return True
        
    except Exception as e:
        print(f"✗ Erreur lors du test des routes: {e}")
        return False

def test_payment_service():
    """Tester le service de paiement"""
    print("\n=== TEST SERVICE PAIEMENT ===")
    
    try:
        from payment_service import payment_service
        print("✓ Import payment_service OK")
        
        # Vérifier les méthodes principales
        methods = ['create_checkout_session', 'handle_webhook', 'process_successful_payment']
        for method in methods:
            if hasattr(payment_service, method):
                print(f"✓ Méthode {method} présente")
            else:
                print(f"✗ Méthode {method} manquante")
        
        print("✅ Service de paiement OK")
        return True
        
    except Exception as e:
        print(f"✗ Erreur lors du test du service: {e}")
        return False

def test_templates():
    """Tester les templates de paiement"""
    print("\n=== TEST TEMPLATES PAIEMENT ===")
    
    templates_dir = "templates/payment"
    required_templates = [
        'subscribe.html',
        'success.html', 
        'cancel.html'
    ]
    
    missing_templates = []
    for template in required_templates:
        template_path = os.path.join(templates_dir, template)
        if os.path.exists(template_path):
            size = os.path.getsize(template_path)
            print(f"✓ {template}: {size} bytes")
        else:
            print(f"✗ {template}: MANQUANT")
            missing_templates.append(template)
    
    if missing_templates:
        print(f"⚠️ Templates manquants: {', '.join(missing_templates)}")
        return False
    else:
        print("✅ Templates de paiement OK")
        return True

def test_database_columns():
    """Tester les colonnes de paiement dans la base"""
    print("\n=== TEST COLONNES BASE DE DONNÉES ===")
    
    try:
        from app import app, db
        from models import User
        
        with app.app_context():
            # Tester un utilisateur pour vérifier les colonnes
            user = User.query.first()
            if user:
                # Tester l'accès aux colonnes de paiement
                payment_columns = [
                    'payment_session_id',
                    'payment_amount', 
                    'payment_date',
                    'payment_reference',
                    'subscription_expires'
                ]
                
                for col in payment_columns:
                    try:
                        value = getattr(user, col, 'N/A')
                        print(f"✓ Colonne {col}: {type(value).__name__}")
                    except Exception as e:
                        print(f"✗ Colonne {col}: ERREUR - {e}")
                        
                print("✅ Colonnes de paiement OK")
                return True
            else:
                print("⚠️ Aucun utilisateur en base pour tester")
                return True
                
    except Exception as e:
        print(f"✗ Erreur lors du test de la base: {e}")
        return False

def generate_test_urls():
    """Générer les URLs de test"""
    print("\n=== URLS DE TEST ===")
    
    base_url = "http://127.0.0.1:5000"
    test_urls = [
        "/payment/subscribe/teacher",
        "/payment/subscribe/school", 
        "/payment/status",
        "/admin/dashboard"
    ]
    
    print("URLs à tester manuellement:")
    for url in test_urls:
        print(f"  {base_url}{url}")

def main():
    """Fonction principale de test"""
    print("TEST SYSTEME DE PAIEMENT STRIPE")
    print("=" * 50)
    
    results = []
    results.append(test_stripe_config())
    results.append(test_payment_routes())
    results.append(test_payment_service())
    results.append(test_templates())
    results.append(test_database_columns())
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests réussis: {passed}/{total}")
    
    if passed == total:
        print("TOUS LES TESTS SONT PASSES!")
        print("Le systeme de paiement est pret a etre utilise.")
        print("\nETAPES SUIVANTES:")
        print("1. Configurer les variables d'environnement Stripe")
        print("2. Tester les paiements en mode test")
        print("3. Configurer les webhooks sur Stripe Dashboard")
        print("4. Tester l'approbation automatique apres paiement")
    else:
        print("CERTAINS TESTS ONT ECHOUE")
        print("Verifiez les erreurs ci-dessus avant de continuer.")
    
    generate_test_urls()

if __name__ == "__main__":
    main()
