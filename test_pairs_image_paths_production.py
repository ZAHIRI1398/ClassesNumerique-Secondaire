"""
Script de diagnostic pour vérifier les chemins d'images dans les exercices de paires en production
Ce script peut être exécuté directement sur le serveur de production pour diagnostiquer les problèmes d'affichage
"""

import os
import json
import sys
import requests
from flask import Flask, current_app
from models import db, Exercise
from improved_normalize_pairs_exercise_paths import normalize_pairs_exercise_content, check_image_paths

# Configuration de l'application Flask
app = Flask(__name__)

# Déterminer le chemin correct de la base de données
base_dir = os.path.abspath(os.path.dirname(__file__))
instance_path = os.path.join(base_dir, 'instance')
db_path = os.path.join(instance_path, 'app.db')

# Vérifier si le fichier existe à cet emplacement
if not os.path.exists(db_path):
    # Essayer avec le fichier à la racine
    db_path = os.path.join(base_dir, 'app.db')
    if not os.path.exists(db_path):
        print(f"ERREUR: Base de données introuvable à {db_path} ou {os.path.join(instance_path, 'app.db')}")
        sys.exit(1)
    else:
        print(f"Utilisation de la base de données à la racine: {db_path}")
else:
    print(f"Utilisation de la base de données dans instance: {db_path}")

# Configurer l'URI SQLAlchemy avec le chemin absolu
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def check_image_path_accessibility(path):
    """
    Vérifie si un chemin d'image est accessible localement ou via URL
    
    Args:
        path (str): Chemin ou URL de l'image à vérifier
        
    Returns:
        tuple: (accessible, message, type)
    """
    if not path or not isinstance(path, str):
        return False, "Chemin vide ou invalide", None
    
    # Vérifier si c'est une URL externe
    if path.startswith(('http://', 'https://', 'data:')):
        try:
            # Pour les URLs externes, on utilise toujours requests
            response = requests.head(path, timeout=5)
            accessible = response.status_code == 200
            content_type = response.headers.get('Content-Type', '')
            is_image = content_type.startswith('image/')
            
            return accessible and is_image, f"Status: {response.status_code}", content_type
        except Exception as e:
            return False, f"Erreur URL externe: {str(e)}", None
    
    # Pour les chemins locaux, vérifier l'existence du fichier
    local_path = path
    
    # Normaliser le chemin local
    if path.startswith('/static/'):
        # Enlever le préfixe /static/ pour obtenir le chemin relatif
        local_path = path[8:]
    elif path.startswith('static/'):
        # Enlever le préfixe static/ pour obtenir le chemin relatif
        local_path = path[7:]
    
    # Construire le chemin absolu
    base_dir = os.path.abspath(os.path.dirname(__file__))
    static_dir = os.path.join(base_dir, 'static')
    absolute_path = os.path.join(static_dir, local_path)
    
    # Vérifier si le fichier existe
    if os.path.isfile(absolute_path):
        # Déterminer le type de fichier
        _, ext = os.path.splitext(absolute_path)
        file_type = f"image/{ext[1:]}" if ext else "unknown"
        file_size = os.path.getsize(absolute_path)
        
        return True, f"Fichier existant ({file_size} octets)", file_type
    else:
        # Essayer avec d'autres chemins possibles
        alternative_paths = [
            os.path.join(static_dir, 'uploads', os.path.basename(local_path)),
            os.path.join(static_dir, 'uploads', 'general', os.path.basename(local_path)),
            os.path.join(static_dir, 'exercise-images', os.path.basename(local_path)),
            os.path.join(static_dir, 'exercise_images', os.path.basename(local_path))
        ]
        
        for alt_path in alternative_paths:
            if os.path.isfile(alt_path):
                _, ext = os.path.splitext(alt_path)
                file_type = f"image/{ext[1:]}" if ext else "unknown"
                file_size = os.path.getsize(alt_path)
                return True, f"Fichier existant dans chemin alternatif ({file_size} octets): {alt_path}", file_type
        
        return False, f"Fichier introuvable: {absolute_path}", None

def check_pairs_exercise_images():
    """Vérifie les chemins d'images dans les exercices de paires"""
    with app.app_context():
        # Récupérer tous les exercices de type 'pairs'
        pairs_exercises = Exercise.query.filter_by(exercise_type='pairs').all()
        
        print(f"Nombre d'exercices de paires trouvés: {len(pairs_exercises)}")
        
        # Statistiques globales
        total_exercises = len(pairs_exercises)
        exercises_with_images = 0
        total_images = 0
        accessible_images = 0
        inaccessible_images = 0
        
        for exercise in pairs_exercises:
            print(f"\n--- Exercice ID: {exercise.id}, Titre: {exercise.title} ---")
            
            if not exercise.content:
                print("  Pas de contenu JSON")
                continue
                
            try:
                content = json.loads(exercise.content)
                
                # Vérifier si le contenu a des paires
                if 'pairs' not in content or not isinstance(content['pairs'], list):
                    print("  Pas de paires dans le contenu")
                    continue
                    
                print(f"  Nombre de paires: {len(content['pairs'])}")
                
                # Compter les images dans cet exercice
                exercise_images = 0
                exercise_accessible_images = 0
                
                # Vérifier chaque paire
                for i, pair in enumerate(content['pairs']):
                    print(f"\n  Paire {i+1}:")
                    
                    # Vérifier l'élément gauche
                    if 'left' in pair and isinstance(pair['left'], dict):
                        left_type = pair['left'].get('type')
                        left_content = pair['left'].get('content')
                        
                        print(f"    Gauche (type: {left_type}): {left_content}")
                        
                        if left_type == 'image' and left_content:
                            total_images += 1
                            exercise_images += 1
                            
                            # Vérifier si l'image est accessible
                            accessible, message, content_type = check_image_path_accessibility(left_content)
                            print(f"    -> Image gauche accessible: {accessible} ({message}, type: {content_type})")
                            
                            if accessible:
                                accessible_images += 1
                                exercise_accessible_images += 1
                            else:
                                inaccessible_images += 1
                    
                    # Vérifier l'élément droit
                    if 'right' in pair and isinstance(pair['right'], dict):
                        right_type = pair['right'].get('type')
                        right_content = pair['right'].get('content')
                        
                        print(f"    Droite (type: {right_type}): {right_content}")
                        
                        if right_type == 'image' and right_content:
                            total_images += 1
                            exercise_images += 1
                            
                            # Vérifier si l'image est accessible
                            accessible, message, content_type = check_image_path_accessibility(right_content)
                            print(f"    -> Image droite accessible: {accessible} ({message}, type: {content_type})")
                            
                            if accessible:
                                accessible_images += 1
                                exercise_accessible_images += 1
                            else:
                                inaccessible_images += 1
                
                # Mettre à jour les statistiques
                if exercise_images > 0:
                    exercises_with_images += 1
                    print(f"\n  Résumé de l'exercice: {exercise_accessible_images}/{exercise_images} images accessibles")
                
                # Tester la normalisation
                print("\n  Test de normalisation:")
                normalized_content = normalize_pairs_exercise_content(content)
                
                # Vérifier si la normalisation a changé quelque chose
                if normalized_content != content:
                    print("  -> La normalisation a modifié le contenu")
                    
                    # Vérifier les changements dans les paires
                    for i, (orig_pair, norm_pair) in enumerate(zip(content['pairs'], normalized_content['pairs'])):
                        if orig_pair != norm_pair:
                            print(f"  -> Paire {i+1} modifiée:")
                            
                            # Vérifier les changements dans l'élément gauche
                            if orig_pair.get('left') != norm_pair.get('left'):
                                print(f"    -> Gauche original: {orig_pair.get('left', {}).get('content')}")
                                print(f"    -> Gauche normalisé: {norm_pair.get('left', {}).get('content')}")
                                
                                # Vérifier si l'image normalisée est accessible
                                if norm_pair.get('left', {}).get('type') == 'image':
                                    norm_path = norm_pair.get('left', {}).get('content')
                                    accessible, message, content_type = check_image_path_accessibility(norm_path)
                                    print(f"    -> Image gauche normalisée accessible: {accessible} ({message}, type: {content_type})")
                            
                            # Vérifier les changements dans l'élément droit
                            if orig_pair.get('right') != norm_pair.get('right'):
                                print(f"    -> Droite original: {orig_pair.get('right', {}).get('content')}")
                                print(f"    -> Droite normalisé: {norm_pair.get('right', {}).get('content')}")
                                
                                # Vérifier si l'image normalisée est accessible
                                if norm_pair.get('right', {}).get('type') == 'image':
                                    norm_path = norm_pair.get('right', {}).get('content')
                                    accessible, message, content_type = check_image_path_accessibility(norm_path)
                                    print(f"    -> Image droite normalisée accessible: {accessible} ({message}, type: {content_type})")
                else:
                    print("  -> La normalisation n'a pas modifié le contenu")
                    
            except Exception as e:
                print(f"  Erreur lors de l'analyse du contenu: {str(e)}")
        
        # Afficher les statistiques globales
        print("\n=== RÉSUMÉ GLOBAL ===")
        print(f"Exercices de paires: {total_exercises}")
        print(f"Exercices avec images: {exercises_with_images}")
        print(f"Images totales: {total_images}")
        print(f"Images accessibles: {accessible_images}")
        print(f"Images inaccessibles: {inaccessible_images}")
        print(f"Taux d'accessibilité: {accessible_images/total_images*100:.2f}% si total_images > 0 else 'N/A'")

def main():
    """Fonction principale"""
    try:
        check_pairs_exercise_images()
        print("\nDiagnostic des chemins d'images terminé avec succès!")
    except Exception as e:
        print(f"\nErreur lors du diagnostic des chemins d'images: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
