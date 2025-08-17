#!/usr/bin/env python3
"""
Script de diagnostic pour simuler une soumission de formulaire fill_in_blanks
et vérifier pourquoi seul le premier mot est compté
"""

import sys
import json
import requests
from bs4 import BeautifulSoup
import argparse
import time

def simulate_form_submission(url, email, password, exercise_id):
    """Simule une soumission de formulaire pour un exercice fill_in_blanks"""
    session = requests.Session()
    
    # 1. Se connecter
    print(f"[INFO] Connexion à {url}/login")
    login_page = session.get(f"{url}/login")
    soup = BeautifulSoup(login_page.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'}).get('value')
    
    login_data = {
        'email': email,
        'password': password,
        'csrf_token': csrf_token
    }
    
    login_response = session.post(f"{url}/login", data=login_data)
    if "Se déconnecter" not in login_response.text and "Logout" not in login_response.text:
        print("[ERREUR] Échec de la connexion")
        return
    
    print("[OK] Connexion réussie")
    
    # 2. Accéder à l'exercice
    print(f"[INFO] Accès à l'exercice {exercise_id}")
    exercise_page = session.get(f"{url}/exercise/{exercise_id}")
    if exercise_page.status_code != 200:
        print(f"[ERREUR] Impossible d'accéder à l'exercice: {exercise_page.status_code}")
        return
    
    # 3. Analyser le formulaire
    soup = BeautifulSoup(exercise_page.text, 'html.parser')
    form = soup.find('form', {'action': lambda x: x and f'/exercise/{exercise_id}/answer' in x})
    
    if not form:
        print("[ERREUR] Formulaire non trouvé")
        return
    
    # 4. Trouver tous les champs de saisie
    inputs = form.find_all('input', {'name': lambda x: x and x.startswith('answer_')})
    if not inputs:
        print("[ERREUR] Aucun champ de saisie trouvé")
        return
    
    print(f"[INFO] {len(inputs)} champs de saisie trouvés:")
    for i, input_field in enumerate(inputs):
        print(f"  - {input_field.get('name')}")
    
    # 5. Préparer les données du formulaire
    form_data = {
        'csrf_token': form.find('input', {'name': 'csrf_token'}).get('value')
    }
    
    # Remplir tous les champs avec des réponses de test
    for i, input_field in enumerate(inputs):
        form_data[input_field.get('name')] = f"test_mot_{i+1}"
    
    print(f"[INFO] Données du formulaire préparées: {form_data}")
    
    # 6. Soumettre le formulaire
    print(f"[INFO] Soumission du formulaire")
    submit_url = f"{url}/exercise/{exercise_id}/answer"
    response = session.post(submit_url, data=form_data)
    
    if response.status_code != 200:
        print(f"[ERREUR] Échec de la soumission: {response.status_code}")
        return
    
    # 7. Analyser la réponse
    print(f"[INFO] Analyse de la réponse")
    result_soup = BeautifulSoup(response.text, 'html.parser')
    
    # Chercher le score
    score_element = result_soup.find(text=lambda t: t and 'Score:' in t)
    if score_element:
        print(f"[RÉSULTAT] {score_element.strip()}")
    
    # Chercher les détails du feedback
    feedback_details = result_soup.find_all('div', {'class': 'feedback-detail'})
    if feedback_details:
        print(f"[INFO] Détails du feedback:")
        for detail in feedback_details:
            print(f"  - {detail.text.strip()}")
    
    # 8. Vérifier les dernières tentatives
    print(f"[INFO] Vérification des dernières tentatives")
    attempts_page = session.get(f"{url}/exercise/{exercise_id}/attempts")
    
    if attempts_page.status_code == 200:
        attempts_soup = BeautifulSoup(attempts_page.text, 'html.parser')
        attempts = attempts_soup.find_all('div', {'class': 'attempt-card'})
        
        if attempts:
            print(f"[INFO] {len(attempts)} tentatives trouvées")
            latest_attempt = attempts[0]
            score_text = latest_attempt.find(text=lambda t: t and 'Score:' in t)
            if score_text:
                print(f"[RÉSULTAT] Dernière tentative: {score_text.strip()}")
    
    # 9. Vérifier les logs côté serveur
    print(f"[INFO] Pour une analyse complète, vérifiez les logs du serveur avec les messages '[FILL_IN_BLANKS_DEBUG]'")

def main():
    parser = argparse.ArgumentParser(description="Diagnostic de soumission de formulaire fill_in_blanks")
    parser.add_argument("--url", default="https://web-production-9a047.up.railway.app", help="URL de base")
    parser.add_argument("--email", required=True, help="Email de connexion")
    parser.add_argument("--password", required=True, help="Mot de passe")
    parser.add_argument("--exercise_id", required=True, type=int, help="ID de l'exercice à tester")
    
    args = parser.parse_args()
    
    simulate_form_submission(args.url, args.email, args.password, args.exercise_id)

if __name__ == "__main__":
    main()
