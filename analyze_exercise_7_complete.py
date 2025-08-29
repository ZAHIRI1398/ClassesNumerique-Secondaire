#!/usr/bin/env python3
"""
Script pour analyser complètement l'exercice 7 et identifier tous les problèmes
"""

import os
import sys
import json

# Ajouter le répertoire parent au path pour importer les modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import db, Exercise, User, ExerciseAttempt
from app import app

def analyze_exercise_7():
    """Analyser complètement l'exercice 7"""
    
    print("=== ANALYSE COMPLETE DE L'EXERCICE 7 ===\n")
    
    with app.app_context():
        # 1. Récupérer l'exercice
        exercise = Exercise.query.get(7)
        if not exercise:
            print("Exercice 7 non trouve!")
            return
        
        print(f"INFORMATIONS GENERALES")
        print(f"ID: {exercise.id}")
        print(f"Titre: {exercise.title}")
        print(f"Type: {exercise.exercise_type}")
        print(f"Sujet: {exercise.subject}")
        print(f"Description: {exercise.description}")
        print(f"Image: {exercise.image_path}")
        print(f"Créé le: {exercise.created_at}")
        print()
        
        # 2. Analyser le contenu JSON
        print(f"CONTENU JSON")
        if exercise.content:
            try:
                content = json.loads(exercise.content)
                print(f"Contenu parsé avec succès:")
                print(json.dumps(content, indent=2, ensure_ascii=False))
                print()
                
                # Analyser selon le type d'exercice
                if exercise.exercise_type == 'fill_in_blanks':
                    analyze_fill_in_blanks_content(content)
                elif exercise.exercise_type == 'underline_words':
                    analyze_underline_words_content(content)
                elif exercise.exercise_type == 'qcm':
                    analyze_qcm_content(content)
                else:
                    print(f"Type d'exercice: {exercise.exercise_type}")
                    
            except json.JSONDecodeError as e:
                print(f"Erreur de parsing JSON: {e}")
                print(f"Contenu brut: {exercise.content}")
        else:
            print("Aucun contenu JSON")
        print()
        
        # 3. Vérifier l'image
        print(f"VERIFICATION DE L'IMAGE")
        if exercise.image_path:
            image_file = f"static/uploads/{exercise.image_path.replace('/static/uploads/', '').replace('static/uploads/', '')}"
            if os.path.exists(image_file):
                size = os.path.getsize(image_file)
                print(f"Image existe: {image_file} ({size} bytes)")
            else:
                print(f"Image manquante: {image_file}")
        else:
            print("Aucune image associee")
        print()
        
        # 4. Analyser les tentatives
        print(f"TENTATIVES D'EXERCICE")
        attempts = ExerciseAttempt.query.filter_by(exercise_id=7).all()
        if attempts:
            print(f"Nombre de tentatives: {len(attempts)}")
            for i, attempt in enumerate(attempts[:5]):  # Afficher les 5 dernières
                print(f"  Tentative {i+1}:")
                print(f"    Utilisateur: {attempt.user_id}")
                print(f"    Score: {attempt.score}%")
                print(f"    Complété: {attempt.completed}")
                print(f"    Date: {attempt.submitted_at}")
                if attempt.answers:
                    try:
                        answers = json.loads(attempt.answers)
                        print(f"    Réponses: {answers}")
                    except:
                        print(f"    Réponses (brut): {attempt.answers}")
                print()
        else:
            print("Aucune tentative enregistrée")
        print()
        
        # 5. Suggestions de correction
        print(f"SUGGESTIONS DE CORRECTION")
        suggest_fixes(exercise, content if exercise.content else {})

def analyze_fill_in_blanks_content(content):
    """Analyser le contenu d'un exercice texte à trous"""
    
    print(f"ANALYSE TEXTE A TROUS")
    
    # Vérifier la structure attendue
    if 'sentences' in content:
        sentences = content['sentences']
        print(f"Phrases trouvées: {len(sentences)}")
        
        total_blanks = 0
        for i, sentence in enumerate(sentences):
            blank_count = sentence.count('___')
            total_blanks += blank_count
            print(f"  Phrase {i+1}: \"{sentence}\" ({blank_count} blancs)")
        
        print(f"Total des blancs: {total_blanks}")
    else:
        print("Pas de champ 'sentences'")
    
    if 'words' in content:
        words = content['words']
        print(f"Mots disponibles: {len(words)}")
        for i, word in enumerate(words):
            print(f"  Mot {i+1}: \"{word}\"")
    elif 'available_words' in content:
        words = content['available_words']
        print(f"Mots disponibles (available_words): {len(words)}")
        for i, word in enumerate(words):
            print(f"  Mot {i+1}: \"{word}\"")
    else:
        print("Pas de champ 'words' ou 'available_words'")
    
    # Vérifier la cohérence
    if 'sentences' in content and ('words' in content or 'available_words' in content):
        words = content.get('words', content.get('available_words', []))
        if total_blanks == len(words):
            print("Coherence: nombre de blancs = nombre de mots")
        else:
            print(f"Incoherence: {total_blanks} blancs != {len(words)} mots")

def analyze_underline_words_content(content):
    """Analyser le contenu d'un exercice souligner les mots"""
    
    print(f"ANALYSE SOULIGNER LES MOTS")
    
    if 'sentences' in content:
        sentences = content['sentences']
        print(f"Phrases trouvées: {len(sentences)}")
        for i, sentence in enumerate(sentences):
            print(f"  Phrase {i+1}: \"{sentence}\"")
    
    if 'target_words' in content:
        target_words = content['target_words']
        print(f"Mots cibles: {target_words}")

def analyze_qcm_content(content):
    """Analyser le contenu d'un exercice QCM"""
    
    print(f"ANALYSE QCM")
    
    if 'questions' in content:
        questions = content['questions']
        print(f"Questions trouvées: {len(questions)}")
        for i, question in enumerate(questions):
            print(f"  Question {i+1}: {question.get('text', 'Pas de texte')}")
            print(f"    Options: {question.get('choices', question.get('options', []))}")
            print(f"    Réponse correcte: {question.get('correct_answer', 'Non définie')}")

def suggest_fixes(exercise, content):
    """Suggérer des corrections pour l'exercice"""
    
    fixes = []
    
    # Vérifications générales
    if not exercise.title or exercise.title.strip() == '':
        fixes.append("Ajouter un titre à l'exercice")
    
    if not exercise.content:
        fixes.append("Ajouter du contenu JSON à l'exercice")
    
    if exercise.image_path:
        image_file = f"static/uploads/{exercise.image_path.replace('/static/uploads/', '').replace('static/uploads/', '')}"
        if not os.path.exists(image_file):
            fixes.append(f"Re-uploader l'image manquante: {exercise.image_path}")
    
    # Vérifications spécifiques au type
    if exercise.exercise_type == 'fill_in_blanks' and content:
        if 'sentences' not in content:
            fixes.append("Ajouter le champ 'sentences' au contenu")
        elif not content['sentences']:
            fixes.append("Ajouter au moins une phrase avec des blancs (___)")
        
        if 'words' not in content and 'available_words' not in content:
            fixes.append("Ajouter le champ 'words' ou 'available_words' au contenu")
        
        # Vérifier la cohérence blancs/mots
        if 'sentences' in content and ('words' in content or 'available_words' in content):
            sentences = content['sentences']
            words = content.get('words', content.get('available_words', []))
            total_blanks = sum(sentence.count('___') for sentence in sentences)
            
            if total_blanks != len(words):
                fixes.append(f"Ajuster le nombre de mots ({len(words)}) pour correspondre aux blancs ({total_blanks})")
    
    # Afficher les corrections suggérées
    if fixes:
        for i, fix in enumerate(fixes, 1):
            print(f"  {i}. {fix}")
    else:
        print(f"  Aucune correction évidente nécessaire")

if __name__ == "__main__":
    analyze_exercise_7()
