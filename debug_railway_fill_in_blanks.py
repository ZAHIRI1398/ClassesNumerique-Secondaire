#!/usr/bin/env python3
"""
Script de diagnostic spécifique Railway pour les problèmes fill_in_blanks
- Image visible en édition mais pas en affichage
- Scoring ne compte qu'un seul blanc sur Railway
"""

import sys
import json
import os
sys.path.append('.')

from app import app, db, Exercise

def debug_railway_fill_in_blanks():
    """Diagnostic complet des problèmes Railway fill_in_blanks"""
    
    with app.app_context():
        print("=== DIAGNOSTIC RAILWAY FILL_IN_BLANKS ===")
        print()
        
        # 1. Vérifier les exercices fill_in_blanks
        exercises = Exercise.query.filter_by(exercise_type='fill_in_blanks').all()
        print(f"1. EXERCICES FILL_IN_BLANKS: {len(exercises)} trouvés")
        
        for ex in exercises:
            print(f"   Exercice {ex.id}: {ex.title}")
            print(f"   Image path: {ex.image_path}")
            
            # Analyser le contenu JSON
            content = json.loads(ex.content)
            print(f"   Format JSON: {list(content.keys())}")
            
            if 'text' in content:
                text = content['text']
                blank_count = text.count('___')
                print(f"   Text: {text}")
                print(f"   Blancs dans text: {blank_count}")
            
            if 'sentences' in content:
                sentences = content['sentences']
                total_blanks = sum(sentence.count('___') for sentence in sentences)
                print(f"   Sentences: {sentences}")
                print(f"   Blancs dans sentences: {total_blanks}")
            
            words = content.get('words', [])
            print(f"   Words: {words} (count: {len(words)})")
            
            # Vérifier la cohérence blancs/mots
            if 'text' in content:
                text_blanks = content['text'].count('___')
                word_count = len(words)
                if text_blanks != word_count:
                    print(f"   ALERTE: {text_blanks} blancs mais {word_count} mots!")
                else:
                    print(f"   OK: {text_blanks} blancs = {word_count} mots")
            
            print()
        
        # 2. Vérifier les dossiers et fichiers d'images
        print("2. VERIFICATION DOSSIERS IMAGES:")
        
        static_dir = os.path.join(os.getcwd(), 'static')
        uploads_dir = os.path.join(static_dir, 'uploads')
        
        print(f"   Dossier static: {static_dir} - Existe: {os.path.exists(static_dir)}")
        print(f"   Dossier uploads: {uploads_dir} - Existe: {os.path.exists(uploads_dir)}")
        
        if os.path.exists(uploads_dir):
            files = os.listdir(uploads_dir)
            print(f"   Fichiers dans uploads: {len(files)}")
            for f in files[:5]:  # Afficher les 5 premiers
                print(f"     - {f}")
            if len(files) > 5:
                print(f"     ... et {len(files) - 5} autres")
        
        # 3. Tester la logique de scoring pour différents cas
        print("\n3. TEST LOGIQUE SCORING:")
        
        # Simuler le scoring pour un exercice avec 2 blancs
        test_exercise = exercises[0] if exercises else None
        if test_exercise:
            content = json.loads(test_exercise.content)
            correct_answers = content.get('words', [])
            
            print(f"   Test avec exercice: {test_exercise.title}")
            print(f"   Réponses correctes: {correct_answers}")
            
            # Simuler des réponses utilisateur parfaites
            user_answers_perfect = {}
            for i, correct_answer in enumerate(correct_answers):
                user_answers_perfect[f'answer_{i}'] = correct_answer
            
            print(f"   Réponses utilisateur parfaites: {user_answers_perfect}")
            
            # Calculer le score manuellement (comme dans le backend)
            total_blanks = len(correct_answers)
            correct_blanks = 0
            
            for i, correct_answer in enumerate(correct_answers):
                user_answer = user_answers_perfect.get(f'answer_{i}', '').strip()
                is_correct = user_answer.lower() == correct_answer.lower()
                if is_correct:
                    correct_blanks += 1
                print(f"     Blanc {i}: '{user_answer}' vs '{correct_answer}' = {'OK' if is_correct else 'KO'}")
            
            score = round((correct_blanks / total_blanks) * 100) if total_blanks > 0 else 0
            print(f"   Score calculé: {correct_blanks}/{total_blanks} = {score}%")
            
            # Test avec seulement le premier blanc correct (pour reproduire le bug Railway)
            print("\n   Test bug Railway (seulement premier blanc):")
            user_answers_partial = {}
            user_answers_partial['answer_0'] = correct_answers[0] if correct_answers else ''
            # Les autres blancs restent vides
            for i in range(1, len(correct_answers)):
                user_answers_partial[f'answer_{i}'] = ''
            
            print(f"   Réponses utilisateur partielles: {user_answers_partial}")
            
            correct_blanks_partial = 0
            for i, correct_answer in enumerate(correct_answers):
                user_answer = user_answers_partial.get(f'answer_{i}', '').strip()
                is_correct = user_answer.lower() == correct_answer.lower() if user_answer else False
                if is_correct:
                    correct_blanks_partial += 1
                print(f"     Blanc {i}: '{user_answer}' vs '{correct_answer}' = {'OK' if is_correct else 'KO'}")
            
            score_partial = round((correct_blanks_partial / total_blanks) * 100) if total_blanks > 0 else 0
            print(f"   Score partiel: {correct_blanks_partial}/{total_blanks} = {score_partial}%")
            
            if score_partial == 50 and total_blanks == 2:
                print("   REPRODUCTION DU BUG: 50% avec 2 blancs dont 1 correct!")
        
        # 4. Vérifier les variables d'environnement Railway
        print("\n4. VARIABLES ENVIRONNEMENT:")
        env_vars = ['DATABASE_URL', 'FLASK_ENV', 'PORT']
        for var in env_vars:
            value = os.environ.get(var, 'NON DEFINI')
            if var == 'DATABASE_URL' and value != 'NON DEFINI':
                # Masquer l'URL complète pour sécurité
                value = value[:20] + "..." if len(value) > 20 else value
            print(f"   {var}: {value}")
        
        print("\n=== FIN DIAGNOSTIC ===")

if __name__ == '__main__':
    debug_railway_fill_in_blanks()
