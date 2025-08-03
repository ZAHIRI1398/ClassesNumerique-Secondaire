#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour créer un exercice "Souligner les mots" de test
"""

import json
from app import app, db
from models import Exercise, Course, User

def create_underline_exercise():
    with app.app_context():
        # Récupérer ou créer un utilisateur enseignant
        teacher = User.query.filter_by(role='teacher').first()
        if not teacher:
            print("Aucun enseignant trouve. Creons un enseignant de test.")
            teacher = User(
                username="prof_test",
                email="prof@test.com",
                role="teacher"
            )
            teacher.set_password("password123")
            db.session.add(teacher)
            db.session.commit()
            print(f"Enseignant cree : {teacher.username} (ID: {teacher.id})")

        # Contenu de l'exercice "Souligner les mots" - Structure compatible avec le template
        exercise_content = {
            "sentences": [
                {
                    "words": ["Le", "chat", "noir", "dort", "sur", "le", "canapé", "rouge."],
                    "words_to_underline": ["chat", "noir", "canapé", "rouge"]
                },
                {
                    "words": ["Les", "enfants", "jouent", "dans", "le", "jardin", "fleuri."],
                    "words_to_underline": ["enfants", "jardin", "fleuri"]
                },
                {
                    "words": ["La", "voiture", "bleue", "roule", "rapidement", "sur", "l'autoroute."],
                    "words_to_underline": ["voiture", "bleue", "rapidement", "autoroute"]
                }
            ],
            "instructions": "Soulignez tous les noms et adjectifs dans chaque phrase.",
            "matiere": "Français"
        }

        # Créer l'exercice
        exercise = Exercise(
            title="Identifier les noms et adjectifs",
            description="Exercice pour identifier et souligner les noms et adjectifs dans des phrases simples.",
            exercise_type="underline_words",
            content=json.dumps(exercise_content, ensure_ascii=False),
            teacher_id=teacher.id
        )

        db.session.add(exercise)
        db.session.commit()

        print(f"Exercice 'Souligner les mots' cree avec succes !")
        print(f"   - ID: {exercise.id}")
        print(f"   - Titre: {exercise.title}")
        print(f"   - Type: {exercise.exercise_type}")
        print(f"   - Enseignant: {teacher.username}")
        print(f"   - URL: http://127.0.0.1:5000/exercise/{exercise.id}")
        
        # Afficher le contenu pour vérification
        print(f"\nContenu de l'exercice:")
        content = json.loads(exercise.content)
        for i, sentence in enumerate(content['sentences'], 1):
            print(f"   Phrase {i}: {sentence['text']}")
            print(f"   Mots à souligner: {', '.join(sentence['words_to_underline'])}")
            print()

        return exercise.id

if __name__ == "__main__":
    exercise_id = create_underline_exercise()
    print(f"Exercice cree ! Testez-le sur : http://127.0.0.1:5000/exercise/{exercise_id}")
