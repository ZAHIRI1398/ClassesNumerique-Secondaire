import os
import sys
import json
import sqlite3
import argparse
from pathlib import Path

def connect_to_db(db_path):
    """Établit une connexion à la base de données SQLite"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Erreur de connexion à la base de données: {e}")
        sys.exit(1)

def get_all_exercises(conn, exercise_types=None):
    """Récupère tous les exercices du type spécifié"""
    cursor = conn.cursor()
    
    if exercise_types:
        placeholders = ','.join(['?' for _ in exercise_types])
        query = f"SELECT * FROM exercise WHERE exercise_type IN ({placeholders})"
        cursor.execute(query, exercise_types)
    else:
        cursor.execute("SELECT * FROM exercise")
    
    return cursor.fetchall()

def check_image_path_consistency(exercise):
    """Vérifie la cohérence entre exercise.image_path et content.main_image"""
    try:
        content = json.loads(exercise['content']) if exercise['content'] else {}
        
        # Récupérer les chemins d'images
        image_path = exercise['image_path']
        content_image = content.get('main_image')
        
        # Vérifier la cohérence
        if image_path and content_image and image_path != content_image:
            return False, f"Incohérence: image_path='{image_path}', content.main_image='{content_image}'"
        elif image_path and not content_image:
            return False, f"Incohérence: image_path existe ('{image_path}') mais content.main_image n'existe pas"
        elif not image_path and content_image:
            return False, f"Incohérence: content.main_image existe ('{content_image}') mais image_path n'existe pas"
        
        return True, "Cohérent"
    except json.JSONDecodeError:
        return False, "Erreur de décodage JSON du contenu"

def check_image_file_exists(base_path, image_path):
    """Vérifie si le fichier image existe physiquement"""
    if not image_path:
        return False, "Pas de chemin d'image"
    
    # Normaliser le chemin d'image
    norm_path = image_path.lstrip('/')
    full_path = os.path.join(base_path, norm_path)
    
    if os.path.exists(full_path):
        return True, f"Fichier trouvé: {full_path}"
    else:
        return False, f"Fichier manquant: {full_path}"

def fix_image_path(exercise, conn):
    """Corrige l'incohérence entre exercise.image_path et content.main_image"""
    try:
        content = json.loads(exercise['content']) if exercise['content'] else {}
        
        # Récupérer les chemins d'images
        image_path = exercise['image_path']
        content_image = content.get('main_image')
        
        # Stratégie de correction
        if image_path and content_image and image_path != content_image:
            # Priorité à content.main_image car c'est ce qui est affiché dans le template
            new_image_path = content_image
            cursor = conn.cursor()
            cursor.execute("UPDATE exercise SET image_path = ? WHERE id = ?", 
                          (new_image_path, exercise['id']))
            conn.commit()
            return True, f"Corrigé: image_path mis à jour de '{image_path}' à '{new_image_path}'"
        
        elif image_path and not content_image:
            # Ajouter image_path à content.main_image
            content['main_image'] = image_path
            new_content = json.dumps(content)
            cursor = conn.cursor()
            cursor.execute("UPDATE exercise SET content = ? WHERE id = ?", 
                          (new_content, exercise['id']))
            conn.commit()
            return True, f"Corrigé: content.main_image ajouté avec la valeur '{image_path}'"
        
        elif not image_path and content_image:
            # Ajouter content.main_image à image_path
            cursor = conn.cursor()
            cursor.execute("UPDATE exercise SET image_path = ? WHERE id = ?", 
                          (content_image, exercise['id']))
            conn.commit()
            return True, f"Corrigé: image_path ajouté avec la valeur '{content_image}'"
        
        return False, "Aucune correction nécessaire"
    
    except (json.JSONDecodeError, sqlite3.Error) as e:
        return False, f"Erreur lors de la correction: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="Vérifier la cohérence des chemins d'images dans les exercices")
    parser.add_argument("--db", default="instance/app.db", help="Chemin vers la base de données SQLite")
    parser.add_argument("--base-path", default=".", help="Chemin de base pour vérifier l'existence des fichiers")
    parser.add_argument("--types", nargs="+", default=["legend", "image_labeling"], 
                        help="Types d'exercices à vérifier (par défaut: legend et image_labeling)")
    parser.add_argument("--fix", action="store_true", help="Corriger les incohérences trouvées")
    parser.add_argument("--verbose", action="store_true", help="Afficher des informations détaillées")
    
    args = parser.parse_args()
    
    # Vérifier que la base de données existe
    if not os.path.exists(args.db):
        print(f"Erreur: La base de données '{args.db}' n'existe pas")
        sys.exit(1)
    
    # Connexion à la base de données
    conn = connect_to_db(args.db)
    
    # Récupérer les exercices
    exercises = get_all_exercises(conn, args.types)
    print(f"Analyse de {len(exercises)} exercices de type {', '.join(args.types)}...")
    
    # Statistiques
    total = len(exercises)
    consistent = 0
    inconsistent = 0
    fixed = 0
    files_missing = 0
    
    # Vérifier chaque exercice
    for exercise in exercises:
        exercise_id = exercise['id']
        exercise_title = exercise['title']
        exercise_type = exercise['exercise_type']
        
        if args.verbose:
            print(f"\n--- Exercice {exercise_id}: {exercise_title} (Type: {exercise_type}) ---")
        
        # Vérifier la cohérence des chemins
        is_consistent, consistency_msg = check_image_path_consistency(exercise)
        
        if is_consistent:
            consistent += 1
            if args.verbose:
                print(f"[OK] Chemins cohérents")
        else:
            inconsistent += 1
            print(f"[ERREUR] Exercice {exercise_id}: {consistency_msg}")
            
            # Corriger si demandé
            if args.fix:
                is_fixed, fix_msg = fix_image_path(exercise, conn)
                if is_fixed:
                    fixed += 1
                    print(f"  [CORRIGÉ] {fix_msg}")
                else:
                    print(f"  [AVERTISSEMENT] {fix_msg}")
        
        # Vérifier l'existence du fichier image
        image_path = exercise['image_path']
        if image_path:
            file_exists, file_msg = check_image_file_exists(args.base_path, image_path)
            if not file_exists:
                files_missing += 1
                print(f"[AVERTISSEMENT] Exercice {exercise_id}: {file_msg}")
            elif args.verbose:
                print(f"[OK] {file_msg}")
    
    # Afficher les statistiques
    print("\n=== Résumé ===")
    print(f"Total d'exercices analysés: {total}")
    print(f"Exercices avec chemins cohérents: {consistent} ({consistent/total*100:.1f}%)")
    print(f"Exercices avec chemins incohérents: {inconsistent} ({inconsistent/total*100:.1f}%)")
    if args.fix:
        print(f"Exercices corrigés: {fixed}")
    print(f"Fichiers images manquants: {files_missing}")
    
    conn.close()

if __name__ == "__main__":
    main()
