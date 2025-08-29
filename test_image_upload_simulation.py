"""
Script pour simuler l'upload d'images sur les exercices Legend et Image Labeling.
Ce script utilise le client de test Flask pour simuler des requêtes POST avec upload d'images.
"""

import os
import sys
import json
import datetime
from io import BytesIO
from app import app, db
from models import Exercise, User
from flask import url_for

def create_test_image(filename="test_image.png", size=100):
    """Crée une image de test en mémoire"""
    # Créer une image PNG simple (un carré noir)
    from PIL import Image
    img = Image.new('RGB', (size, size), color='black')
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io

def test_image_labeling_upload(exercise_id=10):
    """Teste l'upload d'image sur un exercice Image Labeling"""
    print(f"\n=== TEST UPLOAD IMAGE SUR EXERCICE IMAGE LABELING (ID {exercise_id}) ===")
    
    # Vérifier que l'exercice existe
    exercise = Exercise.query.get(exercise_id)
    if not exercise:
        print(f"Erreur: L'exercice avec l'ID {exercise_id} n'existe pas.")
        return False
    
    if exercise.exercise_type != 'image_labeling':
        print(f"Erreur: L'exercice avec l'ID {exercise_id} n'est pas de type 'image_labeling' mais '{exercise.exercise_type}'.")
        return False
    
    print(f"Exercice trouvé: {exercise.title} (Type: {exercise.exercise_type})")
    
    # Afficher l'état actuel de l'exercice
    print("État actuel de l'exercice:")
    print(f"  Image path: {exercise.image_path}")
    content = json.loads(exercise.content) if exercise.content else {}
    main_image = content.get('main_image', None)
    print(f"  Main image dans content: {main_image}")
    
    # Créer une image de test
    test_image = create_test_image(filename="test_image_labeling.png")
    
    # Simuler un upload d'image via le client de test Flask
    with app.test_client() as client:
        client.post('/login', data={
            'email': 'admin@classesnumeriques.com',
            'password': 'admin123'
        }, follow_redirects=True)
        
        # Préparer les données du formulaire
        data = {
            'title': exercise.title,
            'description': exercise.description or '',
            'subject': exercise.subject or '',
        }
        
        # Ajouter l'image au formulaire
        data['main_image'] = (test_image, 'test_image_labeling.png')
        
        # Envoyer la requête POST
        print("Envoi de la requête POST avec upload d'image...")
        response = client.post(f'/exercise/{exercise_id}/edit', 
                              data=data,
                              content_type='multipart/form-data',
                              follow_redirects=True)
        
        print(f"Statut de la réponse: {response.status_code}")
        
        # Vérifier si l'upload a réussi
        exercise = Exercise.query.get(exercise_id)
        print("État de l'exercice après upload:")
        print(f"  Image path: {exercise.image_path}")
        content = json.loads(exercise.content) if exercise.content else {}
        main_image = content.get('main_image', None)
        print(f"  Main image dans content: {main_image}")
        
        # Vérifier si le fichier existe physiquement
        if exercise.image_path and exercise.image_path.startswith('/static/'):
            file_path = os.path.join(app.root_path, exercise.image_path.lstrip('/'))
            print(f"  Chemin physique: {file_path}")
            print(f"  Fichier existe: {os.path.exists(file_path)}")
        
        if main_image and main_image.startswith('/static/'):
            file_path = os.path.join(app.root_path, main_image.lstrip('/'))
            print(f"  Chemin physique (main_image): {file_path}")
            print(f"  Fichier existe: {os.path.exists(file_path)}")
        
        return response.status_code == 200

def test_legend_upload(exercise_id=11):
    """Teste l'upload d'image sur un exercice Legend"""
    print(f"\n=== TEST UPLOAD IMAGE SUR EXERCICE LEGEND (ID {exercise_id}) ===")
    
    # Vérifier que l'exercice existe
    exercise = Exercise.query.get(exercise_id)
    if not exercise:
        print(f"Erreur: L'exercice avec l'ID {exercise_id} n'existe pas.")
        return False
    
    if exercise.exercise_type != 'legend':
        print(f"Erreur: L'exercice avec l'ID {exercise_id} n'est pas de type 'legend' mais '{exercise.exercise_type}'.")
        return False
    
    print(f"Exercice trouvé: {exercise.title} (Type: {exercise.exercise_type})")
    
    # Afficher l'état actuel de l'exercice
    print("État actuel de l'exercice:")
    print(f"  Image path: {exercise.image_path}")
    content = json.loads(exercise.content) if exercise.content else {}
    main_image = content.get('main_image', None)
    print(f"  Main image dans content: {main_image}")
    
    # Créer une image de test
    test_image = create_test_image(filename="test_legend.png")
    
    # Simuler un upload d'image via le client de test Flask
    with app.test_client() as client:
        client.post('/login', data={
            'email': 'admin@classesnumeriques.com',
            'password': 'admin123'
        }, follow_redirects=True)
        
        # Préparer les données du formulaire
        data = {
            'title': exercise.title,
            'description': exercise.description or '',
            'subject': exercise.subject or '',
        }
        
        # Ajouter l'image au formulaire
        data['legend_main_image'] = (test_image, 'test_legend.png')
        
        # Envoyer la requête POST
        print("Envoi de la requête POST avec upload d'image...")
        response = client.post(f'/exercise/edit_exercise/{exercise_id}', 
                              data=data,
                              content_type='multipart/form-data',
                              follow_redirects=True)
        
        print(f"Statut de la réponse: {response.status_code}")
        
        # Vérifier si l'upload a réussi
        exercise = Exercise.query.get(exercise_id)
        print("État de l'exercice après upload:")
        print(f"  Image path: {exercise.image_path}")
        content = json.loads(exercise.content) if exercise.content else {}
        main_image = content.get('main_image', None)
        print(f"  Main image dans content: {main_image}")
        
        # Vérifier si le fichier existe physiquement
        if exercise.image_path and exercise.image_path.startswith('/static/'):
            file_path = os.path.join(app.root_path, exercise.image_path.lstrip('/'))
            print(f"  Chemin physique: {file_path}")
            print(f"  Fichier existe: {os.path.exists(file_path)}")
        
        if main_image and main_image.startswith('/static/'):
            file_path = os.path.join(app.root_path, main_image.lstrip('/'))
            print(f"  Chemin physique (main_image): {file_path}")
            print(f"  Fichier existe: {os.path.exists(file_path)}")
        
        return response.status_code == 200

def test_fix_image_paths():
    """Teste la route de correction automatique des chemins d'images"""
    print("\n=== TEST DE LA ROUTE DE CORRECTION AUTOMATIQUE DES CHEMINS D'IMAGES ===")
    
    with app.test_client() as client:
        # Se connecter en tant qu'admin
        client.post('/login', data={
            'email': 'admin@classesnumeriques.com',
            'password': 'admin123'
        }, follow_redirects=True)
        
        # Tester la route /fix-all-image-paths
        print("Appel de la route /fix-all-image-paths...")
        response = client.get('/fix-all-image-paths', follow_redirects=True)
        print(f"Statut de la réponse: {response.status_code}")
        
        # Afficher le contenu de la réponse
        if response.status_code == 200:
            print("Contenu de la réponse:")
            content = response.data.decode('utf-8')
            print(content[:500] + "..." if len(content) > 500 else content)
        
        # Vérifier les chemins d'images après correction
        print("\nVérification des chemins d'images après correction:")
        exercises = Exercise.query.all()
        for exercise in exercises:
            print(f"ID: {exercise.id}, Type: {exercise.exercise_type}, Titre: {exercise.title}")
            print(f"  Image path: {exercise.image_path}")
            
            try:
                content = json.loads(exercise.content) if exercise.content else {}
                if isinstance(content, dict):
                    if 'main_image' in content:
                        print(f"  Main image dans content: {content['main_image']}")
                    elif 'image' in content:
                        print(f"  Image dans content: {content['image']}")
            except Exception as e:
                print(f"  Erreur lors de la lecture du contenu JSON: {e}")
            
            print("---")
        
        return response.status_code == 200

def main():
    """Fonction principale"""
    with app.app_context():
        print("=== TESTS D'UPLOAD D'IMAGES SUR LES EXERCICES LEGEND ET IMAGE LABELING ===\n")
        
        # Tester l'upload d'image sur l'exercice Image Labeling
        test_image_labeling_upload()
        
        # Tester l'upload d'image sur l'exercice Legend
        test_legend_upload()
        
        # Tester la route de correction automatique des chemins d'images
        test_fix_image_paths()
        
        print("\n=== TESTS TERMINÉS ===")

if __name__ == "__main__":
    main()
