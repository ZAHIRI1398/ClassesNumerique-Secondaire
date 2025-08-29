#!/usr/bin/env python3
"""
Script pour corriger automatiquement tous les chemins d'images incorrects dans la base de données.
Ce script corrige les chemins qui manquent le préfixe /static/ nécessaire pour Flask.
"""

import sqlite3
import json
import os

def fix_image_paths():
    """Corrige tous les chemins d'images incorrects dans la base de données"""
    
    # Connexion à la base de données
    db_path = 'instance/classe_numerique.db'
    if not os.path.exists(db_path):
        print(f"❌ Base de données non trouvée: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== CORRECTION AUTOMATIQUE DES CHEMINS D'IMAGES ===\n")
    
    try:
        # Récupérer tous les exercices avec des images
        cursor.execute('''
            SELECT id, title, image_path, content, exercise_type 
            FROM exercise 
            WHERE image_path IS NOT NULL AND image_path != ""
        ''')
        
        exercises = cursor.fetchall()
        
        if not exercises:
            print("[OK] Aucun exercice avec image trouve.")
            return
        
        corrections_made = 0
        
        for exercise in exercises:
            exercise_id, title, image_path, content_str, exercise_type = exercise
            
            print(f"[*] Exercice {exercise_id}: {title} ({exercise_type})")
            print(f"   Chemin actuel: {image_path}")
            
            # Vérifier si le chemin a besoin d'être corrigé
            needs_correction = False
            corrected_path = image_path
            
            if image_path and not image_path.startswith('/static/'):
                needs_correction = True
                
                if image_path.startswith('static/'):
                    # Cas: static/uploads/filename -> /static/uploads/filename
                    corrected_path = f"/{image_path}"
                elif image_path.startswith('uploads/'):
                    # Cas: uploads/filename -> /static/uploads/filename
                    corrected_path = f"/static/{image_path}"
                else:
                    # Cas: filename seul -> /static/uploads/filename
                    filename = os.path.basename(image_path)
                    corrected_path = f"/static/uploads/{filename}"
            
            # Corriger les chemins /static/exercises/ -> /static/uploads/
            elif image_path and image_path.startswith('/static/exercises/'):
                needs_correction = True
                filename = os.path.basename(image_path)
                corrected_path = f"/static/uploads/{filename}"
            
            if needs_correction:
                print(f"   --> Correction: {corrected_path}")
                
                # Mettre à jour exercise.image_path
                cursor.execute(
                    'UPDATE exercise SET image_path = ? WHERE id = ?',
                    (corrected_path, exercise_id)
                )
                
                # Mettre à jour content.image si le contenu existe
                if content_str:
                    try:
                        content = json.loads(content_str)
                        if 'image' in content:
                            old_content_image = content['image']
                            content['image'] = corrected_path
                            
                            cursor.execute(
                                'UPDATE exercise SET content = ? WHERE id = ?',
                                (json.dumps(content), exercise_id)
                            )
                            
                            print(f"   [+] Content image: {old_content_image} -> {corrected_path}")
                    except json.JSONDecodeError:
                        print(f"   [!] Erreur de parsing JSON pour le contenu")
                
                corrections_made += 1
            else:
                print(f"   [OK] Chemin deja correct")
            
            print()
        
        # Valider les changements
        conn.commit()
        
        print(f"[SUCCESS] CORRECTION TERMINEE")
        print(f"[INFO] {corrections_made} exercice(s) corrige(s) sur {len(exercises)} total")
        
        if corrections_made > 0:
            print("\n[OK] Tous les chemins d'images sont maintenant coherents avec le prefixe /static/")
            print("[OK] Les images devraient s'afficher correctement dans tous les exercices")
        
    except Exception as e:
        print(f"[ERROR] Erreur lors de la correction: {e}")
        conn.rollback()
    
    finally:
        conn.close()

def verify_corrections():
    """Vérifie que toutes les corrections ont été appliquées correctement"""
    
    db_path = 'instance/classe_numerique.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n=== VÉRIFICATION DES CORRECTIONS ===\n")
    
    try:
        cursor.execute('''
            SELECT id, title, image_path, content 
            FROM exercise 
            WHERE image_path IS NOT NULL AND image_path != ""
        ''')
        
        exercises = cursor.fetchall()
        incorrect_paths = 0
        
        for exercise in exercises:
            exercise_id, title, image_path, content_str = exercise
            
            # Vérifier exercise.image_path
            path_correct = image_path.startswith('/static/')
            path_in_correct_folder = not image_path.startswith('/static/exercises/')
            
            # Vérifier content.image
            content_correct = True
            content_in_correct_folder = True
            if content_str:
                try:
                    content = json.loads(content_str)
                    if 'image' in content:
                        content_correct = content['image'].startswith('/static/')
                        content_in_correct_folder = not content['image'].startswith('/static/exercises/')
                except:
                    content_correct = False
                    content_in_correct_folder = False
            
            if not path_correct or not content_correct or not path_in_correct_folder or not content_in_correct_folder:
                print(f"[ERROR] Exercice {exercise_id}: {title}")
                if not path_correct:
                    print(f"   - image_path incorrect: {image_path}")
                elif not path_in_correct_folder:
                    print(f"   - image_path utilise /static/exercises/ au lieu de /static/uploads/: {image_path}")
                if not content_correct:
                    print(f"   - content.image incorrect")
                elif not content_in_correct_folder:
                    print(f"   - content.image utilise /static/exercises/ au lieu de /static/uploads/")
                incorrect_paths += 1
            else:
                print(f"[OK] Exercice {exercise_id}: {title}")
        
        if incorrect_paths == 0:
            print(f"\n[SUCCESS] VERIFICATION REUSSIE: Tous les {len(exercises)} exercices ont des chemins corrects!")
        else:
            print(f"\n[WARNING] {incorrect_paths} exercice(s) ont encore des problemes")
    
    finally:
        conn.close()

def copy_images_if_needed():
    """Copie les images de /static/exercises/ vers /static/uploads/ si nécessaire"""
    import shutil
    
    print("\n=== COPIE DES IMAGES MANQUANTES ===\n")
    
    # Vérifier si les dossiers existent
    exercises_dir = 'static/exercises'
    uploads_dir = 'static/uploads'
    
    if not os.path.exists(exercises_dir):
        print(f"[INFO] Le dossier {exercises_dir} n'existe pas, aucune copie nécessaire")
        return
    
    if not os.path.exists(uploads_dir):
        print(f"[INFO] Création du dossier {uploads_dir}")
        os.makedirs(uploads_dir, exist_ok=True)
    
    # Copier les fichiers
    copied = 0
    for filename in os.listdir(exercises_dir):
        src_path = os.path.join(exercises_dir, filename)
        dst_path = os.path.join(uploads_dir, filename)
        
        if os.path.isfile(src_path) and not os.path.exists(dst_path):
            try:
                shutil.copy2(src_path, dst_path)
                print(f"[+] Copié: {src_path} -> {dst_path}")
                copied += 1
            except Exception as e:
                print(f"[ERROR] Impossible de copier {src_path}: {e}")
    
    print(f"\n[INFO] {copied} fichier(s) copié(s) vers {uploads_dir}")

if __name__ == "__main__":
    # Copier d'abord les images si nécessaire
    copy_images_if_needed()
    
    # Ensuite corriger les chemins dans la base de données
    fix_image_paths()
    verify_corrections()
