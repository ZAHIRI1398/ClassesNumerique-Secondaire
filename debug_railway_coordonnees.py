#!/usr/bin/env python3
"""
Script de diagnostic spécifique pour l'exercice "Les coordonnées" sur Railway
- Analyse la structure de l'exercice
- Vérifie le comptage des blancs
- Simule le scoring avec différentes réponses
"""

import sys
import json
import os
sys.path.append('.')

from app import app, db, Exercise
from flask import request, flash, redirect, url_for

def debug_railway_coordonnees():
    """Diagnostic spécifique pour l'exercice Les coordonnées"""
    
    with app.app_context():
        print("=== DIAGNOSTIC EXERCICE 'LES COORDONNÉES' ===")
        print()
        
        # 1. Rechercher l'exercice par titre
        exercise = Exercise.query.filter(Exercise.title.like('%coord%')).first()
        
        if not exercise:
            print("[ERREUR] Exercice 'Les coordonnees' non trouve!")
            # Chercher des exercices similaires
            similar_exercises = Exercise.query.filter(
                (Exercise.exercise_type == 'fill_in_blanks') | 
                (Exercise.exercise_type == 'word_placement')
            ).limit(10).all()
            
            print(f"Exercices similaires trouves: {len(similar_exercises)}")
            for ex in similar_exercises:
                print(f"  - ID: {ex.id}, Titre: {ex.title}, Type: {ex.exercise_type}")
            return
        
        # 2. Analyser l'exercice trouvé
        print(f"[OK] Exercice trouvé: ID={exercise.id}, Titre='{exercise.title}'")
        print(f"Type: {exercise.exercise_type}")
        print(f"Image: {exercise.image_path}")
        
        # 3. Analyser le contenu JSON
        content = json.loads(exercise.content)
        print("\n=== STRUCTURE DU CONTENU ===")
        print(f"Clés disponibles: {list(content.keys())}")
        
        # 4. Analyser les blancs et réponses
        print("\n=== ANALYSE DES BLANCS ET RÉPONSES ===")
        
        # Compter les blancs dans le texte
        text_blanks = 0
        if 'text' in content:
            text_blanks = content['text'].count('___')
            print(f"Blancs dans 'text': {text_blanks}")
            print(f"Texte: {content['text']}")
        
        # Compter les blancs dans les phrases
        sentences_blanks = 0
        if 'sentences' in content:
            for i, sentence in enumerate(content['sentences']):
                blanks_in_sentence = sentence.count('___')
                print(f"Phrase {i+1}: {sentence}")
                print(f"  - Blancs: {blanks_in_sentence}")
                sentences_blanks += blanks_in_sentence
            print(f"Total blancs dans 'sentences': {sentences_blanks}")
        
        # Analyser les réponses
        answers_count = 0
        if 'answers' in content:
            answers_count = len(content['answers'])
            print(f"Nombre de réponses dans 'answers': {answers_count}")
            for i, answer in enumerate(content['answers']):
                print(f"Réponse {i+1}: {answer}")
        
        # Analyser les mots disponibles
        if 'available_words' in content:
            print(f"Mots disponibles: {content['available_words']}")
        elif 'words' in content:
            print(f"Mots disponibles (words): {content['words']}")
        
        # 5. Vérifier la cohérence
        print("\n=== VÉRIFICATION DE COHÉRENCE ===")
        
        # Déterminer le nombre total de blancs selon la logique corrigée
        if 'sentences' in content:
            total_blanks = sentences_blanks
        elif 'text' in content:
            total_blanks = text_blanks
        else:
            total_blanks = 0
        
        print(f"Total blanks (priorité sentences puis text): {total_blanks}")
        
        # Déterminer le nombre de réponses
        if 'answers' in content:
            answers = content['answers']
        elif 'words' in content:
            answers = content['words']
        else:
            answers = []
        
        answers_count = len(answers)
        print(f"Nombre de réponses: {answers_count}")
        
        if total_blanks != answers_count and answers_count > 0:
            print(f"[ALERTE] INCOHÉRENCE: Le nombre de blancs ({total_blanks}) ne correspond pas au nombre de réponses ({answers_count})!")
        else:
            print("[OK] Cohérence OK: Le nombre de blanks correspond au nombre de réponses.")
        
        # 6. Simuler le scoring
        print("\n=== SIMULATION DE SCORING ===")
        
        # Simuler un scoring parfait (toutes les réponses correctes)
        if answers_count > 0:
            # Simuler des réponses utilisateur parfaites
            user_answers_perfect = {}
            for i, correct_answer in enumerate(answers):
                user_answers_perfect[f'answer_{i}'] = correct_answer
            
            print(f"Réponses utilisateur parfaites: {user_answers_perfect}")
            
            # Calculer le score manuellement (comme dans le backend)
            correct_blanks = 0
            
            for i, correct_answer in enumerate(answers):
                user_answer = user_answers_perfect.get(f'answer_{i}', '').strip()
                is_correct = user_answer.lower() == correct_answer.lower()
                if is_correct:
                    correct_blanks += 1
                print(f"  Blanc {i}: '{user_answer}' vs '{correct_answer}' = {'OK' if is_correct else 'KO'}")
            
            score = round((correct_blanks / total_blanks) * 100) if total_blanks > 0 else 0
            print(f"Score calculé: {correct_blanks}/{total_blanks} = {score}%")
            
            if score != 100.0:
                print(f"[ALERTE] PROBLÈME DE SCORING: Le score devrait être 100% mais est calculé à {score}%")
                
                # Analyser pourquoi le score n'est pas 100%
                if total_blanks > answers_count:
                    print(f"  - Il y a plus de blancs ({total_blanks}) que de réponses ({answers_count})")
                    print(f"  - Certains blancs n'ont pas de réponse associée")
                elif total_blanks < answers_count:
                    print(f"  - Il y a moins de blancs ({total_blanks}) que de réponses ({answers_count})")
                    print(f"  - Certaines réponses ne correspondent à aucun blanc")
        
        # 7. Vérifier les tentatives récentes
        print("\n=== TENTATIVES RÉCENTES ===")
        attempts = db.session.query(
            db.func.max(db.text("id")).label("id"),
            db.text("user_id"),
            db.text("score"),
            db.func.max(db.text("created_at")).label("created_at")
        ).filter_by(exercise_id=exercise.id).group_by(db.text("user_id")).order_by(db.text("created_at DESC")).limit(5).all()
        
        if attempts:
            print(f"Dernières tentatives:")
            for attempt in attempts:
                print(f"ID: {attempt.id}, Utilisateur: {attempt.user_id}, Score: {attempt.score}%, Date: {attempt.created_at}")
        else:
            print("Aucune tentative trouvée pour cet exercice.")
        
        # 8. Vérifier le code de scoring dans app.py
        print("\n=== CODE DE SCORING ACTUEL ===")
        
        if exercise.exercise_type == 'fill_in_blanks':
            print("Logique de scoring pour fill_in_blanks:")
            print("""
if 'sentences' in content:
    sentences_blanks = sum(s.count('___') for s in content['sentences'])
    total_blanks_in_content = sentences_blanks
elif 'text' in content:
    text_blanks = content['text'].count('___')
    total_blanks_in_content = text_blanks
            """)
        elif exercise.exercise_type == 'word_placement':
            print("Logique de scoring pour word_placement:")
            print("""
sentences = content['sentences']
correct_answers = content['answers']
total_blanks = len(correct_answers)
            """)
        
        # 9. Conclusion et recommandations
        print("\n=== CONCLUSION ET RECOMMANDATIONS ===")
        
        if exercise.exercise_type == 'fill_in_blanks':
            if total_blanks != answers_count:
                print("[ALERTE] Le probleme semble etre une incoherence entre le nombre de blancs et le nombre de reponses.")
                print("Recommandation: Verifier la structure du contenu de l'exercice et ajuster soit les blancs, soit les reponses.")
            else:
                print("[OK] La structure de l'exercice semble correcte.")
                print("Recommandation: Verifier si la correction a bien ete deployee et si elle s'applique correctement a cet exercice.")
        elif exercise.exercise_type == 'word_placement':
            print("[ALERTE] L'exercice est de type 'word_placement', pas 'fill_in_blanks'!")
            print("Recommandation: Appliquer la même correction de comptage des blancs pour ce type d'exercice.")

if __name__ == '__main__':
    debug_railway_coordonnees()
