#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour diagnostiquer le contenu JSON des exercices QCM
"""

import os
import sqlite3
import json

def debug_qcm_content():
    """Diagnostiquer le contenu JSON des exercices QCM"""
    
    # Chemin vers la base de données
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')
    
    if not os.path.exists(db_path):
        print(f"Base de donnees non trouvee: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Récupérer les exercices QCM
        cursor.execute("""
            SELECT id, title, image_path, content 
            FROM exercise 
            WHERE exercise_type = 'qcm'
            ORDER BY id
        """)
        
        exercises = cursor.fetchall()
        
        print("DIAGNOSTIC CONTENU JSON DES EXERCICES QCM")
        print("=" * 60)
        
        for exercise in exercises:
            exercise_id, title, image_path, content = exercise
            
            print(f"\nExercice ID {exercise_id}: {title}")
            print(f"Image path (DB): {image_path}")
            
            if content:
                try:
                    content_data = json.loads(content)
                    
                    # Vérifier la présence de 'image' dans le contenu
                    if 'image' in content_data:
                        print(f"Content.image: {content_data['image']}")
                        
                        # Comparer avec image_path
                        if content_data['image'] == image_path:
                            print("Status: COHERENT (image_path == content.image)")
                        else:
                            print("Status: INCOHERENT (image_path != content.image)")
                    else:
                        print("Content.image: MANQUANT")
                        print("Status: PROBLEME - pas d'image dans le JSON")
                    
                    # Afficher la structure du contenu
                    print(f"Cles du contenu: {list(content_data.keys())}")
                    
                    # Vérifier les questions
                    if 'questions' in content_data:
                        print(f"Nombre de questions: {len(content_data['questions'])}")
                    else:
                        print("Questions: MANQUANTES")
                        
                except json.JSONDecodeError as e:
                    print(f"Erreur decodage JSON: {str(e)}")
            else:
                print("Contenu: VIDE")
            
            print("-" * 40)
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Erreur lors du diagnostic: {str(e)}")
        return False

def simulate_template_condition():
    """Simuler la condition du template QCM"""
    
    print(f"\nSIMULATION CONDITION TEMPLATE:")
    print("=" * 40)
    
    # Cas de test
    test_cases = [
        {
            'content': {'image': '/static/exercises/test.png', 'questions': []},
            'description': 'Contenu avec image'
        },
        {
            'content': {'questions': []},
            'description': 'Contenu sans image'
        },
        {
            'content': None,
            'description': 'Contenu null'
        },
        {
            'content': {},
            'description': 'Contenu vide'
        }
    ]
    
    for case in test_cases:
        content = case['content']
        desc = case['description']
        
        print(f"\nCas: {desc}")
        print(f"Content: {content}")
        
        # Condition du template: {% if content and content.image %}
        if content and content.get('image'):
            print(f"Template affichera: OUI")
            print(f"URL image: {content['image']}")
        else:
            print(f"Template affichera: NON")

if __name__ == "__main__":
    debug_qcm_content()
    simulate_template_condition()
