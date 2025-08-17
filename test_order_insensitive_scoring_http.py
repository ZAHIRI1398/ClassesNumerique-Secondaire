#!/usr/bin/env python3
"""
Script pour tester la nouvelle logique de scoring insensible à l'ordre des réponses
en simulant une requête HTTP à la route de soumission d'exercice.
"""
import os
import sys
import json
import logging
import requests
from datetime import datetime
from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.datastructures import ImmutableMultiDict

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Importer les modèles depuis l'application
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from models import db, User, Exercise, ExerciseAttempt
from app import app as flask_app

# URL de base pour les tests (localhost)
BASE_URL = "http://localhost:5000"

def find_fill_in_blanks_exercise():
    """
    Trouve un exercice de type fill_in_blanks dans la base de données.
    
    Returns:
        Exercise: Un exercice de type fill_in_blanks, ou None si aucun n'est trouvé
    """
    with flask_app.app_context():
        exercise = Exercise.query.filter_by(exercise_type='fill_in_blanks').first()
        if exercise:
            logger.info(f"✅ Exercice trouvé: {exercise.title} (ID: {exercise.id})")
            return exercise
        else:
            logger.error("❌ Aucun exercice fill_in_blanks trouvé dans la base de données")
            return None

def find_test_student():
    """
    Trouve un étudiant existant pour les tests.
    
    Returns:
        User: Un utilisateur avec le rôle 'student'
    """
    with flask_app.app_context():
        # Chercher un utilisateur étudiant
        user = User.query.filter_by(role='student').first()
        
        if user:
            logger.info(f"✅ Utilisateur trouvé: {user.name} (ID: {user.id})")
            return user
        else:
            logger.error("❌ Aucun utilisateur étudiant trouvé dans la base de données")
            return None

def test_scoring_with_app(exercise, user, answers_in_order=True):
    """
    Teste le scoring en utilisant directement la fonction de scoring de l'application.
    
    Args:
        exercise: L'exercice à tester
        user: L'utilisateur qui fait la tentative
        answers_in_order: Si True, les réponses sont dans l'ordre correct, sinon elles sont inversées
    
    Returns:
        float: Le score obtenu (0-100)
    """
    with flask_app.app_context():
        content = exercise.get_content()
        
        # Afficher le contenu de l'exercice
        logger.info(f"Contenu de l'exercice: {json.dumps(content, indent=2, ensure_ascii=False)}")
        
        # Récupérer les réponses correctes
        correct_answers = []
        if 'words' in content:
            correct_answers = content['words']
        elif 'available_words' in content:
            correct_answers = content['available_words']
        
        logger.info(f"Réponses correctes: {correct_answers}")
        
        # Préparer les réponses de l'utilisateur
        if answers_in_order:
            user_answers = correct_answers.copy()
            logger.info("Test avec les réponses dans l'ordre CORRECT")
        else:
            user_answers = correct_answers.copy()
            user_answers.reverse()  # Inverser l'ordre des réponses
            logger.info("Test avec les réponses dans l'ordre INVERSÉ")
        
        logger.info(f"Réponses utilisateur: {user_answers}")
        
        # Simuler la soumission des réponses
        form_data = {}
        for i, answer in enumerate(user_answers):
            form_data[f'answer_{i}'] = answer
        
        logger.info(f"Données du formulaire: {form_data}")
        
        # Créer une session de test avec l'utilisateur connecté
        with flask_app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = user.id
            
            # Simuler une requête POST à la route de soumission d'exercice
            response = client.post(
                f"/submit_exercise/{exercise.id}",
                data=form_data,
                follow_redirects=True
            )
            
            # Vérifier si la requête a réussi
            if response.status_code == 200:
                logger.info("✅ Requête de soumission réussie")
            else:
                logger.error(f"❌ Erreur lors de la soumission: {response.status_code}")
            
            # Récupérer la dernière tentative de l'utilisateur pour cet exercice
            attempt = ExerciseAttempt.query.filter_by(
                student_id=user.id,
                exercise_id=exercise.id
            ).order_by(ExerciseAttempt.created_at.desc()).first()
            
            if attempt:
                logger.info(f"✅ Tentative trouvée (ID: {attempt.id})")
                logger.info(f"Score: {attempt.score}%")
                return attempt.score
            else:
                logger.error("❌ Aucune tentative trouvée après la soumission")
                return 0

def main():
    """Fonction principale."""
    logger.info("=== TEST DE LA LOGIQUE DE SCORING INSENSIBLE À L'ORDRE ===")
    
    # Trouver un exercice fill_in_blanks
    exercise = find_fill_in_blanks_exercise()
    if not exercise:
        logger.error("❌ Impossible de continuer sans exercice")
        return
    
    # Trouver un utilisateur pour les tests
    user = find_test_student()
    if not user:
        logger.error("❌ Impossible de continuer sans utilisateur")
        return
    
    # Tester avec les réponses dans l'ordre correct
    logger.info("\n=== TEST AVEC RÉPONSES DANS L'ORDRE CORRECT ===")
    score_correct_order = test_scoring_with_app(exercise, user, answers_in_order=True)
    
    # Tester avec les réponses dans l'ordre inversé
    logger.info("\n=== TEST AVEC RÉPONSES DANS L'ORDRE INVERSÉ ===")
    score_inverse_order = test_scoring_with_app(exercise, user, answers_in_order=False)
    
    # Résumé des tests
    logger.info("\n=== RÉSUMÉ DES TESTS ===")
    logger.info(f"Score avec réponses dans l'ordre correct: {score_correct_order}%")
    logger.info(f"Score avec réponses dans l'ordre inversé: {score_inverse_order}%")
    
    # Vérifier si les scores sont identiques
    if score_correct_order == score_inverse_order and score_correct_order > 0:
        logger.info("✅ SUCCÈS: La logique de scoring est insensible à l'ordre des réponses")
    else:
        logger.warning("❌ ÉCHEC: La logique de scoring est toujours sensible à l'ordre des réponses")
        logger.warning(f"Scores: ordre correct = {score_correct_order}%, ordre inversé = {score_inverse_order}%")

if __name__ == "__main__":
    # Vérifier si le serveur Flask est en cours d'exécution
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            logger.error(f"❌ Le serveur Flask n'est pas accessible (code {response.status_code})")
            logger.error("Veuillez démarrer le serveur Flask avec 'python app.py' avant d'exécuter ce script")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        logger.error("❌ Le serveur Flask n'est pas en cours d'exécution")
        logger.error("Veuillez démarrer le serveur Flask avec 'python app.py' avant d'exécuter ce script")
        sys.exit(1)
    
    main()
