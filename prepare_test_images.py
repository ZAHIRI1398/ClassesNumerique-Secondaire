"""
Script pour préparer des images de test pour les exercices Legend et Image Labeling.
Ce script crée des images de test dans le dossier static/test_images/ et affiche les URLs
pour tester manuellement l'upload d'images via le navigateur.
"""

import os
import sys
import json
from PIL import Image, ImageDraw, ImageFont
from app import app, db
from models import Exercise

def create_test_image(filename, text, size=(400, 300), color='blue'):
    """Crée une image de test avec du texte"""
    # Créer le dossier de destination s'il n'existe pas
    os.makedirs('static/test_images', exist_ok=True)
    
    # Créer une image colorée avec du texte
    img = Image.new('RGB', size, color=color)
    draw = ImageDraw.Draw(img)
    
    # Ajouter du texte
    try:
        # Essayer de charger une police
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        # Utiliser la police par défaut si arial n'est pas disponible
        font = ImageFont.load_default()
    
    # Dessiner le texte au centre de l'image
    text_width, text_height = draw.textsize(text, font=font) if hasattr(draw, 'textsize') else (100, 20)
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    draw.text(position, text, fill="white", font=font)
    
    # Sauvegarder l'image
    filepath = os.path.join('static/test_images', filename)
    img.save(filepath)
    print(f"Image créée: {filepath}")
    return filepath

def check_exercise(exercise_id):
    """Vérifie l'état d'un exercice"""
    exercise = Exercise.query.get(exercise_id)
    if not exercise:
        print(f"Erreur: L'exercice avec l'ID {exercise_id} n'existe pas.")
        return None
    
    print(f"Exercice trouvé: {exercise.title} (Type: {exercise.exercise_type})")
    print(f"  Image path: {exercise.image_path}")
    
    content = json.loads(exercise.content) if exercise.content else {}
    if isinstance(content, dict):
        if 'main_image' in content:
            print(f"  Main image dans content: {content['main_image']}")
        elif 'image' in content:
            print(f"  Image dans content: {content['image']}")
    
    return exercise

def main():
    """Fonction principale"""
    with app.app_context():
        print("=== PRÉPARATION DES IMAGES DE TEST POUR LES EXERCICES LEGEND ET IMAGE LABELING ===\n")
        
        # Créer des images de test
        image_labeling_test = create_test_image(
            "test_image_labeling.png", 
            "Test Image Labeling", 
            color='darkblue'
        )
        
        legend_test = create_test_image(
            "test_legend.png", 
            "Test Legend", 
            color='darkgreen'
        )
        
        # Vérifier les exercices
        print("\nVérification de l'exercice Image Labeling (ID 10):")
        image_labeling = check_exercise(10)
        
        print("\nVérification de l'exercice Legend (ID 11):")
        legend = check_exercise(11)
        
        # Afficher les instructions pour tester manuellement
        print("\n=== INSTRUCTIONS POUR TESTER MANUELLEMENT L'UPLOAD D'IMAGES ===")
        print("1. Assurez-vous que l'application Flask est en cours d'exécution")
        print("2. Connectez-vous en tant qu'administrateur (admin@classesnumeriques.com / admin123)")
        
        if image_labeling:
            print(f"\nPour tester l'upload d'image sur l'exercice Image Labeling:")
            print(f"1. Accédez à: http://127.0.0.1:5000/exercise/{image_labeling.id}/edit")
            print(f"2. Utilisez l'image de test: {image_labeling_test}")
            print(f"3. Cliquez sur le bouton 'Parcourir' à côté de 'Image principale'")
            print(f"4. Sélectionnez l'image de test et cliquez sur 'Enregistrer'")
            print(f"5. Vérifiez que l'image s'affiche correctement après l'enregistrement")
        
        if legend:
            print(f"\nPour tester l'upload d'image sur l'exercice Legend:")
            print(f"1. Accédez à: http://127.0.0.1:5000/exercise/edit_exercise/{legend.id}")
            print(f"2. Utilisez l'image de test: {legend_test}")
            print(f"3. Cliquez sur le bouton 'Parcourir' à côté de 'Image principale'")
            print(f"4. Sélectionnez l'image de test et cliquez sur 'Enregistrer'")
            print(f"5. Vérifiez que l'image s'affiche correctement après l'enregistrement")
        
        print("\nPour tester la route de correction automatique des chemins d'images:")
        print("1. Accédez à: http://127.0.0.1:5000/fix-all-image-paths")
        print("2. Vérifiez que tous les chemins d'images sont corrigés")
        
        print("\n=== FIN DES INSTRUCTIONS ===")

if __name__ == "__main__":
    main()
