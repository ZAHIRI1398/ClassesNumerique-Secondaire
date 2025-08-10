#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from app import app, Exercise, db

def migrate_exercise_22():
    """Migrer l'exercice 22 avec des mots spécifiques par phrase"""
    with app.app_context():
        exercise = Exercise.query.get(22)
        if not exercise:
            print("Exercice 22 non trouvé")
            return
        
        print("=== MIGRATION EXERCICE 22 ===")
        
        # Définir les mots spécifiques pour chaque phrase
        specific_words_mapping = [
            "Les,enfants",      # Phrase 1: Les enfants jouent dans la cour
            "Le,lion",          # Phrase 2: Le lion a mangé la gazelle  
            "je",               # Phrase 3: Hier, je suis allé au cinéma
            "Ma,grand-mere,moi", # Phrase 4: Ma grand-mère et moi sommes très fatiguées
            "Le,petit,cochon",  # Phrase 5: Le petit cochon s'est fait manger le loup
            "Les,portes",       # Phrase 6: Les portes s'ouvrent enfin
            "nous",             # Phrase 7: Ce soir, nous irons chez nos cousins
            "Ma,petite,soeur",  # Phrase 8: Ma petite soeur joue avec les filles de Leon
            "les,murs",         # Phrase 9: À l'école maternelle, les murs sont recouverts de peintures d'enfants
            "Un,eleve"          # Phrase 10: Un élève découvre une feuille
        ]
        
        try:
            content = json.loads(exercise.content)
            
            if 'words' in content and len(content['words']) == 10:
                # Corriger chaque phrase avec ses mots spécifiques
                for i, word_data in enumerate(content['words']):
                    if i < len(specific_words_mapping):
                        # Convertir la chaîne en liste de mots
                        specific_words = [w.strip() for w in specific_words_mapping[i].split(',')]
                        word_data['words_to_underline'] = specific_words
                        print(f"Phrase {i+1}: {specific_words}")
                
                # Sauvegarder
                exercise.content = json.dumps(content, ensure_ascii=False)
                db.session.commit()
                print("✓ Exercice 22 migré avec succès!")
            else:
                print("Structure inattendue pour l'exercice 22")
                
        except Exception as e:
            print(f"Erreur migration exercice 22: {e}")

def migrate_exercise_16():
    """Migrer l'exercice 16 en nettoyant les caractères problématiques"""
    with app.app_context():
        exercise = Exercise.query.get(16)
        if not exercise:
            print("Exercice 16 non trouvé")
            return
        
        print("=== MIGRATION EXERCICE 16 ===")
        
        try:
            # Lire le contenu brut et nettoyer les caractères problématiques
            raw_content = exercise.content
            
            # Remplacer les caractères Unicode problématiques
            clean_content = raw_content.replace('\u25cf', '•').replace('\u2022', '•')
            
            # Parser le JSON nettoyé
            content = json.loads(clean_content)
            
            if 'words' in content:
                print(f"Exercice 16 a {len(content['words'])} phrases")
                
                # Nettoyer chaque phrase
                for i, word_data in enumerate(content['words']):
                    if 'sentence' in word_data:
                        # Nettoyer la phrase
                        sentence = word_data['sentence']
                        clean_sentence = sentence.replace('\u25cf', '•').replace('\u2022', '•')
                        word_data['sentence'] = clean_sentence
                        print(f"Phrase {i+1} nettoyée")
                
                # Sauvegarder avec encodage propre
                exercise.content = json.dumps(content, ensure_ascii=False)
                db.session.commit()
                print("✓ Exercice 16 migré avec succès!")
            else:
                print("Structure inattendue pour l'exercice 16")
                
        except Exception as e:
            print(f"Erreur migration exercice 16: {e}")

def migrate_exercise_24():
    """Migrer l'exercice 24 en nettoyant et corrigeant la structure"""
    with app.app_context():
        exercise = Exercise.query.get(24)
        if not exercise:
            print("Exercice 24 non trouvé")
            return
        
        print("=== MIGRATION EXERCICE 24 ===")
        
        # Définir les mots spécifiques pour chaque phrase (exercice être/avoir)
        specific_words_mapping = [
            ["être"],   # Phrase 1: Il n'y a pas encore de rostre
            ["être"],   # Phrase 2: Avez-vous faim ?
            ["être"],   # Phrase 3: Il est malade depuis trois jours
            ["être"],   # Phrase 4: Vous êtes en vacances à la montagne
            ["être"],   # Phrase 5: Nathalie est plus rapide que Françoise
            ["être"],   # Phrase 6: As-tu assez de pain pour ton repas ?
            ["être"],   # Phrase 7: Je suis le plus petit de la classe
            ["avoir"]   # Phrase 8: À la rentrée, les élèves ont un nouveau cartable
        ]
        
        try:
            # Lire le contenu brut et nettoyer
            raw_content = exercise.content
            clean_content = raw_content.replace('\u25cf', '•').replace('\u2022', '•')
            
            content = json.loads(clean_content)
            
            if 'words' in content and len(content['words']) >= 8:
                # Corriger chaque phrase avec ses mots spécifiques
                for i, word_data in enumerate(content['words']):
                    if i < len(specific_words_mapping):
                        word_data['words_to_underline'] = specific_words_mapping[i]
                        print(f"Phrase {i+1}: {specific_words_mapping[i]}")
                
                # Sauvegarder
                exercise.content = json.dumps(content, ensure_ascii=False)
                db.session.commit()
                print("✓ Exercice 24 migré avec succès!")
            else:
                print("Structure inattendue pour l'exercice 24")
                
        except Exception as e:
            print(f"Erreur migration exercice 24: {e}")

def main():
    print("=== MIGRATION GLOBALE DES EXERCICES 'SOULIGNER LES MOTS' ===")
    migrate_exercise_22()
    print()
    migrate_exercise_16()
    print()
    migrate_exercise_24()
    print()
    print("=== MIGRATION TERMINÉE ===")

if __name__ == '__main__':
    main()
