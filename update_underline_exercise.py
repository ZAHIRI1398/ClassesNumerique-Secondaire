#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour mettre à jour l'exercice "Souligner les mots" existant avec la bonne structure
"""

import json
from app import app, db
from models import Exercise

def update_underline_exercise():
    with app.app_context():
        # Récupérer l'exercice existant
        exercise = Exercise.query.get(11)
        if not exercise:
            print("Erreur: Exercice ID 11 non trouvé")
            return
        
        print(f"Mise à jour de l'exercice: {exercise.title}")
        
        # Nouvelle structure compatible avec le template
        new_content = {
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
        
        # Mettre à jour le contenu
        exercise.content = json.dumps(new_content, ensure_ascii=False)
        db.session.commit()
        
        print("Exercice mis à jour avec succès !")
        print("Structure corrigée pour compatibilité avec le template")
        print("URL de test: http://127.0.0.1:5000/exercise/11")
        
        # Afficher la nouvelle structure
        print("\nNouvelle structure:")
        for i, sentence in enumerate(new_content['sentences'], 1):
            print(f"   Phrase {i}: {' '.join(sentence['words'])}")
            print(f"   Mots à souligner: {', '.join(sentence['words_to_underline'])}")
            print()

if __name__ == "__main__":
    update_underline_exercise()
