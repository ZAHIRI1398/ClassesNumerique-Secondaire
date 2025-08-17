#!/usr/bin/env python3
"""
Script pour déboguer l'affichage du score dans les exercices fill_in_blanks.
Ce script analyse le problème d'affichage du score qui reste à 50% malgré la correction du backend.
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Configuration
DB_PATH = "app.db"  # Chemin vers la base de données
EXERCISE_ID = 6     # ID de l'exercice problématique

def connect_to_db():
    """Établit une connexion à la base de données"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Erreur de connexion à la base de données: {e}")
        return None

def get_exercise_details(conn, exercise_id):
    """Récupère les détails de l'exercice depuis la base de données"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, exercise_type, content 
            FROM exercise 
            WHERE id = ?
        """, (exercise_id,))
        exercise = cursor.fetchone()
        
        if not exercise:
            print(f"Exercice ID {exercise_id} non trouvé dans la base de données.")
            return None
            
        # Convertir le contenu JSON en dictionnaire Python
        content = json.loads(exercise['content'])
        
        return {
            'id': exercise['id'],
            'title': exercise['title'],
            'exercise_type': exercise['exercise_type'],
            'content': content
        }
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération de l'exercice: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Erreur de décodage JSON pour l'exercice {exercise_id}: {e}")
        return None

def get_latest_attempts(conn, exercise_id, limit=5):
    """Récupère les dernières tentatives pour cet exercice"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, student_id, exercise_id, answers, score, feedback, created_at
            FROM exercise_attempt
            WHERE exercise_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (exercise_id, limit))
        
        attempts = []
        for row in cursor.fetchall():
            try:
                answers = json.loads(row['answers'])
                feedback = json.loads(row['feedback'])
                
                attempts.append({
                    'id': row['id'],
                    'student_id': row['student_id'],
                    'exercise_id': row['exercise_id'],
                    'answers': answers,
                    'score': row['score'],
                    'feedback': feedback,
                    'created_at': row['created_at']
                })
            except json.JSONDecodeError as e:
                print(f"Erreur de décodage JSON pour la tentative {row['id']}: {e}")
                continue
                
        return attempts
    except sqlite3.Error as e:
        print(f"Erreur lors de la récupération des tentatives: {e}")
        return []

def analyze_score_calculation(exercise, attempt):
    """Analyse le calcul du score pour une tentative"""
    print("\n=== Analyse du calcul du score ===")
    
    content = exercise['content']
    answers = attempt['answers']
    feedback = attempt['feedback']
    score = attempt['score']
    
    print(f"Score enregistré dans la base de données: {score}%")
    
    # Analyser le contenu de l'exercice
    total_blanks = 0
    if 'sentences' in content:
        sentences_blanks = sum(s.count('___') for s in content['sentences'])
        total_blanks = sentences_blanks
        print(f"Format 'sentences' détecté: {sentences_blanks} blancs")
    elif 'text' in content:
        text_blanks = content['text'].count('___')
        total_blanks = text_blanks
        print(f"Format 'text' détecté: {text_blanks} blancs")
    
    # Récupérer les réponses correctes
    correct_answers = content.get('words', [])
    if not correct_answers:
        correct_answers = content.get('available_words', [])
    
    print(f"Réponses correctes: {correct_answers}")
    print(f"Nombre total de blancs: {total_blanks}")
    
    # Analyser les réponses de l'utilisateur
    user_answers = []
    for i in range(total_blanks):
        key = f'answer_{i}'
        if key in answers:
            user_answers.append(answers[key])
    
    print(f"Réponses utilisateur: {user_answers}")
    
    # Recalculer le score
    correct_blanks = 0
    for i, (user_ans, correct_ans) in enumerate(zip(user_answers, correct_answers)):
        is_correct = user_ans.strip().lower() == correct_ans.strip().lower()
        if is_correct:
            correct_blanks += 1
            print(f"Réponse {i+1}: '{user_ans}' est CORRECTE")
        else:
            print(f"Réponse {i+1}: '{user_ans}' est INCORRECTE (attendu: '{correct_ans}')")
    
    calculated_score = (correct_blanks / total_blanks) * 100 if total_blanks > 0 else 0
    print(f"\nScore recalculé: {calculated_score:.1f}% ({correct_blanks}/{total_blanks})")
    
    if abs(calculated_score - score) < 0.1:
        print("✅ Le score calculé correspond au score enregistré.")
    else:
        print(f"❌ Incohérence: Le score calculé ({calculated_score:.1f}%) ne correspond pas au score enregistré ({score}%)")
    
    # Analyser le feedback
    print("\n=== Analyse du feedback ===")
    if 'details' in feedback:
        print(f"Nombre d'éléments de feedback: {len(feedback['details'])}")
        for i, detail in enumerate(feedback['details']):
            print(f"Détail {i+1}: Réponse '{detail['user_answer']}', Correcte: {detail['is_correct']}")
    else:
        print("Format de feedback non standard ou incomplet")

def check_template_rendering():
    """Vérifie comment le score est rendu dans les templates"""
    print("\n=== Analyse des templates ===")
    
    # Vérifier le template feedback.html
    try:
        with open("templates/feedback.html", "r", encoding="utf-8") as f:
            content = f.read()
            print("Template feedback.html trouvé")
            
            # Chercher comment le score est affiché
            if "<p><strong>Score :</strong> {{ attempt.score }}%" in content:
                print("✅ Le score est affiché directement depuis attempt.score")
            else:
                print("❓ Format d'affichage du score non standard dans feedback.html")
    except FileNotFoundError:
        print("❌ Template feedback.html non trouvé")
    
    # Vérifier s'il y a du JavaScript qui pourrait modifier l'affichage du score
    try:
        js_files = [f for f in os.listdir("static/js") if f.endswith(".js")]
        print(f"Fichiers JavaScript trouvés: {js_files}")
        
        for js_file in js_files:
            with open(f"static/js/{js_file}", "r", encoding="utf-8") as f:
                content = f.read()
                if "score" in content.lower():
                    print(f"⚠️ Le fichier {js_file} contient des références au score et pourrait modifier l'affichage")
    except Exception as e:
        print(f"Erreur lors de la vérification des fichiers JavaScript: {e}")

def check_route_redirect():
    """Vérifie la redirection après soumission d'un exercice"""
    print("\n=== Analyse de la redirection après soumission ===")
    
    # Chercher dans app.py
    try:
        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()
            
            # Chercher la redirection après soumission
            if "return redirect(url_for('view_exercise'" in content:
                print("✅ La soumission redirige vers view_exercise")
                print("⚠️ Cela pourrait expliquer pourquoi le score n'est pas mis à jour dans l'UI")
                print("   La page est rechargée sans afficher le template feedback.html")
            
            if "return redirect(url_for('feedback'" in content:
                print("✅ La soumission redirige vers une page de feedback")
            
            # Chercher les flash messages
            if "flash(f'Vous avez obtenu {score:.1f}%" in content:
                print("✅ Un message flash est affiché avec le score")
                print("⚠️ Le score dans le message flash pourrait être correct mais l'affichage persistant non")
    except FileNotFoundError:
        print("❌ Fichier app.py non trouvé")

def main():
    """Fonction principale"""
    print(f"=== Débogage du score pour l'exercice ID {EXERCISE_ID} ===")
    
    # Connexion à la base de données
    conn = connect_to_db()
    if not conn:
        print("Impossible de continuer sans connexion à la base de données.")
        return
    
    # Récupérer les détails de l'exercice
    exercise = get_exercise_details(conn, EXERCISE_ID)
    if not exercise:
        print("Impossible de continuer sans les détails de l'exercice.")
        conn.close()
        return
    
    print(f"Exercice trouvé: {exercise['title']} (Type: {exercise['exercise_type']})")
    
    # Récupérer les dernières tentatives
    attempts = get_latest_attempts(conn, EXERCISE_ID)
    if not attempts:
        print("Aucune tentative trouvée pour cet exercice.")
        conn.close()
        return
    
    print(f"Nombre de tentatives trouvées: {len(attempts)}")
    
    # Analyser la dernière tentative
    latest_attempt = attempts[0]
    print(f"\nAnalyse de la dernière tentative (ID: {latest_attempt['id']}, Date: {latest_attempt['created_at']})")
    
    # Analyser le calcul du score
    analyze_score_calculation(exercise, latest_attempt)
    
    # Vérifier le rendu des templates
    check_template_rendering()
    
    # Vérifier la redirection après soumission
    check_route_redirect()
    
    # Conclusion et recommandations
    print("\n=== Conclusion et recommandations ===")
    print("1. Le problème pourrait être dû à la redirection après soumission qui ne montre pas le template feedback.html")
    print("2. Vérifiez si un ancien score est affiché à partir du cache ou d'une session")
    print("3. Assurez-vous que l'application Flask a bien été redémarrée après les modifications")
    print("4. Vérifiez s'il y a du JavaScript qui modifie l'affichage du score")
    print("5. Solution possible: modifier la redirection pour afficher feedback.html au lieu de recharger view_exercise.html")
    
    conn.close()

if __name__ == "__main__":
    main()
