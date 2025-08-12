#!/usr/bin/env python3
"""
Configuration temporaire des clés Stripe pour test
"""

import os

# Configuration des clés Stripe
os.environ['STRIPE_SECRET_KEY'] = 'sk_test_51RvPOe0BSlyiNZ4slnNGiOhR9uJl9TdQNTJsPXEVYz1V8XzMvd4NMZiCe2AcfZjcVkjj30ZMJMVjszgEMGJR5G7D00CHbiVjlG'
os.environ['STRIPE_WEBHOOK_SECRET'] = 'whsec_temp_for_testing'

print("Configuration Stripe appliquée:")
print(f"STRIPE_SECRET_KEY: {os.environ.get('STRIPE_SECRET_KEY', 'NON DÉFINI')[:20]}...")
print(f"STRIPE_WEBHOOK_SECRET: {os.environ.get('STRIPE_WEBHOOK_SECRET', 'NON DÉFINI')}")

# Test de connexion Stripe
try:
    import stripe
    stripe.api_key = os.environ['STRIPE_SECRET_KEY']
    
    # Test simple : récupérer les informations du compte
    account = stripe.Account.retrieve()
    print("CONNEXION STRIPE REUSSIE!")
    print(f"   Compte: {account.id}")
    print(f"   Email: {account.email}")
    print(f"   Pays: {account.country}")
    
except stripe.error.AuthenticationError:
    print("ERREUR: Authentification Stripe - Cle invalide")
except Exception as e:
    print(f"ERREUR Stripe: {e}")

# Test du service de paiement
try:
    import sys
    sys.path.insert(0, '.')
    
    from payment_service import payment_service
    from models import User
    
    # Créer un utilisateur de test fictif
    class TestUser:
        def __init__(self):
            self.id = 999
            self.name = "Test User"
            self.email = "test@example.com"
    
    test_user = TestUser()
    
    # Tester la création d'une session de paiement
    session = payment_service.create_checkout_session(test_user, 'teacher')
    print("SESSION DE PAIEMENT CREEE!")
    print(f"   ID: {session.id}")
    print(f"   URL: {session.url}")
    
except Exception as e:
    print(f"ERREUR lors du test du service de paiement: {e}")

print("\nCONFIGURATION STRIPE TERMINEE!")
print("Vous pouvez maintenant tester l'interface de paiement:")
print("http://127.0.0.1:5000/payment/subscribe/teacher")
print("http://127.0.0.1:5000/payment/subscribe/school")
