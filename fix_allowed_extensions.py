"""
Script pour ajouter les extensions audio à la liste des extensions autorisées
"""

import os
import shutil
from datetime import datetime

# Créer une sauvegarde de modified_submit.py avant modification
def backup_file(file_path):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{file_path}.bak_audio_extensions_{timestamp}"
    shutil.copy2(file_path, backup_path)
    print(f"Sauvegarde créée: {backup_path}")
    return backup_path

# Correction du code dans modified_submit.py
def fix_allowed_extensions():
    file_path = 'modified_submit.py'
    backup_path = backup_file(file_path)
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Modification de la liste des extensions autorisées
    old_extensions = "ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}"
    new_extensions = "ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp3', 'wav', 'ogg', 'm4a'}"
    
    content = content.replace(old_extensions, new_extensions)
    
    # Écrire les modifications dans le fichier
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print("Extensions audio ajoutées avec succès dans modified_submit.py")
    return True

if __name__ == "__main__":
    print("Début de l'ajout des extensions audio à la liste des extensions autorisées...")
    success = fix_allowed_extensions()
    if success:
        print("Modification terminée avec succès!")
        print("Vous pouvez maintenant redémarrer l'application pour appliquer les modifications.")
    else:
        print("Une erreur est survenue lors de la modification.")
