"""
Script pour modifier le code de création des exercices image_labeling afin de synchroniser
exercise.image_path et content.main_image.
"""

import os
import re
import shutil
import time

def find_app_py():
    """
    Recherche le fichier app.py dans différents emplacements possibles.
    
    Returns:
        str: Chemin vers le fichier app.py trouvé, ou None si non trouvé
    """
    possible_paths = [
        'app.py',
        'production_code/ClassesNumerique-Secondaire-main/app.py',
        'production_code/app.py'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def backup_file(file_path):
    """
    Crée une sauvegarde du fichier spécifié.
    
    Args:
        file_path (str): Chemin vers le fichier à sauvegarder
        
    Returns:
        str: Chemin vers le fichier de sauvegarde
    """
    if not os.path.exists(file_path):
        print(f"[ERREUR] Le fichier {file_path} n'existe pas.")
        return None
        
    backup_path = f"{file_path}.backup_{int(time.time())}"
    shutil.copy2(file_path, backup_path)
    print(f"[INFO] Sauvegarde créée: {backup_path}")
    return backup_path

def fix_image_labeling_creation(app_py_path):
    """
    Modifie le code de création des exercices image_labeling pour synchroniser
    exercise.image_path et content.main_image.
    
    Args:
        app_py_path (str): Chemin vers le fichier app.py
        
    Returns:
        bool: True si la modification a été effectuée avec succès, False sinon
    """
    if not os.path.exists(app_py_path):
        print(f"[ERREUR] Le fichier {app_py_path} n'existe pas.")
        return False
        
    with open(app_py_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Rechercher le code de création des exercices image_labeling
    image_labeling_pattern = re.compile(
        r'(elif exercise_type == [\'"]image_labeling[\'"].*?'
        r'content\s*=\s*{.*?[\'"]main_image[\'"]\s*:\s*[\'"]([^\'"]*)[\'"](.*?)}\s*'
        r'exercise\s*=\s*Exercise\(.*?\))',
        re.DOTALL
    )
    
    match = image_labeling_pattern.search(content)
    
    if not match:
        print("[ERREUR] Code de création des exercices image_labeling non trouvé.")
        return False
    
    # Extraire le bloc de code complet
    full_block = match.group(1)
    
    # Vérifier si exercise.image_path est déjà défini correctement
    if "exercise.image_path = content['main_image']" in full_block:
        print("[INFO] La synchronisation est déjà présente dans le code.")
        return True
    
    # Trouver l'endroit où ajouter la synchronisation
    exercise_creation_pattern = re.compile(r'(exercise\s*=\s*Exercise\(.*?\))', re.DOTALL)
    exercise_creation_match = exercise_creation_pattern.search(full_block)
    
    if not exercise_creation_match:
        print("[ERREUR] Bloc de création d'exercice non trouvé.")
        return False
    
    exercise_creation = exercise_creation_match.group(1)
    
    # Ajouter la synchronisation après la création de l'exercice
    modified_block = full_block.replace(
        exercise_creation,
        f"{exercise_creation}\n        exercise.image_path = content['main_image']  # Synchronisation avec content.main_image"
    )
    
    # Remplacer le bloc original par le bloc modifié
    modified_content = content.replace(full_block, modified_block)
    
    # Écrire le contenu modifié dans le fichier
    with open(app_py_path, 'w', encoding='utf-8') as file:
        file.write(modified_content)
    
    print("[SUCCÈS] Code de création des exercices image_labeling modifié avec succès.")
    return True

def main():
    """
    Fonction principale pour exécuter le script.
    """
    print("[INFO] Recherche du fichier app.py...")
    app_py_path = find_app_py()
    
    if not app_py_path:
        print("[ERREUR] Fichier app.py non trouvé.")
        return
    
    print(f"[INFO] Fichier app.py trouvé: {app_py_path}")
    
    # Créer une sauvegarde du fichier
    backup_path = backup_file(app_py_path)
    
    if not backup_path:
        print("[ERREUR] Impossible de créer une sauvegarde du fichier app.py.")
        return
    
    # Modifier le code de création des exercices
    if fix_image_labeling_creation(app_py_path):
        print("[SUCCÈS] Le code de création des exercices image_labeling a été modifié avec succès.")
        print("[INFO] La synchronisation entre exercise.image_path et content.main_image est maintenant assurée.")
    else:
        print("[ERREUR] Échec de la modification du code de création des exercices.")
        print(f"[INFO] Vous pouvez restaurer la sauvegarde depuis {backup_path}")

if __name__ == "__main__":
    main()
