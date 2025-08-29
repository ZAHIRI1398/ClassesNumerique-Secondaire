#!/usr/bin/env python3
"""
Script simple pour nettoyer le système d'images via Flask
"""

import os
import sys
import json

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import de l'app Flask existante
from app import app, db
from models import Exercise

def reset_all_images():
    """Supprimer toutes les références d'images dans la base de données"""
    print("Nettoyage complet du systeme d'images...")
    
    with app.app_context():
        try:
            # Compter les exercices avec images
            exercises_with_images = Exercise.query.filter(Exercise.image_path.isnot(None)).count()
            print(f"Exercices avec images trouves: {exercises_with_images}")
            
            # Supprimer toutes les références d'images
            updated_count = Exercise.query.filter(Exercise.image_path.isnot(None)).update({Exercise.image_path: None})
            db.session.commit()
            
            print(f"{updated_count} exercices mis a jour (image_path = NULL)")
            
            # Nettoyer aussi les contenus JSON qui pourraient contenir des images
            exercises_with_content = Exercise.query.filter(Exercise.content.isnot(None)).all()
            content_updated = 0
            
            for exercise in exercises_with_content:
                if exercise.content:
                    try:
                        content = json.loads(exercise.content)
                        if isinstance(content, dict):
                            # Supprimer les clés d'images communes
                            image_keys = ['image', 'main_image', 'exercise_image']
                            updated = False
                            for key in image_keys:
                                if key in content:
                                    del content[key]
                                    updated = True
                            
                            # Nettoyer les images dans les cartes (flashcards)
                            if 'cards' in content and isinstance(content['cards'], list):
                                for card in content['cards']:
                                    if isinstance(card, dict) and 'image' in card:
                                        del card['image']
                                        updated = True
                            
                            # Nettoyer les images dans les paires
                            if 'pairs' in content and isinstance(content['pairs'], list):
                                for pair in content['pairs']:
                                    if isinstance(pair, dict):
                                        for side in ['left', 'right']:
                                            if side in pair and isinstance(pair[side], dict):
                                                if pair[side].get('type') == 'image':
                                                    pair[side]['type'] = 'text'
                                                    pair[side]['content'] = ''
                                                    updated = True
                            
                            if updated:
                                exercise.content = json.dumps(content)
                                content_updated += 1
                    except json.JSONDecodeError:
                        continue
            
            if content_updated > 0:
                db.session.commit()
                print(f"{content_updated} contenus JSON nettoyes")
            
            print("Nettoyage termine avec succes!")
            return True
            
        except Exception as e:
            print(f"Erreur lors du nettoyage: {str(e)}")
            db.session.rollback()
            return False

def create_clean_image_system():
    """Créer un système d'images propre et cohérent"""
    print("\nCreation du nouveau systeme d'images...")
    
    # Créer la structure de dossiers propre
    upload_dirs = [
        'static/uploads',
        'static/uploads/exercises',
        'static/uploads/exercises/qcm',
        'static/uploads/exercises/fill_in_blanks',
        'static/uploads/exercises/flashcards',
        'static/uploads/exercises/pairs',
        'static/uploads/exercises/image_labeling',
        'static/uploads/exercises/legend',
        'static/uploads/exercises/word_placement',
        'static/uploads/exercises/underline_words'
    ]
    
    for directory in upload_dirs:
        os.makedirs(directory, exist_ok=True)
        # Créer un fichier .gitkeep pour préserver la structure
        gitkeep_path = os.path.join(directory, '.gitkeep')
        if not os.path.exists(gitkeep_path):
            with open(gitkeep_path, 'w') as f:
                f.write('# Keep this directory in git\n')
    
    print("Structure de dossiers creee:")
    for directory in upload_dirs:
        print(f"   - {directory}")
    
    print("Nouveau systeme d'images cree!")

def show_statistics():
    """Afficher les statistiques après nettoyage"""
    print("\nStatistiques apres nettoyage:")
    
    with app.app_context():
        try:
            total_exercises = Exercise.query.count()
            exercises_with_images = Exercise.query.filter(Exercise.image_path.isnot(None)).count()
            
            print(f"   - Total exercices: {total_exercises}")
            print(f"   - Exercices avec images: {exercises_with_images}")
            print(f"   - Exercices sans images: {total_exercises - exercises_with_images}")
        except Exception as e:
            print(f"Erreur lors de l'affichage des statistiques: {str(e)}")

if __name__ == "__main__":
    print("Script de nettoyage du systeme d'images")
    print("=" * 50)
    
    # Étape 1: Nettoyer la base de données
    if reset_all_images():
        # Étape 2: Créer le nouveau système
        create_clean_image_system()
        
        # Étape 3: Afficher les statistiques
        show_statistics()
        
        print("\nNettoyage complet termine!")
        print("Vous pouvez maintenant ajouter des images avec un systeme propre.")
    else:
        print("\nEchec du nettoyage. Verifiez les erreurs ci-dessus.")
