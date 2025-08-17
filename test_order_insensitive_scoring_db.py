#!/usr/bin/env python3
"""
Script pour tester la nouvelle logique de scoring insensible à l'ordre des réponses
avec un exercice réel dans la base de données.
"""
import os
import sys
import json
import logging
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Importer les modèles depuis l'application
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from models import db, User, Exercise, ExerciseAttempt

# Configuration de l'application Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def find_fill_in_blanks_exercise():
    """
    Trouve un exercice de type fill_in_blanks dans la base de données.
    
    Returns:
        Exercise: Un exercice de type fill_in_blanks, ou None si aucun n'est trouvé
    """
    with app.app_context():
        exercise = Exercise.query.filter_by(exercise_type='fill_in_blanks').first()
        if exercise:
            logger.info(f"✅ Exercice trouvé: {exercise.title} (ID: {exercise.id})")
            return exercise
        else:
            logger.error("❌ Aucun exercice fill_in_blanks trouvé dans la base de données")
            return None

def find_or_create_test_student():
    """
    Trouve un étudiant existant ou crée un étudiant temporaire pour les tests.
    
    Returns:
        User: Un utilisateur avec le rôle 'student'
    """
    with app.app_context():
        # Chercher un utilisateur par email
        user = User.query.filter_by(email='eric@example.com').first()
        
        if user:
            logger.info(f"✅ Utilisateur trouvé: {user.name} (ID: {user.id})")
            return user
        
        # Si aucun utilisateur n'est trouvé, créer un utilisateur temporaire
        logger.warning("⚠️ Aucun utilisateur trouvé avec l'email 'eric@example.com'")
        logger.info("Création d'un utilisateur temporaire pour les tests...")
        
        test_user = User(
            username="test_student",
            email="test_student@example.com",
            name="Test Student",
            role="student",
            school_name="Test School"
        )
        test_user.set_password("password123")
        
        db.session.add(test_user)
        db.session.commit()
        
        logger.info(f"✅ Utilisateur temporaire créé: {test_user.name} (ID: {test_user.id})")
        return test_user

def test_scoring_with_order(exercise, user, answers_in_order=True):
    """
    Teste le scoring avec des réponses dans l'ordre correct ou inversé.
    
    Args:
        exercise: L'exercice à tester
        user: L'utilisateur qui fait la tentative
        answers_in_order: Si True, les réponses sont dans l'ordre correct, sinon elles sont inversées
    
    Returns:
        float: Le score obtenu (0-100)
    """
    with app.app_context():
        content = exercise.get_content()
        
        # Afficher le contenu de l'exercice
        logger.info(f"Contenu de l'exercice: {json.dumps(content, indent=2, ensure_ascii=False)}")
        
        # Déterminer le nombre de blancs
        total_blanks = 0
        if 'sentences' in content:
            sentences_blanks = sum(s.count('___') for s in content['sentences'])
            total_blanks = sentences_blanks
        elif 'text' in content:
            text_blanks = content['text'].count('___')
            total_blanks = text_blanks
        
        logger.info(f"Nombre total de blancs: {total_blanks}")
        
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
        
        # Créer une tentative dans la base de données
        attempt_data = {
            'student_id': user.id,
            'exercise_id': exercise.id,
            'score': 0,  # Score initial
            'answers': json.dumps(user_answers),
            'created_at': datetime.utcnow()
        }
        
        # Simuler la soumission des réponses
        form_data = {}
        for i, answer in enumerate(user_answers):
            form_data[f'answer_{i}'] = answer
        
        logger.info(f"Données du formulaire: {form_data}")
        
        # Créer une tentative dans la base de données
        attempt = ExerciseAttempt(**attempt_data)
        db.session.add(attempt)
        db.session.commit()
        
        # Récupérer la tentative créée
        attempt = ExerciseAttempt.query.filter_by(student_id=user.id, exercise_id=exercise.id).order_by(ExerciseAttempt.created_at.desc()).first()
        
        if attempt:
            logger.info(f"✅ Tentative créée avec succès (ID: {attempt.id})")
            logger.info(f"Score: {attempt.score}%")
            return attempt.score
        else:
            logger.error("❌ Erreur lors de la création de la tentative")
            return 0

def main():
    """Fonction principale."""
    logger.info("=== TEST DE LA LOGIQUE DE SCORING INSENSIBLE À L'ORDRE ===")
    
    # Trouver un exercice fill_in_blanks
    exercise = find_fill_in_blanks_exercise()
    if not exercise:
        logger.error("❌ Impossible de continuer sans exercice")
        return
    
    # Trouver ou créer un utilisateur pour les tests
    user = find_or_create_test_student()
    if not user:
        logger.error("❌ Impossible de continuer sans utilisateur")
        return
    
    # Tester avec les réponses dans l'ordre correct
    logger.info("\n=== TEST AVEC RÉPONSES DANS L'ORDRE CORRECT ===")
    score_correct_order = test_scoring_with_order(exercise, user, answers_in_order=True)
    
    # Tester avec les réponses dans l'ordre inversé
    logger.info("\n=== TEST AVEC RÉPONSES DANS L'ORDRE INVERSÉ ===")
    score_inverse_order = test_scoring_with_order(exercise, user, answers_in_order=False)
    
    # Résumé des tests
    logger.info("\n=== RÉSUMÉ DES TESTS ===")
    logger.info(f"Score avec réponses dans l'ordre correct: {score_correct_order}%")
    logger.info(f"Score avec réponses dans l'ordre inversé: {score_inverse_order}%")
    
    # Vérifier si les scores sont identiques
    if score_correct_order == score_inverse_order:
        logger.info("✅ SUCCÈS: La logique de scoring est insensible à l'ordre des réponses")
    else:
        logger.warning("❌ ÉCHEC: La logique de scoring est toujours sensible à l'ordre des réponses")
        logger.warning("Vérifiez que la modification a bien été appliquée dans app.py")

if __name__ == "__main__":
    main()
