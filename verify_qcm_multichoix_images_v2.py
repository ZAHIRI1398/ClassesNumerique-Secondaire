#!/usr/bin/env python3
"""
Script de vérification des images QCM Multichoix - Version sécurisée pour production

Cette version est compatible avec PostgreSQL et SQLite, et gère les erreurs
de manière sécurisée pour éviter les crashs en production.
"""

import os
import json
from flask import current_app

def verify_qcm_multichoix_images():
    """
    Vérifie les chemins d'images pour les exercices QCM Multichoix
    
    Returns:
        list: Liste des problèmes détectés
    """
    issues = []
    
    try:
        # Utiliser SQLAlchemy au lieu d'accès direct à la base
        from app import db, Exercise
        
        # Récupérer les exercices QCM Multichoix
        exercises = Exercise.query.filter_by(exercise_type='qcm_multichoix').all()
        
        if not exercises:
            return ["Aucun exercice QCM Multichoix trouvé"]
        
        for exercise in exercises:
            try:
                # Vérifier l'image principale
                if exercise.image_path:
                    file_path = os.path.join(current_app.root_path, exercise.image_path.lstrip('/'))
                    if not os.path.exists(file_path):
                        issues.append(f"Image principale manquante pour l'exercice {exercise.id}: {exercise.image_path}")
                
                # Vérifier les images dans le contenu JSON
                if exercise.content:
                    try:
                        content = json.loads(exercise.content)
                        
                        # Vérifier les images des questions
                        if 'questions' in content:
                            for i, question in enumerate(content.get('questions', [])):
                                if 'image' in question and question['image']:
                                    image_path = question['image']
                                    file_path = os.path.join(current_app.root_path, image_path.lstrip('/'))
                                    if not os.path.exists(file_path):
                                        issues.append(f"Image de question manquante pour l'exercice {exercise.id}, question {i+1}: {image_path}")
                    except (json.JSONDecodeError, TypeError) as e:
                        issues.append(f"Erreur de décodage JSON pour l'exercice {exercise.id}: {str(e)}")
            except Exception as e:
                issues.append(f"Erreur lors de la vérification de l'exercice {exercise.id}: {str(e)}")
    
    except Exception as e:
        issues.append(f"Erreur générale: {str(e)}")
    
    return issues

if __name__ == '__main__':
    # Ce script est conçu pour être importé et utilisé dans l'application Flask
    print("Ce script doit être exécuté dans le contexte de l'application Flask")
