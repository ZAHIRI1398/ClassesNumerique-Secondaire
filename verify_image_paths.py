"""
Script de vérification des chemins d'images après upload.
Ce script vérifie les chemins d'images des exercices Legend et Image Labeling
et valide que les fichiers existent physiquement.
"""

import os
import sys
import json
import io
import locale
from app import app, db
from models import Exercise

# Configurer l'encodage pour éviter les problèmes avec les caractères spéciaux
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def check_image_path(path, root_path):
    """Vérifie si un chemin d'image existe physiquement"""
    if not path:
        return False, "Chemin vide"
    
    # Normaliser le chemin
    if path.startswith('/static/'):
        file_path = os.path.join(root_path, path.lstrip('/'))
    elif path.startswith('static/'):
        file_path = os.path.join(root_path, path)
    else:
        file_path = os.path.join(root_path, 'static', path)
    
    exists = os.path.exists(file_path)
    return exists, file_path

def verify_exercise_images(exercise_id):
    """Vérifie les chemins d'images d'un exercice spécifique"""
    exercise = Exercise.query.get(exercise_id)
    if not exercise:
        print(f"Erreur: L'exercice avec l'ID {exercise_id} n'existe pas.")
        return False
    
    print(f"\n=== VÉRIFICATION DES CHEMINS D'IMAGES POUR L'EXERCICE {exercise.id} ===")
    print(f"Titre: {exercise.title}")
    print(f"Type: {exercise.exercise_type}")
    
    # Vérifier le chemin d'image principal de l'exercice
    print("\n1. Vérification du chemin d'image principal (exercise.image_path):")
    if exercise.image_path:
        exists, file_path = check_image_path(exercise.image_path, app.root_path)
        print(f"  Chemin: {exercise.image_path}")
        print(f"  Chemin physique: {file_path}")
        print(f"  Fichier existe: {exists}")
        if not exists:
            print(f"  ERREUR: Le fichier n'existe pas physiquement!")
    else:
        print("  Aucun chemin d'image principal défini.")
    
    # Vérifier les chemins d'images dans le contenu JSON
    print("\n2. Vérification des chemins d'images dans le contenu JSON:")
    content = json.loads(exercise.content) if exercise.content else {}
    
    if exercise.exercise_type == 'image_labeling':
        main_image = content.get('main_image')
        if main_image:
            exists, file_path = check_image_path(main_image, app.root_path)
            print(f"  Image principale (main_image): {main_image}")
            print(f"  Chemin physique: {file_path}")
            print(f"  Fichier existe: {exists}")
            if not exists:
                print(f"  ERREUR: Le fichier n'existe pas physiquement!")
        else:
            print("  Aucune image principale définie dans le contenu JSON.")
        
        # Vérifier les images des étiquettes
        labels = content.get('labels', [])
        if labels:
            print(f"\n  Vérification des {len(labels)} étiquettes:")
            for i, label in enumerate(labels):
                if 'image' in label:
                    exists, file_path = check_image_path(label['image'], app.root_path)
                    print(f"    Étiquette {i+1}: {label.get('text', 'Sans texte')}")
                    print(f"    Image: {label['image']}")
                    print(f"    Chemin physique: {file_path}")
                    print(f"    Fichier existe: {exists}")
                    if not exists:
                        print(f"    ERREUR: Le fichier n'existe pas physiquement!")
    
    elif exercise.exercise_type == 'legend':
        # Vérifier l'image principale pour les exercices de type Legend
        image = content.get('image')
        if image:
            exists, file_path = check_image_path(image, app.root_path)
            print(f"  Image dans le contenu JSON: {image}")
            print(f"  Chemin physique: {file_path}")
            print(f"  Fichier existe: {exists}")
            if not exists:
                print(f"  ERREUR: Le fichier n'existe pas physiquement!")
        else:
            print("  Aucune image définie dans le contenu JSON.")
        
        # Vérifier les légendes
        legends = content.get('legends', [])
        if legends:
            print(f"\n  Vérification des {len(legends)} légendes:")
            for i, legend in enumerate(legends):
                print(f"    Légende {i+1}: {legend.get('text', 'Sans texte')}")
    
    # Vérifier la cohérence entre les chemins
    print("\n3. Vérification de la cohérence des chemins:")
    if exercise.exercise_type == 'image_labeling' and exercise.image_path and content.get('main_image'):
        if exercise.image_path != content.get('main_image'):
            print(f"  INCOHÉRENCE: Le chemin principal ({exercise.image_path}) ne correspond pas")
            print(f"  au chemin dans le contenu JSON ({content.get('main_image')}).")
        else:
            print("  Les chemins sont cohérents.")
    elif exercise.exercise_type == 'legend' and exercise.image_path and content.get('image'):
        if exercise.image_path != content.get('image'):
            print(f"  INCOHÉRENCE: Le chemin principal ({exercise.image_path}) ne correspond pas")
            print(f"  au chemin dans le contenu JSON ({content.get('image')}).")
        else:
            print("  Les chemins sont cohérents.")
    
    # Vérifier le format des chemins
    print("\n4. Vérification du format des chemins:")
    paths_to_check = []
    if exercise.image_path:
        paths_to_check.append(("image_path", exercise.image_path))
    
    if exercise.exercise_type == 'image_labeling' and content.get('main_image'):
        paths_to_check.append(("main_image", content.get('main_image')))
        for i, label in enumerate(content.get('labels', [])):
            if 'image' in label:
                paths_to_check.append((f"label_{i+1}", label['image']))
    
    elif exercise.exercise_type == 'legend' and content.get('image'):
        paths_to_check.append(("content.image", content.get('image')))
    
    for name, path in paths_to_check:
        if path.startswith('/static/'):
            print(f"  [OK] {name}: Format correct ({path})")
        else:
            print(f"  [ERREUR] {name}: Format incorrect ({path})")
            print(f"    Le chemin devrait commencer par '/static/'")
    
    print("\n=== FIN DE LA VÉRIFICATION ===")
    return True

def main():
    """Fonction principale"""
    with app.app_context():
        print("=== VÉRIFICATION DES CHEMINS D'IMAGES DES EXERCICES ===\n")
        
        # Vérifier l'exercice Image Labeling (ID 10)
        verify_exercise_images(10)
        
        # Vérifier l'exercice Legend (ID 11)
        verify_exercise_images(11)
        
        # Vérifier tous les exercices avec des images
        print("\n=== VÉRIFICATION DE TOUS LES EXERCICES AVEC DES IMAGES ===")
        exercises = Exercise.query.filter(Exercise.image_path.isnot(None)).all()
        print(f"Nombre d'exercices avec des images: {len(exercises)}")
        for exercise in exercises:
            print(f"ID: {exercise.id}, Type: {exercise.exercise_type}, Titre: {exercise.title}")
            print(f"  Image path: {exercise.image_path}")
        
        print("\n=== INSTRUCTIONS POUR CORRIGER LES CHEMINS D'IMAGES ===")
        print("1. Accédez à: http://127.0.0.1:5000/fix-all-image-paths")
        print("2. Vérifiez que tous les chemins d'images sont corrigés")
        print("3. Exécutez à nouveau ce script pour confirmer les corrections")

if __name__ == "__main__":
    main()
