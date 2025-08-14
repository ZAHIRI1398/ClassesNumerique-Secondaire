#!/usr/bin/env python3
"""
Script de diagnostic avancé pour les exercices "Texte à trous" en production
"""

import json
import os
from flask import Flask
from models import Exercise, db

def debug_fill_in_blanks_exercise(exercise_id):
    """Diagnostic approfondi d'un exercice Texte à trous"""
    
    print(f"=== DIAGNOSTIC EXERCICE TEXTE A TROUS ID={exercise_id} ===")
    
    try:
        # Récupérer l'exercice
        exercise = Exercise.query.get(exercise_id)
        if not exercise:
            print(f"ERREUR: Exercice {exercise_id} introuvable")
            return False
        
        print(f"Titre: {exercise.title}")
        print(f"Type: {exercise.exercise_type}")
        print(f"Description: {exercise.description}")
        
        # Analyser le contenu JSON
        try:
            content = json.loads(exercise.content)
            print(f"Contenu JSON parse avec succes")
            print(f"Cles disponibles: {list(content.keys())}")
        except json.JSONDecodeError as e:
            print(f"ERREUR: Impossible de parser le JSON: {e}")
            print(f"Contenu brut: {exercise.content[:200]}...")
            return False
        
        # Analyser la structure du contenu
        print("\n=== ANALYSE STRUCTURE CONTENU ===")
        
        # Vérifier les différents formats possibles
        total_blanks_found = 0
        
        if 'text' in content:
            text_blanks = content['text'].count('___')
            total_blanks_found += text_blanks
            print(f"Format 'text' detecte: {text_blanks} blancs")
            print(f"Texte: {content['text'][:100]}...")
        
        if 'sentences' in content:
            sentences = content['sentences']
            sentences_blanks = sum(s.count('___') for s in sentences)
            total_blanks_found += sentences_blanks
            print(f"Format 'sentences' detecte: {sentences_blanks} blancs")
            print(f"Phrases ({len(sentences)}):")
            for i, sentence in enumerate(sentences):
                blanks_in_sentence = sentence.count('___')
                print(f"  {i}: {sentence} ({blanks_in_sentence} blancs)")
        
        print(f"TOTAL BLANCS DETECTES: {total_blanks_found}")
        
        # Analyser les réponses correctes
        print("\n=== ANALYSE REPONSES CORRECTES ===")
        
        correct_answers = []
        if 'words' in content:
            correct_answers = content['words']
            print(f"Format 'words' detecte: {len(correct_answers)} reponses")
            print(f"Reponses: {correct_answers}")
        
        if 'available_words' in content:
            available_words = content['available_words']
            print(f"Format 'available_words' detecte: {len(available_words)} mots")
            print(f"Mots disponibles: {available_words}")
            if not correct_answers:  # Si pas de 'words', utiliser 'available_words'
                correct_answers = available_words
        
        print(f"REPONSES CORRECTES FINALES: {correct_answers}")
        
        # Simuler le scoring avec notre logique corrigée
        print("\n=== SIMULATION SCORING CORRIGE ===")
        
        # Logique de notre correction
        total_blanks = max(total_blanks_found, len(correct_answers))
        print(f"total_blanks = max({total_blanks_found}, {len(correct_answers)}) = {total_blanks}")
        
        # Simuler des réponses utilisateur (toutes correctes)
        print("Simulation avec toutes les reponses correctes:")
        correct_count = 0
        for i in range(total_blanks):
            correct_answer = correct_answers[i] if i < len(correct_answers) else ''
            user_answer = correct_answer  # Simuler réponse correcte
            
            is_correct = user_answer.lower() == correct_answer.lower() if correct_answer else False
            if is_correct:
                correct_count += 1
            
            print(f"  Blanc {i}: correct='{correct_answer}', user='{user_answer}', ok={is_correct}")
        
        expected_score = round((correct_count / total_blanks) * 100) if total_blanks > 0 else 0
        print(f"Score attendu: {correct_count}/{total_blanks} = {expected_score}%")
        
        # Diagnostic des problèmes potentiels
        print("\n=== DIAGNOSTIC PROBLEMES ===")
        
        if total_blanks_found != len(correct_answers):
            print(f"ATTENTION: Nombre de blancs ({total_blanks_found}) != nombre de reponses ({len(correct_answers)})")
        
        if total_blanks_found == 0:
            print("PROBLEME: Aucun blanc detecte dans le contenu")
        
        if len(correct_answers) == 0:
            print("PROBLEME: Aucune reponse correcte trouvee")
        
        if expected_score != 100:
            print(f"PROBLEME: Score attendu {expected_score}% au lieu de 100%")
        
        return True
        
    except Exception as e:
        print(f"ERREUR lors du diagnostic: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_uploads_folder_production():
    """Vérifier le dossier uploads en production"""
    
    print("\n=== VERIFICATION DOSSIER UPLOADS PRODUCTION ===")
    
    static_dir = "static"
    uploads_dir = os.path.join(static_dir, "uploads")
    
    print(f"Repertoire de travail: {os.getcwd()}")
    
    # Vérifier static
    if os.path.exists(static_dir):
        print(f"OK Dossier {static_dir} existe")
    else:
        print(f"PROBLEME: Dossier {static_dir} manquant")
        try:
            os.makedirs(static_dir)
            print(f"OK Dossier {static_dir} cree")
        except Exception as e:
            print(f"ERREUR creation {static_dir}: {e}")
            return False
    
    # Vérifier uploads
    if os.path.exists(uploads_dir):
        print(f"OK Dossier {uploads_dir} existe")
        files = os.listdir(uploads_dir)
        print(f"Contient {len(files)} fichiers")
    else:
        print(f"PROBLEME: Dossier {uploads_dir} manquant")
        try:
            os.makedirs(uploads_dir, exist_ok=True)
            # Créer .gitkeep
            gitkeep_path = os.path.join(uploads_dir, ".gitkeep")
            with open(gitkeep_path, 'w') as f:
                f.write("# Dossier uploads pour les images\n")
            print(f"OK Dossier {uploads_dir} cree avec .gitkeep")
        except Exception as e:
            print(f"ERREUR creation {uploads_dir}: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("DIAGNOSTIC PRODUCTION TEXTE A TROUS")
    print("="*50)
    
    # Test avec un exercice spécifique (à adapter selon vos exercices)
    exercise_id = 1  # Remplacer par l'ID d'un exercice Texte à trous existant
    
    # Initialiser Flask pour accéder à la DB
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///instance/app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    with app.app_context():
        db.init_app(app)
        
        # Diagnostic exercice
        success = debug_fill_in_blanks_exercise(exercise_id)
        
        # Vérification dossier uploads
        uploads_ok = check_uploads_folder_production()
        
        print("\n" + "="*50)
        print("RESUME DIAGNOSTIC")
        print("="*50)
        
        if success and uploads_ok:
            print("DIAGNOSTIC TERMINE - Verifiez les logs ci-dessus")
        else:
            print("PROBLEMES DETECTES - Consultez les erreurs ci-dessus")
