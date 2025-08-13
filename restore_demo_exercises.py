#!/usr/bin/env python3
"""
Script pour restaurer des exercices de démonstration
"""

from app import app, db
from models import User, Exercise
import json
from datetime import datetime

def restore_demo_exercises():
    with app.app_context():
        try:
            # Récupérer l'utilisateur mr.zahiri@gmail.com
            zahiri_user = User.query.filter_by(email='mr.zahiri@gmail.com').first()
            if not zahiri_user:
                print("Erreur: Compte mr.zahiri@gmail.com non trouve")
                return False
            
            print(f"Utilisateur trouve: {zahiri_user.name} (ID: {zahiri_user.id})")
            
            # Exercices de démonstration à créer
            demo_exercises = [
                {
                    'title': 'QCM - Les nombres decimaux',
                    'description': 'Exercice sur les nombres decimaux pour CM2',
                    'exercise_type': 'qcm',
                    'subject': 'Mathematiques',
                    'content': {
                        'questions': [
                            {
                                'question': 'Combien vaut 2,5 + 1,3 ?',
                                'options': ['3,8', '2,8', '4,8', '3,5'],
                                'correct_answer': 0
                            },
                            {
                                'question': 'Comment ecrit-on "trois virgule sept" en chiffres ?',
                                'options': ['3,7', '37', '3.7', '0,37'],
                                'correct_answer': 0
                            }
                        ]
                    }
                },
                {
                    'title': 'Texte a trous - Les verbes',
                    'description': 'Conjugaison des verbes au present',
                    'exercise_type': 'fill_in_blanks',
                    'subject': 'Francais',
                    'content': {
                        'text': 'Je ___ (aller) a l\'ecole. Tu ___ (avoir) un livre. Il ___ (etre) content.',
                        'words': ['vais', 'as', 'est'],
                        'available_words': ['vais', 'as', 'est', 'va', 'ai', 'es']
                    }
                },
                {
                    'title': 'Association de paires - Capitales',
                    'description': 'Associer les pays a leurs capitales',
                    'exercise_type': 'pairs',
                    'subject': 'Geographie',
                    'content': {
                        'pairs': [
                            {'left': 'France', 'right': 'Paris'},
                            {'left': 'Italie', 'right': 'Rome'},
                            {'left': 'Espagne', 'right': 'Madrid'}
                        ]
                    }
                },
                {
                    'title': 'Mots a placer - Les animaux',
                    'description': 'Placer les noms d\'animaux dans les phrases',
                    'exercise_type': 'word_placement',
                    'subject': 'Francais',
                    'content': {
                        'sentences': [
                            'Le ___ miaule dans le jardin.',
                            'Le ___ aboie fort.',
                            'L\'___ vole dans le ciel.'
                        ],
                        'words': ['chat', 'chien', 'oiseau']
                    }
                },
                {
                    'title': 'Souligner les mots - Adjectifs',
                    'description': 'Souligner tous les adjectifs dans le texte',
                    'exercise_type': 'underline_words',
                    'subject': 'Francais',
                    'content': {
                        'words': [
                            {'text': 'Le', 'underline': False},
                            {'text': 'petit', 'underline': True},
                            {'text': 'chat', 'underline': False},
                            {'text': 'noir', 'underline': True},
                            {'text': 'dort', 'underline': False},
                            {'text': 'sur', 'underline': False},
                            {'text': 'le', 'underline': False},
                            {'text': 'grand', 'underline': True},
                            {'text': 'canape', 'underline': False},
                            {'text': 'confortable', 'underline': True}
                        ]
                    }
                }
            ]
            
            created_count = 0
            for exercise_data in demo_exercises:
                # Vérifier si l'exercice existe déjà
                existing = Exercise.query.filter_by(
                    title=exercise_data['title'],
                    teacher_id=zahiri_user.id
                ).first()
                
                if existing:
                    print(f"Exercice '{exercise_data['title']}' existe deja")
                    continue
                
                # Créer l'exercice
                exercise = Exercise(
                    title=exercise_data['title'],
                    description=exercise_data['description'],
                    exercise_type=exercise_data['exercise_type'],
                    subject=exercise_data['subject'],
                    content=json.dumps(exercise_data['content'], ensure_ascii=False),
                    teacher_id=zahiri_user.id,
                    created_at=datetime.utcnow()
                )
                
                db.session.add(exercise)
                created_count += 1
                print(f"Cree: {exercise_data['title']} ({exercise_data['exercise_type']})")
            
            db.session.commit()
            print(f"Total exercices crees: {created_count}")
            return True
            
        except Exception as e:
            print(f"Erreur lors de la creation des exercices: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("Restauration des exercices de demonstration...")
    success = restore_demo_exercises()
    if success:
        print("Restauration terminee avec succes !")
    else:
        print("Echec de la restauration des exercices")
