#!/usr/bin/env python3
"""
Test d'intégration Stripe avec clés configurées
"""

import os
import sys

def test_stripe_with_keys():
    """Tester Stripe avec les clés configurées"""
    print("=== TEST INTEGRATION STRIPE ===")
    
    # Vérifier les variables d'environnement
    stripe_key = os.environ.get('STRIPE_SECRET_KEY')
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    if not stripe_key:
        print("ERREUR: STRIPE_SECRET_KEY manquant")
        print("Configurez avec: $env:STRIPE_SECRET_KEY=\"sk_test_...\"")
        return False
    
    if not webhook_secret:
        print("ERREUR: STRIPE_WEBHOOK_SECRET manquant") 
        print("Configurez avec: $env:STRIPE_WEBHOOK_SECRET=\"whsec_...\"")
        return False
    
    print(f"STRIPE_SECRET_KEY: {stripe_key[:12]}...")
    print(f"STRIPE_WEBHOOK_SECRET: {webhook_secret[:12]}...")
    
    # Tester la connexion Stripe
    try:
        import stripe
        stripe.api_key = stripe_key
        
        # Test simple : lister les produits (ne crée rien)
        products = stripe.Product.list(limit=1)
        print("Connexion Stripe: OK")
        
        return True
        
    except stripe.error.AuthenticationError:
        print("ERREUR: Clé Stripe invalide")
        return False
    except Exception as e:
        print(f"ERREUR Stripe: {e}")
        return False

def test_payment_flow():
    """Tester le flux de paiement complet"""
    print("\n=== TEST FLUX PAIEMENT ===")
    
    try:
        # Ajouter le répertoire courant au path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from app import app
        from models import User
        from payment_service import payment_service
        
        with app.app_context():
            # Créer un utilisateur de test
            test_user = User(
                name="Test User",
                username="testuser",
                email="test@example.com",
                role="teacher"
            )
            
            # Tester la création d'une session de paiement
            try:
                session = payment_service.create_checkout_session(test_user, 'teacher')
                print(f"Session de paiement créée: {session.id}")
                print(f"URL de paiement: {session.url}")
                print("Flux de paiement: OK")
                return True
                
            except Exception as e:
                print(f"ERREUR lors de la création de session: {e}")
                return False
                
    except Exception as e:
        print(f"ERREUR dans le test du flux: {e}")
        return False

def generate_test_commands():
    """Générer les commandes de test"""
    print("\n=== COMMANDES DE TEST ===")
    print("1. Configurer les clés Stripe:")
    print("   $env:STRIPE_SECRET_KEY=\"sk_test_votre_cle\"")
    print("   $env:STRIPE_WEBHOOK_SECRET=\"whsec_votre_webhook\"")
    print("")
    print("2. Relancer ce test:")
    print("   python test_stripe_integration.py")
    print("")
    print("3. Tester l'interface:")
    print("   http://127.0.0.1:5000/payment/subscribe/teacher")
    print("   http://127.0.0.1:5000/payment/subscribe/school")

def main():
    """Test principal"""
    print("TEST INTEGRATION STRIPE")
    print("=" * 40)
    
    # Test 1: Configuration
    config_ok = test_stripe_with_keys()
    
    if config_ok:
        # Test 2: Flux de paiement
        flow_ok = test_payment_flow()
        
        if flow_ok:
            print("\n" + "=" * 40)
            print("INTEGRATION STRIPE: COMPLETE!")
            print("Le système de paiement est prêt à utiliser.")
            print("\nProchaines étapes:")
            print("1. Tester les paiements en mode test")
            print("2. Configurer les webhooks sur Stripe")
            print("3. Tester l'approbation automatique")
        else:
            print("\nIntégration partiellement fonctionnelle.")
    else:
        print("\nConfiguration requise avant de continuer.")
        generate_test_commands()

if __name__ == "__main__":
    main()
