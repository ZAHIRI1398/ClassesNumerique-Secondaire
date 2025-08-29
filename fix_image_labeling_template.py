"""
Script pour corriger le template d'affichage des exercices image_labeling.
Ce script modifie le template pour afficher correctement l'image principale.
"""

import os
import re
import shutil
from datetime import datetime

def backup_file(file_path):
    """
    Crée une sauvegarde du fichier avant modification.
    """
    if not os.path.exists(file_path):
        print(f"[ERREUR] Le fichier {file_path} n'existe pas.")
        return False
        
    # Créer un nom de fichier de sauvegarde avec timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(os.path.dirname(file_path), f"backup_image_labeling_template_fix_{timestamp}")
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        
    backup_path = os.path.join(backup_dir, os.path.basename(file_path))
    shutil.copy2(file_path, backup_path)
    
    print(f"[INFO] Sauvegarde créée: {backup_path}")
    return True

def fix_image_labeling_template(template_path):
    """
    Corrige le template image_labeling.html pour afficher correctement l'image principale.
    
    Modifications:
    1. Remplacer l'utilisation de url_for('uploaded_file') par une référence directe à l'image
    2. Ajouter un paramètre de cache-busting
    """
    if not os.path.exists(template_path):
        print(f"[ERREUR] Le fichier template {template_path} n'existe pas.")
        return False
        
    # Lire le contenu du template
    with open(template_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Rechercher et remplacer la ligne problématique
    original_pattern = r'<img id="main-image" src="\{\{ url_for\(\'uploaded_file\', filename=content\.main_image\.replace\(\'/static/uploads/\',\'\'\)\.lstrip\(\'/\'\) \) \}\}"'
    replacement = '<img id="main-image" src="{{ content.main_image }}?v={{ range(1000000, 9999999) | random }}"'
    
    # Si le pattern exact n'est pas trouvé, essayer une version plus générique
    if not re.search(original_pattern, content):
        original_pattern = r'<img id="main-image" src="\{\{ url_for\(.*?filename=content\.main_image\.replace.*?\) \}\}"'
    
    # Effectuer le remplacement
    new_content = re.sub(original_pattern, replacement, content)
    
    # Vérifier si un remplacement a été effectué
    if new_content == content:
        print("[AVERTISSEMENT] Aucun remplacement effectué. Le pattern n'a pas été trouvé.")
        
        # Rechercher manuellement la ligne contenant 'main-image'
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'id="main-image"' in line and 'src=' in line:
                print(f"[INFO] Ligne trouvée ({i+1}): {line.strip()}")
                # Remplacer cette ligne spécifique
                lines[i] = '                                    <img id="main-image" src="{{ content.main_image }}?v={{ range(1000000, 9999999) | random }}" '
                new_content = '\n'.join(lines)
                print("[INFO] Remplacement manuel effectué.")
                break
    
    # Écrire le contenu modifié
    with open(template_path, 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    print(f"[SUCCES] Le template {template_path} a été modifié avec succès.")
    return True

def main():
    """
    Fonction principale pour exécuter le script.
    """
    # Chemins possibles vers le template
    template_paths = [
        'templates/exercise_types/image_labeling.html',
        'production_code/ClassesNumerique-Secondaire-main/templates/exercise_types/image_labeling.html'
    ]
    
    # Trouver le premier chemin valide
    template_path = None
    for path in template_paths:
        if os.path.exists(path):
            template_path = path
            break
    
    if not template_path:
        print("[ERREUR] Template image_labeling.html non trouvé.")
        return
    
    print(f"[INFO] Template trouvé: {template_path}")
    
    # Créer une sauvegarde
    if not backup_file(template_path):
        return
    
    # Corriger le template
    if fix_image_labeling_template(template_path):
        print("[SUCCES] Correction du template terminée avec succès.")
    else:
        print("[ERREUR] Échec de la correction du template.")

if __name__ == "__main__":
    main()
