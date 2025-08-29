"""
Script automatique pour corriger les chemins d'images dans tous les exercices de type image_labeling.
Ce script normalise les chemins d'images dans la base de données pour assurer un affichage correct.
"""

import os
import json
import sqlite3

def normalize_image_path(path):
    """
    Normalise un chemin d'image pour s'assurer qu'il commence par /static/uploads/
    """
    if not path:
        return path
        
    # Supprimer le préfixe /static/ s'il existe déjà
    if path.startswith('/static/'):
        path = path[8:]  # Enlever '/static/'
        
    # Supprimer le préfixe static/ s'il existe
    if path.startswith('static/'):
        path = path[7:]  # Enlever 'static/'
        
    # S'assurer que le chemin commence par uploads/
    if not path.startswith('uploads/'):
        if '/' in path:
            # Si le chemin contient déjà un dossier, remplacer ce dossier par uploads
            path = 'uploads/' + path.split('/', 1)[1]
        else:
            # Sinon, ajouter le préfixe uploads/
            path = 'uploads/' + path
            
    # Ajouter le préfixe /static/
    return '/static/' + path

def fix_image_labeling_exercises(db_path):
    """
    Corrige les chemins d'images dans tous les exercices de type image_labeling.
    
    Args:
        db_path (str): Chemin vers le fichier de base de données SQLite
    
    Returns:
        dict: Statistiques sur les corrections effectuées
    """
    print(f"[INFO] Utilisation de la base de donnees: {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Récupérer tous les exercices de type image_labeling
    query = "SELECT * FROM exercise WHERE exercise_type = 'image_labeling'"
    cursor.execute(query)
    exercises = cursor.fetchall()
    
    stats = {
        'total': len(exercises),
        'fixed_image_path': 0,
        'fixed_content_image': 0,
        'already_correct': 0,
        'errors': 0
    }
    
    print(f"[INFO] {stats['total']} exercices de type image_labeling trouvés.")
    
    for exercise in exercises:
        try:
            exercise_id = exercise['id']
            image_path = exercise['image_path']
            content_str = exercise['content']
            content = json.loads(content_str) if content_str else {}
            
            # Vérifier si l'exercice a un contenu valide
            if not content:
                print(f"[AVERTISSEMENT] L'exercice {exercise_id} n'a pas de contenu JSON valide.")
                stats['errors'] += 1
                continue
            
            # Vérifier si l'exercice a une image principale
            if 'main_image' not in content:
                print(f"[AVERTISSEMENT] L'exercice {exercise_id} n'a pas de champ main_image dans son contenu.")
                stats['errors'] += 1
                continue
            
            # Récupérer le chemin de l'image principale
            main_image = content.get('main_image', '')
            
            # Normaliser les chemins
            normalized_image_path = normalize_image_path(image_path) if image_path else None
            normalized_main_image = normalize_image_path(main_image) if main_image else None
            
            # Vérifier si des corrections sont nécessaires
            path_changed = normalized_image_path and normalized_image_path != image_path
            content_changed = normalized_main_image and normalized_main_image != main_image
            
            if path_changed or content_changed:
                # Mettre à jour exercise.image_path si nécessaire
                if path_changed:
                    cursor.execute(
                        "UPDATE exercise SET image_path = ? WHERE id = ?",
                        (normalized_image_path, exercise_id)
                    )
                    stats['fixed_image_path'] += 1
                    print(f"[SUCCES] Exercice {exercise_id}: image_path corrige: {image_path} -> {normalized_image_path}")
                
                # Mettre à jour content['main_image'] si nécessaire
                if content_changed:
                    content['main_image'] = normalized_main_image
                    cursor.execute(
                        "UPDATE exercise SET content = ? WHERE id = ?",
                        (json.dumps(content), exercise_id)
                    )
                    stats['fixed_content_image'] += 1
                    print(f"[SUCCES] Exercice {exercise_id}: main_image corrige: {main_image} -> {normalized_main_image}")
                
                # Synchroniser les deux champs si l'un est vide
                if not normalized_image_path and normalized_main_image:
                    cursor.execute(
                        "UPDATE exercise SET image_path = ? WHERE id = ?",
                        (normalized_main_image, exercise_id)
                    )
                    print(f"[SUCCES] Exercice {exercise_id}: image_path synchronise avec main_image: {normalized_main_image}")
                    stats['fixed_image_path'] += 1
                elif normalized_image_path and not normalized_main_image:
                    content['main_image'] = normalized_image_path
                    cursor.execute(
                        "UPDATE exercise SET content = ? WHERE id = ?",
                        (json.dumps(content), exercise_id)
                    )
                    print(f"[SUCCES] Exercice {exercise_id}: main_image synchronise avec image_path: {normalized_image_path}")
                    stats['fixed_content_image'] += 1
            else:
                stats['already_correct'] += 1
                print(f"[OK] Exercice {exercise_id}: Chemins d'images deja corrects.")
        
        except Exception as e:
            print(f"[ERREUR] Erreur lors du traitement de l'exercice {exercise_id}: {e}")
            stats['errors'] += 1
    
    # Valider les modifications
    conn.commit()
    conn.close()
    
    return stats

def main():
    """
    Fonction principale pour exécuter le script.
    """
    # Chemins possibles vers la base de données
    db_paths = [
        'instance/app.db',
        'instance/classe_numerique.db',
        'app.db',
        'classe_numerique.db'
    ]
    
    # Trouver le premier chemin valide
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("[ERREUR] Aucun fichier de base de donnees trouve.")
        return
    
    # Corriger tous les exercices
    stats = fix_image_labeling_exercises(db_path)
    print("[SUCCES] Correction terminee pour tous les exercices de type image_labeling.")
    
    # Afficher les statistiques
    print("\n[INFO] Statistiques:")
    print(f"- Total d'exercices traites: {stats['total']}")
    print(f"- Exercices avec image_path corrige: {stats['fixed_image_path']}")
    print(f"- Exercices avec main_image corrige: {stats['fixed_content_image']}")
    print(f"- Exercices deja corrects: {stats['already_correct']}")
    print(f"- Erreurs: {stats['errors']}")

if __name__ == "__main__":
    main()
