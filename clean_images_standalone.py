#!/usr/bin/env python3
"""
Script autonome pour nettoyer les références d'images dans la base de données
et créer une structure de répertoires propre pour les images d'exercices.
"""

import sqlite3
import json
import os
import shutil
from datetime import datetime

def find_database():
    """Trouve le fichier de base de données avec des données"""
    possible_paths = [
        'instance/app.db',
        'instance/classe_numerique.db', 
        'instance/classes_numeriques.db',
        'classes_numeriques.db',
        'app.db'
    ]
    
    for path in possible_paths:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            print(f"Base de données trouvée: {path} ({os.path.getsize(path)} bytes)")
            return path
    
    print("Aucune base de données avec données trouvée")
    return None

def backup_database(db_path):
    """Crée une sauvegarde de la base de données"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.backup_{timestamp}"
    shutil.copy2(db_path, backup_path)
    print(f"Sauvegarde créée: {backup_path}")
    return backup_path

def clean_image_references(db_path):
    """Nettoie toutes les références d'images dans la base de données"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Vérifier que la table exercise existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='exercise'")
        if not cursor.fetchone():
            print("Table 'exercise' non trouvée dans la base de données")
            return False
        
        # Obtenir les statistiques avant nettoyage
        cursor.execute("SELECT COUNT(*) FROM exercise")
        total_exercises = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM exercise WHERE image_path IS NOT NULL AND image_path != ''")
        exercises_with_images = cursor.fetchone()[0]
        
        print(f"Statistiques avant nettoyage:")
        print(f"  - Total exercices: {total_exercises}")
        print(f"  - Exercices avec images: {exercises_with_images}")
        
        # Nettoyer les champs image_path
        cursor.execute("UPDATE exercise SET image_path = NULL WHERE image_path IS NOT NULL")
        updated_image_paths = cursor.rowcount
        
        # Nettoyer les références d'images dans le contenu JSON
        cursor.execute("SELECT id, content FROM exercise WHERE content IS NOT NULL AND content != ''")
        exercises_with_content = cursor.fetchall()
        
        updated_content_count = 0
        for exercise_id, content_str in exercises_with_content:
            try:
                content = json.loads(content_str)
                content_modified = False
                
                # Nettoyer les différents champs d'images possibles
                image_fields = ['image', 'main_image', 'background_image', 'illustration']
                for field in image_fields:
                    if field in content and content[field]:
                        content[field] = None
                        content_modified = True
                
                # Nettoyer les images dans les questions (QCM, etc.)
                if 'questions' in content and isinstance(content['questions'], list):
                    for question in content['questions']:
                        if isinstance(question, dict) and 'image' in question:
                            if question['image']:
                                question['image'] = None
                                content_modified = True
                
                # Nettoyer les images dans les éléments (légendes, etc.)
                if 'elements' in content and isinstance(content['elements'], list):
                    for element in content['elements']:
                        if isinstance(element, dict) and 'image' in element:
                            if element['image']:
                                element['image'] = None
                                content_modified = True
                
                # Nettoyer les images dans les paires
                if 'pairs' in content and isinstance(content['pairs'], list):
                    for pair in content['pairs']:
                        if isinstance(pair, dict):
                            for side in ['left', 'right']:
                                if side in pair and isinstance(pair[side], dict) and 'image' in pair[side]:
                                    if pair[side]['image']:
                                        pair[side]['image'] = None
                                        content_modified = True
                
                # Sauvegarder si modifié
                if content_modified:
                    updated_content = json.dumps(content, ensure_ascii=False)
                    cursor.execute("UPDATE exercise SET content = ? WHERE id = ?", (updated_content, exercise_id))
                    updated_content_count += 1
                    
            except json.JSONDecodeError:
                print(f"Erreur JSON pour l'exercice {exercise_id}, ignoré")
                continue
        
        # Valider les changements
        conn.commit()
        
        print(f"\nNettoyage terminé:")
        print(f"  - Champs image_path nettoyés: {updated_image_paths}")
        print(f"  - Contenus JSON modifiés: {updated_content_count}")
        
        return True
        
    except Exception as e:
        print(f"Erreur lors du nettoyage: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def create_clean_directory_structure():
    """Crée une structure de répertoires propre pour les images"""
    base_dir = "static/uploads"
    
    # Créer les répertoires pour chaque type d'exercice
    exercise_types = [
        'qcm',
        'fill_in_blanks',
        'flashcards',
        'pairs',
        'image_labeling',
        'legend',
        'word_placement',
        'drag_and_drop',
        'general'
    ]
    
    created_dirs = []
    for exercise_type in exercise_types:
        dir_path = os.path.join(base_dir, exercise_type)
        os.makedirs(dir_path, exist_ok=True)
        
        # Créer un fichier .gitkeep pour préserver le répertoire
        gitkeep_path = os.path.join(dir_path, '.gitkeep')
        if not os.path.exists(gitkeep_path):
            with open(gitkeep_path, 'w') as f:
                f.write('')
        
        created_dirs.append(dir_path)
    
    print(f"\nStructure de répertoires créée:")
    for dir_path in created_dirs:
        print(f"  - {dir_path}")
    
    return created_dirs

def main():
    """Fonction principale"""
    print("=== Script de nettoyage d'images ===")
    print()
    
    # Trouver la base de données
    db_path = find_database()
    if not db_path:
        print("Impossible de continuer sans base de données")
        return
    
    # Créer une sauvegarde
    backup_path = backup_database(db_path)
    
    # Nettoyer les références d'images
    print("\n1. Nettoyage des références d'images...")
    if clean_image_references(db_path):
        print("Nettoyage réussi!")
    else:
        print("Échec du nettoyage")
        return
    
    # Créer la structure de répertoires
    print("\n2. Création de la structure de répertoires...")
    created_dirs = create_clean_directory_structure()
    
    print(f"\n=== Nettoyage terminé avec succès ===")
    print(f"Sauvegarde: {backup_path}")
    print(f"Répertoires créés: {len(created_dirs)}")
    print("\nVous pouvez maintenant:")
    print("1. Tester l'application pour vérifier que tout fonctionne")
    print("2. Commencer à uploader de nouvelles images dans les répertoires appropriés")
    print("3. Restaurer la sauvegarde si nécessaire")

if __name__ == "__main__":
    main()
