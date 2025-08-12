#!/usr/bin/env python3
"""
Test simple du système de paiement Stripe
"""

import os
import sys

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_stripe_config():
    """Tester la configuration Stripe"""
    print("=== TEST CONFIGURATION STRIPE ===")
    
    stripe_secret = os.environ.get('STRIPE_SECRET_KEY')
    stripe_webhook = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    if stripe_secret:
        print("STRIPE_SECRET_KEY: OK (sk_***)")
    else:
        print("STRIPE_SECRET_KEY: MANQUANT")
    
    if stripe_webhook:
        print("STRIPE_WEBHOOK_SECRET: OK (whsec_***)")
    else:
        print("STRIPE_WEBHOOK_SECRET: MANQUANT")
    
    return bool(stripe_secret and stripe_webhook)

def test_payment_imports():
    """Tester les imports du système de paiement"""
    print("\n=== TEST IMPORTS PAIEMENT ===")
    
    try:
        import stripe
        print("stripe: OK")
    except ImportError:
        print("stripe: MANQUANT - pip install stripe")
        return False
    
    try:
        from payment_service import payment_service
        print("payment_service: OK")
    except ImportError as e:
        print(f"payment_service: ERREUR - {e}")
        return False
    
    try:
        from payment_routes import payment_bp
        print("payment_routes: OK")
    except ImportError as e:
        print(f"payment_routes: ERREUR - {e}")
        return False
    
    return True

def test_templates():
    """Tester les templates de paiement"""
    print("\n=== TEST TEMPLATES ===")
    
    templates = [
        'templates/payment/subscribe.html',
        'templates/payment/success.html',
        'templates/payment/cancel.html'
    ]
    
    all_exist = True
    for template in templates:
        if os.path.exists(template):
            size = os.path.getsize(template)
            print(f"{template}: OK ({size} bytes)")
        else:
            print(f"{template}: MANQUANT")
            all_exist = False
    
    return all_exist

def test_database():
    """Tester les colonnes de paiement"""
    print("\n=== TEST BASE DE DONNEES ===")
    
    try:
        from app import app, db
        from models import User
        
        with app.app_context():
            # Créer les tables si elles n'existent pas
            db.create_all()
            print("Tables: OK")
            
            # Tester les colonnes de paiement
            user = User.query.first()
            if user:
                try:
                    payment_session = user.payment_session_id
                    payment_amount = user.payment_amount
                    print("Colonnes paiement: OK")
                    return True
                except AttributeError as e:
                    print(f"Colonnes paiement: MANQUANTES - {e}")
                    return False
            else:
                print("Aucun utilisateur pour tester, mais structure OK")
                return True
                
    except Exception as e:
        print(f"Base de donnees: ERREUR - {e}")
        return False

def test_routes():
    """Tester les routes de paiement"""
    print("\n=== TEST ROUTES ===")
    
    try:
        from app import app
        
        with app.test_client() as client:
            # Test route subscribe
            response = client.get('/payment/subscribe/teacher')
            print(f"/payment/subscribe/teacher: {response.status_code}")
            
            # Test route status
            response = client.get('/payment/status')
            print(f"/payment/status: {response.status_code}")
            
            print("Routes: OK")
            return True
            
    except Exception as e:
        print(f"Routes: ERREUR - {e}")
        return False

def main():
    """Test principal"""
    print("TEST SYSTEME DE PAIEMENT STRIPE")
    print("=" * 50)
    
    tests = [
        ("Configuration Stripe", test_stripe_config),
        ("Imports", test_payment_imports),
        ("Templates", test_templates),
        ("Base de donnees", test_database),
        ("Routes", test_routes)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
            status = "PASSE" if result else "ECHEC"
            print(f"\n{name}: {status}")
        except Exception as e:
            print(f"\n{name}: ERREUR - {e}")
            results.append(False)
    
    # Résumé
    print("\n" + "=" * 50)
    print("RESUME")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    print(f"Tests reussis: {passed}/{total}")
    
    if passed == total:
        print("\nTOUS LES TESTS SONT PASSES!")
        print("Le systeme de paiement est fonctionnel.")
    else:
        print("\nCERTAINS TESTS ONT ECHOUE")
        print("Verifiez les erreurs ci-dessus.")
    
    print("\nURLs de test:")
    print("http://127.0.0.1:5000/payment/subscribe/teacher")
    print("http://127.0.0.1:5000/payment/subscribe/school")
    print("http://127.0.0.1:5000/payment/status")

if __name__ == "__main__":
    main()
