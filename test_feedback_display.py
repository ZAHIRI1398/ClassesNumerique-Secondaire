#!/usr/bin/env python3
"""
Script pour tester l'affichage du feedback pour les exercices fill_in_blanks
avec plusieurs mots par ligne
"""

import os
import sys
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Configuration
BASE_URL = "http://localhost:5000"
TEST_USERNAME = "test@example.com"
TEST_PASSWORD = "password"
TEST_EXERCISE_ID = 6  # ID de l'exercice fill_in_blanks à tester

def login(session):
    """Se connecte à l'application"""
    print("[INFO] Tentative de connexion...")
    login_url = urljoin(BASE_URL, "/login")
    response = session.get(login_url)
    
    # Vérifier si déjà connecté
    if "Déconnexion" in response.text:
        print("[INFO] Déjà connecté")
        return True
    
    # Soumettre le formulaire de connexion
    login_data = {
        "email": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
    response = session.post(login_url, data=login_data, allow_redirects=True)
    
    # Vérifier si la connexion a réussi
    if "Déconnexion" in response.text:
        print("[OK] Connexion réussie")
        return True
    else:
        print("[ERREUR] Échec de la connexion")
        return False

def get_exercise_content(session, exercise_id):
    """Récupère le contenu de l'exercice"""
    print(f"[INFO] Récupération du contenu de l'exercice {exercise_id}...")
    exercise_url = urljoin(BASE_URL, f"/exercise/{exercise_id}")
    response = session.get(exercise_url)
    
    if response.status_code != 200:
        print(f"[ERREUR] Impossible d'accéder à l'exercice: {response.status_code}")
        return None
    
    print(f"[OK] Contenu de l'exercice récupéré")
    return response.text

def extract_exercise_data(html_content):
    """Extrait les données de l'exercice depuis le HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Vérifier le type d'exercice
    exercise_type = None
    if "fill_in_blanks" in html_content:
        exercise_type = "fill_in_blanks"
    
    if not exercise_type:
        print("[ERREUR] Type d'exercice non reconnu")
        return None
    
    # Extraire les blancs et les réponses correctes
    blanks = []
    correct_answers = []
    
    # Pour les exercices fill_in_blanks
    if exercise_type == "fill_in_blanks":
        # Chercher les champs de saisie
        inputs = soup.find_all("input", {"class": "form-control", "name": lambda x: x and x.startswith("answer_")})
        for input_field in inputs:
            blank_index = input_field.get("name").replace("answer_", "")
            blanks.append(blank_index)
        
        # Chercher les réponses correctes (peut être dans un script JS)
        scripts = soup.find_all("script")
        for script in scripts:
            if script.string and "var words" in script.string:
                words_line = [line for line in script.string.split("\n") if "var words" in line][0]
                words_json = words_line.split("=")[1].strip().rstrip(";")
                try:
                    correct_answers = json.loads(words_json)
                except:
                    print("[AVERTISSEMENT] Impossible de parser les réponses correctes")
    
    return {
        "exercise_type": exercise_type,
        "blanks": blanks,
        "correct_answers": correct_answers
    }

def submit_exercise(session, exercise_id, answers):
    """Soumet l'exercice avec les réponses données"""
    print(f"[INFO] Soumission de l'exercice {exercise_id}...")
    submit_url = urljoin(BASE_URL, f"/submit/{exercise_id}")
    
    # Préparer les données de soumission
    submit_data = {}
    for i, answer in enumerate(answers):
        submit_data[f"answer_{i}"] = answer
    
    # Soumettre l'exercice
    response = session.post(submit_url, data=submit_data, allow_redirects=True)
    
    if response.status_code != 200:
        print(f"[ERREUR] Échec de la soumission: {response.status_code}")
        return None
    
    print(f"[OK] Exercice soumis avec succès")
    return response.text

def analyze_feedback(html_content):
    """Analyse le feedback affiché"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extraire le score
    score_element = soup.find(string=lambda text: text and "%" in text and "Score" in text)
    score = None
    if score_element:
        score = score_element.strip()
    
    # Vérifier si le feedback est groupé par phrase
    cards = soup.find_all("div", {"class": "card"})
    feedback_structure = "Inconnu"
    
    if cards:
        # Vérifier si les cartes ont des titres de phrase
        phrase_titles = [card.find("h5", {"class": "card-title"}) for card in cards]
        phrase_titles = [title.text for title in phrase_titles if title]
        
        if any("Phrase" in title for title in phrase_titles):
            feedback_structure = "Groupé par phrase"
        else:
            feedback_structure = "Non groupé"
    
    # Compter les blancs dans le feedback
    blanks_in_feedback = 0
    if feedback_structure == "Groupé par phrase":
        # Compter les alertes dans chaque carte
        for card in cards:
            alerts = card.find_all("div", {"class": lambda x: x and "alert" in x})
            blanks_in_feedback += len(alerts)
    else:
        # Compter les cartes directement
        blanks_in_feedback = len(cards)
    
    return {
        "score": score,
        "feedback_structure": feedback_structure,
        "blanks_in_feedback": blanks_in_feedback
    }

def test_exercise_with_correct_answers(exercise_id):
    """Teste l'exercice avec toutes les réponses correctes"""
    with requests.Session() as session:
        # Se connecter
        if not login(session):
            return False
        
        # Récupérer le contenu de l'exercice
        html_content = get_exercise_content(session, exercise_id)
        if not html_content:
            return False
        
        # Extraire les données de l'exercice
        exercise_data = extract_exercise_data(html_content)
        if not exercise_data:
            return False
        
        print(f"[INFO] Type d'exercice: {exercise_data['exercise_type']}")
        print(f"[INFO] Nombre de blancs: {len(exercise_data['blanks'])}")
        print(f"[INFO] Réponses correctes: {exercise_data['correct_answers']}")
        
        # Soumettre l'exercice avec les réponses correctes
        feedback_html = submit_exercise(session, exercise_id, exercise_data['correct_answers'])
        if not feedback_html:
            return False
        
        # Analyser le feedback
        feedback_analysis = analyze_feedback(feedback_html)
        
        print("\n=== Résultats du test ===")
        print(f"Score: {feedback_analysis['score']}")
        print(f"Structure du feedback: {feedback_analysis['feedback_structure']}")
        print(f"Nombre de blancs dans le feedback: {feedback_analysis['blanks_in_feedback']}")
        print(f"Nombre attendu de blancs: {len(exercise_data['correct_answers'])}")
        
        # Vérifier que le nombre de blancs dans le feedback correspond au nombre attendu
        if feedback_analysis['blanks_in_feedback'] == len(exercise_data['correct_answers']):
            print("[OK] Le nombre de blancs dans le feedback correspond au nombre attendu")
        else:
            print("[ERREUR] Le nombre de blancs dans le feedback ne correspond pas au nombre attendu")
        
        # Vérifier que le score est de 100%
        if "100%" in feedback_analysis['score']:
            print("[OK] Le score est de 100% comme attendu")
        else:
            print(f"[ERREUR] Le score n'est pas de 100%: {feedback_analysis['score']}")
        
        # Vérifier que le feedback est groupé par phrase
        if feedback_analysis['feedback_structure'] == "Groupé par phrase":
            print("[OK] Le feedback est correctement groupé par phrase")
        else:
            print(f"[ERREUR] Le feedback n'est pas groupé par phrase: {feedback_analysis['feedback_structure']}")
        
        return True

def main():
    """Fonction principale"""
    print("[INFO] Test de l'affichage du feedback pour les exercices fill_in_blanks avec plusieurs mots par ligne")
    
    # Tester l'exercice avec toutes les réponses correctes
    if test_exercise_with_correct_answers(TEST_EXERCISE_ID):
        print("\n[OK] Test terminé avec succès")
    else:
        print("\n[ERREUR] Échec du test")

if __name__ == "__main__":
    main()
