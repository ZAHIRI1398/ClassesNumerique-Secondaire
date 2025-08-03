#!/usr/bin/env python3
"""
Script pour diagnostiquer l'exercice 12 "Test Souligner les mots"
"""

import json
from app import app
from models import Exercise, db

def debug_exercise_12():
    with app.app_context():
        # Récupérer l'exercice 12
        exercise = Exercise.query.get(12)
        
        if not exercise:
            print("[ERROR] Exercice 12 non trouve dans la base de donnees")
            return
        
        print(f"[OK] Exercice trouve: {exercise.title}")
        print(f"[DESC] Description: {exercise.description}")
        print(f"[TYPE] Type: {exercise.exercise_type}")
        print(f"[MAX] Tentatives max: {exercise.max_attempts}")
        print(f"[TEACHER] Enseignant ID: {exercise.teacher_id}")
        print(f"[DATE] Cree le: {exercise.created_at}")
        
        print("\n" + "="*50)
        print("[JSON] CONTENU JSON DE L'EXERCICE:")
        print("="*50)
        
        if exercise.content:
            try:
                content = json.loads(exercise.content)
                print(json.dumps(content, indent=2, ensure_ascii=False))
                
                print("\n" + "="*50)
                print("[ANALYSE] ANALYSE DU CONTENU:")
                print("="*50)
                
                if 'words' in content:
                    words_data = content['words']
                    print(f"[PHRASES] Nombre de phrases: {len(words_data)}")
                    
                    for i, sentence_data in enumerate(words_data):
                        print(f"\n[PHRASE {i+1}]")
                        print(f"   Texte: {sentence_data.get('text', 'MANQUANT')}")
                        print(f"   Mots a souligner: {sentence_data.get('words_to_underline', 'MANQUANT')}")
                else:
                    print("[ERROR] Cle 'words' manquante dans le contenu")
                    print(f"[KEYS] Cles disponibles: {list(content.keys())}")
                    
            except json.JSONDecodeError as e:
                print(f"[ERROR] Erreur de decodage JSON: {e}")
                print(f"[RAW] Contenu brut: {exercise.content}")
        else:
            print("[ERROR] Aucun contenu JSON trouve pour cet exercice")

if __name__ == "__main__":
    debug_exercise_12()
