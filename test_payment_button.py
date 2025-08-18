
from flask import Flask, url_for
from werkzeug.test import Client
from werkzeug.wrappers import Response
import sys
import os

def test_payment_button():
    """
    Test le fonctionnement du bouton 'Souscrire un nouvel abonnement école'
    en vérifiant que la route payment.subscribe est correctement générée.
    """
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
            print("[OK] La route payment.subscribe fonctionne correctement.")
        elif response.status_code == 302:
            print("[ATTENTION] La route payment.subscribe redirige (code 302). Cela peut être normal selon la logique de l'application.")
        else:
            print(f"[ERREUR] La route payment.subscribe retourne un code d'erreur: {response.status_code}")
            
        # Vérifier que la route select_school existe
        select_school_url = url_for('payment.select_school')
        print(f"URL générée pour payment.select_school: {select_school_url}")
        
        select_school_response = client.get(select_school_url)
        print(f"Statut de la réponse: {select_school_response.status_code}")
        
        if select_school_response.status_code == 200:
            print("[OK] La route payment.select_school fonctionne correctement.")
        elif select_school_response.status_code == 302:
            print("[ATTENTION] La route payment.select_school redirige (code 302). Cela peut être normal selon la logique de l'application.")
        else:
            print(f"[ERREUR] La route payment.select_school retourne un code d'erreur: {select_school_response.status_code}")

if __name__ == "__main__":
    print("=== TEST DU BOUTON D'ABONNEMENT ÉCOLE ===")
    test_payment_button()
    print("=== FIN DU TEST ===")
